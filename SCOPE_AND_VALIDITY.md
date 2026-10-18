# Scope and validity card — exactly what this study measured, and what it did not

Purpose: one page the author can answer any "but does that apply to X?" question from.
Each row states what was actually held fixed or measured, and the conclusion that boundary
does NOT license. Everything here is live-verified against the harness (`experiment.py`,
`probe.py`) and the frozen data; nothing is from memory.

| Dimension | What the experiment actually is | Therefore you may NOT conclude |
|---|---|---|
| **Models** | Five named checkpoints behind three different serving paths: nemotron-3.5-super-vl (local vLLM, :8005), qwen-ablated (local llama.cpp, :8006), glm-5.3-flash + kimi-k3 (gateway chat API), gpt-6-luna (gateway Responses API, reasoning effort "low"). Gateway models are not version-pinned by us — the provider can change them behind the endpoint. | Anything about model *families*, other sizes, or future versions of the same names. Model and serving stack are confounded (each model rode one stack); the ablated model has no same-base non-ablated control, so nothing causal about ablation or "safety training". |
| **Scaffold** | One ReAct-style AgentDojo pipeline: system prompt fixed, temperature 0.7, loop cap 15 assistant turns, tools always visible, no retry/verification scaffolding, no user interaction mid-task (until the probe). | That conduct rates are model constants. Concurrent work (Failure-Transparent Agents) moves false-success from ~23% to ~1% with an evidence-contract scaffold — these numbers describe *this scaffold*. Agent products with planners, verifiers, or user check-ins are out of scope. |
| **Tasks** | AgentDojo v1.2.1 (package v0.1.35), all 97 *benign* user tasks in 4 office-style domains (workspace, travel, banking, slack); English only; short horizon (≤15 tool steps); deterministic environment checkers as ground truth. | Anything about coding agents, web browsing, long-horizon tasks, multimodal input, adversarial/injected-prompt settings, or tasks whose success is not machine-checkable. |
| **Failure model** | Seeded per-call Bernoulli injection at assigned rates p ∈ {0,.1,.25,.5,.75,1.0}; five synthetic error strings (timeout, permission, rate-limit, server-error) plus silent response loss (`empty_result` — executes side effects, suppresses the response). Failures are independent, uniform across tools, stateless. | Behavior under *realistic* outages: real failures cluster by service, correlate in time, and carry provider-specific messages. Partial/corrupted responses, schema drift, and slow (rather than failed) tools were not injected. |
| **Outcome instrument** | What the final message *claims* is labeled by a rules→LLM-judge→3-vendor-council cascade; truth of the claim is decided by environment state, never by the judge. No intent attribution — "unsupported success claim" is a correspondence failure, not "lying". Instrument bounds: 500-ep audit 99.4%; independent 2-judge full-text re-audit of all 864 candidates (809 confirmed, honest range 809–842); reverse audit 197/200. No human calibration exists; judge agreement bounds variance, not shared bias. 1,400-char truncation applies outside re-audited numerators. | That any single episode is a proven "lie" (no intent construct); that labels are human-grade; claim rates more precise than the published bound. |
| **Statistics** | Primary tables: design-balanced reps r0–r3; harness errors (0), below-cap artifacts (3), and 901 hidden-rerun episodes excluded; "dosed" = at least one failure actually fired. Exact Jeffreys intervals; task-cluster bootstrap on headline cells (effective sample ≈ 97 tasks, not 19,380 episodes). Paired contrasts are McNemar on identical (task, condition, rep) cells. | Precision beyond the task-clustered intervals; anything from the r4–r7 supplement reps except variance statements; comparisons involving cells the hidden-rerun exclusion emptied (it hit only glm/nemotron/kimi — a disclosed protocol asymmetry). |
| **The probe** (Amendment 5) | All 1,300 cap-censored episodes resumed from replayed state (fidelity-checked); one natural nudge (two wordings, sensitivity declared: W1−W2 = +16 to +23pp on resumed-spin), then a tools-off forced wrap-up. Self-replay only. 217 episodes (17%) excluded for replay infidelity, *concentrated in nemotron (87 of 148) and glm/kimi* — their probe rows describe the clean-replay subset, which is non-random (hidden-rerun episodes are exactly the ones that fail replay). qwen/luna replay losses: 12/0. | What a capped agent would do with a bigger budget and *no* user turn (every probe arm adds a user turn — that counterfactual is unmeasured); unconditional reporting-capability estimates (stage B is conditioned on ignoring stage A, biasing it down — B1 is an existence proof, a lower bound); nemotron/glm/kimi probe rates as population statements about all their censored episodes. |
| **Repro & provenance** | Per-episode seeds; replay demonstrated episode-level — but *broken by construction* for the 901 hidden-rerun episodes (benchmark bug, confirmed empirically by probe fidelity rejections). Local models reproducible; gateway models only as served on 2026-10-17/18. | Bit-exact reproduction of the full corpus, or of gateway-model behavior at a later date. |
| **Time & provenance of claims** | Built 2026-10-17/18 (~16h to dataset freeze, ~33h to evidence package) + review/remediation/probe after. Novelty verdicts are as-of-2026-10-18; the closest prior/concurrent work is Sep–Oct 2026 (see reviews/adversarial-prior-art.md). | "First to do X" for the method (fault injection into agent benchmarks is established); priority over concurrent preprints. |

