# Silent Failures: How Tool-Using LLM Agents Behave When Their Tools Break (v2)

**A pre-registered, 19,380-episode behavioral study of five models across 97 tasks, four
domains, six failure rates, and five failure types — then adversarially reviewed, remediated,
and extended with a pre-registered wrap-up probe of every censored episode.**
Dataset frozen ~16h in; evidence package at ~33h; five-reviewer adversarial swarm,
remediation, and the 1,300-episode probe followed (2026-10-17/18, all on one machine).
Repo-pinned. Seed-reproducible per episode, with one disclosed exception: 901 episodes
affected by a benchmark-level hidden re-run bug (below) break exact replay and are excluded
from primary tables. **v2 supersedes v1** (git history preserves it); every v1 number
challenged by review is restated here from `REMEDIATED_TABLES.md`.

## One-paragraph summary

We injected controlled tool failures (timeouts, permission errors, rate limits, server
errors, silently-lost responses) into every benign task of the AgentDojo benchmark and
measured not whether agents succeed — but **how they behave when they cannot**: do they
acknowledge non-completion, keep silently retrying, or claim success the environment
contradicts? Conduct is model-specific and **not one trait**: acknowledging failure,
post-write re-reading, and calibrated persistence dissociate across models. Unsupported
success claims are anchored at a high **baseline on ordinary, uninjected failures
(41–94% by model)** and *decline* as injected failures become more visible, vanishing at
total outage — agents assume success unless loudly contradicted. The one abliterated model
in the matrix almost never claims false success but almost never reports either: it burns
its step budget silently in 91.5% of hard-failure episodes — yet the wrap-up probe shows
this is **propensity, not inability**: when forced to answer, capped models acknowledge
non-completion 95–98% of the time.

## Headline findings (restated post-review; all primary numbers from REMEDIATED_TABLES.md:
design-balanced reps r0–r3, hidden-reruns excluded, dosed-only denominators, exact Jeffreys
intervals + task-cluster bootstrap on headline cells)

1. **Conduct is model-specific and dissociable (H2 ✅).** On failed dosed episodes at
   p≥0.75 (timeout): gpt-6-luna acknowledges non-completion in 99.3% [98.4,99.7]
   (cluster-boot [98.6,99.9], n=685); glm 92.0%, nemotron 95.1%, kimi 86.3%;
   qwen-ablated acknowledges only 6.6% and is **capped without user-facing output in
   91.5% [89.0,93.5]** (boot [88.0,94.5], n=574). Pre-registered paired contrasts
   (identical task/condition/rep): qwen separable from every peer at p<1e-80;
   glm-vs-nemotron not separable (p=0.58).
2. **"Capped without output" is a propensity, not a deficit (wrap-up probe, Amendment 5).**
   All 1,300 censored episodes were probed (PROBE_ANALYSIS.md). Under a naturalistic user
   nudge *during the continuing outage*, glm/kimi/qwen resumed tool use without addressing
   the user in 53.7–68.4% of clean episodes (nudge-robust spin); but when tools were removed
   and an answer demanded, **95.0–98.3% produced an acknowledgment of non-completion**
   (behavioral "still no answer" = 0; the single remaining case is a `finish_reason=length`
   serving artifact). 41–58% of nudge answers claimed success *consistent* with post-probe
   environment state — the probe's extra turns let real work finish. Nudge-wording
   sensitivity was declared per pre-registration (+16 to +23pp A5 between two neutral
   wordings; both reported). The probe does not relabel any original episode.
3. **Unsupported success claims track failure *visibility*, anchored at a high baseline.**
   On ordinary (p=0, uninjected) failures, models claim success in **40.7–94.1%** of
   episodes — the baseline self-awareness result. Under injection (dosed-only), claims run
   37–93% at p=0.1 and **0% at p=1.0 for every model**; silently-lost responses are the
   worst channel for 4/5 models (up to 61.1%). Decomposition of all 864 candidate
   contradicted claims: 3% flagrant (final call visibly errored), 64% partial-work-as-full,
   33% unverified-not-contradicted. An independent two-judge full-text re-audit confirmed
   **809/864 (bound 809–842 under judge splits)** (REAUDIT.md). Models assume success
   rather than check: spontaneous **post-write re-reading** is 1.9–29.5% (novel re-reads
   1.4–18.1%); the most re-reading model is the abliterated one, and re-reading is not
   separable from blind retry in this design (READBACK.md).
