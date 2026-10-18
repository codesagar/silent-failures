# Research: Is the "AgentDojo hidden re-run" finding worth reporting upstream?

## Summary
**Verdict: (b) real but narrow — file as a low/medium-severity issue with honest scoping.** The mechanism is live-verified in both the installed v0.1.35 and current `main`: `run_task_with_pipeline` silently re-runs the whole pipeline up to 3× on `content=None` finals, without resetting the environment, and both utility and security are evaluated against the cumulative (dirty) environment — so for anyone who triggers it, the retry changes *results*, not just compute. It is undocumented, no existing issue or PR covers it, and the latest release (v0.1.35, 2025-10-27) and `main` are unchanged. It is NOT broad-impact-proven: the trigger (episode ending on a content-None assistant turn) is rare in vanilla frontier-model runs and we cannot quantify its frequency in published AgentDojo numbers from public sources. The retry itself is plausibly intentional (empty-API-response robustness); the non-reset environment and last-attempt-only transcript are plausibly oversights.

## Findings

### 1. The mechanism exists exactly as our review claims (code intent: retry likely deliberate, non-reset likely oversight)
1. **Claim:** `run_task_with_pipeline` re-runs the entire pipeline up to 3× whenever the final assistant message has `content=None`, carrying `task_environment` across attempts; `pre_environment` is copied once. **Sources:** installed source `agentdojo/task_suite/task_suite.py:374` (`pre_environment = task_environment.model_copy(deep=True)`), `:383-394`:
   ```python
   for _ in range(3):
       # Run the user task
       try:
           _, _, task_environment, messages, _ = agent_pipeline.query(prompt, runtime, task_environment)
       except AbortAgentError as e:
           task_environment = e.task_environment
           messages = e.messages
       model_output = model_output_from_messages(messages)
       if model_output is not None:
           break
   if model_output is None:
       warnings.warn(f"Model output was None for task {user_task.ID}")
   ```
   and `model_output_from_messages` (task_suite.py:70-75) returns `messages[-1]["content"]` — `None` for a pure tool-call final turn (`_assistant_message_to_content`, openai_llm.py:120-123 returns `None` when `message.content is None`). **Support:** direct evidence (live-verified code read). **Confidence:** high.

2. **Claim:** The utility checker (and the security checker) see the **dirty cumulative environment**, so for vanilla users a triggered retry changes the RESULT, not just compute. **Sources:** task_suite.py:400-406 — `self._check_task_result(user_task, model_output or [], pre_environment, task_environment, functions_stack_trace)` where `task_environment` is whatever the *last* attempt left behind, built on top of earlier attempts' side effects; same `task_environment` passed for the injection/security check (task_suite.py:412-418). **Support:** direct evidence. **Confidence:** high. **Researcher inference:** corruption is bidirectional — duplicate side effects can break strict diff-style checkers (deflating utility), and a hidden attempt-1 success whose side effects persist can satisfy a checker even though the saved transcript shows a different run (inflating utility, or counting attack success from an unsaved attempt).

3. **Claim:** The saved transcript contains only the LAST attempt; a successful single retry is completely invisible (the `warnings.warn` fires only when all 3 attempts fail). **Sources:** `agentdojo/logging.py:275-278` — `TraceLogger.log` does `self.messages = messages` (replace, not append), so when attempt 2 restarts from system+user, the saved JSON's `messages` are overwritten with the new attempt; warning gate at task_suite.py:396-397. **Support:** direct evidence. **Confidence:** high.

