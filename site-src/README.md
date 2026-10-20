# Silent Failures website

Broad behavioral overview of a final research package, with new deterministic aggregates of frozen episode records. Original reports, data, labels, scripts, registrations, and historical examples remain unchanged. No model experiments are run by the website or its build.

## Build and preview

```sh
python3 site-src/build.py
python3 site-src/validate.py
python3 -m http.server 8765 --directory site
```

Standard-library Python; static GitHub Pages output. The existing workflow rebuilds, validates, checks generated output against the commit, and deploys `site/` on a master-branch push. The pinned research snapshot remains `f12eb47614350aca1cdf21cefc18ab58dd95e9d0`.

## Authoring map

- `index.html`: full probability sweep, outcome/report distributions, persistence, all fault types, repeat consistency, Nemotron focus, and complete selected conversations.
- `overview_data.py`: standard-library aggregation of frozen records, exact population accounting, source hash pins, and deterministic task-cluster bootstrap intervals. Writes `overview.json` and `overview.csv`; validates published rates.
- `overview_render.py`, `overview.css`, `overview.js`: accessible charts, exact cross-tabs, and a progressively enhanced probability inspector.
- `overview_verify.py`: verifies rendered chart coordinates, stack widths, numerators, denominators, and intervals against the export.
- `behavior-definitions.html`, `nemotron-brief.html`: sourced definitions, retrospective checker inspection, and model comparison.
- `comparison_catalog.py`, `comparison-catalog.json`: reproducible, hash-pinned selection of 110 anchors and all eligible exact-condition peers; 511 complete archive members across 107 groups. Full-primary matrix counts, original labels, raw source-line provenance, and excluded peer slots remain explicit. `--extract /path/to/transcripts.tar.zst` reproduces the catalogue; ordinary builds need only the committed catalogue.
- `comparison_render.py`, `comparisons.css`, `comparisons.js`: matrix library, filters, two-agent comparisons, observed fault exposure, and complete paired transcripts.
- `comparison_verify.py`: verifies all selected JSON, rendered messages, exposure tables, category links, and matched conditions.
- `comparison-notes.json`: five trace-audited featured contrasts; notes retain differences in realized faults.
- `conversations.css`, `conversations.js`: complete saved message threads and deep links, including unmatched final tool-call requests.
- `methodology.html`: research chronology, instruments, populations, secondary findings, context, and limitations.
- `build.py`: reads frozen tables, enforces report hashes, generates static pages/data/standalone diagrams.
- `redesign_charts.py`: wide/narrow conduct comparison, quiet-versus-explicit comparison, selected probe flow. Exact conduct counts cross-checked against original result/classification records; published table rates are asserted.
- `presentation.py`: escapes and renders episode extracts, exports individual JSON records, and counts presenter-script words.
- `examples.json`: seven complete selected saved conversations, original result and classification records, excerpt provenance, and one separately identified probe.
- `example-evidence.md`: curation rationale, rejected candidates, archive/member provenance, interpretation boundaries.
- `walkthrough.html`: six suggested segments for a five-minute interview route, with Nemotron in context.
- `styles.css`, `app.js`: responsive layout and progressive enhancement. Core content and native disclosures work without JS.
- `design.md`, `review-notes.md`: visual decisions and critique/verification record.

Fonts and their OFL licenses are self-hosted under `site/fonts/`. No external runtime dependencies. Wide figures have local scrolling; narrow principal figures have their own layouts. Diagram Design 2.6.110 is used at authoring time, not required at runtime or CI.

## Evidence integrity

`research-snapshot.json` pins the source reports and build fails on hash changes. Source links use the frozen commit. `site/data/findings.json` retains published chart values and intervals. `site/data/overview.json` and CSV contain new deterministic descriptive aggregates and 2,000-resample task-cluster intervals. Scores and labels are unchanged. The new views are explicitly distinguished from frozen analyses.

`validate.py` checks local links/anchors, source paths, accessible SVG labels, font signatures, frozen report hashes, chart anchors, source-line episode equality, primary example eligibility, exact final-response excerpts, original label records, the archive hash, five-model coverage, and the selected probe answer. It does not establish human label validity or creative/UI quality.

The full transcript archive is not currently downloadable from GitHub releases. Seven selected conversations were extracted from a local archive matching the frozen SHA-256 and republished as website-specific evidence. Their archive member hashes and pinned source lines are retained. The site discloses the public full-archive access gap.

## Browser and review checks

Two substantive independent critique rounds assess evidence and actual rendered UI. Browser checks cover desktop, tablet, mobile, 320px local scrolling, keyboard controls, deep links/back navigation, all seven selectors, no-JS access, reduced motion, fonts, accessibility scans, and console/network errors. Diagram Design self-checks and probe geometry checks run separately. `review-notes.md` records concrete findings, fixes, and verification limits.

## October 20 coverage update

Three independent agents reviewed evidence, measurement dimensions, and editorial structure; their implementation tasks were separated by file ownership. Raw-record reconciliation corrects a frozen prose overlap error: 91 hidden reruns overlap supplements, two overlap below-cap artifacts; the primary total remains 16,649. The website also documents a retrospective source inspection explaining all 82 checker passes at total timeout, without changing historical scores. Seven selected originals expose 128 complete saved messages and classification provenance. The cap probe remains separate.

## Matched comparison library

The primary matrix partitions checker/report outcomes into six categories: pass+S, fail+F, fail+S, no final answer (either checker result), ambiguous (either checker result), and pass+F. Counts cover all 16,649 primary episodes. Up to four diverse task/condition anchors per model/category are selected deterministically, plus the original seven. All eligible peers with exactly the same task, fault type, assigned probability, and repetition are included: 511 transcripts in 107 groups, with 24 excluded peer slots disclosed. No repetitions are substituted. Model-specific seeds and agent-specific tool choices mean realized errors are not identical.

Generated `comparisons.html` and `comparisons/*.html` are static and work without JavaScript. Progressive enhancement filters matrix cells and shows two selected agents, keeping DOM order aligned with visual order. Full per-episode JSON is under `data/comparison-episodes/`; the public catalogue index contains policy, matrix, group memberships, and episode links.
