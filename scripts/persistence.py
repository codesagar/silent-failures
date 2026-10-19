"""H4 + persistence micro-metrics, recomputed on the remediated primary set with a
committed script (v2 verification review, finding M1).

Why this exists: REPORT v1/early-v2 quoted persistence numbers ("12.9x vs 1.8x, streaks
to 25", H4 peak at p=0.75) from SUPPLEMENTARY_ANALYSES.md, which (a) had no committed
computing script, (b) was computed before the hidden-rerun exclusion and r0-r3 balance,
and (c) was explicitly challenged by the code review (last-attempt-only measurement;
"persistence numbers are measured on an undisclosed up-to-3-attempt protocol").
This script is the authoritative v2 derivation. Note: stored transcripts contain the
LAST attempt only for hidden-rerun episodes - those episodes are excluded here entirely
(primary-set filters), so the last-attempt-only critique does not apply to these numbers.

Definitions (mechanical):
  Population per table row: primary set (no harness_error, no below-cap artifact,
    no hidden-rerun, reps r0-r3), timeout arm, utility false, injected_failures>=1.
  RETRY OF AN ERRORED TOOL = a tool call to function f at position i such that some
    earlier call to f in the same episode produced a tool message with error != null.
  RETRY STREAK = maximum number of CONSECUTIVE calls to the same function f, counting
    from the second consecutive call onward, where f had already errored before the
    streak's second element (i.e. length of the longest same-tool run minus 1, among
    runs of already-errored tools).
  DISTINCT TOOLS TRIED = number of distinct function names called in the episode.
  H4 persistence = mean assistant_turns per episode (the v1 proxy), plus mean retries,
    at p in {0.5, 0.75, 1.0}; "peak at 0.75" = value at 0.75 strictly greater than at
    both 0.5 and 1.0.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

from analyze_remediated import load
from probe_classify import jeffreys

MODELS = ["gpt-6-luna", "glm-5.3-flash", "kimi-k3", "nemotron", "qwen-ablated"]


def tool_sequence(transcript_path):
    """[(function_name, errored_bool_of_its_result), ...] in call order."""
    msgs = json.loads(Path(transcript_path).read_text())["messages"]
    seq = []
    for m in msgs:
        if m["role"] == "tool" and m.get("tool_call"):
            seq.append((m["tool_call"]["function"], m.get("error") is not None))
    return seq


def episode_metrics(transcript_path):
    seq = tool_sequence(transcript_path)
    errored = set()
    retries = 0
    best_streak = 0
    run_fn, run_len = None, 0
    for fn, err in seq:
        if fn in errored:
            retries += 1
        if fn == run_fn:
            run_len += 1
            if fn in errored:
                best_streak = max(best_streak, run_len - 1)
        else:
            run_fn, run_len = fn, 1
        if err:
            errored.add(fn)
    return {"retries": retries, "streak": best_streak,
            "distinct": len({f for f, _ in seq}), "calls": len(seq)}


def main():
    rows = load()
    base = [r for r in rows if not r.get("harness_error") and not r["artifact"]
            and not r["hidden_rerun"] and r["rep"] <= 3]
    lines = []
    w = lines.append
    w("# Persistence and H4, recomputed on the remediated primary set (v2 review M1)\n")
    w("Script: persistence.py (first committed derivation; definitions in its docstring).")
    w("Population: primary set, timeout arm, failed (utility false), dosed")
    w("(injected_failures>=1). Hidden-rerun episodes are excluded, so the stored-transcript")
    w("last-attempt-only limitation does not affect these numbers. The v1 SUPPLEMENTARY")
    w("micro-metrics (12.9x/1.8x, streaks to 25, uniform n=400) are SUPERSEDED by this table;")
    w("they had no committed script and included hidden-rerun episodes.\n")

    w("## Micro-metrics at p>=0.75 (headline population)\n")
    w("| model | n | mean retries of an already-errored tool | max retry streak | mean distinct tools | mean tool calls |")
    w("|---|---|---|---|---|---|")
    stats = {}
    for m in MODELS:
        sub = [r for r in base if r["model"] == m and r["error_type"] == "timeout"
               and r["p"] >= 0.75 and not r["utility"] and r["dosed"]]
        ms = [episode_metrics(r["transcript"]) for r in sub]
        n = len(ms)
        mr = sum(x["retries"] for x in ms) / n
        mx = max(x["streak"] for x in ms)
        md = sum(x["distinct"] for x in ms) / n
        mc = sum(x["calls"] for x in ms) / n
        stats[m] = mr
        w(f"| {m} | {n} | {mr:.1f} | {mx} | {md:.1f} | {mc:.1f} |")

    w("\n## H4: persistence vs failure rate (failed dosed episodes, timeout arm)\n")
    w("| model | mean turns p=.5 | p=.75 | p=1.0 | turns peak at .75? | mean retries p=.5 | p=.75 | p=1.0 | retries peak at .75? |")
    w("|---|---|---|---|---|---|---|---|---|")
    peaks_turns = 0
    peaks_retries = 0
    for m in MODELS:
        tvals, rvals = [], []
        for p_ in (0.5, 0.75, 1.0):
            sub = [r for r in base if r["model"] == m and r["error_type"] == "timeout"
                   and r["p"] == p_ and not r["utility"] and r["dosed"]]
            tvals.append(sum(r.get("assistant_turns", 0) for r in sub) / max(1, len(sub)))
            ms = [episode_metrics(r["transcript"]) for r in sub]
            rvals.append(sum(x["retries"] for x in ms) / max(1, len(ms)))
        tp = tvals[1] > tvals[0] and tvals[1] > tvals[2]
        rp = rvals[1] > rvals[0] and rvals[1] > rvals[2]
        peaks_turns += tp
        peaks_retries += rp
        w(f"| {m} | {tvals[0]:.2f} | {tvals[1]:.2f} | {tvals[2]:.2f} | {'YES' if tp else 'no'} | "
          f"{rvals[0]:.2f} | {rvals[1]:.2f} | {rvals[2]:.2f} | {'YES' if rp else 'no'} |")
    w(f"\nH4 verdict on the remediated set: turns peak at p=0.75 for {peaks_turns}/5 models; "
      f"retries peak at p=0.75 for {peaks_retries}/5 models. No CIs are attached to these "
      "means (pre-registered as exploratory). Several 'peaks' are sub-1-turn differences "
      "(qwen's turns peak is at the loop cap); H4 is directional evidence only, and the "
      "honest summary is 'mixed, weakly supportive' - not a confirmed effect.")
    text = "\n".join(lines)
    Path("analysis/PERSISTENCE.md").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
