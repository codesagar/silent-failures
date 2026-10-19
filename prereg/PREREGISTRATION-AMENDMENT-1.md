# Amendment 1 — scope expansion (2026-10-18, ~1h into the run)

**When decided:** after observing per-episode throughput and streaming progress lines
(episode durations, running utility flags), **before any aggregated analysis** — `analyze.py`
had not been run on the collected data. Hypotheses, outcome measures, grading, and analysis
rules are UNCHANGED from PREREGISTRATION.md.

## Changes

1. **Task set expanded 16 → all 97 benign user tasks** across the four AgentDojo v1.2.1
   suites (workspace 40, travel 20, banking 16, slack 21) for nemotron, qwen-ablated,
   glm-5.3-flash, gpt-6-luna. Motivation: eliminate task-selection bias; capacity allows it.
2. **Non-determinism supplement:** on the original 16 core tasks, rate-sweep reps 4 → 8
   (reps r4–r7 added) for all five models, to quantify run-to-run behavioral variance at
   fixed condition.
3. **kimi-k3 capacity exception:** measured ~110 s/episode (~20× slower than peers).
   kimi keeps the original 16-task matrix plus the supplement (960 episodes). This is a
   throughput decision made before analysis; kimi's results are reported on the core-16
   subset and compared to other models on that same subset only.
4. **Execution:** per-model worker processes sharded by sha256(run_id) mod N
   (nemotron 2, qwen-ablated 3, gateway models 6 each); shards are separate OS processes
   with no shared Python state; per-shard result files. Episode definitions, run_ids, and
   seeds are unchanged — the first hour's 1,100+ episodes remain valid and are not re-run.

## Updated totals

3,876 episodes × 4 models + 960 × 1 model ≈ 16,464 episodes.

## Risk note

Gateway concurrency (6 processes/model) may hit rate limits; the OpenAI SDK retries with
backoff, failures surface as `harness_error` records and are excluded + reported per the
pre-registered rule. The ordered cut list from PREREGISTRATION.md still applies; cuts fire
on wall-clock pressure only.
