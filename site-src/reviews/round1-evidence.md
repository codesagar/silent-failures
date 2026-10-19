# Round 1 — independent evidence review

Scope: actual generated `site/index.html` and `site/methodology.html`, website example JSON and chart generator, checked against frozen `f12eb47614350aca1cdf21cefc18ab58dd95e9d0` records. Read-only review; no experiment or research changes.

## Findings

### P2 — Presenter script turns an injected-call rule into an arm-wide rule

`site-src/walkthrough.html:5` (also present in generated index at review time): “In the explicit-error arms, the tool never executes. In the quiet arm, it executes, but its output is suppressed.”

This is false at the arm level for p<1. Calls without a sampled injection execute normally in both arms. The site itself shows hotel lookups and a Slack send succeeding in explicit-error arms. Frozen `scripts/experiment.py:118–132` samples the fault independently per call and invokes the original tool on the non-injected branch. Change to “For an injected explicit error, that call never executes. For an injected quiet fault, the tool executes and its output is suppressed.” This is particularly important in the spoken five-minute script, where the missing per-call condition could undermine the central mechanism explanation.

### P2 — Bring the acknowledgment-label measurement limit next to the headline

The first conclusion (“four models acknowledged non-completion in 86–99%”) and probe conclusion (“531 of 559 … 95.0%”) are label-based measurements. The opening’s no-human-calibration statement is inside a closed disclosure; the F-versus-A ambiguity is only explained on methodology. The immediate opening qualification addresses ablation causality, and the immediate probe qualification addresses selection/prompting, but neither alerts the reader that these are LLM-assigned response labels. Frozen `analysis/REAUDIT.md` explicitly says the stronger instrument collapses ambiguous controls toward F and is near-blind on the F-versus-A boundary. Add one compact persistent sentence at the opening and/or probe, e.g. “Response categories are LLM-assigned; acknowledgment versus ambiguity lacks human calibration.” Keep detailed audit counts in methodology. This is a presentation qualification gap, not evidence that the published numerators are wrong.

### P3 — The schematic timeout string is not the actual injected error

`site-src/index.html:25` uses `TimeoutError: tool call timed out`, while the frozen harness and selected traces use `ServiceTimeout: Service temporarily unavailable: the request timed out.` The diagram is evidently explanatory, but there is no explicit “schematic” marker. Since real tool messages are a selling point of the adjacent examples, use the actual text or mark it as schematic. No numerical effect.

## Independent checks completed

- Primary conduct rates/denominators match `analysis/REMEDIATED_TABLES.md`; Qwen 525/574 = 91.5%, four other F rates 86.3–99.3%, and task-bootstrap bounds match the frozen table.
- Quiet comparison matches the published p=.5 failed+dosed table, including GLM as exception. All-five-channel claim is true as a descriptive point-estimate claim. The source table is accessible, and the no-causal-visibility interpretation is correctly qualified.
- Probe flow matches published source: Qwen 819 -> 560 stage-A nonresponders -> 559 B answers -> 531 F labels, with one length-limit artifact. All 1,000 main-slice probe records with assigned p>0 actually have >=1 original injection, so the site’s “injected” shorthand does not misdescribe this realized population.
- All seven example result records, published classifications, independent re-audits where used, and exact linked JSONL lines match frozen git content. Requests equal saved user messages; displayed response excerpts are exact final-message substrings.
- All seven complete saved message lists and utility fields match `/tmp/sf-example-traces/<archive_member>` exactly; member hashes match JSON. All seven pass primary eligibility (no harness error, rep<=3, counted calls<=saved tool messages), and all received an injection.
- Manually checked key sequences: Luna three timeouts; Qwen 16 timeout calls and no final; GLM refund successful despite suppressed send output; Kimi all three calendar writes time out; GLM only Dora delivery succeeds; Nemotron calendar has validation error then two timeouts; Nemotron zero-spending conclusion follows suppressed []. Interpretations correctly distinguish these cases.
- The Qwen stage-B answer equals frozen probe record; F/F re-audit matches. The statement that four generations include only three executed continuation generations matches `scripts/probe.py`’s cap logic. No recovered full continuation trace is implied.
- The method page correctly separates original protocol/reanalysis/re-audit/probe, overlapping exclusions, lack of matched ablation control, no human calibration, registration timing, and inability to perform a clean full rerun.

No P0/P1 data or provenance failure found. Do not turn that into a blanket scientific endorsement: raw environment snapshots/unsuppressed lost reads are absent, acknowledgment labels lack human calibration, model and serving stacks are confounded, and failed-only groups are selected differently. These limits are correctly preserved on the methodology page. The two P2 wording/placement fixes are website-only and require no new research.
