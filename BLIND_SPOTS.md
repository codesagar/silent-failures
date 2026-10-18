# Known blind spots — self-audit register (input for adversarial review)

Design-level:
1. One scaffold: single system prompt, single loop cap (15), AgentDojo pipeline only.
   Conduct rates are conditional on this scaffold; cap = censoring (reported, not varied).
2. Sampling heterogeneity: four models at temperature 0.7; gpt-6-luna via Responses API at
   provider-default sampling with reasoning effort "low" — its comparisons carry that asterisk.
3. Failure injection is uniform-random over ALL tools; real outages cluster by service.
   No adversarially-targeted or correlated failure patterns.
4. empty_result suppresses responses but executes side effects; per-call suppression identity
   is reconstructible by seed replay (demonstrated), full replay not run corpus-wide.
5. English-only; one benchmark family (AgentDojo); short-horizon episodes (<=15 tool steps).
6. "Fabrication" construct: claims contradicted by final env state; intent is not claimed.
   Class B (33%) is unverified-not-contradicted; renamed accordingly after internal challenge.

Instrument-level:
7. Rule labels (6,955 episodes) audited only via the 500-episode random council audit (99.4%
   agreement) and 13 synthetic positive controls; no full human calibration (Amendment 4).
8. Judge council shares a vendor family with one evaluated model (gpt-6.1-sol / gpt-6-luna).
9. A/F boundary soft (hedged messages); S-vs-not-S is the hard, validated axis.
10. Finish reasons not captured; empty-generation artifacts identified behaviorally (3 cases).
13. Audit-design caveats found by the adversarial swarm (Finding 3), remediated in REAUDIT.md:
    the original 500-ep audit sampled only non-candidates (candidate fabrications were never
    independently audited until the re-audit); gemini sat on the council validating its own
    stage-1 labels; S-labels got one-directional re-scrutiny. The strengthened re-audit
    (grok+gpt-6.1-sol, full text, reworded prompt) confirmed 809/864 candidates and 197/200
    reverse-audit F-labels; council agreement still bounds instrument variance, not shared
    bias — no human calibration exists (ruled out by the owner for time, disclosed).

Operational history (all documented in amendments):
11. Worker-death incident (undetermined cause); TLS sentinel-label incident; gemini quota
    incident — each produced a control that now exists, but each also consumed re-run budget.
12. kimi tool-call latency differed by 20x from peers; time-on-task is confounded with vendor
    infrastructure for cross-model latency comparisons (we make none).
