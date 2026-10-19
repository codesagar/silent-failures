# Amendment 2 — kimi-k3 parity override (2026-10-18, ~2h into the run)

The study owner overrode Amendment 1's kimi-k3 capacity exception: **all five models now
run the identical full matrix** (97 tasks, full rate/type sweeps + non-determinism
supplement). kimi-k3 runs with 16 worker shards due to its ~110 s/episode latency.
Decision made before any aggregated analysis.

Known risk, stated in advance: kimi may not complete by the reporting deadline. Worker
cell order is now seeded-shuffled (all models), so any partial completion is approximately
uniform over tasks and conditions, and every reported cell carries its realized n.

No changes to hypotheses, measures, grading, or analysis rules.
