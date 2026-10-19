# Silent Failures website

Presentation-only addition. Existing research reports, data, labels, scripts, and examples are treated as the final evidence package. No fresh experiments, classifications, or scientific corrections are required to build this site.

## Build and preview

```sh
python3 site-src/build.py
python3 site-src/validate.py
python3 -m http.server 8765 --directory site
```

Open http://localhost:8765. Standard-library Python only; no Node build step, backend, or model access.

`index.html` and `methodology.html` here are authoring templates. `build.py` reads the frozen published Markdown tables, produces inline SVGs and standalone infographic HTML, and writes `site/`. Website CSS and JavaScript are copied from this directory. Fonts are self-hosted under `site/fonts/`, with their OFL licenses. GitHub Pages publishes only `site/`, via `.github/workflows/pages.yml`.

`research-snapshot.json` pins the research commit and SHA-256 hashes of the source reports. The build fails if pinned evidence changes. Source links use that commit. `site/data/findings.json` contains chart values, intervals, and denominators extracted from the published tables. Website charts use the table's rounded values; they are not a fresh statistical analysis.

## Visual system and provenance

Infographics follow the Diagram Design plugin 2.6.110: restrained editorial hierarchy, accessible inline SVG, orthogonal flow connectors, sparse focal accents, common quantitative scales, local scrolling for wide diagrams, and static readable output. Custom project styling is documented in `design.md`; the installed plugin and global profiles are not modified.

Every infographic has a standalone self-contained HTML counterpart in `site/diagrams/`. Website versions inherit the locally hosted Geist and Instrument Serif fonts; standalone versions use their declared Arial/Georgia fallbacks for offline portability. The probe has a dedicated mobile composition preserving counts and selection. Charts remain readable without JavaScript; the only script enhances navigation state.

## Content contract

- Main run, corrected analysis, and post-hoc follow-up remain distinguishable.
- Original 24-hour intent is separate from actual duration.
- Model names refer to the evaluated endpoints, not general model families.
- Reported claims do not imply mental states or deceptive intent.
- Denominators and interval types accompany findings; large episode counts do not imply independent samples.
- No causal attribution to ablation, scaffold-free production guarantee, or claim of external peer review.
- Historical inconsistencies are explained with links to their existing dispositions, not silently rewritten.
- AI-assisted review, absent human calibration, registration timing, replay losses, and budget constraints remain visible.

## Checks

`validate.py` checks links, anchor IDs, frozen evidence, key chart values, font files, and accessible SVG labels. During initial implementation, all standalone diagrams also passed the plugin's `self_check.py`, and both full flowcharts passed its `verify-geometry.py`. Browser QA covers desktop/mobile layouts, local diagram scrolling, native details controls, no-JavaScript rendering, keyboard navigation, missing resources, and console errors.

The workflow rebuilds, validates, checks generated output is current, and publishes the static directory. It does not install the Diagram Design plugin or require its files at runtime.
