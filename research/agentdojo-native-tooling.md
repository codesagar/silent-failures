# Research: AgentDojo — native evaluation tooling, fault-injection support, statistics, extension mechanism, and reliability-focused follow-ups

**Repo:** [ethz-spylab/agentdojo](https://github.com/ethz-spylab/agentdojo) · **Paper:** [arXiv:2406.13352](https://arxiv.org/abs/2406.13352) (NeurIPS 2024 D&B) · **Docs:** [agentdojo.spylab.ai](https://agentdojo.spylab.ai/)
**Verified against:** live clone of `main` + GitHub API, fetched 2026-02 (this run). Latest release: **v0.1.35, published 2025-10-27** (GitHub Releases API: `published_at: 2025-10-27T18:09:56Z`; `pyproject.toml` version `0.1.35`). API explicitly marked "still under development" in README.

## Summary

AgentDojo natively ships a complete **prompt-injection** evaluation stack: 4 task suites with programmatic utility/security checkers, a benchmark CLI with attacks and defenses, per-task JSON trace logging with caching, and a static HTML results table linked to Invariant Explorer. It has **no native tool-failure / fault-injection machinery** (no way to make tools deliberately return errors, time out, or fail at a configurable rate) and **no shipped statistics tooling** (no confidence intervals, repeated runs, or pass^k — aggregation is a plain mean). Both would have to be built; wrapping tool functions is compatible with, but not the documented, extension pattern (documented extensions are: new suites/tasks, new attacks, new pipeline elements).

## Findings

### 1. Native evaluation machinery (what ships)

All items below are **direct evidence** from the cloned repo (`main`, Feb 2026) and docs. **Confidence: high.**

| Component | Native? | Details |
|---|---|---|
| **Task suites** | ✅ | 4 default suites — `workspace`, `banking`, `slack`, `travel` (benchmark versions up to **v1.2.2**, the CLI default in `src/agentdojo/scripts/benchmark.py`). Suites = Pydantic environment (`environment.yaml`) + injection vectors (`injection_vectors.yaml`) + tools + registered user/injection tasks. |
| **Utility checkers** | ✅ | Per-user-task `utility()` evaluated **programmatically over environment state** (pre/post), plus optional `utility_from_traces()` for tasks that leave no environment trace ([docs](https://agentdojo.spylab.ai/concepts/task_suite_and_tasks/)). The paper stresses formal state checks instead of LLM judges. |
| **Security checkers** | ✅ | Per-injection-task `security()` method; `SuiteResults` holds `utility_results` and `security_results` keyed by (user_task, injection_task) pairs (`src/agentdojo/benchmark.py`). |
| **Benchmark CLI** | ✅ | `python -m agentdojo.scripts.benchmark` (Click): `--model`, `--attack` (registry incl. `direct`, `ignore_previous`, `important_instructions`, `tool_knowledge`, DoS variants), `--defense` (e.g. `tool_filter`, PI detector, spotlighting), `-s/-ut/-it` task selection, `--logdir`, `--force-rerun`, `-ml` module loading, multiprocessing `Pool`. Plus `agentdojo.scripts.check_suites` to validate ground truths/injectability. |
| **Trace logging** | ✅ | `TraceLogger`/`OutputLogger` (`agentdojo.logging`) write one JSON per (pipeline, suite, user_task, attack, injection_task) under `./runs/`, containing full `messages`, `injections`, `error`, `utility`, `security`, `duration`. Cached results are reloaded and skipped unless `--force-rerun` (`benchmark.py: load_task_results`). The repo itself commits run artifacts under `runs/` (e.g. `runs/Meta-SecAlign-70B/...`). |
| **Results viewer** | ⚠️ partial | A **static DataTables HTML table** in the docs ([results page](https://agentdojo.spylab.ai/results/), `docs/results.md` + `results-table.html`), with per-row "Explore →" links to the **third-party Invariant Explorer** for trajectory inspection. **No local trace-viewer app ships in the package** — inspecting your own runs means reading the JSON logs or the external explorer. |
| **Ground-truth pipeline** | ✅ | `GroundTruthPipeline` replays each task's `ground_truth()` tool calls to validate suites. |

### 2. Tool-failure / fault injection: **NOT native — must be built**

1. **Claim:** AgentDojo has no mechanism to inject tool faults (deliberate errors, timeouts, failure rates). Its only adversarial machinery is prompt-injection placeholders in environment data (`injection_vectors.yaml`) filled by `BaseAttack.attack()`. **Sources:** [attacks concept](https://agentdojo.spylab.ai/concepts/attacks/), [functions runtime docs](https://agentdojo.spylab.ai/concepts/functions_runtime/), repo source. **Support:** direct evidence (absence verified by reading docs/source + issue/PR search). **Confidence: high.**

2. **Claim:** The runtime *does* have an error pathway — `FunctionsRuntime` by default **catches exceptions raised inside tools and returns the error text to the LLM** ("This is useful to let the LLM recover from errors"; `raise_on_error` optionally re-raises) — but nothing ever *triggers* faults deliberately; errors occur only when the LLM passes bad arguments or a tool genuinely raises. **Sources:** [`docs/concepts/functions_runtime.md` § Error handling](https://agentdojo.spylab.ai/concepts/functions_runtime/). **Support:** direct evidence. **Confidence: high.** *Researcher inference:* this existing error-return path means a fault-injection wrapper that raises exceptions would surface to the agent naturally, with no runtime changes needed.

3. **Claim:** GitHub issue/PR search (`fault`, `failure injection`, `tool error`, `timeout`, `reliability` via GitHub search API, Feb 2026) finds **no fault-injection feature requests or implementations** — only infra-stability items: [PR #136 "Improve Stability"](https://github.com/ethz-spylab/agentdojo/pull/136) (fix crashes parsing local-LLM tool calls), [issue #220](https://github.com/ethz-spylab/agentdojo/issues/220) (LocalLLM turns server errors into empty answers, mis-scored), [issue #202](https://github.com/ethz-spylab/agentdojo/issues/202) (LocalLLM drops fenced tool calls), [issue #78](https://github.com/ethz-spylab/agentdojo/issues/78) (model ignoring tool responses), and `benchmark.py` catching provider API errors (`BadRequestError` context-length, Cohere `ApiError`, Google `ServerError`). All concern *accidental* failures of the harness/provider, not injected tool faults. **Support:** direct evidence. **Confidence: high.**

4. **Caveat — don't confuse with "DoS attacks":** `agentdojo.attacks.dos_attacks` (`DoSAttack`, `SwearwordsDoSAttack`, `CaptchaDoSAttack`, `OffensiveEmailDoSAttack`) are **prompt-injection payloads** that try to make the agent abort the user task (benchmark runs only one injection task for them since the target is irrelevant — `benchmark.py: attack.is_dos_attack`). They are availability *attacks via text*, not tool-level fault injection. **Support:** direct evidence (`docs/api/attacks/dos_attacks.md`, `benchmark.py`). **Confidence: high.**

### 3. Transcript-analysis / statistics tooling: **essentially none shipped**

1. **Claim:** Native aggregation is a **plain mean**: `aggregate_results()` in `benchmark.py` computes `sum(bools)/len(bools)`; the CLI prints "Average utility/security: X%". **No confidence intervals, no repeated-run support (no `--runs`/seed flag; caching actively skips already-run tasks), no pass^k / pass-hat-k.** Each (model, suite, user_task, attack, injection_task) combination is run **once**. **Sources:** `src/agentdojo/benchmark.py`, `src/agentdojo/scripts/benchmark.py`. **Support:** direct evidence. **Confidence: high.** *Researcher inference:* repeated runs require manually pointing `--logdir` at fresh directories or `--force-rerun` (which overwrites), then aggregating yourself.

2. **Claim:** A research notebook `notebooks/analysis.ipynb` exists that loads per-task JSON logs into Pandas and uses `statsmodels.stats.proportion` (i.e., proportion confidence intervals) for the paper's figures — but it is a **repo artifact, not packaged tooling**: `statsmodels`, `pandas`, `seaborn` are not dependencies in `pyproject.toml`. **Sources:** `notebooks/analysis.ipynb`, `pyproject.toml`. **Support:** direct evidence (notebook imports read live). **Confidence: high.**

3. Transcript analysis beyond this = read the JSON logs (full `ChatMessage` lists are stored) or use the external Invariant Explorer. **Must be built** for anything systematic.

### 4. Intended extension mechanism — and does tool-wrapping fit?

1. **Claim:** The documented extension points are: **(a) new task suites/tasks** — `TaskSuite(name, EnvType, [make_function(tool), ...], data_path)` + `@task_suite.register_user_task` / `@register_injection_task` + `register_suite(...)` with `-ml` module loading and `check_suites` validation; **(b) new attacks** — subclass `BaseAttack`, `register_attack`; **(c) new pipeline elements/defenses** — compose `BasePipelineElement`s into an `AgentPipeline` (docs: agent_pipeline concept). **Sources:** [task suite docs](https://agentdojo.spylab.ai/concepts/task_suite_and_tasks/), [attacks docs](https://agentdojo.spylab.ai/concepts/attacks/), `examples/counter_benchmark/`. **Support:** direct evidence. **Confidence: high.**

2. **Does wrapping tool functions match the recommended pattern?** *Researcher interpretation* (docs never discuss fault injection): tools are **plain Python functions** registered via `make_function`/`@runtime.register_function`, so building a derivative suite whose tool list wraps the original functions (e.g., a decorator that probabilistically raises or delays before delegating) is fully compatible with the architecture — the wrapped tool's exception is auto-converted into an error message to the agent (§2.2 above), and the new suite registers via the standard `register_suite` path. It is **consistent with**, though not an *explicitly documented*, extension pattern. The alternative framework-blessed interception point is a custom **pipeline element** around the tools-execution stage (this is how defenses like the PI detector transform tool outputs), which would inject faults model-agnostically without duplicating suites. Both are reasonable; neither is officially endorsed for fault injection because the use case doesn't exist upstream. **Confidence: medium** (interpretation of design intent, grounded in verified docs/source).

### 5. 2025–2026 forks / follow-ups adding reliability or failure evaluation

1. **[usnistgov/agentdojo-inspect](https://github.com/usnistgov/agentdojo-inspect)** — US AISI/NIST fork (created 2025-01-14, now **archived**). Ported AgentDojo to the Inspect framework, added new injection tasks and sandboxed (bash/terminal) tasks. Per its README update (**2025-10-23**), superseded by the **UK AISI port in [UKGovernmentBEIS/inspect_evals](https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/agentdojo)** ([eval page](https://ukgovernmentbeis.github.io/inspect_evals/evals/agentdojo/)). Focus remains **prompt-injection security + utility**, *not* tool-failure/reliability. Side benefit (*researcher inference*): Inspect provides generic `--epochs` repeated-run support and score aggregation that upstream AgentDojo lacks. **Support:** direct evidence for the fork/port facts; inference flagged. **Confidence: high / medium (inference).**
2. **[arXiv:2506.01055](https://arxiv.org/abs/2506.01055)** (Jun 2025) — extends AgentDojo with data-exfiltration attacks on a banking agent. Security-focused, not reliability. **Confidence: high** (abstract).
3. **[arXiv:2510.05244](https://arxiv.org/abs/2510.05244)** (Oct 2025) — tool-interface "firewall" defenses evaluated on AgentDojo et al.; argues for stronger benchmarks. Security-focused. **Confidence: high** (abstract).
4. **No fork or follow-up adding tool-failure / fault-injection / reliability evaluation to AgentDojo was found** in searches of GitHub issues/PRs, forks, and 2025 arXiv follow-ups. Absence-of-evidence claim: searches were targeted but not exhaustive across all 251 forks. **Confidence: medium.**

## Contradictions
None found. (Minor terminology trap: AgentDojo's "DoS attacks" and PR #136 "Improve Stability" sound reliability-related but are prompt-injection payloads and harness bugfixes respectively.)

## Missing evidence
- No exhaustive scan of all 251 forks' diffs — a private/obscure fork adding fault injection could exist (unlikely to be findable).
- Did not execute the benchmark CLI to confirm `--help` output matches source (CLI options read directly from source instead).
- Exact composition of suite task counts per version (paper says 97 user tasks / 629 security cases for v1; v1.2.2 adds tasks via PR #130) not re-verified in detail.

## Sources
- **Kept:** [ethz-spylab/agentdojo repo clone @ main](https://github.com/ethz-spylab/agentdojo) — primary source: `benchmark.py`, `scripts/benchmark.py`, docs, `pyproject.toml`, `notebooks/analysis.ipynb`, changelog.
- **Kept:** [GitHub Releases API](https://api.github.com/repos/ethz-spylab/agentdojo/releases) — v0.1.35 published 2025-10-27 (dates).
- **Kept:** [GitHub issue search API, repo-scoped](https://github.com/ethz-spylab/agentdojo/issues) — fault/failure/timeout/reliability hits (#136, #220, #202, #78, #184…), all infra not fault injection.
- **Kept:** [AgentDojo docs site](https://agentdojo.spylab.ai/) — functions runtime error handling, task-suite extension guide, attacks guide, results page.
- **Kept:** [usnistgov/agentdojo-inspect](https://github.com/usnistgov/agentdojo-inspect) + [UKGovernmentBEIS inspect_evals agentdojo](https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/agentdojo) — the main 2025 fork lineage.
- **Kept:** [arXiv:2406.13352](https://arxiv.org/abs/2406.13352), [arXiv:2506.01055](https://arxiv.org/abs/2506.01055), [arXiv:2510.05244](https://arxiv.org/abs/2510.05244) — paper + follow-ups.
- **Rejected/deprioritized:** context7.com llms.txt mirror (secondary mirror of docs); Invariant Benchmark Registry page (viewer link only, no new facts).

## Next steps
- If fault injection is needed on AgentDojo: decide between (a) wrapped-tool derivative suites vs (b) a fault-injecting pipeline element around tools execution — the latter avoids duplicating all 4 suites. Prototype against `examples/counter_benchmark` first.
- If repeated runs + CIs matter, evaluate running AgentDojo via the Inspect port (`inspect_evals/agentdojo`), which inherits Inspect's epochs/aggregation, instead of building statistics tooling on raw JSON logs.
