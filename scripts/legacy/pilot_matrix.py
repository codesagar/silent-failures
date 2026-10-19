"""Pilot matrix: 2 models x {control, transient, persistent} x 3 reps on user_task_0, temp 0.7."""
import json
import time
from pathlib import Path

import openai
from agentdojo.agent_pipeline import (
    AgentPipeline, InitQuery, OpenAILLM, SystemMessage, ToolsExecutionLoop, ToolsExecutor,
)
from agentdojo.benchmark import run_task_without_injection_tasks
from agentdojo.logging import OutputLogger
from agentdojo.task_suite.load_suites import get_suite

from pilot import ENDPOINTS, inject_failure

BROKEN = ["search_calendar_events", "get_day_calendar_events"]
TASK = "user_task_0"
OUT = Path("pilot_results.jsonl")

results = []
for model_name in ["nemotron", "qwen-ablated"]:
    base_url, model = ENDPOINTS[model_name]
    for mode in ["control", "transient", "persistent"]:
        for rep in range(3):
            suite = get_suite("v1.2.1", "workspace")  # fresh tools each run
            stats = {"calls": 0, "failed": 0}
            restore = lambda: None
            if mode != "control":
                stats, restore = inject_failure(suite, BROKEN, mode)
            client = openai.OpenAI(base_url=base_url, api_key="local", timeout=600)
            llm = OpenAILLM(client, model, temperature=0.7)
            pipeline = AgentPipeline([
                SystemMessage("You are a helpful assistant with access to tools."),
                InitQuery(), llm,
                ToolsExecutionLoop([ToolsExecutor(), llm]),
            ])
            pipeline.name = f"{model_name}-{mode}-r{rep}"
            task = suite.user_tasks[TASK]
            t0 = time.time()
            try:
                with OutputLogger(logdir="logs"):
                    utility, _ = run_task_without_injection_tasks(
                        suite, pipeline, task, logdir=Path("logs"), force_rerun=True)
                err = None
            except Exception as e:  # endpoint hiccups: record, continue
                utility, err = None, f"{type(e).__name__}: {e}"
            finally:
                restore()
            dt = time.time() - t0

            rec = {"model": model_name, "mode": mode, "rep": rep, "utility": utility,
                   "injected_failures": stats["failed"], "secs": round(dt, 1), "error": err}
            log = Path("logs") / pipeline.name / "workspace" / TASK / "none" / "none.json"
            if log.exists():
                msgs = json.loads(log.read_text())["messages"]
                finals = [m for m in msgs if m["role"] == "assistant" and m.get("content")
                          and not m.get("tool_calls")]
                final = ""
                if finals:
                    c = finals[-1]["content"]
                    final = c if isinstance(c, str) else " ".join(str(x.get("content", x)) for x in c)
                rec.update({
                    "assistant_turns": sum(1 for m in msgs if m["role"] == "assistant"),
                    "tool_errors": sum(1 for m in msgs if m["role"] == "tool" and m.get("error")),
                    "final_empty": not final.strip(),
                    "final_message": final[:400],
                })
            results.append(rec)
            OUT.write_text("\n".join(json.dumps(r) for r in results))
            print(f"{pipeline.name}: utility={utility} turns={rec.get('assistant_turns')} "
                  f"tool_errors={rec.get('tool_errors')} empty_final={rec.get('final_empty')} {dt:.0f}s",
                  flush=True)
print("DONE")
