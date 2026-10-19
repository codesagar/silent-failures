# Silent Failures: How Tool-Using LLM Agents Behave When Their Tools Break

A pre-registered, 19,380-episode behavioral study of five LLM agents under seeded tool-failure
injection on AgentDojo — measuring not whether agents succeed, but **what they do when they
cannot**: acknowledge non-completion, keep silently retrying, or claim success the environment
contradicts. The study was then adversarially reviewed (five independent reviewers),
remediated, extended with a pre-registered post-hoc probe of all 1,300 censored episodes, and
independently re-verified (every headline number recomputed from raw data by code the authors
never touched).

**Start here: [REPORT.md](REPORT.md)** — headline findings, engineering insights, related
work, limitations. **[docs/SCOPE_AND_VALIDITY.md](docs/SCOPE_AND_VALIDITY.md)** states exactly what was
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

## Repository layout

| Path | Contents |
|---|---|
| `REPORT.md` | The master write-up (start here) |
| `prereg/` | Frozen pre-registration + 5 amendments (every mid-run decision, timestamped) |
| `docs/` | Governance: TRANSPARENCY (all findings + dispositions), REVIEW_RESPONSE, SCOPE_AND_VALIDITY (what the design does/doesn't license), TIMELINE (git-verified), BLIND_SPOTS |
| `analysis/` | Current primary tables: REMEDIATED_TABLES, PROBE_ANALYSIS, REAUDIT, READBACK, PERSISTENCE, per_task_rates.csv; `analysis/v1/` holds the superseded pre-remediation analyses |
| `reviews/` | The five adversarial review reports, verbatim |
| `verification/` | Independent re-verification of the remediated package (recomputation audit + methodology review + AgentDojo bug assessment) |
| `research/` | Background research that drove design decisions (AgentDojo tooling, judge-calibration evidence) |
| `scripts/` | The harness: experiment.py (injector + runner), probe.py, classifier.py + probe_classify.py (claim-label cascade), reaudit.py, analyze_remediated.py, readback.py, persistence.py, figures_v2.py, qa_check.py; `scripts/legacy/` holds day-0 pilot/smoke and v1 analyses |
| `results/`, `probe_results/`, `classify/` | All 19,380 episode records; 1,300 probe episodes + transcripts; every label with judge votes |
| `data/` | DATA_MANIFEST.json, QA_FINAL.txt, labeling sheet, TRANSCRIPTS_SHA256 |
| `figures/`, `demos/` | v2 figures (committed generator) and four exemplar transcripts |

## Reproducing

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp endpoints.example.json endpoints.json   # fill in your gateway / model servers / token file
# Analyses re-run from the frozen data without any model access (run from repo root):
.venv/bin/python scripts/analyze_remediated.py    # -> analysis/REMEDIATED_TABLES.md
.venv/bin/python scripts/probe_classify.py table  # -> analysis/PROBE_ANALYSIS.md
.venv/bin/python scripts/figures_v2.py            # -> figures/*_v2.png
# Re-running experiments/judging requires live endpoints (see REPORT.md for the model roster).
```

Episode records in `results/` are self-contained for all table-level analyses. Full
step-by-step transcripts (~300 MB) are published as a release asset
(`transcripts.tar.zst`); `data/TRANSCRIPTS_SHA256` pins its hash. Transcript-dependent
analyses (readback.py, persistence.py, probe replay) need them unpacked at `logs-experiment/`.

## Provenance note

This public history was exported from the private research repository with
`git filter-repo`: per-commit author dates and messages are preserved (the pre-registration
timeline in TIMELINE.md is stated against them); employer-identifying hostnames, usernames,
and two ephemeral working notes were mechanically redacted/removed across all commits, and
commit hashes therefore differ from those cited in documents frozen before export (mapping in
docs/TIMELINE.md). No data, labels, or analysis content was altered.

## License

Apache-2.0 (see LICENSE). AgentDojo is a separate project (MIT) by the ETH Zurich SPY Lab.
