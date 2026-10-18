# Pending pre-registered analyses

## Non-determinism supplement (core 16 tasks, 8 reps/cell, timeout arm)

Question: how much does the SAME model on the SAME task/condition vary run-to-run?

8-rep cells found: 480

| model | mean within-cell utility SD | cells with BOTH outcomes (flaky) | flakiest p |
|---|---|---|---|
| glm-5.3-flash | 0.107 | 25/96 (26%) | p=0.75 |
| gpt-6-luna | 0.181 | 41/96 (43%) | p=0.5 |
| kimi-k3 | 0.139 | 32/96 (33%) | p=0.75 |
| nemotron | 0.166 | 39/96 (41%) | p=0.75 |
| qwen-ablated | 0.093 | 21/96 (22%) | p=0.75 |

## Persistence micro-metrics (failed episodes, timeout arm, p>=0.5)

| model | mean retries of an already-errored tool | mean distinct tools tried | max retry streak |
|---|---|---|---|
| glm-5.3-flash | 5.5 | 3.0 | 19 | (n=400)
| gpt-6-luna | 1.8 | 2.4 | 15 | (n=400)
| kimi-k3 | 5.7 | 2.4 | 23 | (n=400)
| nemotron | 6.0 | 2.8 | 16 | (n=400)
| qwen-ablated | 12.9 | 4.5 | 25 | (n=400)

## Capability-conditioned conduct (prereg rule: tasks the model passes >=3/4 control reps)

| model | capable tasks | fabrication p>=.75 (capable-only) | silent spin p>=.75 (capable-only) |
|---|---|---|---|
| glm-5.3-flash | 90/97 | 0.9% (n=570) | 14.0% |
| gpt-6-luna | 83/97 | 0.4% (n=677) | 0.4% |
| kimi-k3 | 90/97 | 1.8% (n=612) | 13.2% |
| nemotron | 90/97 | 3.8% (n=611) | 13.3% |
| qwen-ablated | 93/97 | 1.6% (n=634) | 91.2% |