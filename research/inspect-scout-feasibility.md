# Research: Inspect Scout (AISI / Meridian Labs transcript-analysis tool)

Research date: live-verified from primary sources (docs, GitHub repo, PyPI JSON API, AISI blog) at time of writing.

## Summary

Inspect Scout is an open-source tool for in-depth, scalable analysis of AI agent transcripts, built by **Meridian Labs in close collaboration with the UK AI Security Institute (AISI)** on top of the Inspect AI framework. **Note: the repo is NOT under `github.com/UKGovernmentBEIS` — it lives at [`meridianlabs-ai/inspect_scout`](https://github.com/meridianlabs-ai/inspect_scout)** (the UKGovernmentBEIS Inspect docs integrate it as "Scanners"). It runs LLM-powered or pattern-based "scanners" over stored transcripts, fully standalone (no Inspect eval run required), and crucially has an explicit **Transcript import API** for arbitrary external sources — so ingesting ~19k AgentDojo-style JSON message lists is a **small-script, hours-not-days** job.

## Key links

| Resource | URL |
|---|---|
| Repo | https://github.com/meridianlabs-ai/inspect_scout (MIT, created 2025-09) |
| Docs | https://meridianlabs-ai.github.io/inspect_scout/ |
| Importing transcripts | https://meridianlabs-ai.github.io/inspect_scout/db_importing.html |
| Transcript API reference | https://meridianlabs-ai.github.io/inspect_scout/reference/transcript.html |
| Inspect-side integration ("Scanners") | https://inspect.aisi.org.uk/scanners.html |
| AISI blog (pipeline announcement, pipeline screenshot dated 2026-02-25) | https://www.aisi.gov.uk/blog/a-pipeline-for-transcript-analysis-using-inspect-scout |
| Paper: "Seven simple steps for log analysis in AI systems" | https://arxiv.org/html/2604.09563v2 |
| PyPI | https://pypi.org/project/inspect-scout/ |

## Findings

### 1. Purpose, architecture, release status

1. **Claim:** Scout's purpose is systematic, quantitative transcript analysis — detecting refusals, evaluation awareness, environment misconfiguration, reward hacking, command errors, etc. in agent rollouts. **Sources:** [Docs index](https://meridianlabs-ai.github.io/inspect_scout/), [AISI blog](https://www.aisi.gov.uk/blog/a-pipeline-for-transcript-analysis-using-inspect-scout). **Support:** direct evidence. **Confidence:** high.

2. **Claim (architecture):** Yes — scanners over *stored* transcripts. Core model: a **Transcript** (LLM conversation / agent rollout) is read from Inspect logs or a **transcripts database** (local dir or S3; Parquet-backed, DuckDB/PyArrow under the hood); a **Scanner** function maps each Transcript to a **Result**; results land as Parquet data frames in `./scans` (readable via `scan_results_df()`). Online scanning (attached to a live `eval()`) also exists but offline scanning over stored logs/DBs is first-class. **Sources:** [Docs index](https://meridianlabs-ai.github.io/inspect_scout/), [inspect.aisi.org.uk/scanners.html](https://inspect.aisi.org.uk/scanners.html). **Support:** direct evidence. **Confidence:** high.

3. **Claim (release status/maturity):** Pre-1.0 but actively developed and officially promoted by AISI. PyPI package `inspect-scout`: first release **0.1.0 on 2025-09-07**; latest at check time **0.6.0, uploaded 2026-10-15** (requires Python >= 3.11, depends on `inspect-ai>=0.3.281`, `inspect-swe`, duckdb, pyarrow, pandas, fastapi). Repo is MIT-licensed, ~53 stars, release-please automated releases, CHANGELOG maintained. **Sources:** [PyPI JSON](https://pypi.org/pypi/inspect-scout/json), [repo](https://github.com/meridianlabs-ai/inspect_scout). **Support:** direct evidence (version/date fields from PyPI API). **Confidence:** high. *Researcher inference:* 0.x versioning means API churn risk; pin the version.

### 2. What a scanner is; open-ended LLM queries; API

4. **Claim:** A scanner is a decorated async function `Scanner[Transcript]` (also `ChatMessage`, `Event`, or `Timeline` granularity) returning a `Result`. The high-level **`llm_scanner()`** runs an arbitrary natural-language question over each transcript with structured answers (boolean, number, string, single/multi classification, structured JSON) — i.e. **yes, open-ended LLM-powered queries over large transcript sets are the central use case**, with parallelism (`--max-transcripts`, default 25), batching, resume-on-error fault tolerance, and a validation workflow against human labels. **Sources:** [Docs index](https://meridianlabs-ai.github.io/inspect_scout/), [Scanner API ref](https://meridianlabs-ai.github.io/inspect_scout/reference/scanner.html). **Support:** direct evidence. **Confidence:** high.

   Example straight from the docs:

   ```python
   from inspect_scout import Scanner, Transcript, llm_scanner, scanner

   @scanner(messages="all")
   def ctf_environment() -> Scanner[Transcript]:
       return llm_scanner(
           question="In the transcript above do you detect "
                    "instances of environment misconfiguration "
                    "preventing the agent from completing it's task?",
           answer="boolean",
       )
   ```

   Run: `scout scan scanner.py -T ./transcripts --model openai/gpt-5`. There is also `grep_scanner()` for pure pattern matching, and fully custom scanners calling `get_model().generate(...)` directly, with `message_numbering()` for citing message references in results.

### 3. CRITICAL — transcript format / external import

5. **Claim:** Scout is **not limited to Inspect native eval logs.** The [Importing Transcripts](https://meridianlabs-ai.github.io/inspect_scout/db_importing.html) doc lists 7 ingestion paths: Inspect logs; Arize Phoenix / LangSmith / Logfire / MLFlow / W&B Weave observability sources; Claude Code sessions; Harbor ATIF trajectories; a **Transcript Python API** for anything else; direct **PyArrow `RecordBatchReader`** insertion; and reading an existing schema-conformant **Parquet data lake** directly. **Support:** direct evidence. **Confidence:** high.

6. **Claim (the dataclass):** `Transcript(TranscriptInfo)` is a Pydantic model with fields `transcript_id: str` (required), `source_type`, `source_id`, `metadata`, **`messages: list[ChatMessage]`** (the standard `inspect_ai` chat message types — system/user/assistant-with-tool_calls/tool), and optional `events` (only needed for complex multi-agent timelines). **Sources:** [Transcript reference](https://meridianlabs-ai.github.io/inspect_scout/reference/transcript.html), [db_importing](https://meridianlabs-ai.github.io/inspect_scout/db_importing.html). **Support:** direct evidence. **Confidence:** high.

7. **Claim (exact fit for AgentDojo-style JSON message lists):** The import doc shows precisely this pattern — a `json_to_transcript()` example that reads a JSON file and uses **`inspect_ai.model.messages_from_openai()`** / `model_output_from_openai()` to convert raw OpenAI-format message dicts (roles system/user/assistant+tool_calls/tool) into `ChatMessage` objects, then yields `Transcript(...)` via an async generator into `transcripts_db("./my-transcripts").insert(...)`. Insertion is **idempotent** (safe to resume interrupted imports) and auto-chunks into ~75–100 MB Parquet files. **Sources:** [db_importing — Transcript API/Streaming/Transcripts sections](https://meridianlabs-ai.github.io/inspect_scout/db_importing.html). **Support:** direct evidence (code shown in docs). **Confidence:** high. *Researcher inference:* AgentDojo transcripts are OpenAI-style message lists, so `messages_from_openai()` should map them nearly 1:1; any framework-specific quirks (e.g. nonstandard tool-call encoding) are a small adapter concern, not an architecture mismatch. Not live-verified against actual AgentDojo files.

   Minimal import sketch (adapted from docs):

   ```python
   from inspect_ai.model import messages_from_openai
   from inspect_scout import Transcript, transcripts_db

   async def read_transcripts(dir):
       for f in dir.rglob("*.json"):
           data = json.loads(f.read_text())
           yield Transcript(
               transcript_id=data["id"],
               source_type="agentdojo",
               metadata={...},
               messages=await messages_from_openai(data["messages"]),
           )

   async with transcripts_db("./transcripts") as db:
       await db.insert(read_transcripts(Path("rollouts/")))
   ```

   There is also a `scout import` CLI for the registered sources (claude_code, phoenix, langsmith, weave, atif, …); a custom JSON format goes through the Python API above (or you can register a custom source).

### 4. Install friction / standalone use

8. **Claim:** `pip install inspect-scout` (PyPI name `inspect-scout`, import name `inspect_scout`). It pulls in `inspect_ai` as a dependency but **runs fully standalone over stored logs/databases — no Inspect eval run is required** (`scout scan scanner.py -T ./logs` is explicitly "Offline Scanning"; `transcripts_from()` reads local dirs or S3). Scanning with `llm_scanner` needs a model API key in the environment (`OPENAI_API_KEY` etc. or `.env`). Optional VS Code extension and `scout view` web viewer for exploring results. **Sources:** [Docs index](https://meridianlabs-ai.github.io/inspect_scout/), [inspect.aisi.org.uk/scanners.html](https://inspect.aisi.org.uk/scanners.html), PyPI. **Support:** direct evidence. **Confidence:** high.

### 5. Feasibility verdict for ~19,000 JSON transcripts

9. **Verdict: ingestion is hours (likely well under one), not days.** *Researcher inference from direct evidence:* the docs' streaming-generator import is exactly built for this ("when importing a large number of transcripts you should always write a generator"); the docs index states Scout is designed to "scale to thousands of transcripts with parallel processing, batching, and fault tolerance." Writing the ~30-line adapter (JSON → `messages_from_openai` → `Transcript`) is the main effort — call it 1–3 hours including format quirks; the actual `db.insert()` of 19k transcripts into local Parquet is I/O-bound and should take minutes. Idempotent inserts mean a bad first pass can be rerun safely. The *scanning* cost is separate and dominated by LLM calls: 19k transcripts × 1 LLM call each at default 25-way parallelism is a many-hour/overnight job depending on transcript length and model rate limits — tunable via `--max-transcripts`/`--max-connections`, with `scout scan resume` for interruptions. **Confidence:** medium-high (no live benchmark run; based on documented design, not measured on BENCH).

## Contradictions

- **Repo location vs. task premise:** the task pointed at `github.com/UKGovernmentBEIS`; the actual repo is `meridianlabs-ai/inspect_scout`. AISI's blog confirms AISI "worked closely with Meridian Labs to build Inspect Scout"; UKGovernmentBEIS repos (inspect_ai docs, inspect_evals) reference and integrate it. No other contradictions found.

## Missing evidence

- No live-verified import of an actual AgentDojo transcript (field-mapping of its tool-call encoding to `messages_from_openai()` is inferred, not tested).
- No published ingestion benchmark numbers; the hours-not-days verdict is a design-based estimate.
- Did not verify whether `messages_from_openai` handles multi-tool-call assistant messages with every edge case AgentDojo emits.

## Sources

- Kept: Inspect Scout docs index (https://meridianlabs-ai.github.io/inspect_scout/) — authoritative overview, scanner API, scan CLI, parallelism.
- Kept: Importing Transcripts (https://meridianlabs-ai.github.io/inspect_scout/db_importing.html) — the decisive page for question 3, with the exact JSON-import code pattern.
- Kept: Transcript reference (https://meridianlabs-ai.github.io/inspect_scout/reference/transcript.html) — `Transcript`/`TranscriptInfo` Pydantic model fields.
- Kept: GitHub repo meridianlabs-ai/inspect_scout — license, structure, install, maturity signals.
- Kept: PyPI JSON API (https://pypi.org/pypi/inspect-scout/json) — exact release dates/versions (0.1.0 → 2025-09-07; 0.6.0 → 2026-10-15).
- Kept: AISI blog + arXiv 2604.09563 — provenance (AISI × Meridian Labs) and methodology paper.
- Kept: inspect.aisi.org.uk/scanners.html — official Inspect-side integration (online/offline scanning, scanner-as-scorer).
- Deprioritized: UKGovernmentBEIS/inspect_evals SKILL.md — downstream consumer, confirms real-world usage but adds no API facts.

## Next steps

- Smoke-test on BENCH: `pip install inspect-scout` in a venv, convert 5 sample AgentDojo JSON files via `messages_from_openai()`, `db.insert()`, and run one `llm_scanner` — this converts the medium-confidence feasibility inference into a verified result in <1 hour.
