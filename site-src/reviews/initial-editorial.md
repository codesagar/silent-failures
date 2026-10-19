# Independent editorial/UI critique — Silent Failures

Reviewed current HEAD 1114374 (clean at inspection), site-src/index.html/styles.css/README.md, published primary tables and probe analysis. No applicable AGENTS.md found in repository or ancestor directories. Inspected actual published page in Chrome: first viewport and Findings anchor, plus full accessibility tree. Read-only review; no repository files modified.

## Recommendation

Rebuild as a compact visual argument about three different observables: **what the tool reveals, what the agent reports, and what the environment actually did**. The current design looks like a polished essay template but does not make the experiment's distinctive result visible quickly. Its eight equally weighted sections turn the presenter into a tour guide.

Lead with the high-timeout conduct contrast; make lost-response ambiguity the second message and the cap/probe correction the third. Do not lead with the baseline success-claim percentages: their changing failure populations and n=17–53 require too much qualification for a first impression. Keep that sweep as secondary context. Do not use persistence as a main finding.

### Proposed three claims (editorial drafts, final evidence critic to check)

1. **Under severe timeouts, four models usually acknowledge non-completion. Qwen ablated usually reaches the cap without an answer.**
   - Use five horizontal rows, with acknowledgment and capped-without-output shown as two aligned measures; modest third column for unsupported claims. Highlight 99.3% acknowledgment for Luna and 91.5% capped for Qwen, but show all five and task-cluster intervals.
   - Population label ABOVE the plot: failed episodes with an actual timeout injection, assigned p=75% or 100%; primary sample. n per model.
   - Qualification directly below: these are specific evaluated model/serving configurations; no matched ablation control. Cap means the observation ended, not permanent inability.
   - Supporting source: analysis/REMEDIATED_TABLES.md, first table. Three existing separate panels are defensible but too repetitive and consume height; one shared model-label column improves scanning.

2. **A missing tool response can hide an action that already happened.**
   - First explain mechanism with a two-lane diagram: explicit timeout -> tool did not execute -> error shown; lost response -> tool executes -> return value replaced with []. Put tool execution and agent-visible message in different columns. Label this a protocol schematic, not a trace.
   - Then show the p=.5 error-channel data as five compact per-model comparisons, ideally all five channels with lost response accented. Lost response has the highest point rate of unsupported claims in four models, not all five; GLM is the visible exception. Avoid an averaged universal number.
   - Put one actual lost-response trace directly beside/under this chart: request, tool return seen, answer, checker outcome. Do not hide it in details.
   - Qualification: conditional on failed, actually injected episodes; channel populations differ and point rankings are not significance tests. This supports a visibility hypothesis, not an isolated causal mechanism.

3. **An agent can fail to report at the cap and still acknowledge non-completion when asked differently.**
   - Show Qwen selection as a compact, clearly labeled flow: 819 clean main-slice capped originals -> 259 answers after nudge / 560 still tool-using -> 559 usable tools-off answers -> 531 acknowledge (95.0%, interval 92.9–96.6%). The one discarded artifact stays visible.
   - Give GLM and Kimi corresponding selected-stage-B acknowledgment fractions in small comparison rows, not the pooled 95–98% headline alone.
   - Qualification adjacent: post-hoc follow-up; stage B selected stage-A nonresponders and changed both instruction and tool availability. No inference about unlimited autonomous continuation.
   - Original behavior remains capped; follow-up does not relabel the original run.

## Concrete incumbent failures

- At a 1800×1040 browser viewport, the first screen contains a huge question, one Nemotron trace, four study counts, and the beginning of the budget note. It contains no aggregate finding. The research result starts below the fold.
- Clicking Findings lands on another large abstract heading and 91.5% callout; the five-model comparison is still partly below the fold. Chart titles/labels repeat across three panels.
- The opening trace demonstrates a rare outcome in the primary high-timeout slice, so it can accidentally frame unsupported claims as the dominant finding before the denominator is established.
- The lost-response example is hidden inside a disclosure, despite being one of the most useful explanations of the experiment.
- Elegant headings ('Failure is an outcome', 'The loudest failures get the clearest response') ask the audience to infer the conclusion. The latter also sounds causally stronger than the qualifying text.
- Repeated serif headline + introductory paragraph + large chart + two notes creates a homogeneous rhythm. The typography is stylish, but no visual distinction tells a reader which content matters most.
- Mobile styles reduce important prose to 11–13px and captions to 10px. Technical qualification becoming tiny is not meaningful prioritization.

