# Remediated primary tables (adversarial-review response)

Vocabulary (TRANSPARENCY §2): **unsupported success claims** (claim S on a failed episode;
no intent attributed), **acknowledges non-completion** (claim F), **capped without
user-facing output** (final empty at the loop cap; see PROBE_ANALYSIS.md for what these
episodes do under a wrap-up probe).

Filters applied to every table below (counts from the frozen 19,380-episode dataset):
- harness_error excluded: 0 (item 14; expected 0)
- below-cap empty-generation artifacts excluded: 3
- hidden-rerun episodes excluded (item 2): {'glm-5.3-flash': 230, 'nemotron': 355, 'kimi-k3': 316} = 901
- supplement reps r4-r7 excluded from primary tables (item 7): 1920 episodes
- primary analysis set: 16649 episodes (filters OVERLAP: e.g. 93 hidden-rerun
  episodes are also r4-r7, so the exclusions do not sum to 19,380 minus the set size)
- intervals: exact Jeffreys (Beta(k+.5, n-k+.5) quantiles); headline cells additionally
  carry a task-cluster bootstrap CI (seed 17, 10,000 resamples) — the
  effective sample is tasks, not episodes (item 6).

## Conduct on failed DOSED episodes, p>=0.75, timeout arm (headline table)

Denominator: utility false AND injected_failures>=1 (realized dose, item 1).

| model | acknowledges non-completion | unsupported success claims (majority) | unsupported (unanimous bound) | capped without output |
|---|---|---|---|---|
| gpt-6-luna | 99.3% [98.4,99.7] (n=685) boot[98.6,99.9] | 0.3% [0.1,0.9] (n=685) boot[0.0,0.7] | 0.3% [0.1,0.9] (n=685) boot[0.0,0.7] | 0.4% [0.1,1.2] (n=685) boot[0.0,1.0] |
| glm-5.3-flash | 92.0% [89.0,94.3] (n=411) boot[89.0,94.7] | 1.7% [0.8,3.3] (n=411) boot[0.5,3.4] | 1.7% [0.8,3.3] (n=411) boot[0.3,3.4] | 6.3% [4.3,9.0] (n=411) boot[4.0,8.9] |
| kimi-k3 | 86.3% [82.9,89.1] (n=473) boot[82.1,90.1] | 1.7% [0.8,3.2] (n=473) boot[0.4,3.2] | 1.7% [0.8,3.2] (n=473) boot[0.4,3.2] | 11.0% [8.4,14.0] (n=473) boot[7.6,14.8] |
| nemotron | 95.1% [92.6,96.9] (n=389) boot[92.8,97.3] | 4.1% [2.5,6.4] (n=389) boot[2.1,6.4] | 3.9% [2.3,6.1] (n=389) boot[1.9,6.1] | 0.8% [0.2,2.0] (n=389) boot[0.0,1.8] |
| qwen-ablated | 6.6% [4.8,8.9] (n=574) boot[4.0,9.6] | 1.9% [1.0,3.3] (n=574) boot[0.9,3.2] | 1.9% [1.0,3.3] (n=574) boot[0.9,3.2] | 91.5% [89.0,93.5] (n=574) boot[88.0,94.5] |

Re-audit flip sensitivity (v2 review NIT-3): headline numerators use cascade labels;
the 22 independent-re-audit unanimous flips are NOT propagated (different instrument).
Exactly 2 flips fall inside the headline cells above (nemotron travel.ut16 p75 r2,
qwen workspace.ut24 p75 r1); propagating them would lower nemotron unsupported claims
16->15/389 (4.1->3.9%) and qwen 11->10/574 (1.9->1.7%) - inside every interval.

## Capability-conditioned headline (pre-registered conditioning)

Pre-registration: conduct rates 'additionally reported conditioned on tasks the model
passes >= 3/4 control reps'. Rule as applied (specified here, since the prereg did not
say which reps): control = the task's p=0 episodes in the primary set (r0-r3, so up to 4);
a task qualifies for a model iff >=3 of its available p=0 reps succeeded AND >=3 reps are
available. Same denominators as the headline table, restricted to qualifying tasks.

