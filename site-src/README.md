# Silent Failures website

Presentation-only redesign of a final research package. Original reports, data, labels, scripts, registrations, and historical examples remain unchanged. No model experiments are run by the website or its build.

## Build and preview

```sh
python3 site-src/build.py
python3 site-src/validate.py
python3 -m http.server 8765 --directory site
```

Standard-library Python; static GitHub Pages output. The existing workflow rebuilds, validates, checks generated output against the commit, and deploys `site/` on a master-branch push. The pinned research snapshot remains `f12eb47614350aca1cdf21cefc18ab58dd95e9d0`.

## Authoring map

- `index.html`: three findings, prominent real-episode selector, five-minute route.
- `methodology.html`: research chronology, instruments, populations, secondary findings, context, and limitations.
- `build.py`: reads frozen tables, enforces report hashes, generates static pages/data/standalone diagrams.
- `redesign_charts.py`: wide/narrow conduct comparison, quiet-versus-explicit comparison, selected probe flow. Exact conduct counts cross-checked against original result/classification records; published table rates are asserted.
- `presentation.py`: escapes and renders episode extracts, exports individual JSON records, and counts presenter-script words.
- `examples.json`: seven complete selected saved conversations, original result and classification records, excerpt provenance, and one separately identified probe.
- `example-evidence.md`: curation rationale, rejected candidates, archive/member provenance, interpretation boundaries.
- `walkthrough.html`: six paced segments totaling five minutes; reading speed is explicitly an estimate.
- `styles.css`, `app.js`: responsive layout and progressive enhancement. Core content and native disclosures work without JS.
- `design.md`, `review-notes.md`: visual decisions and critique/verification record.

Fonts and their OFL licenses are self-hosted under `site/fonts/`. No external runtime dependencies. Wide figures have local scrolling; narrow principal figures have their own layouts. Diagram Design 2.6.110 is used at authoring time, not required at runtime or CI.

## Evidence integrity

`research-snapshot.json` pins the source reports and build fails on hash changes. Source links use the frozen commit. `site/data/findings.json` contains published chart values and intervals; this is a presentation extract, not a fresh analysis.

`validate.py` checks local links/anchors, source paths, accessible SVG labels, font signatures, frozen report hashes, chart anchors, source-line episode equality, primary example eligibility, exact final-response excerpts, original label records, the archive hash, five-model coverage, and the selected probe answer. It does not establish human label validity or creative/UI quality.

The full transcript archive is not currently downloadable from GitHub releases. Seven selected conversations were extracted from a local archive matching the frozen SHA-256 and republished as website-specific evidence. Their archive member hashes and pinned source lines are retained. The site discloses the public full-archive access gap.

## Browser and review checks

Two substantive independent critique rounds assess evidence and actual rendered UI. Browser checks cover desktop, tablet, mobile, 320px local scrolling, keyboard controls, deep links/back navigation, all seven selectors, no-JS access, reduced motion, fonts, accessibility scans, and console/network errors. Diagram Design self-checks and probe geometry checks run separately. `review-notes.md` records concrete findings, fixes, and verification limits.
