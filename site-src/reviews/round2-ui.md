# Round-two UI and editorial review

Reviewed the actual built site at http://localhost:8765 on 2026-10-18 using installed Chrome via Playwright. Read-only; no repository edits. Widths: 320, 390, 650, 768, 1024, 1280, 1440 px, 900 px viewport height. This review covered layout, seven examples, interaction, no-JavaScript behavior and presentation flow; scientific re-adjudication belongs to the evidence review.

## Verdict

No remaining blocking UI finding. Both material round-one defects are fixed. The page now makes a coherent three-part argument, and the examples show the behavioral differences more clearly than aggregate metrics alone. The skeptical reading remains available beside each claim: failed-only population, asymmetric checkpoint comparison, quiet-fault execution semantics, and selected probe stage B.

## Fixes verified

- **1024 px clipping fixed.** The opening chart is now 928 px wide with an equally wide container, and the quiet comparison also fits. At 1280 the opening chart fits exactly at 640 px. All three graphics fit at 390/650/768/1024/1280/1440; no page-level horizontal overflow at any tested width. At 320 the 336 px graphic has a 284 px scroll container, explicitly says “Scroll chart horizontally to see every value,” and the focused visible region scrolls 40 px with ArrowRight. The remaining deliberate 320 px local overflow is discoverable and keyboard accessible. Evidence: `/tmp/sf-r2-1024-top.png`, `/tmp/sf-r2-1280-top.png`, `/tmp/sf-r2-320-chart-scrolled.png`.
- **Selector jump fixed.** After the opening CTA and Qwen selection, the selector stays at the same vertical position. Desktop 1440: y=349 before/after; mobile 390: y=416 before/after. All seven choices remain visible above the panel. Evidence: `/tmp/sf-r2-1440-selector-settled.png`, `/tmp/sf-r2-390-selector-settled.png`.
- **Second finding now matches its visual.** The lead compares lost response with explicit timeout in four of five models; it no longer makes the five-channel ranking claim that the immediate graphic could not establish.
- **Cap defined immediately.** Opening copy now says “tool-use loop limit without an answer.”

## Functional checks

- All seven selectors open the intended panel: Luna acknowledgment, Qwen cap, GLM successful lost receipt, Kimi partial acknowledgment, GLM partial claim, Nemotron contradiction, Nemotron unverified conclusion.
- Tab reaches the next native link; Enter selects Qwen. Browser Back/Forward restores the corresponding selected episode and hash. Direct GLM episode URL opens that episode and lands below the sticky header (panel y=104; mobile header bottom=94).
- No JavaScript: all seven native episode disclosures exist and the Qwen disclosure opens; core prose and all graphics remain available.
- All seven examples visually reviewed at desktop, with mobile Qwen and deep-link GLM additionally inspected. Request, tool evidence, response, environment outcome, classification and source records remain distinct. Markdown syntax inside verbatim quotations is visibly preserved; that is acceptable evidence presentation.
- No page errors or HTTP responses >=400 occurred during the home-page review. Methods page at 320 has no page-width overflow.
- Main screenshots: `/tmp/sf-r2-detail-example-*.png`, `/tmp/sf-r2-390-probe.png`, `/tmp/sf-r2-650-quiet.png`. Deep-link screenshots intentionally put the episode at the top, leaving its selector above the viewport; this is different from in-selector switching and is not the fixed jump bug.

## First 30 seconds and five-minute route

At 1280/1440, the first viewport shows the plain-language result, the five-model comparison, the Qwen denominator and interval, and the key qualifications. At tablet/mobile the prose result appears first and the chart follows immediately. The hierarchy makes the opening question and main answer understandable without reading the methods page.

I exercised the route: opening → Luna/Qwen → GLM lost receipt → quiet comparison → Nemotron contradiction → probe → closing conclusion. It has no broken or unexpectedly hidden destination. The 533-word script needs about 4:06 at 130 wpm, leaving about 54 seconds for pointing, selecting and scrolling. This is a plausible five-minute presenter route, **not a performed human spoken rehearsal**. Do not present automated navigation timing as a human demo duration.

## Remaining non-blocking design tradeoffs

1. **The walkthrough doubles back.** After the quiet chart it returns upward for a contradictory-claim example before moving down to the probe. The persistent Real episodes link makes that workable. The presenter should know this route; a visitor casually reading linearly may skip the contradiction examples. An optional future polish would add a direct Nemotron contradiction link near the quiet interpretation, but this is not needed to ship.
2. **Small-screen evidence takes several viewports.** The seven-way selector wraps to three/four rows and an episode becomes long at 320–390 px. This is an acceptable tradeoff for legible text and full provenance; the five-minute live demonstration is strongest at desktop width.
3. **No human timing claim yet.** The script is transparently marked as a pacing plan. Keep that distinction in acceptance reporting.

## Reproducibility

Scripts: `/tmp/silent-failures-qa/round2.cjs`, `r2-interact.cjs`, `r2-detail.cjs`, `r2-final.cjs`. Measurements: `/tmp/sf-r2-results.json`, `/tmp/sf-r2-interact.json`, `/tmp/sf-r2-detail.json`. The interaction-specific script waits for smooth scrolling to settle; use its `*-selector-settled.png` screenshots rather than immediate-capture selector screenshots from the first script.