4. **Over-persistence is a measurable trait.** The abliterated model retries an
   already-failed tool 12.9×/episode (streaks to 25) vs 1.8× for the most calibrated
   model; 3/5 models peak persistence at p=0.75 rather than p=1.0 (intermittent
   reinforcement, H4 partially supported). (Micro-metrics from SUPPLEMENTARY_ANALYSES.md,
   computed pre-remediation; the review challenged their *construct naming*, not these
   values.)
5. **Repeat-reliability, restated honestly (replication, not novelty).** The v1 "22–43%
   of identical cells flip" conflated injected-environment randomness with model
   nondeterminism. On p=0 cells (no injection randomness): **5.2–15.5%** of
   identical-condition cells still produce both success and failure in 4 reps at temp 0.7.
   Agent benchmarks without repetitions report noise — consistent with, and a replication
   of, the 2026 agentic-randomness literature.
6. **The abliterated model, described (H3 half-refuted — no causal claim).** One
   abliterated model, on one serving stack: near-zero in-budget reporting, extreme
   persistence, highest re-reading, lowest unsupported-claim rate. v1's "safety training
   removed → destroyed communication" phrasing is withdrawn: **no same-base non-ablated
   control exists in this matrix** (stock Qwen3.8-Flash on the identical llama.cpp server
   is the experiment that would license a causal claim). What survives is the descriptive
   dissociation: the model least likely to claim false success is also least likely to
   say anything at all.
7. **Nemotron 3.5 Super note (scoped).** Highest unsupported-claim rate among peers on
   failed dosed episodes at p≥0.75: 4.1% [2.5,6.4] (boot [2.1,6.4], n=389), and elevated
   across error channels. One scaffold, one benchmark; measured, not mechanism.

## Method in one diagram

```
97 AgentDojo benign tasks x {0,.1,.25,.5,.75,1.0} failure rates x 5 error types x 3-4 reps
   (+16-task supplement reps, variance analysis only)
     -> seeded Bernoulli failure injector wrapping every tool
     -> 5 models (nemotron-3.5-super-vl, qwen-ablated, glm-5.3-flash, kimi-k3, gpt-6-luna)
     -> deterministic env-state utility (ground truth) + transcript capture
     -> claim labels: rules -> gemini-3.6-flash -> 3-vendor council (claims only;
        the environment, not the judge, decides truth)
     -> adversarial review (5 reviewers) -> remediated tables + strengthened re-audit
        (gemini-free, full-text, reworded-prompt, controls-gated)
     -> wrap-up probe of all 1,300 censored episodes (seeded env replay, fidelity-checked)
```

Instrument validation, with its limits: 500-episode random audit 99.4% agreement — but that
audit excluded candidate fabrications by construction and gemini validated its own labels
(swarm Finding 3). Remediation: independent two-judge full-text re-audit of **all 864**
candidates (809 confirmed; the one reviewer-proven unanimous misread was independently
caught and removed) plus a 200-episode reverse audit of F-labels (197 confirmed, 0 flips).
Probe grading: fresh 100-episode council audit, 98/100. Judge agreement bounds instrument
variance, not shared bias: no human calibration exists (disclosed).

## Related work (post-hoc sweep; the pre-registered Day-0 novelty sweep was skipped under
time pressure — a recorded process failure. Verdicts as of 2026-10-18; several closest
works are Sep–Oct 2026 preprints, i.e. concurrent.)

**The method is not novel.** Fault injection into tool-calling agent benchmarks is
established: ChaosLLM (ISSRE 2025), Fail-TaLMs, ResiliBench (ICLR 2026), ReliabilityBench,
AgentChaos, Agent Error Simulator, and closest overall, *Loud Failures, Quiet Failures*
(arXiv 2610.10062, Oct 2026: typed faults over a function-calling benchmark, 6 models).
Conduct-under-failure measurement is also adjacent in *Failure-Transparent Agents*
(2609.35732: post-failure claim auditing, 3,600 human-annotated responses), *Guardrails as
Scapegoats* (2607.19449: honest-surrender/fabrication taxonomy), and *Upward Deceivers*
(2512.04864: failure concealment). Finding 5 here (single-run unreliability) is an explicit
**replication** of the 2026 randomness literature (2602.07150, 2512.06710, 2609.33812;
τ-bench pass^k).

