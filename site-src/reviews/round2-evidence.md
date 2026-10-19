# Round 2 — fresh-context evidence review

Reviewed the actual generated `site/index.html` and `site/methodology.html`, verified byte-for-byte against the pages served at `http://localhost:8765/`, plus the example JSON and chart generator. Reference research: frozen `f12eb47614350aca1cdf21cefc18ab58dd95e9d0`. Read-only review; no experiment, label, or research changes.

## Findings

No P0/P1 defect or numerical/provenance blocker found. The three-message narrative stays within the evidence. One small wording cleanup remains:

**P3 — Finish conditioning the quiet-fault explanation in the spoken script.** `site-src/walkthrough.html:5` now correctly says “When an explicit-error injection fires, that tool call does not execute,” but follows with “In the quiet arm, it executes, but its output is suppressed.” At p=0.5, unselected quiet-arm calls return normally; the GLM refund example itself includes one normal read. Frozen `scripts/experiment.py:118–132` calls the original tool and suppresses output only inside the sampled injection branch. Replace the second sentence with “When a quiet injection fires, the tool executes, but its output is suppressed.” The preceding sentence and correct mechanism disclosure make this a minor residual ambiguity, not a numerical failure.

## First-round fix verification

- The opening now defines the cap as the **tool-use loop limit**, and its persistent qualification says acknowledgment labels are LLM-assigned without human calibration. The probe caption also names the uncertain ambiguous/non-completion boundary. This resolves the measurement-placement finding.
- The mechanism schematic now uses the actual `ServiceTimeout: Service temporarily unavailable: the request timed out.` text.
- The second conclusion now compares lost responses directly with **timeouts** in four of five models, matching the visible two-series infographic. The larger five-channel table remains available. No all-channel ranking must be inferred from that graphic.
- The original presenter-script arm-wide explicit-error assertion is fixed. The quiet sentence merits the small symmetrical correction above.
- Chart cropping and selector positioning require rendered interaction verification and belong to the separate round-two UI review; this evidence review does not claim that source inspection proves those fixes.

## Independent evidence checks

1. Re-read frozen `analysis/REMEDIATED_TABLES.md` and `analysis/PROBE_ANALYSIS.md`. Conduct values, all five denominators, Qwen 525/574 = 91.5% with task-bootstrap 88.0–94.5 interval, quiet-versus-timeout point rates and Jeffreys intervals, and probe 819 → 560 → 559 → 531 match the presentation. The 51/163 pre-completed A3 tasks are explicitly described as the full-probe success-consistent answer group, not the Qwen main slice.
2. Independently checked **all seven** episode records and pinned JSONL source lines against `git show` of the frozen commit; published classifications and independent re-audit records match exactly where supplied. Every selected original passes primary inclusion and received an injection. All seven saved message lists match their extracted original archive member, each member SHA-256 matches the extract, and displayed quotes are exact final-message substrings. This verifies selected evidence, not the full corpus anew.
3. Read the decisive tool sequences: Luna's three timeouts; Qwen's 16 timeouts and absent final; successful GLM refund with suppressed send result; Kimi's three failed calendar writes; Nemotron's validation error plus two failed writes; GLM's blocked Eve send and successful Dora send; Nemotron's suppressed transaction read and zero-spending conclusion. The site correctly separates visible contradiction, partial completion, and unverified inference. It does not invent the lost transaction payload or present the refund as failure.
4. Checked the selected Qwen probe against its frozen JSONL record and independent F/F re-audit. The answer is exact; original versus follow-up populations remain distinct. Three executed continuation generations versus four generated tool-call responses is explicitly qualified. No full continuation transcript is implied.
5. The public evidence route exposes complete selected conversations through static JSON, pinned result/label lines, archive member identities and hashes, and methodology provenance. It explicitly discloses that the full archive is not hosted here and that the October 18 release lookup found no releases despite the frozen README. It does not pretend the absent release archive is accessible. Publication of the newly generated site still requires deployment verification by the integrator.

## Interpretation boundary

The site does not attribute Qwen's behavior causally to ablation, isolate failure visibility as a mechanism, treat selected stage-B answers as unconditional recovery, infer deceptive intent from silence, or imply human-calibrated response labels. It retains asymmetric exclusions, clustering, registration timing, gateway/stack confounding, missing raw environment snapshots, and lack of a clean full rerun in the evidence record. The opening presents a failed-episode comparison rather than an overall model-quality ranking. Those restrictions are appropriate and should survive the final edit.