4. **Claim (intent):** The 3-attempt loop is plausibly a *deliberate* robustness feature for genuinely-empty model outputs (provider returns no content and no tool calls → `ToolsExecutionLoop` exits immediately → retry recovers a transient API glitch). The warning text ("Model output was None for task …") and the `model_output or []` fallback read as "this is an anomaly we paper over", not a specified protocol. The non-reset environment is plausibly an **oversight**: the authors deep-copy `pre_environment` precisely because they care about clean pre/post diffs (task_suite.py:373-374 comment: "Create a copy of the environment before running the user task to then diff if needed"), yet retries silently violate that invariant; resetting would be one line. **Support:** interpretation of code; no docstring/docs mention retries at all (the `run_task_with_pipeline` docstring, task_suite.py:355-369 and the rendered API docs at https://agentdojo.spylab.ai/api/task_suite/, describe inputs/outputs only). **Confidence:** medium (intent is inherently inferential).

5. **Claim:** The trigger also fires in vanilla use whenever an episode ends at the tool-loop cap on a tool-calls-only turn: `ToolsExecutionLoop` defaults to `max_iters=15` (tool_execution.py:131) and exits with whatever the last assistant message is; chat adapters leave `content=None` on pure tool-call turns. So "ends capped while still tool-calling" ⇒ hidden re-run, for any OpenAI-style adapter, no fault injection needed. **Support:** direct evidence (code paths), **researcher inference** on how often vanilla runs actually hit the cap (unquantified; likely rare for strong models on benign tasks, more common for weak/local models and under prompt-injection pressure). **Confidence:** high on mechanism, low on vanilla frequency.

### 2. Upstream status (web, live-verified where cited)
6. **Claim:** The behavior is undocumented. Checked: rendered API docs for `TaskSuite.run_task_with_pipeline` (https://agentdojo.spylab.ai/api/task_suite/ — docstring says nothing about retries), changelog (https://agentdojo.spylab.ai/changelog/), v0.1.35 release notes (https://github.com/ethz-spylab/agentdojo/releases/tag/v0.1.35). No mention of retry/re-run/attempts. **Support:** direct evidence (fetched pages). **Confidence:** high for the pages checked; I did not read every docs page or the paper appendix, so "undocumented anywhere" is not exhaustively proven.

7. **Claim:** No existing GitHub issue or PR covers this. GitHub issue-search API queries against `repo:ethz-spylab/agentdojo` for `retry`, `run_task_with_pipeline`, `environment reset` returned: #220 "LocalLLM turns server errors into an empty answer, which is scored as a failed attack" (+ fix PR #222 "raise LocalLLM server errors instead of returning an empty answer"), #209 (tool_filter), #135 "Poor security checks", and unrelated feature PRs. Nothing mentions the TaskSuite 3-attempt loop or non-reset environments. **Support:** direct evidence (API search results), with the caveat that GitHub code-free issue search is keyword-based; a differently-worded duplicate could exist. Notably #220/#222 are *adjacent precedent*: upstream accepted that empty-answer handling distorting scores is a valid bug class. **Confidence:** medium-high.

8. **Claim:** No newer release fixed it. v0.1.35 (2025-10-27, commit a75aba7) is the latest tag; the raw `main` branch `src/agentdojo/task_suite/task_suite.py` (fetched from raw.githubusercontent.com) still contains the identical `for _ in range(3)` loop with no env reset. Commit history for the file (16 commits, last touching it 2025-05-09 "Fix issue with Together API for llama 3") shows no retry-related change; an agentgym-era commit (44094d8, pre-rename) already contains the "Model output was None" warning, so the loop predates the public AgentDojo releases — i.e., **the paper-era benchmark numbers were produced under this protocol too**. **Support:** direct evidence (raw file fetch; commits API; commit diff snippet). **Confidence:** high.

### 3. Adversarial self-check: is OUR framing overblown?
- **Where our framing holds up:** mechanism, non-reset, last-attempt-only logging, dirty-env scoring — all byte-level verified in installed source and current main; our empirical replay-divergence probe is consistent and was independently predicted by the mechanism. The claim "nothing logs that a retry happened" is accurate for the saved JSON transcript (single-retry case); only the all-3-fail case emits a Python warning to stderr, which is not persisted in the trace.
- **Where our framing must be softened before filing:** (i) our 901/19,380 (~4.6%) hit rate is a product of *fault injection deliberately forcing loop-cap endings* — it says nothing about vanilla rates; (ii) the retry on truly-empty outputs is defensible design (and #220 shows empty finals are a real operational problem upstream wrestles with); (iii) we cannot show any published AgentDojo utility/ASR number is materially wrong — only that the protocol permits silent cross-attempt contamination when triggered. Filing this as "benchmark results are corrupted" would be overclaiming; filing it as "silent retry violates the single-episode/clean-environment invariant and is invisible in logs" is precise and defensible.
- **Why not verdict (c) (intentional, don't file):** nothing in docstrings, docs, changelog, or issues acknowledges the retry, the non-reset, or the transcript overwrite; the pre_environment deep-copy shows the authors value environment cleanliness. Even if the retry is intentional, the *combination* (no reset + no log + overwrite transcript) is worth surfacing — worst case, maintainers reply "intended, documented now", which is itself a useful outcome.
- **Why not verdict (a) (broad impact):** breadth is unproven. Trigger requires a content-None final; strong models on benign tasks usually end with text. Impact on published leaderboards is speculation.

## Contradictions
None found in sources. Internal tension worth disclosing in any report: the retry *helps* in the genuinely-empty-API-response case (its likely purpose) while *harming* in the capped-tool-call case; a fix must preserve the former.

## Missing evidence
- Frequency of content-None finals (and hence hidden re-runs) in vanilla AgentDojo security/utility runs with default pipelines — not quantifiable from public sources; would require instrumenting a run.
- Whether any published AgentDojo result actually flipped due to a hidden retry — unknown, likely unknowable without upstream rerun.
- Exhaustive doc coverage (paper appendix, all docs pages) — spot-checked only.
- GitHub issue search is keyword-based; a differently-worded duplicate can't be fully ruled out.

## Sources
- Kept: installed source `.venv/.../agentdojo/task_suite/task_suite.py` (lines 70-75, 355-418), `logging.py` (153-278), `tool_execution.py` (119-134), `llms/openai_llm.py` (120-132) — primary evidence, live-read.
- Kept: raw `main` task_suite.py (https://raw.githubusercontent.com/ethz-spylab/agentdojo/main/src/agentdojo/task_suite/task_suite.py) — proves unfixed on main.
- Kept: Releases/tags (https://github.com/ethz-spylab/agentdojo/releases, .../tags), changelog (https://agentdojo.spylab.ai/changelog/), PyPI (https://pypi.org/project/agentdojo/) — v0.1.35 is latest.
- Kept: GitHub search API results incl. issue #220 / PR #222 — no duplicate; adjacent precedent.
- Kept: API docs (https://agentdojo.spylab.ai/api/task_suite/) — retry undocumented.
- Kept: file commit history via GitHub API (16 commits; agentgym-era commit 44094d8) — loop is ancient and unchanged.
- Rejected: cephalochromoscope.net "Some Incredible Code" hits — garbled/mutated code mirrors, unreliable.
- Note: `source_check` was not used; all decision-critical claims were instead verified by direct code reads and direct fetches of upstream pages (disclosed per policy).

## Draft GitHub issue (verdict b ⇒ file; against v0.1.35, also present on `main` as of this writing)

**Title:** `run_task_with_pipeline` silently re-runs the pipeline up to 3× on `content=None` finals without resetting the environment; only the last attempt is logged

**Environment:** agentdojo v0.1.35 (also present on current `main`), Python 3.12, default pipelines with OpenAI-style tool-calling adapters.

**Observed behavior**
`TaskSuite.run_task_with_pipeline` contains (src/agentdojo/task_suite/task_suite.py, ~L383):
```python
for _ in range(3):
    try:
        _, _, task_environment, messages, _ = agent_pipeline.query(prompt, runtime, task_environment)
    except AbortAgentError as e:
        ...
    model_output = model_output_from_messages(messages)
    if model_output is not None:
        break
```
`model_output_from_messages` returns `messages[-1]["content"]`, which is `None` whenever the final assistant turn is tool-calls-only (e.g., the agent is still calling tools when `ToolsExecutionLoop` hits `max_iters`). When that happens:
1. The whole pipeline is re-run, but `task_environment` is **not reset** — attempt 2 starts in a world already mutated by attempt 1's side effects (emails sent, events created, transactions made). `pre_environment` is copied only once, so utility/security are then checked against the cumulative environment.
2. Nothing records that a retry happened: `TraceLogger.log` replaces `self.messages`, so the saved trace contains only the last attempt; the `warnings.warn` fires only if all three attempts return `None`.

**Reproduction sketch**
Run any side-effecting benign task (e.g., workspace/banking) with a chat-model pipeline and force the episode to end at the tool-loop cap while still emitting tool calls (easily induced by injecting tool failures so the agent keeps retrying tools, or by lowering `max_iters`). Observe: the pipeline runs again from the user prompt; the environment contains duplicated side effects from both attempts; the saved trace shows only the second run; utility is evaluated against the merged state.

**Expected behavior**
Either (a) each attempt starts from a fresh deep copy of the initial environment, or (b) retries are not performed for tool-call-only finals (only for truly empty responses), or at minimum (c) retries are logged in the trace so downstream analysis can detect them.

**Impact scoping (honest):** This only affects episodes whose final assistant message has `content=None` — e.g., step-capped runs, weaker/local models that spin on tool calls, or fault-injection studies. Typical frontier-model benign runs that end with a text answer are unaffected. But when triggered, it changes *results* (both utility and injection-security are checked against the dirty environment), not just compute, and it is invisible in the saved traces.

**Suggested fix (smallest):** inside the loop, re-derive `task_environment` from a deep copy of the initial environment on each retry (and/or append an `attempts` counter to the logged context). Happy to send a PR for whichever option you prefer; also fine if the retry is intentional — in that case a docs note on the 3-attempt semantics would already help.

## Next steps
- File the issue as drafted (verdict b). If maintainers respond "intentional", request a docs note and close.
- Optional strengthening before filing: run ~50 vanilla benign episodes with a weak local model and count content-None finals, to replace the "unquantified vanilla frequency" caveat with a number.
