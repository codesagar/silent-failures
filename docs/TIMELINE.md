# Timeline reconstruction (v2 verification review, finding M7)

The v2 methodology review found the document-stated dates internally impossible
(PREREGISTRATION.md says "Committed: 2026-10-18" while episode timestamps and Amendment 3
say 2026-10-17). This note reconstructs the actual timeline from the two tamper-evident
sources — git commit timestamps (UTC) and the frozen per-episode `ts` fields — and
assesses what the pre-registration claim is actually worth. The frozen documents are NOT
edited; their header dates stand as written, with the errors documented here.

## Verified timeline (git `%ci`, episode `ts`; bench runs UTC/GMT)

| When (2026, UTC) | Event | Source |
|---|---|---|
| 10-17 03:08:39 | First full-run episode executes | episode `ts` min |
| 10-17 03:54:53 | Initial commit: harness + PREREGISTRATION.md + pilot (n=18) | git 9e253f1 |
| 10-17 04:01 / 04:04 | Amendments 1–2 committed (scope expansion; kimi parity) | git 19a19e6, dcc3006 |
| 10-17 14:49 | Amendment 3 committed (worker-death incident) | git 80f01cb |
| 10-17 19:36:50 | Last episode executes | episode `ts` max |
| 10-17 19:37:57 | Dataset freeze commit (19,380/19,380, QA clean) | git c2a1011 |
| 10-17 23:10 → 10-18 | Amendment 4, classifier, controls, analysis, report | git log |

## The two documented date errors (clerical, now disclosed)

1. **PREREGISTRATION.md header says "Committed: 2026-10-18"; git says 2026-10-17
   03:54:53 UTC.** Off by one day. Amendments 1–2 headers repeat the same wrong date
   ("2026-10-18, ~1h/~2h into the run"); their relative claims ("~1h/~2h into the run")
   are correct against git (run start 03:08, commits 04:01/04:04). Amendment 3's header
   ("2026-10-17 ~15:00") matches git (14:49).
2. **Run start precedes the pre-registration COMMIT by 46 minutes.** 1,166 of 19,380
   episodes (6.0%; glm 228, nemotron 527, qwen 201, luna 185, kimi 25) carry `ts` earlier
   than the initial commit. The pre-registration text necessarily existed when the workers
   launched (the committed harness and prereg landed in the same initial commit, and the
   design the early episodes follow is the pre-registered one), but git proof of
   precedence exists only for the 94.0% of episodes after 03:54:53.

## What may and may not be claimed

- MAY: "pre-registered, with the registration committed 46 minutes into the ~16.5-hour
  run; all hypotheses/analysis rules predate any result inspection (first analysis
  artifact: 13:11 UTC commit); 94% of episodes post-date the registration commit."
- MAY NOT: "every episode post-dates the committed registration" — unprovable for the
  first 1,166 episodes, and v2 does not claim it.
- The headline p≥0.75 cells are unaffected in interpretation (the design was fixed before
  any outcome was readable), but a hostile reader is entitled to discount the first-46-
  minute episodes' pre-registration status. Sensitivity check (live-verified): dropping
  all 1,166 pre-commit episodes from the headline p>=0.75 table shifts no rate by more
  than 0.9pp (largest: nemotron acknowledges 95.1%->94.2%, unsupported claims
  4.1%->4.9%), well inside every published interval.

## Public-export note

This public history was rewritten from the private original with `git filter-repo`
(identifying strings redacted; two ephemeral working notes removed; see README provenance
note). Author/commit DATES are preserved exactly — every timestamp above is unchanged —
but commit HASHES differ from the private originals; the hashes cited in this file are the
public ones. The private repository remains the canonical audit trail.
