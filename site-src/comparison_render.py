"""Model-by-behavior library and exact-condition conversation comparisons."""
import html
import json
import re
from urllib.parse import urlencode

from presentation import _conversation, _content

MODEL_NAMES = {
    "gpt-6-luna": "GPT-6 Luna", "glm-5.3-flash": "GLM-5.3 Flash",
    "kimi-k3": "Kimi K3", "nemotron": "Nemotron", "qwen-ablated": "Qwen ablated",
}
BEHAVIOR_NAMES = {
    "pass_success": "Pass + success claim",
    "fail_acknowledges": "Failure acknowledged",
    "fail_success": "Unsupported success claim",
    "empty": "No final answer",
    "ambiguous": "Ambiguous report",
    "pass_acknowledges": "Pass + non-completion report",
}
E = lambda value: html.escape(str(value), quote=True).replace("\n", "&#10;")


def group_key(key):
    return (key["suite"], key["task"], key["error_type"], key["p"], key["rep"])


def condition(key):
    kind = {"none": "uninjected baseline", "empty_result": "lost response"}.get(key["error_type"], key["error_type"].replace("_", " "))
    return f'{key["suite"]} · {key["task"]} · {kind} · p={round(100*key["p"])}% · repetition {key["rep"]}'


def shell(title, content, prefix="", description="Matched agent conversations and complete recorded evidence."):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{E(title)} · Silent Failures</title><meta name="description" content="{E(description)}">
    <link rel="icon" href="{prefix}favicon.svg"><link rel="stylesheet" href="{prefix}styles.css"><link rel="stylesheet" href="{prefix}overview.css"><link rel="stylesheet" href="{prefix}conversations.css"><link rel="stylesheet" href="{prefix}comparisons.css"><script src="{prefix}comparisons.js" defer></script>
    </head><body class="comparison-page"><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><a class="brand" href="{prefix}index.html"><span class="brand-mark" aria-hidden="true">sf</span>Silent Failures</a><nav aria-label="Main navigation"><a href="{prefix}index.html#findings">Overview</a><a href="{prefix}comparisons.html">Compare agents</a><a href="{prefix}index.html#nemotron-focus">Nemotron</a><a href="{prefix}methodology.html">Methods</a></nav></header>
    <main id="main" class="wrap">{content}</main><footer class="site-footer wrap"><p>Existing primary episodes. Original checker scores and report labels retained.</p><p><a href="{prefix}data/comparison-catalog.json">Catalogue and selection policy (JSON)</a> · <a href="{prefix}index.html#behavior-definitions">Behavior definitions</a></p></footer></body></html>'''


def matrix_html(catalog, landing=False):
    target = "" if landing else "comparisons.html"
    heads = "".join(f'<th scope="col">{E(label)}</th>' for label in BEHAVIOR_NAMES.values())
    rows = []
    for model, name in MODEL_NAMES.items():
        cells = []
        for behavior in BEHAVIOR_NAMES:
            cell = catalog["matrix"][model][behavior]
            n, available = cell["count"], len(cell["anchor_ids"])
            if available:
                content = f'<a href="{target}#cell-{model}-{behavior}"><strong>{n:,}</strong><span>{available} starting examples →</span></a>'
            else:
                content = f'<strong>{n:,}</strong><span>No episodes in this category</span>'
            cells.append(f'<td data-model="{model}" data-behavior="{behavior}">{content}</td>')
        rows.append(f'<tr><th scope="row">{E(name)}</th>{"".join(cells)}</tr>')
    return f'''<div class="table-scroll behavior-matrix" tabindex="0" role="region" aria-label="Model by behavior matrix; scroll horizontally to inspect six behavior categories">
    <table><caption>Episode counts across all 16,649 primary records. Click a cell to compare selected examples with their matched peers.</caption><thead><tr><th scope="col">Model</th>{heads}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>
    <p class="matrix-boundary">These six categories partition the primary corpus. Counts pool different fault conditions and are not a performance ranking. “Pass” means benchmark checker pass; “no final answer” includes both passing and failing tasks. Persistence is shown as turns and tool use within each comparison.</p>'''


def matching_note():
    return '''<aside class="matching-boundary"><strong>What is matched?</strong> The same task, fault type, assigned probability, and repetition index. What is <strong>not</strong> matched: the exact sequence of tool calls or injected faults. Seeds include the model's run ID, and agents choose different calls. Compare the recorded exposure before interpreting a behavioral difference. This is contextual evidence, not a controlled causal comparison.</aside>'''


def _sources(example):
    return ' · '.join(f'<a href="{E(s["url"])}">{E(s["label"])} ↗</a>' for s in example["sources"])


