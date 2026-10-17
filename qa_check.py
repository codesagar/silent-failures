"""Data-quality audit: integrity checks that could challenge analysis veracity."""
import json
from collections import Counter, defaultdict
from pathlib import Path

rows = []
for f in sorted(Path("results").glob("*.jsonl")):
    for line in f.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))

print(f"episodes recorded: {len(rows)}")
by_model = Counter(r["model"] for r in rows)
print("per model:", dict(by_model))

# 1. duplicates (shard overlap / resume race)
ids = Counter(r["run_id"] for r in rows)
dups = {k: v for k, v in ids.items() if v > 1}
print(f"\n1. duplicate run_ids: {len(dups)}", list(dups)[:3])

# 2. harness errors (endpoint failures, crashes mid-episode)
herr = [r for r in rows if r.get("harness_error")]
print(f"2. harness_error episodes: {len(herr)}")
for m, c in Counter(r["model"] for r in herr).items():
    kinds = Counter((r.get("harness_error") or "")[:60] for r in herr if r["model"] == m)
    print(f"   {m}: {c}", dict(list(kinds.items())[:3]))

# 3. missing transcript / missing behavior fields
no_tx = [r for r in rows if not r.get("harness_error") and "assistant_turns" not in r]
print(f"3. valid-but-no-transcript episodes: {len(no_tx)}", [r["run_id"] for r in no_tx[:3]])

# 4. utility=None without harness_error
un = [r for r in rows if r["utility"] is None and not r.get("harness_error")]
print(f"4. utility=None without harness_error: {len(un)}")

# 5. control-condition sanity (capability + systemic-failure detector)
print("5. control (p=0) success / silent-final rates per model:")
for m in sorted(by_model):
    ctrl = [r for r in rows if r["model"] == m and r["p"] == 0.0 and not r.get("harness_error")]
    if not ctrl:
        continue
    succ = sum(1 for r in ctrl if r["utility"])
    empty = sum(1 for r in ctrl if r.get("final_empty"))
    print(f"   {m}: success {succ}/{len(ctrl)} ({100*succ/len(ctrl):.0f}%), empty-final {empty}/{len(ctrl)}")

# 6. anomaly: empty final BELOW the loop cap (possible generation failure, not behavior)
anom = [r for r in rows if r.get("final_empty") and (r.get("assistant_turns") or 0) < 16
        and not r.get("harness_error")]
print(f"6. empty-final below loop cap (needs manual review): {len(anom)}")
for m, c in Counter(r["model"] for r in anom).items():
    print(f"   {m}: {c}")

# 7. injection accounting: p=1.0 episodes where model made calls but saw no errors (impossible)
bad_inj = [r for r in rows if r["p"] == 1.0 and (r.get("tool_calls_total") or 0) > 0
           and r.get("injected_failures") == 0]
print(f"7. p=1.0 with calls but zero injections (must be 0): {len(bad_inj)}")

# 8. p=1.0 episodes where model made NO tool calls at all (refused to engage - behavior, but flag)
no_eng = [r for r in rows if r["p"] == 1.0 and (r.get("tool_calls_total") or 0) == 0
          and not r.get("harness_error")]
print(f"8. p=1.0 zero-tool-call episodes (non-engagement, kept but sliced): {len(no_eng)}")
for m, c in Counter(r["model"] for r in no_eng).items():
    print(f"   {m}: {c}")

# 9. duration outliers (hung episodes)
longs = sorted(rows, key=lambda r: -r["secs"])[:5]
print("9. slowest episodes:", [(r["model"], r["secs"]) for r in longs])

# 10. shard-file vs matrix accounting per model (no silent worker death)
print("10. episodes per model vs expected 3876 (in progress; checked for monotone growth externally)")
