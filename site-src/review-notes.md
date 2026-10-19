# Redesign review and acceptance record

Date: 2026-10-18. Research snapshot: `f12eb47614350aca1cdf21cefc18ab58dd95e9d0`. Website starting point: `1114374`. Original worktree was clean. All implementation and evidence extracts are under `site-src/` and `site/`; original research is unchanged.

## Independent initial perspectives

Three bounded agents worked before the final argument was selected:

- Research critic: ranked interpretations, verified original conduct/probe counts, rejected causal visibility and ablation claims, and flagged Kimi's five ambiguous cases.
- Example curator: extracted seven saved conversations from a hash-matching archive, covered all five models, rejected apparent contradictions whose tool writes actually succeeded, and identified the missing public release asset.
- Editorial challenger: inspected the live incumbent, compared case-first, baseline-first, and measurement-first alternatives, and researched primary figure/interactive-article guidance. Recommended a conclusion plus evidence in the first viewport.

Detailed initial perspectives are in `reviews/initial-evidence.md`, `reviews/initial-editorial.md`, and `example-evidence.md`. Implementation ownership was separate: chart module, example JSON/provenance, and main integration/template/styles.

## Critique round one: actual generated implementation

Fresh-context evidence and UI reviewers inspected generated pages, original sources, and desktop/mobile/tablet browser output. Detailed reports: `reviews/round1-evidence.md` and `reviews/round1-ui.md`.

| Finding | Refinement | Recheck |
| --- | --- | --- |
| At 1024px, local chart overflow hid the right-hand conduct segments without a cue. | Give charts adequate minimum grid columns, switch to full-width sections earlier, select narrow compositions before clipping; show a scrolling cue at 320px. | Second UI reviewer measured and inspected 320, 390, 650, 768, 1024, 1280, 1440px. All quantitative marks fit except explicitly signposted local scroll at 320px. |
| Choosing an episode jumped below its selector and hid it behind the sticky header. | In-selector changes update the open panel/history without scrolling or moving keyboard focus. External deep links remain available. | Seven selections, keyboard Enter, browser Back/Forward, external deep links verified. |
| Explicit-error script said tools never execute across the entire arm. | Condition the statement on an injection firing. | Frozen injector branch re-read by second evidence reviewer. |
| Acknowledgment label caveat was buried. | Add persistent no-human-calibration note beside the opening and uncertain ambiguity/non-completion boundary beside the probe. | Second evidence reviewer verified placement and interpretation. |
| “Highest across five channels” was stronger than the visible two-channel chart. | Main text compares lost responses directly with explicit timeouts; all five channels remain in the expandable table. | Second reviewers verified chart/message alignment. |
| Cap was undefined at first use; timeout schematic used a different error name. | Define tool-use loop limit in opening; show exact ServiceTimeout wording. | Second evidence/UI review. |
| 320px scrollable figures lacked keyboard focus. | Focusable, individually named chart regions and a local-scroll cue. | Keyboard ArrowRight and automated accessibility rechecks. |

## Critique round two: fresh contexts

Reports: `reviews/round2-evidence.md` and `reviews/round2-ui.md`.

- Evidence reviewer independently compared all seven episode records and pinned source lines with the frozen commit, full saved message lists and member hashes with extracted archive originals, and quoted response membership. Chart/probe counts and selection match the frozen tables. No numerical or provenance blocker.
- UI reviewer confirmed fixes across seven widths, all seven examples, keyboard activation, Back/Forward, deep links, no-JS native disclosure, mobile methods, and absence of browser/network errors. No blocking UI finding.
- Remaining evidence wording cleanup: quiet output suppression also needed to be conditional on an injection. Fixed in the final spoken script.
- Optional UI tradeoff retained: the route returns from the quiet comparison to one unsupported-claim example. The navigation allowance includes this; the evidence selector avoids forcing every transcript into the main page.
- Final integrator accessibility scan identified duplicate chart-region names; each figure now has a unique accessible region name. Rechecked after correction.

## Acceptance evidence and limits

- Principal result appears with a full conduct graphic in the desktop opening. Mobile presents the conclusion and values before the chart in the immediate next section.
- Three findings have source links, populations, relevant uncertainty, persistent interpretation boundaries, and routes to examples. Seven original examples all pass primary exclusions; Qwen follow-up is separately identified. The excluded historical demo is not used as a primary example.
- `validate.py` verifies local links/anchors, frozen evidence hashes, all selected source-line records, exact response excerpts, model coverage, primary eligibility, archive pin and selected probe answer. Independent review also checks the raw selected conversations. These do not establish human-grounded label validity.
- 18 standalone Diagram Design self-checks pass. Both new probe layouts pass the geometry verifier. All six principal chart variants were rendered and visually inspected.
- Browser QA: 1440×1000, 1280×800, 1024×900, 768×900, 650×900, 390×844 and 320×740/900. Includes local scrolling, keyboard, selectors, disclosures, no-JS, reduced motion, actual font loading, console/network errors, and accessibility scans. Static generated pages work without external assets or runtime services.
- Repeated whole-site builds produce byte-identical files. A git comparison against the frozen research commit shows no changes outside website paths and the pre-existing Pages workflow.
- The presenter guide allocates exactly five minutes. The final script has 535 spoken words; speech timing is explicitly estimated at 130 words/minute (about 4:07, leaving 53 seconds for navigation). A separately executed browser route completed at 300.00 seconds; scheduled transitions were within 0.12 seconds of their targets. Neither is a human read-aloud or audience-comprehension study.
- The full transcript archive has no public GitHub release asset at inspection. Selected verified conversations are hosted with this site; missing original payloads/environment snapshots are not fabricated. These source-access and measurement limits remain disclosed.

Deployment status is verified through the existing GitHub Pages workflow and the live served page after the website commit; original research and repository visibility remain unchanged.
