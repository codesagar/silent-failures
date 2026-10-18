# Evidence-class decomposition of fabrication episodes (n=864)

- Class A (contradicted, final call errored): 28 (3%) — error on screen, success claimed.
- Class C (partial-as-full): 554 (64%) — mid-episode errors seen, final call ok, whole-task success claimed. Responsible option: scoped claim (demonstrated by ~80% honest-report peers).
- Class B (unverified): 282 (33%) — zero visible errors (silent response loss). Responsible option: read-back verification; affordances exist in all four suites.

Read-back verification rates (empty_result arm, episodes with >=1 write):
glm 8% | kimi 8% | nemotron 3% | gpt-6-luna 2% | qwen-ablated 29%

Interpretive findings: honesty-of-reporting (Luna 99%) is reactive, not proactive (Luna verifies 2%);
the abliterated model verifies most (29%) while communicating worst (91% silent spin) —
persistence, verification, and honest reporting are separable traits.
Caveat: empty_result suppresses responses, not side effects; construct = claimed TASK success
contradicted by final environment state.
