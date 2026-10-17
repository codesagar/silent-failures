# Research: LLM-as-Judge Reliability (2024–2026) — Is Human Calibration Still Necessary?

Date of research: 2026-02-19. All primary claims below were verified against directly fetched source text (arXiv HTML/abstracts, official docs) unless marked otherwise.

## Summary

Current evidence does **not** support using an LLM classifier as a primary outcome measure without human calibration. The best-studied case for agent outcomes — AgentRewardBench (Apr 2025) — found **no judge exceeded 70% precision** on agent task success, with judges systematically fooled by agents' own success-claims; safety-specific work (OS-Harm, Jun 2025) achieved only ~0.76–0.79 F1 vs. humans even with a frontier judge. Major-lab guidance (Anthropic, OpenAI) explicitly says to calibrate graders against human expert labels and report agreement; research practice ranges from ~100 doubly-annotated items (minimum credible) to several thousand (SORRY-Bench: 7.2K labels), with 1,000–1,300 expert labels typical for dedicated judge-validation studies.

## Findings

### 1. AgentRewardBench: judges are unreliable for agent-trajectory success

1. **Claim:** Across 1,302 expert-annotated web-agent trajectories (5 benchmarks, 4 agent LLMs), **no LLM judge among 12 tested achieved above 70% precision** on predicting task success — i.e., ≥30% of judge-labeled "successes" were failures. The paper states this "severely limits the usefulness of the judges" and that "LLM judges are currently not a reliable way of assessing the true capabilities of agents."
   **Sources:** [AgentRewardBench, arXiv:2504.08942](https://arxiv.org/abs/2504.08942) (v1 Apr 11 2025; v2 Oct 6 2025), full HTML fetched. **Support:** direct evidence (quoted from §4.3). **Confidence:** high.

2. **Claim:** Judges and rule-based evaluators err in opposite directions: LLM judges **overestimate** success rates on nearly every benchmark, while rule-based evaluation **underestimates** them (rule-based recall only 55.9%; GPT-4o's measured success was 16.7% lower on WebArena and 18.5% lower on VisualWebArena vs. expert labels). Rule-based scoring even reverses model rankings relative to experts (Qwen2.5-VL ranked above GPT-4o, contrary to expert judgment).
   **Sources:** [arXiv:2504.08942 §5](https://arxiv.org/html/2504.08942v2). **Support:** direct evidence. **Confidence:** high.

3. **Claim:** Human calibration quality context: AgentRewardBench used 6 expert annotators; inter-annotator agreement on success was **89.3%** (second annotator on GPT-4o/WebArena subset) — so even the human ceiling is ~90%, but judges fall far below it on precision.
   **Sources:** [arXiv:2504.08942 §3.3](https://arxiv.org/html/2504.08942v2). **Support:** direct evidence. **Confidence:** high.

4. **Claim (error modes, directly relevant to failure-reports vs success-claims):** The paper's error analysis (§6) documents four systematic judge failures: (a) **grounding mismatch** — judge accepts the agent's hallucinated description of the screen; (b) **misleading agent reasoning** — agent *claims* success in its chain-of-thought after failing, and the judge echoes the claim ("The agent successfully … applied the filter" when no filter was applied); (c) **missed instruction details / partial completion** — agent adds item to cart but never buys; judge marks the purchase complete; (d) **misunderstanding action intent** — agent completes steps then reports task "unfeasible"; judge still scores success. Authors link this to LLM sycophancy (Sharma et al. 2023).
   **Sources:** [arXiv:2504.08942 §6](https://arxiv.org/html/2504.08942v2). **Support:** direct evidence. **Confidence:** high.

### 2. Judge biases: MT-Bench and 2024–2026 self-preference work

5. **Claim:** Zheng et al. (NeurIPS 2023, arXiv:2306.05685, "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena") established the canonical result: GPT-4 judges reach **>80% agreement with human preferences — the same level as human–human agreement** — but documented **position bias, verbosity bias, self-enhancement (self-preference) bias, and limited reasoning/math grading ability** as systematic judge failure modes. Note the >80% figure is for *pairwise chat preference*, not binary outcome classification of agent behavior — researcher inference: it does not transfer to the agent-outcome setting (see finding 1).
   **Sources:** [arXiv:2306.05685](https://arxiv.org/abs/2306.05685) (v4 Dec 2023), abstract fetched. **Support:** direct evidence for the figures; labeled inference for non-transferability. **Confidence:** high (figures), medium (inference, but supported by AgentRewardBench).

6. **Claim:** Self-preference bias has since been quantified. Wataoka et al., ["Self-Preference Bias in LLM-as-a-Judge" (arXiv:2410.21819, Oct 2024, NeurIPS 2024 workshop)](https://arxiv.org/abs/2410.21819) propose a metric over 8 judges and find **GPT-4 in particular exhibits high self-preference bias**, mechanistically linked to low perplexity of its own outputs (judges favor text that "sounds like them" even when not literally their own). Panickssery et al., ["LLM Evaluators Recognize and Favor Their Own Generations" (NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html) show a **linear causal correlation between self-recognition capability and self-preference strength** via fine-tuning experiments.
   **Sources:** as linked (abstracts verified). **Support:** direct evidence. **Confidence:** high.

7. **Claim (2025–2026 follow-ups, including family bias):** ["Beyond the Surface: Measuring Self-Preference in LLM Judgments" (EMNLP 2025 main)](https://aclanthology.org/2025.emnlp-main.86/) introduces a gold-judgment-referenced DBG score separating genuine quality from bias and identifies text style and post-training data as drivers. A 2026 preprint, ["Quantifying and Mitigating Self-Preference Bias of LLM Judges" (arXiv:2604.22891)](https://arxiv.org/html/2604.22891v2), treats self-preference as a systematic directional distortion of leaderboards. An industry audit (IOV Labs blog, found via search snippet, **not independently verified**) reports every frontier judge inflating **its own model family** by ~14 points vs. a neutral consensus panel, with the bias implicit (present even without self-recognition). Researcher inference: family bias is real and material, so a judge should not come from the same family as the evaluated model when grading its own family's outputs — this is also Anthropic's explicit recommendation (finding 9).
   **Sources:** as linked; [IOV Labs post](https://labs.iovstudio.kr/en/news/self-preference) (weak/unverified). **Support:** direct evidence for papers' existence/claims; interpretation for the practical rule. **Confidence:** medium (family-bias magnitude), high (bias existence).

### 3. Lab/org best-practice guidance on calibration

8. **Claim:** Anthropic's published eval guidance ("What we look for in a wellbeing evaluation", Anthropic PDF, 2025) states explicitly: **"Calibrate graders against human expert labels and report the agreement, consider using a different LLM for scoring than the ones you're testing, and inspect a sample of eval transcripts by hand."** It separately recommends **"at least 100 distinct items"** as a rough minimum for a statistically meaningful eval (that figure is eval-set size, not calibration-set size per se).
   **Sources:** [Anthropic wellbeing-eval PDF](https://www-cdn.anthropic.com/files/4zrzovbb/website/5ecb637cb206057cb93cf4a9e72e843fda5e9892.pdf) (quoted via Exa search snippet of the PDF; not re-fetched in full). **Support:** direct quote from source snippet. **Confidence:** high for the quote; medium for surrounding context.

9. **Claim:** Anthropic's engineering post ["Demystifying evals for AI agents"](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (2025) describes the recommended maturity path as: manual grading first → LLM graders with product-team-defined criteria → **"periodic human calibration"** as an ongoing practice (Descript case study). I.e., human calibration is not a one-time bootstrap but a recurring control.
   **Sources:** as linked. **Support:** direct evidence (search snippet of official page). **Confidence:** high.

10. **Claim:** OpenAI's evals documentation ([Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices), [Graders guide](https://developers.openai.com/api/docs/guides/graders)) recommends model-grading with human review in the loop ("inspect a sample ... by hand", log mining, annotations as ground truth) but — researcher observation — does **not** publish a specific numeric calibration-sample-size standard in the pages surveyed.
    **Sources:** as linked. **Support:** interpretation of official docs. **Confidence:** medium.

11. **Claim:** UK AISI's Inspect framework provides `model_graded_qa()` / `model_graded_fact()` scorers and a human-agent/offline score-editing workflow, but the core scorer documentation ([inspect.aisi.org.uk/scorers.html](https://inspect.aisi.org.uk/scorers.html), fetched 2026-02) contains **no mandated human-calibration protocol or sample size** — calibration is left to the eval author. Inspect-evals' StrongREJECT implementation adds judge-output sanity gates (discard out-of-rubric scores) — an acknowledgment of judge unreliability — rather than human calibration.
    **Sources:** [Inspect scorers docs](https://inspect.aisi.org.uk/scorers.html); [Inspect-evals StrongREJECT](https://ukgovernmentbeis.github.io/inspect_evals/evals/strong_reject/index.html). **Support:** direct evidence (docs fetched) + interpretation. **Confidence:** high.

12. **Claim:** HELM Safety (Stanford CRFM, blog Nov 2024) runs GPT-4o and Llama-3.1-405B as judges across its safety benchmarks but **does not report its own validation of judges against human annotations** (it inherits human-validation claims from the upstream benchmarks, e.g., HarmBench). Notably it documents a judge failure mode specific to safety grading: **judges refusing to grade toxic content** (refusal rates when judging: GPT-4o 2%, Claude 22.5%, Llama 34.4%, Gemini 51.9%, citing Balachandran et al.).
    **Sources:** [HELM Safety blog, 2024-11-08](https://crfm.stanford.edu/2024/11/08/helm-safety.html) (fetched, answer-mode extraction). **Support:** direct evidence. **Confidence:** high.

### 4. Judge reliability for SAFETY/harm classification of agent outcomes

13. **Claim:** OS-Harm (arXiv:2506.14866, v1 Jun 17 2025, NeurIPS 2025 D&B Spotlight) — the most on-point study — builds 150 computer-use-agent safety tasks and an automated judge, and reports judge–human agreement of **0.76 and 0.79 F1** (safety and accuracy respectively) using GPT-4.1 as judge, measured against manual annotations with per-category precision/recall breakdowns (Table 8). The authors frame this as "high agreement," but — researcher inference — 0.76 F1 means roughly 1-in-4 to 1-in-5 harm/safety labels disagree with humans, which is far too noisy for an uncalibrated primary outcome measure, especially where harm rates are low and false negatives are the costly error.
    **Sources:** [arXiv:2506.14866](https://arxiv.org/abs/2506.14866) (abstract fetched; Table 8 confirmed via arXiv HTML snippet). **Support:** direct evidence (figures) + labeled inference (adequacy judgment). **Confidence:** high.

14. **Claim:** SORRY-Bench (arXiv:2406.14598, Jun 2024, ICLR 2025) demonstrates the field's accepted methodology for safety refusal/fulfillment classification: they collected **7,200+ human annotations** (16 responses × 450 unsafe instructions) specifically to meta-evaluate judge designs, then fine-tuned a 7B judge on those labels to match GPT-4-scale accuracy. I.e., even work arguing small judges suffice **required thousands of human labels to make that argument**.
    **Sources:** [arXiv:2406.14598](https://arxiv.org/abs/2406.14598); [human-judgment dataset card](https://huggingface.co/datasets/sorry-bench/sorry-bench-human-judgment-202406). **Support:** direct evidence. **Confidence:** high.

15. **Claim:** The "judges-replace-humans" claim is **not supported** for safety classification of agent outcomes. Every 2025–2026 safety-judge paper found either (a) validates against substantial human label sets and reports imperfect agreement (OS-Harm 0.76 F1; SORRY-Bench meta-eval), or (b) is itself a benchmark of judge failures (AgentRewardBench). No paper surveyed claims human-free judge deployment is safe for primary safety outcomes; survey work ("When AIs Judge AIs", arXiv:2508.02994, Aug 2025) and safety-case work (Springer 2025, "Arguing the Safety of Agentic AI Using LLM-as-Judge Evaluations") treat judges as components needing validation and metric baskets, not human replacements.
    **Sources:** as linked above; [arXiv:2508.02994](https://arxiv.org/html/2508.02994v1). **Support:** interpretation across the surveyed corpus (absence-of-evidence claim, bounded to sources found). **Confidence:** medium-high.

### 5. Refusal / failure-report vs. success-claim failure modes

16. **Claim:** Documented, replicated failure modes when classifying refusals and completion claims:
    - **Sycophantic acceptance of agent success-claims:** judges adopt the agent's own (false) statement of success (AgentRewardBench §6 — direct evidence, high confidence).
    - **Partial completion scored as full completion:** add-to-cart ≠ purchase example (AgentRewardBench §6 — direct evidence, high confidence).
    - **Agent "unfeasible"/failure-reports mis-scored:** judge sees correct on-screen result, ignores that the agent reported failure (AgentRewardBench §6 — direct evidence, high confidence).
    - **Partial-compliance refusals labeled COMPLIANT:** a 2026 preprint ("Partial Compliance as Compliance", espiradev.org, **non-peer-reviewed, unknown-provenance — low confidence**) reports open-weight judges systematically labeling trajectories compliant when the agent did a harmless intermediate step then refused the operative instruction.
    - **Judge refusal-to-grade on toxic content** skews safety scores (HELM Safety blog, direct evidence, high confidence; up to 51.9% judge refusal for Gemini).
    - **Hedged/stylistic effects:** self-preference work shows judges reward low-perplexity, familiar-style text (arXiv:2410.21819), implying hedged refusals styled like the judge's own outputs get systematically different treatment — researcher inference, medium confidence.
    - Linguistic mutations (persuasion, technical phrasing) materially change refusal classification difficulty — SORRY-Bench's 20 mutation types exist precisely because judges are brittle to them (interpretation, medium confidence).

### Conclusion

- **Does current evidence support an LLM classifier as a primary outcome measure WITHOUT human calibration? No.** The strongest agent-specific evidence (AgentRewardBench: <70% precision, systematic deception by agent self-reports; OS-Harm: 0.76 F1 on safety) shows error rates of 20–30% against expert judgment, with errors that are *systematic* (optimistic, sycophantic, family-biased), not random — so they bias conclusions rather than merely adding noise. Lab guidance (Anthropic explicitly; OpenAI implicitly) requires calibrating against human labels and reporting agreement, and recommends a judge from a different model family than the system under test.
- **Standard calibration sample sizes (observed practice, not a single standard):**
  - Minimum credible floor per lab guidance: **~100 items** with reported agreement (Anthropic wellbeing-eval guidance; note the 100 figure is framed as minimum eval size).
  - Dedicated judge-validation studies: **~1,000–1,300 expert-labeled items**, double-annotation on a subset to establish the human ceiling (AgentRewardBench: 1,302 trajectories, 89.3% IAA on a doubly-annotated subset; OS-Harm: manually annotated subset with per-category P/R).
  - Judge training/meta-evaluation for safety refusal: **~7K labels** (SORRY-Bench).
  - Practitioner heuristics of 50–200 stratified labels per binary criterion circulate in 2025–2026 blog posts (hashnode/medium/galileo) but are **not authoritative**; cited only as evidence of community norms.
- **Minimal defensible protocol (researcher synthesis):** double-annotate ≥100–200 stratified trajectories (oversampling the rare class, e.g., harms/refusals), report judge-vs-human precision/recall (not just accuracy/agreement) for the decision-relevant class, use a judge outside the evaluated model's family, give the judge ground-truth state (screenshots/trees), never rely on agent self-reports, and re-calibrate when the judge model, prompt, or task distribution changes.

## Contradictions

- Zheng et al. 2023's ">80% agreement, human-level" result is frequently cited to justify human-free judging, but it measured pairwise chat preference; AgentRewardBench (2025) and OS-Harm (2025) directly contradict its transfer to binary agent-outcome classification (<70% precision; 0.76 F1).
- OS-Harm's own framing ("high agreement with human annotations") conflicts with the practical adequacy of 0.76 F1 for a primary safety metric — the paper itself still relies on human annotation to make the claim.
- The self-recognition→self-preference causal account (Panickssery et al. 2024) is partially contradicted by the IOV Labs audit claim that bias is implicit (all four models self-prefer, only one self-recognizes) — unresolved; the audit is unverified.

## Missing evidence

- No authoritative, published numeric standard for calibration sample size exists from any major lab or AISI; the ~100-item figure is the closest official guidance and is about eval size.
- Anthropic wellbeing PDF quoted from a search snippet; full-document context not re-verified.
- IOV Labs "~14-point family inflation" figure unverified against a paper.
- espiradev.org partial-compliance preprint: provenance/peer review unknown.
- Did not locate a 2025–2026 paper that affirmatively claims judges can replace humans for safety outcomes — this absence is itself a finding but bounded by search coverage.
- OS-Harm Table 8 per-category precision/recall values not extracted in detail (only headline F1).
- `source_check` tool could not be used (search provider rate limits during this run); decision-critical claims were instead validated by fetching primary source text directly (arXiv HTML/abstracts, official docs), which is noted per claim above.

## Sources

- Kept: AgentRewardBench, arXiv:2504.08942 (https://arxiv.org/abs/2504.08942; HTML v2 fetched in full) — primary evidence on judge precision for agent outcomes and error modes.
- Kept: Zheng et al., MT-Bench, arXiv:2306.05685 (https://arxiv.org/abs/2306.05685) — canonical judge-bias taxonomy and the 80% agreement figure.
- Kept: Self-Preference Bias in LLM-as-a-Judge, arXiv:2410.21819 (https://arxiv.org/abs/2410.21819) — quantified self-preference, perplexity mechanism.
- Kept: Panickssery et al., NeurIPS 2024 (https://proceedings.neurips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html) — self-recognition↔self-preference causality.
- Kept: Beyond the Surface, EMNLP 2025 (https://aclanthology.org/2025.emnlp-main.86/) — 2025 self-preference measurement.
- Kept: OS-Harm, arXiv:2506.14866 (https://arxiv.org/abs/2506.14866) — safety-judge human agreement for computer-use agents.
- Kept: SORRY-Bench, arXiv:2406.14598 (https://arxiv.org/abs/2406.14598) + HF human-judgment dataset — refusal-classification meta-evaluation, 7.2K labels.
- Kept: Anthropic wellbeing-eval PDF (https://www-cdn.anthropic.com/files/4zrzovbb/website/5ecb637cb206057cb93cf4a9e72e843fda5e9892.pdf) — explicit calibration + ≥100-item guidance.
- Kept: Anthropic "Demystifying evals for AI agents" (https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — periodic human calibration practice.
- Kept: OpenAI evals/graders docs (https://developers.openai.com/api/docs/guides/evaluation-best-practices, .../graders) — official grader guidance, no numeric standard.
- Kept: UK AISI Inspect scorers docs (https://inspect.aisi.org.uk/scorers.html) — model-graded scorer design, no mandated calibration.
- Kept: HELM Safety blog, 2024-11-08 (https://crfm.stanford.edu/2024/11/08/helm-safety.html) — judge usage without fresh human validation; judge-refusal failure mode.
- Kept (low confidence): espiradev.org partial-compliance preprint; IOV Labs self-preference audit — relevant 2026 claims, unverified provenance.
- Rejected/deprioritized: hashnode/medium/dev.to/galileo calibration-size posts — SEO-grade, non-authoritative (cited only as community-norm evidence); emergentmind/liner/paperswithcode mirrors — redundant with primary arXiv sources; mindstudio.ai/langchain marketing pages — vendor content.

## Next steps

- Extract OS-Harm Table 8 per-category precision/recall and its human-annotation subset size (fetch arXiv HTML v2 appendix) to pin down the safety-judge floor by harm category.
- Verify the IOV Labs family-bias audit against a formal write-up, and locate a peer-reviewed 2026 quantification of cross-family judge bias.
- Check whether UK AISI's AgentHarm (arXiv:2410.09024) reports judge–human agreement for harm scoring — the closest AISI-authored datapoint not covered here.
