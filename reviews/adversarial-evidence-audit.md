# Claims-vs-Evidence Audit — `silent-failures/REPORT.md`

**Method & provenance (disclosure).** This session had no shell tool. Per supervisor agreement, I authored all verification code myself; the supervisor executed my two snippets **verbatim** with `.venv/bin/python` from `/path/to/silent-failures` (read-only) and returned raw stdout. Everything labeled "recomputed" below comes from that stdout; everything labeled "read" I inspected directly with the Read tool (including `.git/logs/HEAD`, so git timestamps are live-verified without running git). I recomputed **12+ load-bearing numbers** from the raw jsonl (exceeds the ≥5 requirement). Residual chain-of-custody caveat: I could not observe execution myself.

## Claim-by-claim table

| # | Claim (REPORT.md) | Status | Evidence | Notes |
|---|---|---|---|---|
| 1 | 19,380 episodes; 3,876/model; 0 duplicate run_ids | **VERIFIED** | recomputed from `results/*.jsonl`; `QA_FINAL.txt`; `DATA_MANIFEST.json` | exact match |
| 2 | 97 tasks, 4 domains, 6 failure rates, 5 failure types, 4–8 reps | **VERIFIED** | recomputed: tasks=97, suites=4, p∈{0,.1,.25,.5,.75,1.0}, err types = 5 + `none` control | |
| 3 | "zero harness errors" / "0 harness errors" | **VERIFIED** | recomputed: 0 records with `harness_error`; matches `QA_FINAL.txt` item 2 | |
| 4 | "2026-10-17/18, built on bench" | **VERIFIED** | `.git/logs/HEAD`: first commit 1792209293 (2026-10-17 03:54 UTC), last 1792328689 (2026-10-18 13:05 UTC); committer host buildhost | |
| 5 | "built … in **~24 hours**" | **DISCREPANT** | `.git/logs/HEAD` | First→last commit span = **33.2 h**; first commit→dataset-freeze commit = **15.7 h**. "~24 h" matches neither. Suggested wording: "~16 h to dataset freeze; ~33 h to complete evidence package." |
| 6 | "**seed-reproducible**" (headline) | **DISCREPANT (overstated)** | `experiment.py` (`random.Random(seed)`, sha256-of-run_id per PREREGISTRATION), `SUPPLEMENTARY_ANALYSES.md` | Only the **failure-injection schedule** is seeded. Model sampling runs at temperature 0.7 via APIs and is not reproducible — the report's own finding #4 (22–43% flaky identical-condition cells) demonstrates episodes do **not** replay. **No replay is demonstrated anywhere in the repo** (no replay script, no replay artifact). Accurate claim would be "seeded injection schedule," not "seed-reproducible" study. |
| 7 | "repo-pinned" | **UNCLEAR (partial)** | `experiment.py`/`PREREGISTRATION.md` pin AgentDojo suite version "v1.2.1" | Version string only; no lockfile/commit pin found in file listing. Interpretation, not contradiction. |
| 8 | Instrument audit "99.4% [98.6,100.0]" agreement, n=500 | **VERIFIED** (with caveats, see concerns) | recomputed from `classify/stage0_rules.jsonl` + `stage1_judge.jsonl` vs `stage2_council.jsonl` (is_audit=500): **497/500 = 99.40%**, CI (98.6,100) reproduced | All 3 disagreements are pipeline=S → council=F (pipeline over-calls S) |
| 9 | Council unanimity 98.4% on audit | **VERIFIED** | recomputed: 492/500 | |
| 10 | "zero S-direction errors for rules" (positive controls) | **VERIFIED** | recounted all 30 records in `classify/positive_controls.json`: rules fired 13×, every S-fire on a true-S item | |
| 11 | "0/30 unanimous-S errors" | **VERIFIED** | same file: the single S-direction miss (i=27, truth A, majority S) was a split vote (F,S,S), not unanimous | Majority-S error 1/30 is disclosed in AMENDMENT-4 |
| 12 | Battery composition "10 S / 10 F / 10 hedged" (AMENDMENT-4, feeding REPORT's "0/30") | **DISCREPANT** | `classifier.py` SYNTHETIC + `positive_controls.json`: actual composition **10 S / 13 F / 7 A** | Does not change #10/#11 verdicts, but the documented battery design ≠ shipped battery |
| 13 | gpt-6-luna honest 99.0% [98.2,99.6], spin 0.4% | **VERIFIED** | recomputed: 796/804 honest, 3/804 spin, CIs match | |
| 14 | glm/kimi/nemotron "near 80% honest / ~15% spin" | **VERIFIED** | recomputed: 82.9/82.0/79.8% honest; 15.2/14.8/16.0% spin | |
| 15 | qwen-ablated spin 90.9% [88.7,93.0], honest 7.4%; "silently burns budget in 91%" | **VERIFIED** | recomputed: 611/672 spin, 50/672 honest | |
| 16 | Success-claims "35–93% at p=0.1, ~0% at p=1.0 for every model" | **VERIFIED** | recomputed: p=0.1 range 34.6%–92.9%; p=1.0 = 0/433..436 for all five | |
| 17 | Silently-lost responses "up to 61%" | **VERIFIED** | recomputed: qwen empty_result p=0.5 failed: 44/72 = 61.1% | |
| 18 | Decomposition of 864 fabrications: 3% / 64% / 33% | **PARTIALLY VERIFIED** | recomputed: total fab = **864** exact; Class B = **282** exact (fab with `tool_errors_seen==0`); Class A=28 / C=554 from `evidence_classes.md` only | A/C split needs transcript-level final-call parsing I did not perform; A+C = 582 = 864−282 is internally consistent |
| 19 | Read-back verification rates 2–29%; ablated model most-verifying (29%) | **UNSUPPORTED by recomputation (artifact-only)** | `evidence_classes.md` | Requires transcript parsing; no independent check performed. Not contradicted. |
| 20 | Retries 12.9× vs 1.8×, streaks to 25 | **UNSUPPORTED by recomputation (artifact-only)** | `SUPPLEMENTARY_ANALYSES.md` | Transcript-level metric; left unverified (bounded audit) |
| 21 | "3/5 models peak persistence at p=0.75" | **VERIFIED (artifact-consistent)** | CONDUCT H4 + DETERMINISTIC_TABLES agree (two scripts, same raw); not raw-recomputed by me | |
| 22 | "22–43% of 8-rep cells produced both success AND failure"; 480 cells | **VERIFIED** | recomputed: 480 cells; flaky 21/96 (22%), 25/96 (26%), 32/96 (33%), 39/96 (41%), 41/96 (43%) | |
| 23 | Nemotron 4.3% [2.8,5.8]; 3.8% capability-conditioned | **VERIFIED / artifact-only** | 4.3% recomputed (29/682, CI matches); 3.8% from SUPPLEMENTARY only | |
| 24 | Nemotron "high across error types" | **DISCREPANT (overstated)** | CONDUCT error-type table (the only such table, at p=0.5): nemotron permission arm = **8.5%**, below glm (11.7), kimi (11.9), qwen (29.5) | No error-type-at-p≥0.75 table exists to support the sentence's scope |
| 25 | "consistent with 2026 randomness literature" | **UNSUPPORTED (in-repo)** | no citation or research note shipped in the repo | External claim with no evidence trail |
| 26 | "Any agent benchmark without repetitions and intervals is reporting noise" | **INFERENCE (overgeneralized)** | own data: one scaffold, one benchmark family — a limit the report itself states | Flag as editorializing beyond evidence |
| 27 | Artifact map (figures/fig1–3, demos/demo1–4, all listed files) | **VERIFIED (existence)** | directory listing: all present | Contents of figures/demos not audited |
| 28 | "first/novel" phrasing | **N/A — none found** | full read of REPORT.md | No novelty claims needing as-of-date hedging. The hedging burden instead falls on the headline adjectives "seed-reproducible" (#6) and "repo-pinned" (#7) |
| 29 | QA item: p=1.0 episodes with calls but zero injections must be 0 | **VERIFIED** | recomputed: 0 | |
| 30 | "sensitivity bounds (unanimous vs majority) **wherever claims are counted**" | **DISCREPANT (minor)** | CONDUCT_ANALYSIS.md | Both bounds appear only in the H2 table; dose-response, error-type, and domain fabrication tables report majority only |

## 1. Verified claims
Rows 1–4, 8–11, 13–17, 22, 27, 29 above — every recomputed number matched the artifacts **exactly** (497/500, 864, 282, 61.1%, all H2 cells, flaky-cell counts, CIs via the repo's Jeffreys formula).

## 2. Contradicted claims
- **"built in ~24 hours"** (row 5): git evidence says 33.2 h end-to-end / 15.7 h to data freeze. Supervisor confirms intent was "to dataset freeze"; even so, 15.7 h ≠ 24 h and the report lacks the qualifier.
- **Battery composition** (row 12): 10/13/7, not 10/10/10.
- **"high across error types"** (row 24).
- **PREREGISTRATION self-dating** (see §6).

## 3. Weak / unclear / unsupported claims
- **"seed-reproducible"** (row 6): injection seeding is real and live-verified in code; whole-episode reproducibility is false by the study's own finding #4, and **no replay demonstration exists**. This is the report's largest wording/evidence gap.
- Rows 7, 19, 20, 23 (3.8%), 25, 26: artifact-only or in-repo-unsupported, as tabled.

## 4. Material source-quality concerns
- **Judge circularity in the 99.4% audit**: gemini-3.6-flash is both the stage-1 pipeline judge and a council voter (`classifier.py` PRIMARY ∈ JUDGES), so pipeline-vs-council agreement is partly self-agreement; it inflates the 99.4%.
- **Audit population excludes the hard cases**: `council_targets()` removes candidate fabrications and parse failures before sampling the 500 audit episodes (seeded, `random.Random(7)` — "random audit" is itself verified). The 99.4% therefore measures agreement on *non-candidate* episodes only; mitigated because all fabrication candidates were council-adjudicated directly, but REPORT does not say this.
- **Directionality**: all 3 audit disagreements were pipeline=S → council=F; non-candidate S labels elsewhere inherit a slight S-over-call.
- ~1,303 episodes (6.7%) carry no claim label (empty finals; label sources sum to 18,077 of 19,380) — handled coherently as spin/artifact, but only implicitly disclosed.

## 5. Missing evidence
- No replay/reproduction artifact (row 6). No in-repo citation for the "2026 randomness literature" (row 25). Evidence-class A/C split and read-back rates have no judge-free intermediate file to check (rows 18–19). DATA_MANIFEST sha256 hashes exist but were not re-verified against file bytes (bounded audit; low risk given exact episode-count matches).

## 6. Material contradictions
- **PREREGISTRATION.md header "Committed: 2026-10-18, before the full experimental run"** contradicts git: the "pre-registered experiment harness" initial commit is 2026-10-17 03:54 UTC and the dataset-freeze commit is 2026-10-17 19:37 UTC — a prereg dated 10-18 cannot precede a run frozen 10-17. Most likely a header typo or later edit (AMENDMENT-4's 10-18 date *is* commit-consistent); resolving requires `git log -p PREREGISTRATION.md`. Also, the first episode timestamp (2026-10-17T03:08:47, tz-unlabeled) precedes the initial commit by ~46 min. Neither invalidates results; both weaken the "pre-registered" paper trail as literally worded.
- Report finding #4 (nondeterminism) vs headline "seed-reproducible" — internal tension, as above.

## 7. Implications for the original conclusion
The quantitative core is **solid**: every one of the 12+ load-bearing numbers I recomputed from raw jsonl matched exactly, and the QA claims (0 duplicates, 0 harness errors) reproduce. The scientific findings (conduct dissociability, visibility inversion, ablation→spin-not-lying, run-to-run noise) stand on the recomputed evidence. What needs correction before external use: (a) reword "seed-reproducible" → "seeded failure injection; episodes are stochastic (see finding 4)"; (b) fix "~24 hours" → "~16 h to dataset freeze, ~33 h total" ; (c) soften nemotron "high across error types"; (d) disclose the gemini judge/council overlap and audit-population exclusion next to the 99.4% figure; (e) fix the prereg header date and the 10/10/10 battery description; (f) cite or cut the "2026 randomness literature" sentence and hedge the "any agent benchmark is reporting noise" generalization.