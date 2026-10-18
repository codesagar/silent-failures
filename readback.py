"""Post-write re-reading metric, committed with explicit definitions (TRANSPARENCY item 10).

The REPORT v1 "read-back verification" rates were computed ad hoc and never committed
(adversarial-construct Finding 4 / TRANSPARENCY #10). This script is the authoritative
re-derivation, with the constructs the review demanded:

Definitions (all mechanical, auditable below):
  WRITE call  = tool name starting with: add_ append_ create_ delete_ invite_ post_
                remove_ reschedule_ reserve_ schedule_ send_ share_ update_
  READ call   = tool name starting with: check_ get_ list_ read_ search_
  (every tool name observed in the arm is printed with its class; unmapped names are fatal)
  Denominator = empty_result-arm episodes (p=0.5) containing >=1 WRITE call, after the
                remediated-primary filters (no harness_error, no below-cap artifact,
                no hidden-rerun, reps r0-r3).
  POST-WRITE RE-READ = >=1 READ call strictly after the episode's LAST WRITE call.
    Split: "repeat" = that read's (function, args) already occurred earlier in the episode
           (observationally identical to a blind retry under empty_result);
           "novel"  = first occurrence of that (function, args).
RENAMED CONSTRUCT: this is "post-write re-reading". Verification intent and blind retry
are NOT separable in this design (the suppressed read gives no signal of why it was made);
read-only tasks are excluded and counted (the Class-B narrative must not cite this metric
for them).
"""
import json
from collections import Counter
from pathlib import Path

from probe_classify import jeffreys

WRITE_PRE = ("add_", "append_", "create_", "delete_", "invite_", "post_", "remove_",
             "reschedule_", "reserve_", "schedule_", "send_", "share_", "update_")
READ_PRE = ("check_", "get_", "list_", "read_", "search_")

PREV_STATED = {"glm-5.3-flash": "8%", "kimi-k3": "8%", "nemotron": "3%",
               "gpt-6-luna": "2%", "qwen-ablated": "29%"}


def classify_tool(name):
    if name.startswith(WRITE_PRE):
        return "W"
    if name.startswith(READ_PRE):
        return "R"
    raise SystemExit(f"UNMAPPED TOOL NAME: {name} — extend the mapping explicitly")


def calls_of(transcript_path):
    msgs = json.loads(Path(transcript_path).read_text())["messages"]
    calls = []
    for m in msgs:
        if m.get("tool_calls"):
            for tc in m["tool_calls"]:
                calls.append((tc["function"], json.dumps(tc.get("args") or {}, sort_keys=True)))
    return calls


def main():
    rows = []
    for f in Path("results").glob("*.jsonl"):
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if (r["error_type"] == "empty_result" and not r.get("harness_error")
                        and r["rep"] <= 3
                        and not (r.get("final_empty") and (r.get("assistant_turns") or 0) < 16)
                        and not ((r.get("tool_calls_total") or 0) > (r.get("tool_msgs") or 0))):
                    rows.append(r)
    print(f"empty_result arm after remediated-primary filters: {len(rows)}")

    seen_tools = Counter()
    stats = {}
    for r in rows:
        calls = calls_of(r["transcript"])
        for name, _ in calls:
            seen_tools[name] += 1
        kinds = [classify_tool(n) for n, _ in calls]
        if "W" not in kinds:
            r["_class"] = "no-write"
            continue
        last_w = max(i for i, k in enumerate(kinds) if k == "W")
        post = [(i, calls[i]) for i in range(last_w + 1, len(calls)) if kinds[i] == "R"]
        if not post:
            r["_class"] = "no-reread"
        else:
            earlier = set(calls[:post[0][0]])
            novel = any(c not in earlier for _, c in post)
            r["_class"] = "reread-novel" if novel else "reread-repeat"

    lines = []
    w = lines.append
    w("# Post-write re-reading (renamed from 'read-back verification'; TRANSPARENCY item 10)\n")
    w("Script: readback.py (this file is the first committed derivation; the v1 numbers were")
    w("ad hoc and are shown for comparison). Definitions in the script docstring. Verification")
    w("and blind retry are NOT separable in this design; 'most-verifying model' claims are")
    w("retired in favor of 'most re-reading model'.\n")
    w("Tool-name classes observed in the arm (mechanical prefix mapping):")
    w("- WRITE: " + ", ".join(sorted(n for n in seen_tools if classify_tool(n) == "W")))
    w("- READ: " + ", ".join(sorted(n for n in seen_tools if classify_tool(n) == "R")) + "\n")
    w("| model | episodes w/ >=1 write | post-write re-read (any) | ...novel (function,args) | ...repeat-only | read-only episodes (excluded) | v1 stated |")
    w("|---|---|---|---|---|---|---|")
    for m in ("gpt-6-luna", "glm-5.3-flash", "kimi-k3", "nemotron", "qwen-ablated"):
        sub = [r for r in rows if r["model"] == m]
        wr = [r for r in sub if r.get("_class") != "no-write"]
        n = len(wr)
        any_rr = sum(1 for r in wr if r["_class"].startswith("reread"))
        novel = sum(1 for r in wr if r["_class"] == "reread-novel")
        rep = sum(1 for r in wr if r["_class"] == "reread-repeat")
        nowrite = len(sub) - n

        def f(k):
            lo, hi = jeffreys(k, n)
            return f"{100*k/n:.1f}% [{100*lo:.1f},{100*hi:.1f}]"
        w(f"| {m} | {n} | {f(any_rr)} | {f(novel)} | {f(rep)} | {nowrite} | {PREV_STATED[m]} |")
    text = "\n".join(lines)
    Path("READBACK.md").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