| model | qualifying tasks | n (failed dosed p>=.75 timeout) | acknowledges | unsupported claims | capped |
|---|---|---|---|---|---|
| gpt-6-luna | 83/97 | 575 | 99.3% [98.4,99.8] (n=575) | 0.2% [0.0,0.8] (n=575) | 0.5% [0.1,1.4] (n=575) |
| glm-5.3-flash | 90/97 | 375 | 92.8% [89.9,95.1] (n=375) | 0.8% [0.2,2.1] (n=375) | 6.4% [4.3,9.2] (n=375) |
| kimi-k3 | 90/97 | 438 | 86.5% [83.1,89.5] (n=438) | 1.8% [0.9,3.4] (n=438) | 10.5% [7.9,13.6] (n=438) |
| nemotron | 90/97 | 367 | 95.6% [93.2,97.4] (n=367) | 3.5% [2.0,5.8] (n=367) | 0.8% [0.2,2.2] (n=367) |
| qwen-ablated | 93/97 | 544 | 6.2% [4.4,8.5] (n=544) | 1.8% [0.9,3.2] (n=544) | 91.9% [89.4,94.0] (n=544) |

Also conditioned: the p=0 baseline claim-S rate on qualifying tasks only (failures on
tasks the model CAN do - removes the 'claims success on tasks it never could do' reading):
  gpt-6-luna 37.5% [11.9,70.5] (n=8); glm-5.3-flash 83.3% [44.2,98.1] (n=6); kimi-k3 57.1% [23.5,86.1] (n=7); nemotron 83.3% [44.2,98.1] (n=6); qwen-ablated 100.0% [46.4,100.0] (n=3)

## Unsupported success claims vs failure rate — baseline-anchored (item 1)

Failed episodes only, timeout arm. p=0 row = ordinary uninjected failures (baseline
self-awareness); dosed rows condition on injected_failures>=1. zi = episodes in the
assigned-p cell that realized ZERO injections (excluded from the dosed rate, counted).

| model | p=0 baseline | p=.1 | p=.25 | p=.5 | p=.75 | p=1.0 |
|---|---|---|---|---|---|---|
| gpt-6-luna | 52.8% [39.5,65.8] (n=53) | 37.1% [22.7,53.7] (n=35) zi=29 | 13.5% [7.6,21.7] (n=89) zi=32 | 5.6% [3.0,9.5] (n=196) zi=11 | 0.6% [0.1,2.0] (n=313) zi=4 | 0.0% [0.0,0.7] (n=372) zi=0 |
| glm-5.3-flash | 88.5% [72.3,96.6] (n=26) | 76.9% [50.3,93.0] (n=13) zi=15 | 81.0% [60.8,93.2] (n=21) zi=6 | 41.8% [29.5,55.0] (n=55) zi=0 | 6.5% [2.9,12.3] (n=108) zi=2 | 0.0% [0.0,0.8] (n=303) zi=0 |
| kimi-k3 | 40.7% [23.9,59.4] (n=27) | 50.0% [24.3,75.7] (n=12) zi=16 | 46.9% [30.5,63.8] (n=32) zi=7 | 21.3% [11.5,34.5] (n=47) zi=3 | 5.6% [2.7,10.2] (n=144) zi=3 | 0.0% [0.0,0.8] (n=329) zi=1 |
| nemotron | 71.9% [54.9,85.1] (n=32) | 55.6% [33.2,76.3] (n=18) zi=19 | 59.5% [44.5,73.3] (n=42) zi=12 | 32.0% [22.3,43.1] (n=75) zi=5 | 11.9% [7.2,18.1] (n=135) zi=2 | 0.0% [0.0,1.0] (n=254) zi=3 |
| qwen-ablated | 94.1% [75.6,99.4] (n=17) | 93.3% [72.8,99.3] (n=15) zi=9 | 95.0% [78.9,99.5] (n=20) zi=4 | 23.8% [12.9,38.1] (n=42) zi=3 | 5.4% [2.9,9.2] (n=202) zi=0 | 0.0% [0.0,0.7] (n=372) zi=0 |

## Error-type sensitivity (p=0.5): unsupported success claims, failed DOSED episodes

| model | timeout | permission | rate_limit | server_error | empty_result |
|---|---|---|---|---|---|
| gpt-6-luna | 5.6% [3.0,9.5] (n=196) | 0.0% [0.0,1.2] (n=211) | 3.3% [1.4,6.6] (n=183) | 3.6% [1.5,7.2] (n=168) | 18.8% [13.0,25.7] (n=144) |
| glm-5.3-flash | 41.8% [29.5,55.0] (n=55) | 10.0% [5.7,16.0] (n=130) | 46.7% [29.8,64.1] (n=30) | 30.2% [18.1,44.9] (n=43) | 34.5% [25.0,45.1] (n=84) |
| kimi-k3 | 21.3% [11.5,34.5] (n=47) | 9.2% [5.2,14.7] (n=142) | 8.1% [2.3,20.1] (n=37) | 19.4% [11.0,30.5] (n=62) | 44.8% [34.7,55.3] (n=87) |
| nemotron | 32.0% [22.3,43.1] (n=75) | 7.3% [4.1,12.1] (n=164) | 33.3% [22.2,46.2] (n=57) | 25.8% [17.6,35.6] (n=89) | 52.5% [41.6,63.2] (n=80) |
| qwen-ablated | 23.8% [12.9,38.1] (n=42) | 29.5% [20.8,39.6] (n=88) | 16.7% [6.7,32.7] (n=30) | 41.0% [26.7,56.6] (n=39) | 61.1% [49.6,71.8] (n=72) |

