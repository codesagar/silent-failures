# Silent Failures: How Tool-Using LLM Agents Behave When Their Tools Break

A pre-registered, 19,380-episode behavioral study of five LLM agents under seeded tool-failure
injection on AgentDojo — measuring not whether agents succeed, but **what they do when they
cannot**: acknowledge non-completion, keep silently retrying, or claim success the environment
contradicts. The study was then adversarially reviewed (five independent reviewers),
remediated, extended with a pre-registered post-hoc probe of all 1,300 censored episodes, and
independently re-verified (every headline number recomputed from raw data by code the authors
never touched).

**Start here: [REPORT.md](REPORT.md)** — headline findings, engineering insights, related
work, limitations. **[SCOPE_AND_VALIDITY.md](SCOPE_AND_VALIDITY.md)** states exactly what was
measured and what the design does not license.

## Headline results (details and intervals in REPORT.md / REMEDIATED_TABLES.md)

- Conduct under failure is model-specific and dissociable: on hard-failure episodes, one model
  acknowledges non-completion 99.3% of the time; a safety-ablated model acknowledges 6.6% and
  silently burns its step budget in 91.5%.
- Silence is a propensity, not a capability gap: capped models that ignore a live user nudge
  still produce an honest acknowledgment in 95–98% of cases when tools are removed and an
  answer is demanded.
- Unsupported success claims track failure *visibility*, not failure rate: 41–94% on ordinary
  uninjected failures, falling to 0% for every model under total outage.
- Single-run agent evals are noise even without injected randomness: 5–16% of
  identical-condition cells flip outcome across 4 repetitions (replicating the 2026
  agentic-randomness literature).
- Found along the way: a previously unreported silent re-run behavior in the benchmark
  substrate itself (verification/agentdojo-bug-assessment.md).

## Repository map

| Area | Files |
|---|---|
| Write-up | REPORT.md (v2, master), SCOPE_AND_VALIDITY.md, TIMELINE.md |
| Pre-registration | PREREGISTRATION.md + PREREGISTRATION-AMENDMENT-1..5.md (frozen; every mid-run decision timestamped) |
| Review trail | reviews/ (five adversarial reports, verbatim), TRANSPARENCY.md (all findings + dispositions), REVIEW_RESPONSE.md, BLIND_SPOTS.md, verification/ (independent recomputation audit + methodology review of the remediated package) |
| Primary analyses | REMEDIATED_TABLES.md, PROBE_ANALYSIS.md, REAUDIT.md, READBACK.md, PERSISTENCE.md, per_task_rates.csv, figures/ |
| v1 analyses (superseded where TRANSPARENCY says so) | CONDUCT_ANALYSIS.md, SUPPLEMENTARY_ANALYSES.md, evidence_classes.md, DETERMINISTIC_TABLES.md |
| Harness | experiment.py (injector + runner), probe.py (wrap-up probe), classifier.py + probe_classify.py (claim-label cascade), reaudit.py, analyze*.py, readback.py, persistence.py, figures_v2.py, qa_check.py |
| Data | results/ (all 19,380 episode records, JSONL), probe_results/ (1,300 probe episodes + transcripts), classify/ (every label with votes), DATA_MANIFEST.json |

## Reproducing

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp endpoints.example.json endpoints.json   # fill in your gateway / model servers / token file
# Analyses re-run from the frozen data without any model access:
.venv/bin/python analyze_remediated.py     # -> REMEDIATED_TABLES.md
.venv/bin/python probe_classify.py table   # -> PROBE_ANALYSIS.md
.venv/bin/python figures_v2.py             # -> figures/*_v2.png
# Re-running experiments/judging requires live endpoints (see REPORT.md for the model roster).
```

Episode records in `results/` are self-contained for all table-level analyses. Full
step-by-step transcripts (~300 MB) are published as a release asset
(`transcripts.tar.zst`); `TRANSCRIPTS_SHA256` in this repo pins its hash. Transcript-dependent
analyses (readback.py, persistence.py, probe replay) need them unpacked at `logs-experiment/`.

## Provenance note

This public history was exported from the private research repository with
`git filter-repo`: per-commit author dates and messages are preserved (the pre-registration
timeline in TIMELINE.md is stated against them); employer-identifying hostnames, usernames,
and two ephemeral working notes were mechanically redacted/removed across all commits, and
commit hashes therefore differ from those cited in documents frozen before export (mapping in
TIMELINE.md). No data, labels, or analysis content was altered.

## License

Apache-2.0 (see LICENSE). AgentDojo is a separate project (MIT) by the ETH Zurich SPY Lab.