## The one-sentence scope statement (say this before any number)

> "On one fixed single-agent scaffold over 97 benign English office tasks with seeded,
> uniform synthetic tool failures, judged by an LLM cascade against deterministic
> environment state — five specific models showed the following, with task-clustered
> intervals."

## Quick answers to "does this apply to…"

- **…production agents?** Directionally informative, numerically no: scaffolds change
  conduct by an order of magnitude. The deployment-relevant claims are the *shape* results
  (visibility-tracking of false claims; silence-as-propensity; three-trait dissociation).
- **…other benchmarks/domains?** Unknown; one benchmark family. The per-task CSV shows
  within-benchmark heterogeneity, which argues against extrapolating further.
- **…your judge being wrong?** Bounded, published, and the environment — not the judge —
  decides truth. Range under instrument disagreement always shipped next to the point rate.
- **…tomorrow's models?** Three of five are API models we don't pin. The claim is about
  measured behavior at a date, not model identity over time.

## The hostile-expert question bank (from verification/v2-methodology-review.md), with artifact answers

1. *How many probed episodes already had utility=true pre-probe?* — 85 of the graded
   originals; A3 mechanism split (112 finished during probe / 51 already complete) in
   PROBE_ANALYSIS.md.
2. *Why did the probe audit reuse the Finding-3 design?* — It did; disclosed in
   PROBE_ANALYSIS.md, and discharged by the strengthened gemini-free full-text re-audit of
   all 1,082 probe answers (REAUDIT.md §probe).
3. *What do the reverse-audit confirmations mean given the A→F collapse?* — They bound
   F-should-be-S errors only; declared in REAUDIT.md and REPORT; the A/F boundary stays a
   limitation (BLIND_SPOTS #9).
4. *Does gpt-6.1-sol shield its vendor-sibling luna?* — No: on luna's 124 candidates sol
   confirms S less often than grok (115 vs 119); vendor-overlap check in REAUDIT.md.
5. *Where is the capability-conditioned table and which reps count?* — REMEDIATED_TABLES.md:
   rule specified (≥3 of the ≤4 primary-set p=0 reps pass); headline rates move <1pp;
   conditioned p=0 baseline has n=3–8 (precision caveat attached to the baseline range).
6. *Persistence on the primary set, committed script, why n=400 everywhere?* —
   PERSISTENCE.md/persistence.py; the uniform n=400 was a v1 artifact, superseded; real
   n=389–685; qwen 13.1× vs luna 2.3×; H4 "mixed, weakly supportive."
7. *Do the borderline McNemar contrasts survive clustering/multiplicity?* — Not claimed:
   REMEDIATED_TABLES.md now states only the p<1e-80 rows and the null are conclusions.
8. *Can the timeline be reconstructed from git?* — TIMELINE.md: two clerical document
   dates; registration commit 46 min into the run; 94% of episodes provably post-commit;
   ≤0.9pp headline sensitivity to dropping the rest (live-verified).
9. *What happened in the zi>0 cells at p=1.0?* — 4 primary-set episodes, zero tool calls,
   all acknowledged non-completion (REMEDIATED_TABLES.md); exclusion hides nothing.
10. *A5 pooled across p?* — Per-dose A5 table added to PROBE_ANALYSIS.md: qwen resumes
    spinning through a TOTAL outage in 74.6% [70.2,78.7] of p=1.0 censored episodes.
