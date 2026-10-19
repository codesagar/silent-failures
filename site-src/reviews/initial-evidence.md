# Independent evidence critic — Silent Failures redesign

Read the handoff, REPORT, final remediated tables/probe/re-audit/persistence/readback, scope/transparency/timeline, Amendment 5, and relevant generators/injector. No applicable ancestor AGENTS.md found. Research and site implementation untouched. Independently recomputed main integer numerators/denominators from `results/*.jsonl` and cascade label files; independently recomputed probe selection/counts from `probe_results/*.jsonl` and probe label files. Main results below match frozen tables. CIs were source-checked, not freshly bootstrap-recomputed.

## Recommended three messages, ranked by evidentiary strength

### 1. A failed task does not tell you whether the agent will explain the failure.

Strongest result: under severe timeout injection, Luna usually acknowledges non-completion; Qwen ablated usually consumes the budget without a user-facing answer. Show all five models as horizontal stacked conduct bars, not an honesty leaderboard. Keep the five ambiguous Kimi cases visible as a fourth residual category: its three headline rates sum to 98.9%, not 100%.

Population: primary r0–r3 episodes; hidden reruns and below-cap artifacts excluded; task utility false; at least one actual injection; timeout arm; assigned p≥.75. Exact recomputed counts:

| Model | n | Ack F | Unsupported S | Cap/no output | Ambiguous |
|---|---:|---:|---:|---:|---:|
| Luna | 685 | 680 (99.3%) | 2 | 3 | 0 |
| GLM | 411 | 378 (92.0%) | 7 | 26 | 0 |
| Kimi | 473 | 408 (86.3%) | 8 | 52 | 5 |
| Nemotron | 389 | 370 (95.1%) | 16 | 3 | 0 |
| Qwen ablated | 574 | 38 (6.6%) | 11 | 525 (91.5%) | 0 |

Put task-cluster 95% intervals beside salient rates: Luna acknowledgment 98.6–99.9%; Qwen capped 88.0–94.5%. Use published bootstrap intervals, not episode-independent Jeffreys intervals, for this headline. Source `analysis/REMEDIATED_TABLES.md:19–35`; capability restriction preserves conduct contrast (`:37–55`, Qwen cap 91.9%, Luna ack 99.3%). The Qwen/Luna comparison avoids the asymmetric hidden-rerun exclusions that affect the other models.

Adjacent qualification: **One scaffold and serving setup per model; this does not isolate the effect of removing safety training.** “Acknowledgment” is a claim label; partial-progress statements are not independently verified and F/A ambiguity remains. A low success-claim rate does not establish good reporting when most outcomes are silence.

### 2. Silence at the cap can coexist with the ability to report non-completion.

This is the most memorable follow-up to finding 1 and the strongest demonstration of research judgment: test the tempting interpretation instead of asserting inability. Suggested visualization is an explicitly conditional flow: cap → user nudge with tools live → selected nonresponders → tools-off answer. Lead with one actual Qwen trajectory, then show the three adequately sized model rows.

Main probe slice is **p>0, clean replay, hidden reruns excluded**, not the original primary-table population. It includes eligible supplements and conditions beyond p≥.75 timeout. Never draw a numeric funnel from the original 525/574 cap cell into the 819 probe cases.

| Model | Clean capped probe cases | Still tool-only after nudge | Tools-off graded answers | Ack after tools removed |
|---|---:|---:|---:|---:|
| GLM | 67 | 36/67 = 53.7% | 36 | 35/36 = 97.2% [87.7,99.7] |
| Kimi | 106 | 60/106 = 56.6% | 60 | 59/60 = 98.3% [92.5,99.8] |
| Qwen ablated | 819 | 560/819 = 68.4% | 559 | 531/559 = 95.0% [92.9,96.6] |

Source `analysis/PROBE_ANALYSIS.md:19–28`, Amendment 5. These are Jeffreys intervals; no task-cluster intervals were published for probe. Qwen's 560→559 is one `finish_reason=length` serving artifact; show that tiny exit if plotting the flow. Luna n=5 and Nemotron n=3 are descriptive only; neither licenses a five-model capability comparison. 1,300 attempted probes, 217 replay/harness exclusions; clean replay is non-random for three models.

Adjacent qualification: **Stage B tests only agents that did not answer the nudge, under a changed prompt and no tools. It does not test a larger budget without a user turn.** Call this “reporting is possible under the probe,” not “the problem is solved.” Post-hoc probe registered before it ran; never call it part of the original preregistered run.

Optional small note: silence also concealed already-completed work. Among 163 post-probe success-consistent answers, 51 were already complete and 112 finished during probe (`PROBE_ANALYSIS.md:60–76`). That population includes slices excluded from the main table (Kimi A3=21 here versus 19 main). This is not 51/1,300 or 31% of all capped episodes. Re-audit of all 1,082 answers confirms 647/652 original B1 labels, but is near-blind at the ambiguous/noncompletion boundary (`analysis/REAUDIT.md`, final section).

