# Persistence and H4, recomputed on the remediated primary set (v2 review M1)

Script: persistence.py (first committed derivation; definitions in its docstring).
Population: primary set, timeout arm, failed (utility false), dosed
(injected_failures>=1). Hidden-rerun episodes are excluded, so the stored-transcript
last-attempt-only limitation does not affect these numbers. The v1 SUPPLEMENTARY
micro-metrics (12.9x/1.8x, streaks to 25, uniform n=400) are SUPERSEDED by this table;
they had no committed script and included hidden-rerun episodes.

## Micro-metrics at p>=0.75 (headline population)

| model | n | mean retries of an already-errored tool | max retry streak | mean distinct tools | mean tool calls |
|---|---|---|---|---|---|
| gpt-6-luna | 685 | 2.3 | 14 | 2.0 | 4.4 |
| glm-5.3-flash | 411 | 5.4 | 18 | 2.7 | 8.2 |
| kimi-k3 | 473 | 5.9 | 16 | 2.1 | 8.1 |
| nemotron | 389 | 4.9 | 14 | 2.5 | 7.5 |
| qwen-ablated | 574 | 13.1 | 22 | 4.1 | 17.3 |

## H4: persistence vs failure rate (failed dosed episodes, timeout arm)

| model | mean turns p=.5 | p=.75 | p=1.0 | turns peak at .75? | mean retries p=.5 | p=.75 | p=1.0 | retries peak at .75? |
|---|---|---|---|---|---|---|---|---|
| gpt-6-luna | 5.49 | 5.10 | 3.88 | no | 2.98 | 3.04 | 1.65 | YES |
| glm-5.3-flash | 8.15 | 8.77 | 7.76 | YES | 6.49 | 6.54 | 5.06 | YES |
| kimi-k3 | 8.34 | 8.71 | 7.32 | YES | 6.57 | 6.99 | 5.44 | YES |
| nemotron | 7.17 | 7.23 | 8.67 | no | 3.52 | 4.20 | 5.33 | no |
| qwen-ablated | 14.33 | 15.45 | 15.41 | YES | 13.95 | 13.82 | 12.66 | no |

H4 verdict on the remediated set: turns peak at p=0.75 for 3/5 models; retries peak at p=0.75 for 3/5 models. No CIs are attached to these means (pre-registered as exploratory). Several 'peaks' are sub-1-turn differences (qwen's turns peak is at the loop cap); H4 is directional evidence only, and the honest summary is 'mixed, weakly supportive' - not a confirmed effect.
