# Silent Failures: five-minute evidence briefing

The redesign replaces the rejected eight-section essay with three principal findings, a prominent evidence selector, and a separate research record. The first desktop viewport contains a conclusion and the full five-model comparison; mobile presents the conclusion first and then a dedicated narrow chart.

## Chosen argument and alternatives

1. Reporting conduct is distinct from task success: four configurations predominantly acknowledge failure under heavy timeouts; Qwen ablated predominantly reaches the cap without output.
2. Missing tool output is not failed execution: a quiet injection runs the tool before suppressing its result. Failed-episode claim rates are higher than explicit timeouts in four configurations, with GLM the exception.
3. Cap silence does not establish inability: a selected tools-off follow-up elicits acknowledgment. The stage-B selection is part of the figure.

The independent initial reviews considered case-first, baseline-first, and measurement-first narratives. Baseline-first was rejected because small, changing failure denominators consume the opening explanation. Case-first overweights an illustrative rare outcome. Persistence is mixed exploratory evidence, not a headline. Detailed alternatives and critique dispositions are in `review-notes.md`.

## Visual direction

A warm editorial research briefing, with shared baselines and source-backed trace panels instead of decorative study counts. Custom project tokens override the Diagram Design default skin locally; no global skill profile was changed.

| Role | Token |
| --- | --- |
| Paper | `#f7f5ef` |
| Secondary paper | `#ebece4` |
| Figure surface | `#fffefa` |
| Ink | `#252b29` |
| Muted text | `#59635d` (diagram helper retains `#626b65`) |
| Rule | `#ced3c8` (diagram helper retains `#d9dcd2`) |
| Accent | `#ad4328` |
| Acknowledgment series | `#3c6655` |
| Probe section | `#243a32` |
| Editorial headings / quoted responses | Instrument Serif |
| Body / chart labels | Geist |
| IDs and tool syntax | System monospace |

The website self-hosts its fonts. Standalone diagram HTML is self-contained and declares Arial/Georgia fallbacks for offline use. No animated charts, external runtime requests, backend, or model calls.

## Diagram Design decisions

Diagram Design 2.6.110 supplies accessible SVG, the stacked-bar/paired-dot grammar, orthogonal connectors, restrained focal color, and local overflow. The `fit` preset is used; no semantic pattern exactly matches the sampling-selection flow, so the flowchart type governs it directly. Relevant references read: style guide, output spec, bar chart, flowchart, and semantic patterns.

- Conduct: five rows, a common 0–100% whole. Geometry uses independently verified integer counts; printed percentages retain published rounding. Kimi's five ambiguous cases remain visible. A compact adjacent disclosure provides every task-cluster interval and denominator.
- Quiet comparison: explicit-timeout and lost-response points on the same 0–100% scale. Hollow versus filled points preserve meaning without color. Jeffreys intervals and both denominators accompany each row. Other fault types remain in the full table.
- Probe: a selection flow, not a proportional Sankey. The 259 respondents leave the continuation branch; only 560 nonresponders reach stage B. The single artifact and the denominator of 559 remain visible.
- Every principal diagram has separate wide and narrow layouts. Intermediate-width sections expand to a single column before a chart can crop its marks. At 320px, labeled, keyboard-focusable local scrolling preserves legible type.

Older standalone infographics remain available, while secondary tables and methodological depth live on `methodology.html`. Every principal graphic has accessible title/description IDs and a standalone HTML counterpart. The main argument survives JavaScript being disabled.

## Interaction and pacing

Seven primary episodes cover all five models. Native disclosures work without JavaScript. Enhancement adds a compact linked selector, keeps keyboard focus and the selector in place, and supports deep links and browser history. Every selected record includes request, summarized tool sequence, exact response/absence, environment outcome, classification, limitations, and pinned sources. Qwen's follow-up is separately identified.

`walkthrough.html` contains the exact spoken script and six time allocations totaling five minutes. The build counts the spoken words. Speech duration is explicitly a 130-word/minute estimate; browser navigation was separately rehearsed on a five-minute clock. This is not a human usability or read-aloud study.
