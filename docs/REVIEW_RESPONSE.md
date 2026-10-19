# Review response: finding → disposition → artifact

Companion to TRANSPARENCY.md (which holds the full dispositions and is updated first).
This file is the one-page map from each adversarial-swarm finding to the artifact that
answers it. "Fixed" means the regenerated artifact exists in this repo and is cited —
nothing else. Reviewer reports are archived verbatim in `reviews/`.

| # | Finding (short) | Status | Artifact(s) | What changed |
|---|---|---|---|---|
| 1 | Claims conditioned on assigned p, not realized injections; zero-injection contamination | **fixed** | REMEDIATED_TABLES.md (baseline-anchored dose-response, zi counts); figures/fig3_v2 | Dosed-only denominators; p=0 baseline row (40.7–94.1% claims on ordinary failures); headline 3 restated |
| 2 | AgentDojo hidden re-run bug (901 episodes, glm/nemotron/kimi) | **fixed** (tables); upstream report declared-not-done | REMEDIATED_TABLES.md (exclusion + counts); PROBE_ANALYSIS.md (separate slice); Amendment 5 (replay-fidelity confirmation) | Excluded from all primary tables; protocol asymmetry disclosed; bug confirmed empirically via probe replay infidelity |
| 3 | Instrument circularity (gemini self-validation; audit excluded candidates; one proven misread) | **fixed** (human labels substituted, disclosed) | REAUDIT.md + classify/reaudit*.json(l); BLIND_SPOTS #13 | Gemini-free full-text controls-gated re-audit of all 864 candidates: 809 confirmed, bound 809–842; reviewer-proven misread independently caught; reverse audit 197/200, 0 flips. Owner ruled out hand-labeling (time) — disclosed |
| 4 | Ablation-causal language unsupported | **fixed in v2 prose** | REPORT.md v2 headline 6 | All causal phrasing withdrawn; missing same-base control named as the licensing experiment |
| 5 | "Silent spin" right-censored; "never reports" overclaims | **fixed** | PREREGISTRATION-AMENDMENT-5.md; PROBE_ANALYSIS.md; probe.py + probe_results/ | All 1,300 censored episodes probed: spin is nudge-robust (54–68%; wording-sensitive, W1−W2 +16 to +23pp, both reported; A6=0) but capability exists (95–98% forced acknowledgment); construct renamed "capped without user-facing output" |
| 6 | CIs ignore task clustering; "Jeffreys" was a normal approximation | **fixed** | REMEDIATED_TABLES.md | Task-cluster bootstrap (10k, seed 17) on headline cells; exact Beta-quantile Jeffreys everywhere; headlines survive clustering |
| 7 | Core-16 oversampling reweights pooled cells; stale header | **fixed** | REMEDIATED_TABLES.md (r0–r3); DETERMINISTIC_TABLES.md + analyze.py headers | Primary tables design-balanced; 1,920 supplement episodes confined to variance analysis; header corrected (pool was all 97 tasks) |
| 8 | Flakiness conflated injection randomness with model nondeterminism | **fixed** | REMEDIATED_TABLES.md (p=0-only table); REPORT.md v2 headline 5 | Honest rate 5.2–15.5% (was 22–43%); presented as replication of 2026 randomness literature |
| 9 | 1,400-char judge truncation blind spot | **fixed for numerators**; corpus-wide declared-not-done | REAUDIT.md (169 long finals re-judged full-text: 5 flips, 17 splits) | Truncation effect on fabrication numerators measured and small; probe long-answer counts disclosed in PROBE_ANALYSIS.md |
| 10 | Read-back metric: no committed script; retry-vs-verify confound | **fixed** | readback.py + READBACK.md | Script committed with mechanical definitions; v1 numbers reproduced; novel-vs-repeat split added; construct renamed "post-write re-reading"; "most-verifying" retired |
| 11 | Pre-registered paired contrasts and per-task slices never produced | **fixed** | REMEDIATED_TABLES.md (McNemar contrasts); per_task_rates.csv | qwen separable from every peer (p<1e-80); glm-vs-nemotron not separable (p=0.58); 97×5 per-task table |
| 12 | "Honest report" asymmetric construct | **fixed in v2 prose** | REPORT.md v2 + REMEDIATED_TABLES.md vocabulary | Renamed "acknowledges non-completion" in all v2 tables and headlines |
| 13 | "~24 hours" / "seed-reproducible" overclaims | **fixed in v2 prose** | REPORT.md v2 header; BLIND_SPOTS #4 | "~16h to dataset freeze; ~33h to evidence package"; seed replay scoped (hidden-rerun episodes break it — confirmed empirically) |
| 14 | Latent: 1/1/1 council split; unlocked writes; missing harness_error filter | **fixed** | classifier.py, probe_classify.py, analyze_conduct.py patches | 3-way split → A; write locks; harness_error exclusion. All verified no-ops on frozen data before patching |
| 15 | Method novelty scooped; Day-0 sweep skipped | **fixed in v2 prose** | REPORT.md v2 related-work section; reviews/adversarial-prior-art.md | Method framed as established; closest/concurrent work cited; surviving contributions hedged as-of-date; sweep skip recorded as process failure |

## What remains open (declared, not done)

- Upstream AgentDojo bug report: independently assessed (verification/
  agentdojo-bug-assessment.md) — verdict: real but narrow; unfixed on current main,
  undocumented, no duplicate issue; results-corrupting when triggered (checkers see the
  dirty cumulative environment) but vanilla-frequency unquantified; issue text drafted
  with honest scoping and a PR offer. Filing from the owner's GitHub account is the
  owner's call.
- Corpus-wide full-text re-judge outside fabrication numerators (cost; residual risk
  documented in TRANSPARENCY #9).
- Clean no-stage-A V1 probe arm — pre-registered contingency NOT triggered (behavioral
  B3 = 0), so not run.
- Same-base non-ablated control (stock Qwen3.8-Flash on the identical llama.cpp stack) —
  the experiment that would license any ablation-causal claim.
- Human calibration of the claim instrument — ruled out for time by the study owner;
  the strengthened re-audit bounds instrument variance, not shared bias.

## The v2 verification round (post-remediation cross-validation)

| Check | Agent | Verdict | Artifact |
|---|---|---|---|
| Independent recomputation of every targeted v2 number from raw JSONL (fresh code, analysis scripts never opened; supervisor-executed verbatim, disclosed) | recomputation auditor | **CLEAN** — ~70/70 match; 2 reproducibility gaps (now patched in REAUDIT.md and PROBE_ANALYSIS disclosures) | verification/v2-recompute-audit.md |
| Adversarial methodology & inference review of the v2 layer | methodology reviewer | **BLOCK → fixed**: 0 fatal, 7 major (M1–M7), 4 minor, 4 nits — every item fixed or disclosed; see TRANSPARENCY §5 | verification/v2-methodology-review.md |

Fixes landed for the round: PERSISTENCE.md + persistence.py (M1); A3 mechanism split in
PROBE_ANALYSIS.md + prose corrections in three documents (M2); strengthened probe-label
re-audit in REAUDIT.md §probe (M3); direction-of-bias caveat on the reverse audit (M4);
864-pool scoping (M5); capability-conditioned tables (M6); TIMELINE.md (M7); McNemar
caveats, A5-by-dose table, zero-call p=1.0 episode disclosure, vendor-overlap check,
NIT-1 code note, filter-overlap note (minors).