### 3. Unsupported success claims were common among failures without a clear error signal.

A defensible headline is descriptive: **“An agent can say ‘done’ while the task is still incomplete.”** Support with the baseline and fault-type evidence; do not claim visibility was causally isolated. A concrete quiet-loss trace must show that the tool actually executed and only its response disappeared. The visible error arm raises before execution; the quiet arm runs the tool and suppresses output (`scripts/experiment.py:102–129`). Thus fault types change both visibility AND world state.

Baseline recomputed S counts among ordinary uninjected failed tasks: Luna 28/53=52.8%; GLM 23/26=88.5%; Kimi 11/27=40.7%; Nemotron 23/32=71.9%; Qwen 16/17=94.1%. These are NOT failure rates over all tasks. Published CIs are wide; conditioning further on baseline-capable tasks leaves n=3–8. Source `REMEDIATED_TABLES.md:53–69`. Assigned p=1 timeout has zero observed S claims, but published upper interval bounds remain 0.7–1.0%; “none observed” is safer than an unqualified universal zero.

At assigned p=.5, among failed dosed episodes, timeout versus quiet-loss S counts are Luna 11/196 vs 27/144; GLM 23/55 vs 29/84; Kimi 10/47 vs 39/87; Nemotron 24/75 vs 42/80; Qwen 10/42 vs 44/72. Quiet-loss rate is higher than timeout for 4/5 models, with GLM the exception. Across all five error types it is the highest point estimate in the same four models (`REMEDIATED_TABLES.md:71–79`). Show the exception clearly. These comparisons have Jeffreys intervals, not published cluster intervals, and condition on different sets of failures.

Adjacent qualification: **“Consistent with a visibility interpretation; failure types and the failed-task population also change.”** Avoid “agents assume success unless contradicted” as an asserted mechanism; it is an interpretation.

## Headlines I would reject or demote

- “Removing safety training destroys communication”: no matched non-ablated control; model and serving stack confounded.
- “The honest model / deceptive models”: construct measures output correspondence, not intent. F is acknowledgment, not verified honesty.
- “Quiet errors are worse for every model”: GLM is a direct counterexample; clarify which outcome is “worse.”
- “95–98% of silent agents can be recovered”: selected stage-B denominator and intervention conflated; recovered reporting is not recovered task success.
- “Persistence peaks at intermittent failure”: exploratory, mixed, small differences, cap effects, no CIs; `analysis/PERSISTENCE.md` explicitly rejects a confirmed effect.
- “Agents do not verify”: re-reading is a mechanical prefix metric, cannot separate verification from retries; measured only on quiet-loss episodes with writes, n106–166.
- “864 proven fabrications” or a giant 3/64/33 pie: the 864 pool includes hidden reruns/supplements/zero-dose failures; only 742 survive primary filters; class decomposition is not a re-audited causal or intent taxonomy. Historical decomposition may be disclosed secondarily, while trace-backed examples distinguish visible contradiction, partial work as full, and unverified claims.
- “Five minutes of eight findings”: repetition reliability, re-reading, persistence and instrument incidents are valuable drill-down material, not competing top-level claims.

## Non-negotiable presentation checks

1. State 19,380 recorded / 16,649 primary; overlap means exclusions must not be drawn as disjoint subtraction boxes. Raw recomputation confirms both totals.
2. Attach each denominator to its graphic; “failure probability” means assigned per-call Bernoulli p, “dosed” means ≥1 realized injection, and rates shown are conditional on failed tasks.
3. Keep an “observed, reanalyzed, probed” chronology accessible: registration committed 46 min into original run (first 6% predate it); later remediation and probe; no clean rerun after all corrections. `docs/TIMELINE.md`.
4. Source links should pin f12eb47614350aca1cdf21cefc18ab58dd95e9d0 and correct line/section; do not cite old prose if final table contradicts it. Current snapshot hashes define frozen artifacts.
5. Put one study-wide label caveat near the core evidence: automated claim labels, independent model re-audit, no human calibration. Detailed audit history belongs in methodology.
6. Use actual excerpts and IDs, clearly selected illustrations not estimates. `demo1_honest_abandon` is an excluded hidden-rerun example and unsuitable as the clean main Luna/GLM acknowledgment story.

## Five-minute argument

0:00–0:30: “Success/failure scoring misses what users are told. I injected tool faults, measured world state separately from final claims, and found three different reporting outcomes.”
0:30–1:45: all-five conduct chart plus one silence/ack trace.
1:45–2:50: probe flow; challenge and reject the inability interpretation with its conditional evidence.
2:50–4:15: quiet-loss trace plus baseline/fault comparison; explain action versus response and show GLM exception.
4:15–5:00: implication: evaluate task outcome, user-facing report, and cap censoring separately; methodology link shows what reviews changed and what remains uncertain. This is a suggested narration allocation, not a completed timed runtime test.
