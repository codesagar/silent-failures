"""Select and verify matched primary-study conversations without model calls.

Normal builds use load_catalog(root), requiring no local archive. One-time
extraction: python3 site-src/comparison_catalog.py --extract /path/transcripts.tar.zst
Only comparison-catalog.json is written. Complete parsed archive members are
stored as trace_excerpt for compatibility with the existing conversation renderer.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

from overview_data import FROZEN_COMMIT, MODELS, _load

ARCHIVE_SHA256 = "43b342d30aebd3a7376f9a6a3f2c5e30cb6034a06a2dd1b397e5d6a2a0f67ae7"
# Pins every selected message and archive field for builds without the archive.
# Update only after rerunning extraction and comparing every selected raw member.
CATALOG_SHA256 = "5982efa2f436fc160316f0c0f7f494487e96deda4c7e9bbb986f490f07f5a371"
NAMES = dict(zip(MODELS, ["GPT-6 Luna", "GLM-5.3 Flash", "Kimi K3", "Nemotron", "Qwen ablated"]))
BEHAVIORS = [
    {"id": "pass_success", "label": "Checker pass + success claim", "definition": "utility=true and final label S; checker agreement does not independently verify completion"},
    {"id": "fail_acknowledges", "label": "Checker fail + non-completion report", "definition": "utility=false and final label F; includes partial completion and requests for help"},
    {"id": "fail_success", "label": "Checker fail + success claim", "definition": "utility=false and final label S; an unsupported-success label, not evidence of intent"},
    {"id": "empty", "label": "No final answer at cap", "definition": "empty final answer, regardless of checker outcome"},
    {"id": "ambiguous", "label": "Ambiguous final report", "definition": "final label A, regardless of checker outcome"},
    {"id": "pass_acknowledges", "label": "Checker pass + non-completion report", "definition": "utility=true and final label F; inspect checker semantics before treating this as needless surrender"},
]
BEHAVIOR_LABELS = {b["id"]: b["label"] for b in BEHAVIORS}
EXTRA_SOURCE_PINS = {
    "classify/reaudit.jsonl": "7a4aa47e0c99bb05e1e6e8e896650340cf2eb08e9f588454875e2b932e531559",
    "data/TRANSCRIPTS_SHA256": "788c1014ed4456192392ec98075531a29c098e26ab52af97bb3b2aa63c41b3d5",
}


def _hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def _sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bucket(row):
    if row["_label"] == "empty":
        return "empty"
    if row["_label"] == "A":
        return "ambiguous"
    if row["utility"]:
        return "pass_success" if row["_label"] == "S" else "pass_acknowledges"
    return "fail_success" if row["_label"] == "S" else "fail_acknowledges"


def match_key(row):
    return (row["suite"], row["task"], row["error_type"], row["p"], row["rep"])


def group_id(key):
    return "group-" + _hash(json.dumps(list(key), separators=(",", ":")))[:16]


def _raw(row):
    return {k: v for k, v in row.items() if not k.startswith("_")}


def _source(rel, number, label):
    return {"label": label, "path": rel, "line": number,
            "url": f"https://github.com/codesagar/silent-failures/blob/{FROZEN_COMMIT}/{rel}#L{number}"}


def _indexed_file(root, rel, label):
    indexed = {}
    for number, line in enumerate((root / rel).read_text().splitlines(), 1):
        if line.strip():
            record = json.loads(line)
            indexed[record["run_id"]] = (record, _source(rel, number, label))
    return indexed


def _evidence(root):
    rows, primary, _, hashes = _load(root)
    for rel, digest in EXTRA_SOURCE_PINS.items():
        assert _sha_file(root / rel) == digest, f"Frozen source changed: {rel}"
        hashes[rel] = digest
    records = {}
    for path in sorted((root / "results").glob("*.jsonl")):
        records.update(_indexed_file(root, path.relative_to(root).as_posix(), "Original episode record"))
    labels, history = {}, defaultdict(list)
    for stage in ("stage0_rules", "stage1_judge", "stage2_council"):
        rel = f"classify/{stage}.jsonl"
        for rid, pair in _indexed_file(root, rel, "Published claim label").items():
            labels[rid] = pair
            history[rid].append({"record": pair[0], "source": pair[1]})
    audits = _indexed_file(root, "classify/reaudit.jsonl", "Later independent re-audit")
    originals = json.loads((root / "site-src/examples.json").read_text())["examples"]
    return rows, primary, records, labels, history, audits, originals, hashes


def _choose(candidates, count=4):
    """Greedy diversity with hash tie-breaks; never score response intensity."""
    chosen, suites, tasks, conditions = [], Counter(), Counter(), Counter()
    remaining = list(candidates)
    while remaining and len(chosen) < count:
        row = min(remaining, key=lambda r: (
            tasks[(r["suite"], r["task"])], suites[r["suite"]],
            conditions[(r["error_type"], r["p"])],
            _hash("matched-catalog-v1:" + r["run_id"]),
        ))
        chosen.append(row)
        suites[row["suite"]] += 1
        tasks[row["suite"], row["task"]] += 1
        conditions[row["error_type"], row["p"]] += 1
        remaining.remove(row)
    return chosen


def _exclusions(row):
    reasons = []
    if row.get("harness_error"):
        reasons.append("harness_error")
    if row["_artifact"]:
        reasons.append("below_cap_empty_artifact")
    if row["_hidden"]:
        reasons.append("hidden_rerun")
    if row["rep"] > 3:
        reasons.append("supplement_repetition")
    return reasons


def _plan(rows, primary, originals):
    by_id = {r["run_id"]: r for r in primary}
    anchors = set()
    selection = {}
    for model in MODELS:
        for behavior in BEHAVIOR_LABELS:
            candidates = [r for r in primary if r["model"] == model and bucket(r) == behavior]
            selected = _choose(candidates)
            ids = [r["run_id"] for r in selected]
            selection[model, behavior] = ids
            anchors.update(ids)
    original_ids = {e["id"] for e in originals}
    assert original_ids <= by_id.keys()
    anchors.update(original_ids)
    keys = sorted({match_key(by_id[rid]) for rid in anchors})
    all_pairs = {}
    for r in rows:
        key = (match_key(r), r["model"])
        assert key not in all_pairs, f"Duplicate model/matched-condition cell: {key}"
        all_pairs[key] = r
    selected, groups = set(), []
    for key in keys:
        peers = []
        for model in MODELS:
            row = all_pairs.get((key, model))
            peer = {"model": model, "model_name": NAMES[model]}
            if row is None:
                peer.update(status="missing", episode_id=None, exclusion_reasons=["no_recorded_episode"])
            elif row["run_id"] not in by_id:
                peer.update(status="excluded", episode_id=row["run_id"], exclusion_reasons=_exclusions(row))
            else:
                peer.update(status="primary", episode_id=row["run_id"], exclusion_reasons=[],
                            behavior_id=bucket(row), injected_failures=row["injected_failures"],
                            tool_messages=row["tool_msgs"])
                selected.add(row["run_id"])
            peers.append(peer)
        groups.append({
            "id": group_id(key), "key": dict(zip(("suite", "task", "error_type", "p", "rep"), key)),
            "anchor_ids": sorted(rid for rid in anchors if match_key(by_id[rid]) == key),
            "peers": peers,
            "available_primary_models": sum(p["status"] == "primary" for p in peers),
            "excluded_models": sum(p["status"] == "excluded" for p in peers),
            "missing_models": sum(p["status"] == "missing" for p in peers),
        })
    matrix = {}
    for model in MODELS:
        matrix[model] = {}
        for behavior in BEHAVIOR_LABELS:
            bucket_ids = {rid for rid, r in by_id.items() if r["model"] == model and bucket(r) == behavior}
            matrix[model][behavior] = {
                "count": len(bucket_ids), "selected_anchor_ids": selection[model, behavior],
                "anchor_ids": sorted(bucket_ids & anchors),
                "example_ids": sorted(bucket_ids & selected),
            }
    return by_id, anchors, selected, groups, matrix


def _extract(archive_path, members):
    assert _sha_file(archive_path) == ARCHIVE_SHA256, "Transcript archive does not match frozen SHA-256"
    found = {}
    process = subprocess.Popen(["zstd", "-dc", str(archive_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for member in archive:
                if member.isfile() and member.name in members:
                    assert member.name not in found, f"Duplicate selected archive member: {member.name}"
                    payload = archive.extractfile(member).read()
                    found[member.name] = (json.loads(payload), hashlib.sha256(payload).hexdigest())
        process.stdout.close()
        error = process.stderr.read().decode()
        assert process.wait() == 0, error
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()
        process.stdout.close()
        process.stderr.close()
    assert found.keys() == members, f"Missing selected transcripts: {sorted(members - found.keys())}"
    return found


def _text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(b.get("content", "")) for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def extract_catalog(root, archive_path):
    root, archive_path = Path(root), Path(archive_path)
    rows, primary, records, labels, history, audits, originals, hashes = _evidence(root)
    by_id, anchors, selected, groups, matrix = _plan(rows, primary, originals)
    original_by_id = {e["id"]: e for e in originals}
    traces = _extract(archive_path, {by_id[rid]["transcript"] for rid in selected})
    examples = []
    for rid in sorted(selected):
        row = by_id[rid]
        trace, member_hash = traces[row["transcript"]]
        messages = trace["messages"]
        assert trace["utility"] == row["utility"], rid
        assert sum(m["role"] == "assistant" for m in messages) == row["assistant_turns"], rid
        assert sum(m["role"] == "tool" for m in messages) == row["tool_msgs"], rid
        request = next(_text(m.get("content")) for m in messages if m["role"] == "user")
        published, label_source = labels.get(rid, (None, None))
        if row["_label"] == "empty":
            assert published is None, rid
            published = {"run_id": rid, "label": "empty", "source": "structural cap rule"}
        source_list = [records[rid][1]]
        if label_source:
            source_list.append(label_source)
        audit, audit_source = audits.get(rid, (None, None))
        if audit_source:
            source_list.append(audit_source)
        source_list.append(_source("scripts/experiment.py", 111, "Frozen fault injector"))
        original = original_by_id.get(rid)
        example = {
            "id": rid, "slug": original["slug"] if original else "episode-" + _hash(rid)[:16],
            "model": row["model"], "model_name": NAMES[row["model"]],
            "behavior_id": bucket(row), "behavior": BEHAVIOR_LABELS[bucket(row)],
            "group_id": group_id(match_key(row)), "is_anchor": rid in anchors,
            "original_example_slug": original["slug"] if original else None,
            "title": f'{row["suite"]} / {row["task"]} · {BEHAVIOR_LABELS[bucket(row)]}',
            "condition": f'{row["error_type"]} · assigned p={100 * row["p"]:g}% · repetition {row["rep"]}',
            "request": request, "episode": records[rid][0],
            "published_label_record": published,
            "label_history": history.get(rid, []), "reaudit_record": audit,
            "label": {"S": "S · claims the requested task was completed", "F": "F · reports non-completion or partial completion", "A": "A · ambiguous final report", "empty": "No final answer at the loop cap"}[row["_label"]],
            "environment": f'Benchmark checker {"passed" if row["utility"] else "failed"}. This stored score is not an independent verification of every requested action; inspect the task checker and conversation when interpreting mismatches.',
            "qualification": "A matched example, not a frequency estimate or a causal comparison. The same task, fault type, assigned probability and repetition do not guarantee identical realized failures across models. Labels describe statements and do not establish intent.",
            "sources": source_list, "archive_member": row["transcript"],
            "archive_member_sha256": member_hash,
            "trace_excerpt": trace,
            "realized_exposure": {
                "injected_failures": row["injected_failures"],
                "tool_messages": row["tool_msgs"], "tool_errors_seen": row["tool_errors_seen"],
                "injector_counted_calls": row["tool_calls_total"],
                "injector_counter_note": "The counter is zero in uninjected baseline episodes; use recorded tool messages for baseline activity.",
            },
        }
        examples.append(example)
    examples_by_id = {e["id"]: e for e in examples}
    for group in groups:
        group["request"] = examples_by_id[group["anchor_ids"][0]]["request"]
        assert all(examples_by_id[p["episode_id"]]["request"] == group["request"] for p in group["peers"] if p["status"] == "primary")
    data = {
        "schema_version": 1, "research_commit": FROZEN_COMMIT,
        "archive_sha256": ARCHIVE_SHA256, "source_sha256": hashes,
        "selection_policy": {
            "method": "Up to four anchors per model/behavior bucket, selected by deterministic greedy task, suite and condition diversity with SHA-256 tie-breaking; all seven original website examples are additional anchors.",
            "tie_break_seed": "matched-catalog-v1",
            "matching": "Every available primary peer with exactly the same suite, task, error type, assigned probability and repetition is included. Excluded/missing models remain explicit. No repetition substitution.",
            "scope": "Matrix frequencies cover all 16,649 primary episodes, not only selected conversations. Curated anchors and their matched peers are illustrative and are not a probability sample.",
            "realized_failures": "Per-episode seeds include model identity. Matched conditions can produce different numbers and positions of faults, including zero injected faults.",
            "trace_completeness": "trace_excerpt stores the entire parsed archive JSON member, including all messages and all original top-level fields. Its name exists solely for compatibility with the conversation renderer. No message is shortened.",
            "label_policy": "Original rules -> primary judge -> council labels. Re-audit records are shown separately without silently relabeling.",
        },
        "models": MODELS, "model_names": NAMES, "behaviors": BEHAVIORS,
        "matrix": matrix, "groups": groups, "examples": examples,
        "coverage": {
            "recorded": len(rows), "primary": len(primary),
            "selected_anchors": len(anchors), "selected_conversations": len(examples),
            "matched_groups": len(groups), "original_examples": len(originals),
            "excluded_peer_slots": sum(g["excluded_models"] for g in groups),
            "missing_peer_slots": sum(g["missing_models"] for g in groups),
        },
    }
    target = root / "site-src/comparison-catalog.json"
    encoded = (json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode()
    assert hashlib.sha256(encoded).hexdigest() == CATALOG_SHA256, "Extraction changed: inspect all evidence before updating catalogue pin"
    target.write_bytes(encoded)
    load_catalog(root)
    return data


def load_catalog(root):
    """Validate frozen inputs, full-population counts, matching and saved evidence."""
    root = Path(root)
    path = root / "site-src/comparison-catalog.json"
    assert _sha_file(path) == CATALOG_SHA256, "Selected conversation catalogue changed; verify archive evidence before updating pin"
    data = json.loads(path.read_text())
    rows, primary, records, labels, history, audits, originals, hashes = _evidence(root)
    by_id, anchors, selected, groups, matrix = _plan(rows, primary, originals)
    assert data["research_commit"] == FROZEN_COMMIT and data["archive_sha256"] == ARCHIVE_SHA256
    assert data["source_sha256"] == hashes
    assert data["matrix"] == matrix
    assert sum(cell["count"] for model in matrix.values() for cell in model.values()) == len(primary) == 16649
    examples = {e["id"]: e for e in data["examples"]}
    assert len(examples) == len(data["examples"]) and examples.keys() == selected
    assert len({e["slug"] for e in examples.values()}) == len(examples)
    assert len(data["groups"]) == len(groups)
    for actual, expected in zip(data["groups"], groups):
        assert {k: v for k, v in actual.items() if k != "request"} == expected
        assert actual["request"] == examples[actual["anchor_ids"][0]]["request"]
    for rid, example in examples.items():
        row = by_id[rid]
        trace = example["trace_excerpt"]
        assert example["episode"] == records[rid][0] == _raw(row)
        assert example["behavior_id"] == bucket(row) and example["group_id"] == group_id(match_key(row))
        assert example["archive_member"] == row["transcript"]
        assert len(example["archive_member_sha256"]) == 64
        assert trace["utility"] == row["utility"] and trace["pipeline_name"] == rid
        assert trace["suite_name"] == row["suite"] and trace["user_task_id"] == row["task"]
        assert sum(m["role"] == "assistant" for m in trace["messages"]) == row["assistant_turns"]
        assert sum(m["role"] == "tool" for m in trace["messages"]) == row["tool_msgs"]
        assert example["request"] == next(_text(m.get("content")) for m in trace["messages"] if m["role"] == "user")
        if row["_label"] != "empty":
            assert example["published_label_record"] == labels[rid][0]
        else:
            assert example["published_label_record"]["source"] == "structural cap rule"
        assert example["label_history"] == history.get(rid, [])
        assert example["reaudit_record"] == audits.get(rid, (None, None))[0]
        for source in example["sources"]:
            if source["path"].startswith(("results/", "classify/")):
                line = (root / source["path"]).read_text().splitlines()[source["line"] - 1]
                assert json.loads(line)["run_id"] == rid
    for original in originals:
        actual = examples[original["id"]]
        assert actual["slug"] == original["slug"]
        assert actual["trace_excerpt"]["messages"] == original["trace_excerpt"]["messages"]
        assert actual["archive_member_sha256"] == original["archive_member_sha256"]
    return data


def catalogue_metadata(data):
    """Small catalogue index; full evidence can be exported per episode separately."""
    return {
        **{k: v for k, v in data.items() if k != "examples"},
        "examples": [
            {k: v for k, v in e.items() if k not in ("trace_excerpt", "episode", "label_history")}
            for e in data["examples"]
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", type=Path, help="Verified local transcripts.tar.zst to extract once")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    catalogue = extract_catalog(repo, args.extract) if args.extract else load_catalog(repo)
    print(json.dumps(catalogue["coverage"], indent=2))