**What this study adds (hedged, as of its date):** (a) the **baseline-anchored
visibility dose-response** — unsupported-claim rate as a function of injected failure
probability, anchored at the uninjected baseline and vanishing at total outage — no prior
found reporting claim rates vs failure *probability*; (b) the **non-monotonic persistence
peak at p=0.75** — no prior found for operant-conditioning-shaped agent persistence;
(c) **three-trait dissociation** (acknowledging, re-reading, persistence decorrelate across
models — e.g. the most re-reading model is the least communicative); (d) the
**ablation-descriptive contrast** (no found work measures failure-*reporting* conduct of an
abliterated agent); (e) spontaneous **post-write re-reading base rates** (prior work tests
instructed verification). Full sweep with per-claim verdicts and contradictions:
`reviews/adversarial-prior-art.md`.

## Artifact map

| File | Contents |
|---|---|
| PREREGISTRATION.md + AMENDMENT-1..5 | hypotheses, design, every mid-run decision with timestamps, incl. corrections |
| DATA_MANIFEST.json, QA_FINAL.txt | episode counts, content hashes, integrity audit (0 duplicates, 0 harness errors) |
| **REMEDIATED_TABLES.md** + per_task_rates.csv | **primary v2 tables** (dosed-only, baseline-anchored, cluster-bootstrapped, paired contrasts, per-task) |
| **PROBE_ANALYSIS.md** + probe_results/ | wrap-up probe outcomes + claim grading, per-model, pre-registered slices |
| **REAUDIT.md** | strengthened independent re-audit of all fabrication candidates + reverse audit |
| **READBACK.md** + readback.py | post-write re-reading, committed definitions, novel-vs-repeat split |
| TRANSPARENCY.md | all 15 review findings with dispositions; REVIEW_RESPONSE.md maps finding→artifact |
| reviews/ | the five adversarial reports + probe design review, verbatim |
| CONDUCT_ANALYSIS.md, SUPPLEMENTARY_ANALYSES.md, evidence_classes.md, DETERMINISTIC_TABLES.md | v1 analyses (superseded where TRANSPARENCY says so; micro-metrics still current) |
| figures/fig1..3_v2*.png + figures_v2.py | v2 figures with committed generator |
| demos/demo1..4 | exemplar transcripts: honest abandon, silent spin, contradicted claim, unverified claim |
| BLIND_SPOTS.md | self-audit register, updated post-review |
| experiment.py, probe.py, classifier.py, probe_classify.py, reaudit.py, analyze*.py, qa_check.py | full harness |

## Limitations (abbreviated; full register in BLIND_SPOTS.md and TRANSPARENCY.md)

One scaffold and loop cap; a hidden AgentDojo re-run bug (capped episodes silently re-run
up to 3× on the mutated environment; 901 episodes across glm/nemotron/kimi, never
luna/qwen) — quantified, excluded from primary tables, upstream report pending; sampling
heterogeneity for gpt-6-luna; uniform-random failure injection; English-only, one benchmark
family, short horizon; claims-vs-environment construct attributes no intent; judge council
is not human calibration (variance bounded, shared bias not); 1,400-char judge truncation
remains for the corpus outside re-audited numerators; conduct profiles are
scaffold/policy-sensitive (Failure-Transparent Agents moves false-success 22.8%→0.8% with
an evidence contract — these are not fixed model constants); the probe cannot say what
would happen with a raised cap and *no* user turn.

## Operational incident log (all in amendments; each produced a control that now exists)

Cached-suite injection leak (caught by control cells) · silent worker-death event (cause
undetermined; survived by systemd supervision + atomic episodes) · TLS sentinel-label
incident (caught by label-distribution inspection) · gemini quota exhaustion (produced
quota-aware retries) · hidden-rerun benchmark bug (found by adversarial review, quantified
by code audit, confirmed by probe replay-fidelity failures). Each is also a finding about
evaluation infrastructure: **the harness lies unless you build the checks that catch it.**
