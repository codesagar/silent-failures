"""Smoke test: run one benign AgentDojo workspace task against an h200 vLLM endpoint."""
from endpoints import EP
import sys
from pathlib import Path

import openai
from agentdojo.logging import OutputLogger
from agentdojo.agent_pipeline import (
    AgentPipeline, InitQuery, OpenAILLM, SystemMessage, ToolsExecutionLoop, ToolsExecutor,
)
from agentdojo.benchmark import run_task_without_injection_tasks
from agentdojo.task_suite.load_suites import get_suite

ENDPOINTS = {
    "llama-70b": (EP["llama_url"], "meta/llama-3.3-70b-instruct"),
    "nemotron": (EP["nemotron_url"], "nemotron-3.5-super-vl"),
    "qwen-ablated": (EP["qwen_url"], "qwen-ablated"),
}

name = sys.argv[1] if len(sys.argv) > 1 else "llama-70b"
task_id = sys.argv[2] if len(sys.argv) > 2 else "user_task_0"
base_url, model = ENDPOINTS[name]

client = openai.OpenAI(base_url=base_url, api_key="local", timeout=600)
llm = OpenAILLM(client, model, temperature=0.0)
pipeline = AgentPipeline([
    SystemMessage("You are a helpful assistant with access to tools."),
    InitQuery(),
    llm,
    ToolsExecutionLoop([ToolsExecutor(), llm]),
])
pipeline.name = f"{name}-smoke"

suite = get_suite("v1.2.1", "workspace")
task = suite.user_tasks[task_id]
print(f"Running {task_id} on {name}: {task.PROMPT[:80]}...")
with OutputLogger(logdir="logs"):
    utility, security = run_task_without_injection_tasks(
        suite, pipeline, task, logdir=Path("logs"), force_rerun=True,
    )
print(f"RESULT utility={utility} security={security}")