## Visual direction and information architecture

Use a **research briefing / annotated evidence board**: warm white, near-black sans-serif conclusions, a single electric blue or deep teal for measured patterns, restrained amber for missing evidence, red only for contradiction. Keep serif only for quoted agent speech if desired. Color denotes semantics, not model branding. Fine rules and shared alignment replace nested generic cards.

Above fold: small project title and author, one 2-line result headline, a 1-line scope statement, compact conduct chart occupying most of the width, and a 3-stop navigation ('Reporting', 'Missing responses', 'After the cap'). Study scale becomes one line, not four decorative metrics. A brief frozen-study status line links to methodology.

Examples deserve their own prominent evidence bench connected from each finding. Show all five models in a compact index with behavior/condition badges; selecting one opens a readable trace with consistent columns: request -> observed tool sequence -> agent response -> outcome and published label. Default should be meaningful, not empty. Native details can hold full transcript excerpts and provenance; all core examples remain accessible without JS. Label illustrative selection, unmatched cases, omitted repetitions, and excluded historical slices.

Target main path: approximately 5–6 desktop screenfuls, not eight long sections. Methods, review chronology, baseline sweep, persistence, readback, full uncertainty tables, and literature belong on the methodology page. Preserve links and essential adjacent caveats.

## Five-minute route (proposed budget, not an executed timing claim)

- 0:00–0:30: question, scaffold, principal severe-timeout contrast visible immediately.
- 0:30–1:30: three possible reporting outcomes; one capped trace contrasted with one acknowledgment; no model-family causal claims.
- 1:30–2:40: explicit-error versus suppressed-output mechanism; actual lost-response example and channel comparison.
- 2:40–3:40: tools-off probe flow; show why the interpretation of original silence narrows.
- 3:40–4:30: quick five-model example index and one unsupported-claim subtype distinction.
- 4:30–5:00: takeaway: evaluate environment outcome and user-facing report separately; note frozen scope, judge limitations, and source trail.

## Alternatives considered

A. **Case-first forensic narrative:** open on a vivid contradictory success claim and reveal aggregate rates later. Better emotional hook, but overweights a selected rare case and delays the strongest frequency result. Choose only if the case and rates fit the same first screen.

B. **Measurement-first narrative:** show outcome × report taxonomy before any findings. Most rigorous pedagogically, but can spend the first minute on method. Use a tiny inline legend rather than a full opening section.

C. **Missing-response-first narrative:** most technically interesting setup and gives the best failure-mechanism explanation. Defensible alternative if curator finds a very clean write/readback example, but weaker as a general headline because the comparative claims have wider intervals and changing conditional populations. My choice remains conduct -> missing response -> probe.

## Bounded primary-source research and how it changes the design

- Rougier, Droettboom & Bourne (2014), *Ten Simple Rules for Better Figures*: message and medium should govern composition; a short oral presentation needs simpler figures with larger labels, while captions supply exact numerical context. Use one comparison per main figure and put key values on the marks. https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003833
- Hohman et al. (2020), *Communicating with Interactive Articles*: interaction can support guided explanation and exploration. Here, the useful interaction is selecting real trace evidence; a dashboard or decorative animation adds little to a five-minute argument. This application is my design inference. https://distill.pub/2020/communicating-with-interactive-articles/
- W3C WAI, *Page Structure Tutorial* and *Writing for Web Accessibility*: semantic regions and descriptive, logically nested headings help people navigate and prioritize. Make the headings themselves state the three conclusions; give source/details controls explicit names. https://www.w3.org/WAI/tutorials/page-structure/ and https://www.w3.org/WAI/tips/writing/
- Debenedetti et al. (2024), *AgentDojo*, NeurIPS Datasets and Benchmarks: the framework was introduced for prompt-injection robustness and already reports benign task failures. This study uses its benign task environment for synthetic tool faults; do not imply it is a prompt-injection experiment or that baseline task failure itself is novel. https://arxiv.org/abs/2406.13352 and https://proceedings.neurips.cc/paper_files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-Datasets_and_Benchmarks_Track.pdf

No NVIDIA-private priorities inferred. No external result should appear in this experiment's quantitative graphics. This review does not replace episode-level provenance checking by the example curator or evidence critic.
