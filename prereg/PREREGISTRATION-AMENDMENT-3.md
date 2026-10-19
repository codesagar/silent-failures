# Amendment 3 — worker-death incident, re-run policy, supervised relaunch (2026-10-17 ~15:00)

## Incident

At ~13:25–13:30, all 19 then-running worker processes (qwen-ablated ×3, kimi-k3 ×16) died
silently and simultaneously; the three completed models' workers had already exited with
DONE. Root cause **undetermined**: user-slice cgroup shows `oom_kill 0` and no memory limit
(memory exonerated); user journal empty for the window; no tracebacks. The simultaneity and
the fact that all victims shared the launching tool-session's scope point at session-scope
cleanup, but this is inference, not evidence. Data integrity is unaffected: episodes are
atomic (an interrupted episode writes no record), resume is id-based, and the QA audit
(`qa_check.py`) shows zero duplicates and zero partial records.

## Re-run policy (decided before any aggregated analysis)

Treated as instrument failures and **re-run once** via the normal resume path:
- 30 qwen-ablated episodes with recorded endpoint failures (HTTP 503 / connection errors);
- 65 below-loop-cap empty-generation episodes (63 kimi, 2 qwen) — mechanism verified by
  probe: thinking exhausts the output budget (`finish_reason=length`), an artifact of the
  serving stack, not conduct. Recurrences on re-run stay excluded and are reported in the
  artifact count. Silent-spin remains defined as empty final AT the 16-turn loop cap.

## Execution changes

Remaining work (596 qwen, 1,425 kimi episodes) relaunched as **systemd user units**
(`sf-qwen-*`, `sf-kimi-*`; linger is enabled, so they run under the persistent user manager,
independent of any login session; `Restart=on-failure` self-heals; terminations are
journaled). Lane counts reduced: qwen 3 → 2 (its llama.cpp server returned 503s under 3-way
load), kimi 16 → 12 (gateway latency spikes up to ~98 min/episode under 16-way load).

No changes to hypotheses, measures, grading, or analysis rules.
