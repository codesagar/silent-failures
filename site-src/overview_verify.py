"""Check rendered overview chart geometry and table populations against exports.

Run after build.py. This checks the data-to-presentation boundary; independent
raw-record verification remains a separate check.
"""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

SVG = "{http://www.w3.org/2000/svg}"


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.current = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.current = []
        elif tag == "tr":
            self.row = []
        elif tag in ("th", "td"):
            self.cell = ""

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.current.append(self.row)
            self.row = None
        elif tag == "table":
            self.tables.append(self.current)
            self.current = None


def _svgs(markup):
    return [ET.fromstring(svg) for svg in re.findall(r"<svg\b.*?</svg>", markup, re.S)]


def _tables(markup):
    parser = Tables()
    parser.feed(markup)
    return parser.tables


def verify_overview_render(data, blocks, page=None):
    """Fail on missing conditions, wrong numerators, wrong scales or wrong CIs."""
    if page is not None:
        for name in ("SUCCESS_SWEEP", "OUTCOME_SWEEP", "EFFORT_SWEEP", "FAULT_SUCCESS", "DOSE_COMPARISON"):
            assert blocks[name] in page, f"Built homepage has a missing or stale overview block: {name}"
    models, ps = data["models"], data["probabilities"]
    cells = {(c["model"], c["p"]): c for c in data["rate_sweep"]}
    assert len(cells) == len(models) * len(ps) == 30
    for block, metric, maximum in [("SUCCESS_SWEEP", "success", 100), ("EFFORT_SWEEP", "mean_turns", 16)]:
        svg, = _svgs(blocks[block])
        series = svg.findall(f"{SVG}polyline")
        assert len(series) == len(models)
        for model, line in zip(models, series):
            points = [tuple(map(float, pair.split(","))) for pair in line.attrib["points"].split()]
            assert len(points) == len(ps)
            for p, (x, y) in zip(ps, points):
                cell = cells[model, p]
                value = cell[metric] if metric == "mean_turns" else cell["rates"][metric]["value"]
                assert abs((x - 60) / 800 - p) < .0001, (block, model, p, "wrong x")
                assert abs((1 - (y - 44) / 248) * maximum - value) < .003, (block, model, p, "wrong y")
        assert len(svg.findall(f"{SVG}circle")) == 30
    panels = _svgs(blocks["OUTCOME_SWEEP"])
    assert len(panels) == len(models)
    for model, panel in zip(models, panels):
        bars = panel.findall(f"{SVG}rect")
        assert len(bars) == len(ps) * 5
        for j, p in enumerate(ps):
            c = cells[model, p]
            expected = [c["success"]] + [c["cross_tab"]["fail"][label] for label in ("F", "S", "empty", "A")]
            segments = bars[j * 5:(j + 1) * 5]
            assert abs(sum(float(s.attrib["width"]) for s in segments) - 260) < .003
            cursor = 60
            for count, segment in zip(expected, segments):
                width = float(segment.attrib["width"])
                assert abs(width / 260 - count / c["n"]) < .00001
                assert abs(float(segment.attrib["x"]) - cursor) < .003
                cursor += width
                title = segment.find(f"{SVG}title").text
                assert f'{count}/{c["n"]} ' in title, (model, p, title)
    success_table, = _tables(blocks["SUCCESS_SWEEP"])
    assert len(success_table) == 6 and len(success_table[0]) == 7
    for model, row in zip(models, success_table[1:]):
        for p, rendered in zip(ps, row[1:]):
            rate = cells[model, p]["rates"]["success"]
            match = re.search(r"([\d.]+)% · (\d+)/(\d+) · CI ([\d.]+)–([\d.]+)", rendered)
            assert match, rendered
            assert (int(match[2]), int(match[3])) == (rate["k"], rate["n"])
            for value, key in [(match[1], "value"), (match[4], "lo"), (match[5], "hi")]:
                assert abs(float(value) - rate[key]) <= .051
    joint, conditional = _tables(blocks["OUTCOME_SWEEP"])
    assert len(joint) == len(conditional) == 31
    for index, (model, p) in enumerate((m, p) for m in models for p in ps):
        c = cells[model, p]
        row = joint[index + 1]
        assert row[1] == f"{round(100 * p)}%"
        counts = list(map(int, row[2:]))
        assert counts == [c["cross_tab"][outcome][label] for outcome in ("pass", "fail") for label in ("S", "F", "A", "empty")]
        assert sum(counts) == c["n"]
        row = conditional[index + 1]
        q = c["conditional"]
        assert int(row[2]) == q["n"]
        for value, key in zip(row[3:], ("acknowledges", "unsupported", "cap", "ambiguous")):
            assert abs(float(value.rstrip("%")) - q["rates"][key]["value"]) < .051
    fault_table, = _tables(blocks["FAULT_SUCCESS"])
    lookup = {(c["model"], c["error_type"]): c for c in data["fault_types"]}
    for model, row in zip(models, fault_table[1:]):
        for error, value in zip(("timeout", "permission", "rate_limit", "server_error", "empty_result"), row[1:]):
            match = re.search(r"([\d.]+)% · (\d+)/(\d+)", value)
            assert match, value
            c = lookup[model, error]
            assert (int(match[2]), int(match[3])) == (c["success"], c["n"])
            assert abs(float(match[1]) - c["rates"]["success"]["value"]) < .051
    return True


if __name__ == "__main__":
    from overview_render import overview_blocks
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "site/data/overview.json").read_text())
    verify_overview_render(data, overview_blocks(data, root / "site"),
                           (root / "site/index.html").read_text())
    print("Overview render verified: 60 line points, 150 stack segments, all sweep cross-tabs, conditional denominators, success CIs and fault-type table values.")