def _report(example):
    r = example["episode"]
    if r["final_empty"]:
        return "No final answer"
    return {"S": "Claims success", "F": "Acknowledges non-completion", "A": "Ambiguous"}.get(
        (example.get("published_label_record") or {}).get("label"), "Unlabeled")


def build_comparisons(root, out, catalog):
    examples = {e["id"]: e for e in catalog["examples"]}
    groups = catalog["groups"]
    by_episode = {rid: g for g in groups for rid in g["anchor_ids"]}
    notes_path = root / "site-src/comparison-notes.json"
    notes_payload = json.loads(notes_path.read_text()) if notes_path.exists() else []
    notes_list = notes_payload.get("groups", []) if isinstance(notes_payload, dict) else notes_payload
    notes = {group_key(n["key"]): n for n in notes_list}
    behaviors = {b["id"]: b for b in catalog["behaviors"]}
    (out / "comparisons").mkdir(exist_ok=True)
    (out / "data/comparison-episodes").mkdir(exist_ok=True)
    for example in examples.values():
        (out / "data/comparison-episodes" / (example["slug"] + ".json")).write_text(json.dumps(example, indent=2, ensure_ascii=False) + "\n")
    public = {k: v for k, v in catalog.items() if k != "examples"}
    public["examples"] = [{k: e[k] for k in ["id", "slug", "model", "behavior_id"]} for e in examples.values()]
    public["episode_files"] = {e["id"]: "comparison-episodes/" + e["slug"] + ".json" for e in examples.values()}
    (out / "data/comparison-catalog.json").write_text(json.dumps(public, indent=2, ensure_ascii=False) + "\n")
    featured = {}
    for g in groups:
        note = notes.get(group_key(g["key"]), {})
        peers = [examples[p["episode_id"]] for p in g["peers"] if p["status"] == "primary"]
        assert peers
        ids = {e["episode"]["model"] for e in peers}
        ordered_models = [m for m in MODEL_NAMES if m in ids]
        default_left = note.get("preferred_left")
        if default_left:
            default_left = default_left.split("__")[0]
        if default_left not in ids:
            default_left = next(e["episode"]["model"] for e in peers if e["id"] in g["anchor_ids"])
        default_right = note.get("preferred_right")
        if default_right:
            default_right = default_right.split("__")[0]
        if default_right not in ids or default_right == default_left:
            default_right = next((e["episode"]["model"] for e in peers if e["episode"]["model"] != default_left and not e["episode"]["utility"] and (e.get("published_label_record") or {}).get("label") == "F"), next((m for m in ordered_models if m != default_left), default_left))
        title = note.get("title", "Compare the same task and fault condition")
        summary = note.get("summary", "Read how each available model handled this task, then inspect its complete saved conversation and original classification.")
        if note:
            query = urlencode({"left":default_left, "right":default_right})
            featured[group_key(g["key"])] = f'<article class="comparison-feature"><p class="eyebrow">{E(condition(g["key"]))}</p><h3><a href="comparisons/{g["id"]}.html?{query}">{E(title)}</a></h3><p>{E(summary)}</p><a class="text-link" href="comparisons/{g["id"]}.html?{query}">Compare {E(MODEL_NAMES[default_left])} and {E(MODEL_NAMES[default_right])} →</a></article>'
        peer_rows, panels = [], []
        per_model = note.get("per_model", {})
        for e in peers:
            r, m = e["episode"], e["episode"]["model"]
            messages = e["trace_excerpt"]["messages"]
            calls = sum(len(x.get("tool_calls") or []) for x in messages)
            results = sum(x["role"] == "tool" for x in messages)
            fault = f'{r["injected_failures"]}/{r["tool_calls_total"]}' if r["p"] > 0 else "0 · no injection"
            peer_rows.append(f'<tr><th scope="row">{E(MODEL_NAMES[m])}</th><td>{"Pass" if r["utility"] else "Fail"}</td><td>{E(_report(e))}</td><td>{r["assistant_turns"]}</td><td>{calls} / {results}</td><td>{fault}</td><td>{r["tool_errors_seen"]}</td></tr>')
            final = next((x for x in reversed(messages) if x["role"] == "assistant" and not x.get("tool_calls") and x.get("content")), None)
            final_html = '<p class="pair-no-answer">No final answer was recorded before the cap.</p>' if r["final_empty"] else _content(final.get("content") if final else r["final_message"])
            explanation = per_model.get(m, "")
            if isinstance(explanation, dict):
                explanation = explanation.get("note", explanation.get("summary", ""))
            conversation = _conversation(e)
            conversation = conversation.replace("Follow every message and tool call", E(MODEL_NAMES[m]) + " · every message and tool call")
            conversation = conversation.replace("How this episode was classified", E(MODEL_NAMES[m]) + " · classification evidence")
            # Model panels are h2 sections; preserve a sequential heading outline.
            conversation = conversation.replace("<h4", "<h3").replace("</h4>", "</h3>")
            conversation = conversation.replace("<h5", "<h4").replace("</h5>", "</h4>")
            panels.append(f'''<article class="comparison-model" data-model="{m}" data-model-label="{E(MODEL_NAMES[m])}" id="model-{m}">
            <h2>{E(MODEL_NAMES[m])}</h2><p class="pair-behavior">{E(BEHAVIOR_NAMES[e["behavior_id"]])}</p><p>{E(explanation)}</p>
            <dl class="pair-metrics"><div><dt>Checker</dt><dd>{"Pass" if r["utility"] else "Fail"}</dd></div><div><dt>Recorded turns</dt><dd>{r["assistant_turns"]}</dd></div><div><dt>Injected / intercepted</dt><dd>{fault}</dd></div><div><dt>Requested / returned</dt><dd>{calls} / {results}</dd></div></dl>
            <details class="pair-final" open><summary>Final report · complete saved answer</summary>{final_html}</details>
            <p><a class="text-link" href="#classification-{e["slug"]}">Inspect the recorded label and judge votes ↓</a></p>
            <details class="model-conversation"><summary>Read every message, tool call, result, and classification</summary>{conversation}</details>
            <div class="pair-provenance"><p>Episode <code>{E(e["id"])}</code></p><p><a href="#paired-traces">Back to agent selection ↑</a> · <a href="../data/comparison-episodes/{e["slug"]}.json">Download this complete record</a></p><p>{_sources(e)}</p></div></article>''')
        unavailable = []
        for peer in g["peers"]:
            if peer["status"] != "primary":
                reasons = ", ".join(peer.get("exclusion_reasons", []))
                unavailable.append(f'{MODEL_NAMES[peer["model"]]}: {peer["status"]}' + (f' ({reasons})' if reasons else ''))
        options = "".join(f'<option value="{e["episode"]["model"]}">{E(MODEL_NAMES[e["episode"]["model"]])}</option>' for e in peers)
        body = f'''<div class="comparison-hero"><a class="text-link" href="../comparisons.html">← Model × behavior library</a><p class="eyebrow">MATCHED TASK / ASSIGNED CONDITION / REPETITION</p><h1>{E(title)}</h1><p class="lead">{E(summary)}</p><p>{E(condition(g["key"]))}</p><a class="button" href="#paired-traces">Jump to the paired conversations ↓</a></div>
        <div class="matched-request"><span class="eyebrow">THE SAME USER REQUEST</span><p>{E(g["request"])}</p></div>{matching_note()}
        <p class="comparison-specific-limit">{E(note.get("matching_limits", ""))}</p>
        <div class="table-scroll" tabindex="0" role="region" aria-label="Actual outcomes and fault exposure for every eligible peer"><table><caption>All available primary peers in this exact task/condition/repetition cell</caption><thead><tr><th scope="col">Model</th><th scope="col">Checker</th><th scope="col">Final report</th><th scope="col">Turns</th><th scope="col">Tool requests / results</th><th scope="col">Injected / intercepted attempts</th><th scope="col">Recorded tool errors</th></tr></thead><tbody>{"".join(peer_rows)}</tbody></table></div>
        <p class="matrix-boundary">“Intercepted” counts attempts entering the fault injector. Schema-validation errors can occur before that counter; requested calls may also have no returned result when the loop ends. At baseline the injection counter is disabled. Tool errors and injected faults are different counts.</p>
        {('<p class="unavailable-peers"><strong>Unavailable in this primary comparison:</strong> '+E("; ".join(unavailable))+'</p>') if unavailable else ''}
        <section class="paired-comparison" id="paired-traces" data-default-left="{default_left}" data-default-right="{default_right}" aria-label="Compare complete agent conversations">
        <div class="pair-controls" hidden><label for="pair-left">Left agent<select id="pair-left">{options}</select></label><label for="pair-right">Right agent<select id="pair-right">{options}</select></label><button type="button" id="pair-expand">Open both full conversations</button></div><p class="pair-status" aria-live="polite"></p>
        <p class="matrix-boundary">Read each agent in its own recorded order. Message positions across columns are not aligned events. “Acknowledges” describes this response; it is not an endorsement of a model as universally responsible.</p><div class="pair-columns">{"".join(panels)}</div></section>'''
        page = shell(title,body,"../")
        (out / "comparisons" / (g["id"] + ".html")).write_text(re.sub(r'[ \t]+\n', '\n', page))
    features = '<div class="comparison-features">' + "".join(featured[group_key(n["key"])] for n in notes_list if group_key(n["key"]) in featured) + '</div>'
    cells_html = []
    for model, name in MODEL_NAMES.items():
        for behavior, label in BEHAVIOR_NAMES.items():
            cell = catalog["matrix"][model][behavior]
            if not cell["anchor_ids"]:
                continue
            cards = []
            for rid in cell["anchor_ids"]:
                e, g = examples[rid], by_episode[rid]
                eligible = [p for p in g["peers"] if p["status"] == "primary"]
                right = next((p["model"] for p in eligible if p["model"] != model and examples[p["episode_id"]]["behavior_id"] == "fail_acknowledges"), next((p["model"] for p in eligible if p["model"] != model), model))
                query = urlencode({"left":model,"right":right})
                peer_text = " · ".join(f'{MODEL_NAMES[p["model"]]}: {BEHAVIOR_NAMES[examples[p["episode_id"]]["behavior_id"]]}' for p in eligible if p["model"] != model)
                cards.append(f'''<article class="comparison-example-card"><p class="eyebrow">{E(condition(g["key"]))}</p><h4><a href="comparisons/{g["id"]}.html?{query}">{E(e["request"])}</a></h4><p>{len(eligible)-1} eligible peer models in the same task, assigned condition, and repetition.</p><p class="comparison-peer-summary">{E(peer_text) if peer_text else "No eligible exact-match peer remains; exclusions are listed in the record."}</p><a class="text-link" href="comparisons/{g["id"]}.html?{query}">Open matched conversations →</a></article>''')
            cells_html.append(f'''<section class="comparison-cell" data-model="{model}" data-behavior="{behavior}" id="cell-{model}-{behavior}"><p class="eyebrow">{E(name)}</p><h3>{E(label)}</h3><p>{cell["count"]:,} episodes in the primary corpus · {len(cell["anchor_ids"])} selected starting examples</p><div class="comparison-card-grid">{"".join(cards)}</div></section>''')
    model_options = "".join(f'<option value="{m}">{E(n)}</option>' for m,n in MODEL_NAMES.items())
    behavior_options = "".join(f'<option value="{k}">{E(v)}</option>' for k,v in BEHAVIOR_NAMES.items())
    definitions = "".join(f'<dt>{E(label)}</dt><dd>{E(behaviors[key]["definition"])}</dd>' for key,label in BEHAVIOR_NAMES.items())
    library = f'''<div class="comparison-hero"><p class="eyebrow">BEYOND A SINGLE EXAMPLE</p><h1>Same task.<br><em>Different agents.</em></h1><p class="lead">Compare complete conversations under the same assigned fault condition. Explore {len(examples)} saved episodes in {len(groups)} matched groups, starting from a model and an observed behavior.</p></div>
    {matching_note()}<h2 class="featured-comparison-title">Start with a matched comparison.</h2>{features}<section class="comparison-browser" aria-label="Explore models and behavior"><h2>Model × behavior</h2>{matrix_html(catalog,True)}
    <details><summary>Category definitions, sample selection & limits</summary><dl class="matrix-definitions">{definitions}</dl><p>Up to four starting episodes per model/category are selected deterministically to diversify tasks and conditions, plus the original annotated examples. Every available primary peer from the exact task, fault type, probability, and repetition is included. Missing or excluded peers are disclosed; different repetitions are not substituted.</p><p>Categories and counts use the original checker outcomes and rules/LLM labels. The catalogue is an inspectable sample, not a random sample for estimating frequencies. Matrix counts come from the full primary dataset. Original scores and labels are not changed, and no new model runs were performed.</p><p><a href="data/comparison-catalog.json">Selection policy, memberships, archive hash, and source references (JSON)</a> · <a href="index.html#behavior-definitions">Checker and label limitations</a></p></details>
    <div class="comparison-filters" hidden><label for="comparison-model-filter">Model<select id="comparison-model-filter"><option value="all">All five models</option>{model_options}</select></label><label for="comparison-behavior-filter">Observed behavior<select id="comparison-behavior-filter"><option value="all">All behaviors</option>{behavior_options}</select></label></div><p class="comparison-filter-status" aria-live="polite"></p>
    {"".join(cells_html)}</section>'''
    (out / "comparisons.html").write_text(shell("Compare models and behavior",library))
    home = f'''<p class="comparison-introduction">Move from a behavior to a matched task comparison. The library contains <strong>{len(examples)} complete saved episodes in {len(groups)} groups</strong>; every eligible peer in each selected task/condition/repetition cell is available.</p>{matching_note()}{features}{matrix_html(catalog)}<p><a class="button" href="comparisons.html">Explore the full comparison library →</a></p>'''
    return {"COMPARISON_LIBRARY":home}