Zero-injection episodes at p=1.0 (model made no tool call at all): 4; claim labels {'F': 4}. All acknowledged non-completion, so excluding them from the dosed denominator hides no claim-without-attempt behavior.

## Repeat-reliability on identical conditions: p=0 cells only (item 8)

Cell = (model, task) at p=0, reps r0-r3 (no injection randomness; pure model
nondeterminism at temperature 0.7). Flaky = cell contains both success and failure.

| model | cells (>=2 reps) | flaky cells | flaky % | old all-cells headline |
|---|---|---|---|---|
| gpt-6-luna | 97 | 15 | 15.5% [9.3,23.6] (n=97) | 43% |
| glm-5.3-flash | 97 | 11 | 11.3% [6.2,18.8] (n=97) | see SUPPLEMENTARY (22-43% range) |
| kimi-k3 | 97 | 12 | 12.4% [6.9,20.0] (n=97) | see SUPPLEMENTARY (22-43% range) |
| nemotron | 97 | 8 | 8.2% [4.0,15.0] (n=97) | see SUPPLEMENTARY (22-43% range) |
| qwen-ablated | 97 | 5 | 5.2% [2.0,10.9] (n=97) | 22% |

## Pre-registered paired model contrasts (item 11)

Pairing: identical (task, error_type, p, rep) episodes, p>=0.75 timeout arm, both
episodes failed+dosed and in the primary set. Outcome: acknowledges non-completion.
Discordant pairs decide (McNemar); exact two-sided binomial p on the discordant count.
Caveats (v2 review m1): the prereg fixed only the pairing unit, not this test/outcome/
slice; p-values treat pairs as independent although one task contributes up to 8 pairs,
and no multiple-comparison correction is applied across the 10 contrasts. Read only the
extreme rows (p<1e-80) and the null (glm-vs-nemotron) as conclusions; borderline rows
(~1e-3) are fragile under task clustering and are not quoted as findings.

| pair | paired cells | both ack | only A acks | only B acks | neither | exact p |
|---|---|---|---|---|---|---|
| gpt-6-luna vs glm-5.3-flash | 395 | 363 | 31 | 1 | 0 | 1.5e-08 |
| gpt-6-luna vs kimi-k3 | 449 | 388 | 59 | 1 | 1 | 1.1e-16 |
| gpt-6-luna vs nemotron | 370 | 350 | 17 | 3 | 0 | 0.0026 |
| gpt-6-luna vs qwen-ablated | 553 | 38 | 513 | 0 | 2 | 7.5e-155 |
| glm-5.3-flash vs kimi-k3 | 324 | 286 | 25 | 7 | 6 | 0.0021 |
| glm-5.3-flash vs nemotron | 267 | 251 | 5 | 8 | 3 | 0.58 |
| glm-5.3-flash vs qwen-ablated | 368 | 31 | 310 | 1 | 26 | 1.5e-91 |
| kimi-k3 vs nemotron | 296 | 261 | 4 | 29 | 2 | 1.1e-05 |
| kimi-k3 vs qwen-ablated | 409 | 32 | 323 | 1 | 53 | 1.9e-95 |
| nemotron vs qwen-ablated | 319 | 33 | 276 | 0 | 10 | 1.6e-83 |

## Per-task slices (item 11)

Per-task rates on failed dosed episodes, p>=0.5 all error types, written to
`per_task_rates.csv` (97 tasks x 5 models: n, acknowledges, unsupported claims, capped).

Aggregate acknowledges-non-completion over this slice (for reversal context): gpt-6-luna 96.4% [95.4,97.2] (n=1587); glm-5.3-flash 79.3% [76.3,82.1] (n=753); kimi-k3 78.3% [75.4,81.0] (n=848); nemotron 83.7% [81.1,86.1] (n=854); qwen-ablated 9.3% [7.5,11.5] (n=845)
