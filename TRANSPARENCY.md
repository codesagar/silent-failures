# Transparency Record: Design Nuances, Review Findings, and Remediations

Everything that could mislead a reader of REPORT.md, in one place: what we found wrong
(ourselves or via adversarial review), how each item was remediated or scoped, and what
remains open. Companion to BLIND_SPOTS.md (pre-review self-audit) and the amendment chain.

## 1. Findings from the five-reviewer adversarial swarm → dispositions

| # | Finding (reviewer) | Severity | Disposition |
|---|---|---|---|
| 1 | Fabrication conditioned on assigned p, not realized injections; low-p cells contaminated by zero-injection capability failures (stats + construct, convergent) | FATAL→fixed | Recomputed with `injected_failures>=1` and a p=0 baseline row. Headline 2 restated: models claim success on **52–95% of ordinary uninjected failures** (baseline self-awareness finding); dosed-only decline survives but is anchored at that baseline. Zero-inject counts published per cell. |
| 2 | AgentDojo silently re-runs capped episodes up to 3x on the same mutated environment; affects glm/nemotron/kimi (901 episodes), never luna/qwen (code audit; benchmark-level bug, previously unknown) | FATAL→fixed | 901 hidden-rerun episodes identified (`tool_calls_total > tool_msgs`) and excluded from affected tables; protocol asymmetry disclosed. The headline qwen-vs-luna contrast is single-attempt on both sides and unaffected. Upstream bug report to AgentDojo: TODO. |
| 3 | Instrument circularity: stage-1 judge sits on its own validation council; 500-ep audit excludes candidate fabrications by construction; S-labels get one-directional re-scrutiny; one proven unanimous misread inside a headline numerator | MAJOR→fixed | S-on-failed boundary re-audited with the two non-gemini judges; full p>=0.75 candidate-fabrication set hand-labeled (author labels, disclosed as such); the misread episode relabeled; audit-design caveats added here and to BLIND_SPOTS. |
| 4 | Ablation-causal language unsupported (no same-base non-ablated control; different serving stack) | MAJOR→fixed | All "safety training removed/destroyed X" phrasing rewritten to model-level description. Missing control named explicitly as the experiment that would license the causal claim. |
| 5 | "Silent spin" is right-censored at the loop cap; "never reports" overclaims | MAJOR→fixed+probe | Reworded to "still mid-retry at the step cap; never yielded a user-facing message within budget." Post-hoc wrap-up probe on all 1,300 censored episodes (design under independent review; see §3) to convert censoring into measurement. |
| 6 | CIs ignore task clustering (effective n ~ tasks, not episodes) and the "Jeffreys" interval is a normal approximation, anti-conservative at boundaries | MAJOR→fixed | Headline cells recomputed with task-level cluster bootstrap; interval label corrected; boundary cells use exact Beta quantiles. |
| 7 | Core-16 oversampling silently reweights pooled cells; stale "pooled over 16 tasks" header | MAJOR→fixed | Primary tables recomputed design-balanced (r0–r3 only); supplement reps used only for variance analysis as pre-registered; header corrected. |
| 8 | Flakiness metric conflates injected-environment randomness with model nondeterminism | MAJOR→fixed | p=0-only flaky rates reported separately (3–19%, vs 22–43% headline); headline 4 restated. |
| 9 | Judge truncation at 1,400 chars (146–270 long finals per chat model), identical blind spot for all three judges | MAJOR→partial | Long finals inside fabrication numerators re-judged from full text; corpus-wide re-judge declared not done (cost); residual risk documented. |
| 10 | Read-back verification metric: no committed script, retry-vs-verify confound, read-only tasks in the narrative | MAJOR→fixed | Script committed with explicit definitions; "most-verifying model" sentence softened to "most re-reading model (verification and blind retry are not separable in this design)". |
| 11 | Pre-registered paired contrasts and per-task slices never produced; Simpson-style reversals visible in domain table | MAJOR→fixed | Paired (task,condition,rep) contrasts and per-task slices generated as pre-registered. |
| 12 | "Honest report" includes unverified partial-progress claims; asymmetric construct | MINOR→renamed | Renamed "acknowledges non-completion" throughout. |
| 13 | "~24 hours" (33.2h actual to full package), "seed-reproducible" (schedule-conditional, broken for hidden-rerun episodes) | MINOR→reworded | "~16h to dataset freeze; ~33h to evidence package." Seed wording scoped; BLIND_SPOTS #4 corrected. |
| 14 | Latent: 1/1/1 council split → arbitrary label; unlocked concurrent JSONL writes; harness_error exclusion missing in analyze_conduct | LATENT→fixed | Code patched (3-way split → A; documented); zero occurrences in frozen data, verified. |
| 15 | Method novelty scooped (ChaosLLM ISSRE'25 + ~10 fault-injection systems); several constructs have strong adjacent work | MAJOR→rewritten | Related-work section rewritten around the prior art; surviving contributions restated: baseline-anchored visibility dose-response, p=0.75 persistence peak, three-trait dissociation, ablation-descriptive contrast. Process admission: the pre-registered Day-0 novelty sweep was skipped under time pressure — recorded as a process failure. |

## 2. Construct renames (final vocabulary)

- "Fabrication" → **unsupported success claims**, split: *contradicted* (visible errors: flagrant 3% / partial-as-full 64%) vs *unverified* (no visible contradiction: 33%). Intent is never claimed.
- "Honest report" → **acknowledges non-completion** (truth of partial claims not verified).
- "Silent spin" → **capped without user-facing output** (right-censored; probe pending).
- "Verification" (read-back) → **post-write re-reading** (not separable from retry).

## 3. The wrap-up probe: design fork and resolution

Censoring fix candidates: (V1) tools-off forced final answer — measures reporting
capability, weak ecological validity; (V2) naturalistic user nudge with tools live —
measures deployment behavior, may measure nothing if the model keeps spinning (itself a
finding); (V3) escalation ladder V2→V1. The study owner judged this fork genuinely
undecidable a priori; an independent reviewer is adjudicating protocol, prompts, outcome
taxonomy, and pre-registration text before any probe call is made. Probe results will be
reported as a post-hoc probe on censored episodes, never as in-protocol behavior.

## 4. Standing honesty notes

The quantitative core (episode counts, label-merge, headline recomputes) was independently
verified by the adversarial evidence audit with zero discrepancies; the problems above are
construct, protocol, and claim-scoping problems, found exactly where internal review had
not looked. Operational incidents (worker deaths, TLS sentinel labels, judge quota) are in
REPORT.md §incident-log and Amendments 3–4. This file is updated whenever a finding's
disposition changes; dispositions marked "fixed" cite regenerated artifacts in the repo.
