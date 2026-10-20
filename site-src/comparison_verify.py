"""Verify generated matched-comparison pages against the pinned evidence catalogue.

This checks actual files and HTML-decoded message contents, not renderer output
regenerated in memory. It never invokes models or changes files.
"""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from comparison_catalog import load_catalog


class Node:
    def __init__(self, tag="", attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []

    def text(self):
        return "".join(c.text() if isinstance(c, Node) else c for c in self.children)

    def find_all(self, tag=None, css_class=None):
        result = []
        for child in self.children:
            if isinstance(child, Node):
                if (tag is None or child.tag == tag) and (
                    css_class is None or css_class in child.attrs.get("class", "").split()
                ):
                    result.append(child)
                result.extend(child.find_all(tag, css_class))
        return result


class Document(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.ids = {}
        self.feed(text)
        assert len(self.stack) == 1, f"Unclosed HTML element: {self.stack[-1].tag}"

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if "id" in node.attrs:
            assert node.attrs["id"] not in self.ids, f"Duplicate HTML ID: {node.attrs['id']}"
            self.ids[node.attrs["id"]] = node
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        assert self.stack[-1].tag == tag, f"Invalid nesting: closing {tag} inside {self.stack[-1].tag}"
        self.stack.pop()

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _one(values, context):
    assert len(values) == 1, (context, len(values))
    return values[0]


def _json_pre(value, nodes, context):
    """A structured field must survive as an equivalent displayed JSON value."""
    for node in nodes:
        try:
            parsed = json.loads(node.text())
        except json.JSONDecodeError:
            continue
        if parsed == value:
            return
    raise AssertionError(("Missing structured field", context, value))


def _value(value, pres, context):
    if isinstance(value, str):
        assert any(p.text() == value for p in pres), ("Missing/truncated verbatim text", context)
    else:
        _json_pre(value, pres, context)


def _content(content, pres, context):
    if content is None or content == [] or content == "":
        return
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text" and set(block) <= {"type", "content"}:
                if block.get("content", "") != "":
                    _value(block["content"], pres, context)
            else:
                _json_pre(block, pres, context)
    else:
        _value(content, pres, context)


def _verify_message(doc, example, index, message, calls_by_id):
    context = f'{example["id"]} message {index + 1}'
    node = doc.ids[f'message-{example["slug"]}-{index + 1}']
    assert node.tag == "li" and node.attrs["data-message-index"] == str(index), context
    assert f'role-{message["role"]}' in node.attrs["class"].split(), context
    pres = node.find_all("pre")
    _content(message.get("content"), pres, context)
    calls = node.find_all("div", "conversation-call")
    assert len(calls) == len(message.get("tool_calls") or []), context
    for call, rendered in zip(message.get("tool_calls") or [], calls):
        title = _one(rendered.find_all("h4"), context).text()
        assert title == f'Call · {call.get("function", "Unnamed tool")}', context
        assert str(call.get("id", "Not recorded")) in [c.text() for c in rendered.find_all("code")], context
        _value(call.get("args"), rendered.find_all("pre", "conversation-arguments"), context)
        for key, value in call.items():
            if key not in ("function", "id", "args") and value is not None:
                assert key in [p.text() for p in rendered.find_all("p", "conversation-field")], context
                _value(value, rendered.find_all("pre"), context)
    result_id = message.get("tool_call_id")
    if result_id:
        assert result_id in [c.text() for c in node.find_all("code")], context
        # Tool-result call metadata duplicates the matching assistant request.
        # Its full arguments are rendered on that request, verified above/below.
        assert calls_by_id[result_id] == message.get("tool_call"), context
        function = message["tool_call"]["function"]
        assert function in _one(node.find_all("div", "message-heading"), context).text(), context
    if message.get("error") is not None:
        error = _one(node.find_all("div", "conversation-error"), context)
        _value(message["error"], error.find_all("pre"), context)
    extra = {key: value for key, value in message.items() if key not in
             {"role", "content", "tool_calls", "tool_call_id", "tool_call", "error"}}
    if extra:
        _json_pre(extra, pres, context)


def _matrix(doc, catalog, landing):
    cells = [n for n in doc.root.find_all("td") if "data-model" in n.attrs and "data-behavior" in n.attrs]
    assert len(cells) == 30
    seen = set()
    for node in cells:
        model, behavior = node.attrs["data-model"], node.attrs["data-behavior"]
        assert (model, behavior) not in seen
        seen.add((model, behavior))
        cell = catalog["matrix"][model][behavior]
        assert int(_one(node.find_all("strong"), (model, behavior)).text().replace(",", "")) == cell["count"]
        anchors = node.find_all("a")
        if cell["anchor_ids"]:
            link = _one(anchors, (model, behavior))
            assert link.attrs["href"] == ("" if landing else "comparisons.html") + f"#cell-{model}-{behavior}"
            assert f'{len(cell["anchor_ids"])} starting examples' in link.text()
        else:
            assert not anchors and cell["count"] == 0
    assert sum(catalog["matrix"][m][b]["count"] for m, b in seen) == 16649


def verify_comparisons(root):
    root = Path(root)
    out = root / "site"
    catalog = load_catalog(root)
    examples = {e["id"]: e for e in catalog["examples"]}
    groups = {g["id"]: g for g in catalog["groups"]}
    assert len(examples) == 511 and len(groups) == 107
    exported = json.loads((out / "data/comparison-catalog.json").read_text())
    assert {k: v for k, v in exported.items() if k not in ("examples", "episode_files")} == {
        k: v for k, v in catalog.items() if k != "examples"
    }
    assert exported["examples"] == [
        {k: e[k] for k in ("id", "slug", "model", "behavior_id")} for e in catalog["examples"]
    ]
    assert exported["episode_files"] == {rid: f'comparison-episodes/{e["slug"]}.json' for rid, e in examples.items()}
    expected_files = {f'{e["slug"]}.json' for e in examples.values()}
    assert {p.name for p in (out / "data/comparison-episodes").glob("*.json")} == expected_files
    assert {p.stem for p in (out / "comparisons").glob("*.html")} == set(groups)
    for e in examples.values():
        actual = json.loads((out / "data/comparison-episodes" / f'{e["slug"]}.json').read_text())
        assert actual == e, f'Export differs from pinned full evidence: {e["id"]}'
    statuses, seen_episodes = Counter(), set()
    for group_id, group in groups.items():
        doc = Document((out / "comparisons" / f"{group_id}.html").read_text())
        request = _one(doc.root.find_all("div", "matched-request"), group_id)
        assert _one(request.find_all("p"), group_id).text() == group["request"]
        key = group["key"]
        hero = _one(doc.root.find_all("div", "comparison-hero"), group_id).text()
        for token in (key["suite"], key["task"], f'p={round(key["p"] * 100)}%', f'repetition {key["rep"]}'):
            assert token in hero, (group_id, "wrong displayed condition", token)
        type_name = {"none": "uninjected baseline", "empty_result": "lost response"}.get(key["error_type"], key["error_type"].replace("_", " "))
        assert type_name in hero
        table = _one(doc.root.find_all("table"), group_id)
        rows = table.find_all("tr")[1:]
        primary = [p for p in group["peers"] if p["status"] == "primary"]
        assert len(rows) == len(primary)
        for peer, rendered_row in zip(primary, rows):
            e = examples[peer["episode_id"]]
            seen_episodes.add(e["id"])
            r = e["episode"]
            assert all(r[k] == v for k, v in key.items()), (group_id, "unmatched episode", e["id"])
            assert r["model"] == peer["model"]
            calls_by_id = {c["id"]: c for m in e["trace_excerpt"]["messages"] for c in (m.get("tool_calls") or [])}
            calls = sum(len(m.get("tool_calls") or []) for m in e["trace_excerpt"]["messages"])
            results = sum(m["role"] == "tool" for m in e["trace_excerpt"]["messages"])
            fault = f'{r["injected_failures"]}/{r["tool_calls_total"]}' if r["p"] > 0 else "0 · no injection"
            report = "No final answer" if r["final_empty"] else {"S": "Claims success", "F": "Acknowledges non-completion", "A": "Ambiguous"}[e["published_label_record"]["label"]]
            expected = [e["model_name"], "Pass" if r["utility"] else "Fail", report,
                        str(r["assistant_turns"]), f"{calls} / {results}", fault, str(r["tool_errors_seen"])]
            actual = [n.text() for n in rendered_row.find_all() if n.tag in ("th", "td")]
            assert actual == expected, (e["id"], actual, expected)
            panel = doc.ids[f'model-{r["model"]}']
            assert panel.attrs["data-model"] == r["model"]
            assert e["id"] in [c.text() for c in panel.find_all("code")]
            links = {a.attrs.get("href") for a in panel.find_all("a")}
            assert all(s["url"] in links for s in e["sources"]), e["id"]
            assert f'../data/comparison-episodes/{e["slug"]}.json' in links
            assert f'classification-{e["slug"]}' in doc.ids
            classified = _one(panel.find_all("section", "classification-evidence"), e["id"])
            assert e["label"] in classified.text(), e["id"]
            assert ("Benchmark checker passed" if r["utility"] else "Benchmark checker failed") in classified.text()
            expected_votes = [
                record["votes"] for record in (e["published_label_record"], e.get("reaudit_record"))
                if record and record.get("votes")
            ]
            rendered_votes = classified.find_all("ul", "judge-votes")
            assert len(rendered_votes) == len(expected_votes), e["id"]
            for votes, vote_list in zip(expected_votes, rendered_votes):
                displayed = {}
                for li in vote_list.find_all("li"):
                    displayed[_one(li.find_all("span"), e["id"]).text()] = _one(li.find_all("strong"), e["id"]).text()
                assert displayed == votes, e["id"]
            for index, message in enumerate(e["trace_excerpt"]["messages"]):
                _verify_message(doc, e, index, message, calls_by_id)
            message_nodes = panel.find_all("li", "conversation-message")
            assert len(message_nodes) == len(e["trace_excerpt"]["messages"])
            final = _one(panel.find_all("details", "pair-final"), e["id"])
            if r["final_empty"]:
                assert "No final answer was recorded before the cap." in final.text()
                assert f'ending-{e["slug"]}' in doc.ids
            else:
                source_final = next(m for m in reversed(e["trace_excerpt"]["messages"])
                                    if m["role"] == "assistant" and not m.get("tool_calls") and m.get("content"))
                _content(source_final["content"], final.find_all("pre"), e["id"] + " complete final")
        for peer in group["peers"]:
            statuses[peer["status"]] += 1
            if peer["status"] != "primary":
                unavailable = _one(doc.root.find_all("p", "unavailable-peers"), group_id).text()
                assert peer["model_name"] in unavailable and peer["status"] in unavailable
                assert all(reason in unavailable for reason in peer["exclusion_reasons"])
                assert f'model-{peer["model"]}' not in doc.ids
        boundary = _one(doc.root.find_all("aside", "matching-boundary"), group_id).text()
        assert "Seeds include the model's run ID" in boundary and "not a controlled causal comparison" in boundary
    assert seen_episodes == examples.keys()
    assert statuses == {"primary": 511, "excluded": 24}
    library = Document((out / "comparisons.html").read_text())
    _matrix(library, catalog, True)
    _matrix(Document((out / "index.html").read_text()), catalog, False)
    by_anchor = {rid: g for g in groups.values() for rid in g["anchor_ids"]}
    for model, buckets in catalog["matrix"].items():
        for behavior, cell in buckets.items():
            section_id = f"cell-{model}-{behavior}"
            if not cell["anchor_ids"]:
                assert section_id not in library.ids
                continue
            section = library.ids[section_id]
            assert section.attrs["data-model"] == model and section.attrs["data-behavior"] == behavior
            cards = section.find_all("article", "comparison-example-card")
            assert len(cards) == len(cell["anchor_ids"])
            for rid, card in zip(cell["anchor_ids"], cards):
                g = by_anchor[rid]
                links = card.find_all("a")
                assert len(links) == 2
                eligible = {p["model"] for p in g["peers"] if p["status"] == "primary"}
                for link in links:
                    parsed = urlparse(link.attrs["href"])
                    assert parsed.path == f'comparisons/{g["id"]}.html'
                    query = parse_qs(parsed.query)
                    assert query["left"] == [model] and query["right"][0] in eligible
                assert _one(card.find_all("h4"), rid).text() == examples[rid]["request"]


if __name__ == "__main__":
    verify_comparisons(Path(__file__).resolve().parents[1])
    print("Comparison evidence verified: 107 pages, 511 exact JSON exports, every saved message/call/result/error, all matched outcome tables, source links and 30 full-population matrix cells.")
