"""Accessible overview views of the frozen corpus; no new model evaluations."""
import html
import json

MODELS = ["gpt-6-luna", "glm-5.3-flash", "kimi-k3", "nemotron", "qwen-ablated"]
NAMES = ["GPT-6 Luna", "GLM-5.3 Flash", "Kimi K3", "Nemotron", "Qwen ablated"]
COLORS = ["#496f86", "#777044", "#826483", "#ad4328", "#3c6655"]
PS = [0, .1, .25, .5, .75, 1]
ESC = lambda x: html.escape(str(x), quote=True)


def table(headers, rows, caption):
    return '<div class="table-scroll" tabindex="0" role="region" aria-label="' + ESC(caption) + '"><table><caption>' + ESC(caption) + '</caption><thead><tr>' + ''.join('<th scope="col">' + ESC(h) + '</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(('<th scope="row">' if i == 0 else '<td>') + ESC(c) + ('</th>' if i == 0 else '</td>') for i, c in enumerate(row)) + '</tr>' for row in rows) + '</tbody></table></div>'


def text(x, y, value, size=12, fill="#59635d", anchor="start", weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" font-family="Geist,Arial,sans-serif">{ESC(value)}</text>'


def chart(slug, cells, metric, title, ytitle, maximum=100):
    """Shared scales, real probability spacing, patterns redundant with colors."""
    w, h, left, top, pw, ph = 920, 400, 60, 44, 800, 248
    body = text(left, 24, ytitle, 12)
    for tick in ([0, 25, 50, 75, 100] if maximum == 100 else [0, 4, 8, 12, 16]):
        y = top + ph * (1 - tick / maximum)
        body += f'<line x1="{left}" y1="{y}" x2="{left+pw}" y2="{y}" stroke="#ced3c8"/>'
        body += text(left-12, y+4, tick, anchor="end")
    for p in PS:
        x = left + pw*p
        body += text(x, top+ph+24, str(round(p*100))+"%", anchor="middle")
    body += text(left+pw/2, 342, "Assigned fault probability per tool call · timeout sweep", anchor="middle")
    dashes = ["", "7 3", "2 4", "", "10 3 2 3"]
    for i, m in enumerate(MODELS):
        sub = sorted([c for c in cells if c["model"] == m], key=lambda c:c["p"])
        values = [(c["mean_turns"] if metric == "mean_turns" else c["rates"][metric]["value"]) for c in sub]
        points = [(left+pw*c["p"], top+ph*(1-v/maximum)) for c, v in zip(sub, values)]
        body += '<polyline points="' + ' '.join(f'{x:.2f},{y:.2f}' for x,y in points) + f'" fill="none" stroke="{COLORS[i]}" stroke-width="{3 if m=="nemotron" else 2}" stroke-dasharray="{dashes[i]}"/>'
        for c, v, (x,y) in zip(sub, values, points):
            body += f'<circle cx="{x}" cy="{y}" r="{4 if m=="nemotron" else 3}" fill="{COLORS[i]}" stroke="#fffefa"><title>{ESC(NAMES[i])}: {v:.1f}; p={c["p"]}; n={c["n"]}</title></circle>'
        lx = 42+i*176
        body += f'<line x1="{lx}" y1="376" x2="{lx+20}" y2="376" stroke="{COLORS[i]}" stroke-width="3" stroke-dasharray="{dashes[i]}"/>'
        body += text(lx+27, 380, NAMES[i], 11, weight=650 if m=="nemotron" else 400)
    detail = "Descriptive means and cap rates in the accompanying table; no uncertainty intervals for effort means." if metric == "mean_turns" else "Exact counts and task-cluster uncertainty in the accompanying table."
    desc = f"{title}. Five model configurations, six assigned timeout probabilities. All eligible primary episodes in each condition. {detail}"
    return f'<div class="overview-plot" tabindex="0" role="region" aria-label="{ESC(title)}; scroll horizontally on a small screen"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{slug}-title {slug}-desc"><title id="{slug}-title">{ESC(title)}</title><desc id="{slug}-desc">{ESC(desc)}</desc>{body}</svg></div>'


def overview_blocks(data, out):
    cells = data["rate_sweep"]
    success = chart("success-sweep", cells, "success", "Task outcome across fault probabilities", "Task success · benchmark checker pass (%)")
    rows = []
    for m, name in zip(MODELS, NAMES):
        sub = sorted([c for c in cells if c["model"] == m], key=lambda c:c["p"])
        vals = []
        for c in sub:
            r = c["rates"]["success"]
            vals.append(f'{r["value"]:.1f}% · {r["k"]}/{r["n"]} · CI {r["lo"]:.1f}–{r["hi"]:.1f}')
        rows.append([name]+vals)
    success += '<details><summary>Exact results, denominators & task-cluster 95% intervals</summary>' + table(["Model"]+[f"{round(p*100)}% faults" for p in PS], rows, "Benchmark checker pass; all eligible primary episodes in the assigned condition") + '<p>Intervals resample tasks, retaining their repeated episodes (2,000 bootstrap draws). These describe the retained sample; exclusions affect model configurations differently. Curves join tested conditions, not fitted predictions.</p></details>'
    # A broad outcome view uses disjoint cross-product groups, not success vs silence.
    labels = [("success", "Checker pass", "#3c6655"), ("ack", "Failed + acknowledges", "#496f86"), ("unsupported", "Failed + success claim", "#ad4328"), ("empty", "Failed + no answer", "#77746d"), ("ambiguous", "Failed + ambiguous", "#b6a6ba")]
    outcome_panels = []
    joint_rows = []
    for mi, (m, name) in enumerate(zip(MODELS, NAMES)):
        sub = sorted([c for c in cells if c["model"] == m], key=lambda c:c["p"])
        body = text(20, 28, name, 16, "#ad4328" if m=="nemotron" else "#252b29", weight=650)
        body += text(20, 50, "All eligible episodes · each bar totals 100%", 10)
        for j, c in enumerate(sub):
            x, y, width = 60, 72+j*38, 260
            body += text(45, y+17, f'{round(c["p"]*100)}%', 11, anchor="end")
            counts = [c["success"], c["cross_tab"]["fail"]["F"], c["cross_tab"]["fail"]["S"], c["cross_tab"]["fail"]["empty"], c["cross_tab"]["fail"]["A"]]
            assert sum(counts) == c["n"]
            for (key, lab, color), k in zip(labels, counts):
                bw = width*k/c["n"]
                body += f'<rect x="{x:.3f}" y="{y}" width="{bw:.3f}" height="24" fill="{color}"><title>{ESC(lab)}: {k}/{c["n"]} ({100*k/c["n"]:.1f}%)</title></rect>'
                x += bw
            body += text(334, y+16, f'n={c["n"]}', 9)
            joint_rows.append([name, f'{round(c["p"]*100)}%'] + [c["cross_tab"][outcome][label] for outcome in ["pass","fail"] for label in ["S","F","A","empty"]])
        body += text(60, 326, "0", 10)+text(190, 326, "50", 10, anchor="middle")+text(320, 326, "100%", 10, anchor="end")
        slug = "outcomes-"+m
        outcome_panels.append(f'<figure class="outcome-panel"><div class="mini-plot" tabindex="0" role="region" aria-label="{ESC(name)} outcome distribution"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 392 348" role="img" aria-labelledby="{slug}-title {slug}-desc"><title id="{slug}-title">{ESC(name)} outcomes</title><desc id="{slug}-desc">Benchmark pass and four reporting outcomes among failures across six timeout probabilities. Counts in the full cross-tab.</desc>{body}</svg></div></figure>')
    outcomes = '<div class="outcome-grid">'+''.join(outcome_panels)+'<aside class="outcome-key"><h3>What does a bar mean?</h3><p>Every episode is counted once. Green includes every checker pass, whether or not the agent reported success.</p><p>For checker failures, color shows what the final answer said—or that no answer arrived.</p><p>Acknowledgment can follow many retries. Silence can also accompany a checker pass; inspect the cross-tab below.</p></aside></div>'
    outcomes += '<div class="chart-legend">'+''.join(f'<span><i style="background:{col}"></i>{ESC(lab)}</span>' for _, lab, col in labels)+'</div>'
    outcomes += '<details><summary>Full task outcome × final report cross-tab · every condition</summary>'+table(["Model","Fault probability","Pass + S","Pass + F","Pass + A","Pass + empty","Fail + S","Fail + F","Fail + A","Fail + empty"],joint_rows,"Counts, not percentages. S: claims success; F: reports failure/partial completion; A: ambiguous. All primary timeout-sweep episodes.")+'</details>'
    conditional_rows = []
    for m,name in zip(MODELS,NAMES):
        for c in sorted([c for c in cells if c["model"]==m],key=lambda c:c["p"]):
            q=c["conditional"]
            conditional_rows.append([name,f'{round(c["p"]*100)}%',q["n"]]+[f'{q["rates"][k]["value"]:.1f}%' for k in ["acknowledges","unsupported","cap","ambiguous"]])
    outcomes += '<details><summary>Reporting among failed tasks · baseline and fault-exposed conditions</summary><p>This changes the denominator: at 0%, all failed baseline episodes; above 0%, only failed episodes with at least one injected timeout. Do not compare these percentages as if they were shares of every episode.</p>'+table(["Model","Fault probability","Eligible failed n","Acknowledges","Success claim","No answer at cap","Ambiguous"],conditional_rows,"Conditional failure conduct across the full sweep")+'</details>'
    effort = chart("effort-sweep",cells,"mean_turns","How long agents keep trying","Mean recorded assistant turns",16)
    effort_rows=[]
    for m,name in zip(MODELS,NAMES):
        sub=sorted([c for c in cells if c["model"]==m],key=lambda c:c["p"])
        effort_rows.append([name]+[f'{c["mean_turns"]:.2f} turns · {100*c["cap_all"]/c["n"]:.1f}% capped · n={c["n"]}' for c in sub])
    effort += '<details><summary>Turns and cap rates across every fault probability</summary>'+table(["Model"]+[f"{round(p*100)}% faults" for p in PS],effort_rows,"Descriptive means and cap rates; all eligible primary timeout-sweep episodes")+'<p>The configured loop limit is 15; the transcript can record 16 assistant turns. An assistant turn can contain multiple tool calls. No uncertainty intervals are attached to these descriptive effort means.</p></details>'
    faults=[]
    for m,name in zip(MODELS,NAMES):
        cs={c["error_type"]:c for c in data["fault_types"] if c["model"]==m}
        faults.append([name]+[f'{cs[t]["rates"]["success"]["value"]:.1f}% · {cs[t]["success"]}/{cs[t]["n"]}' for t in ["timeout","permission","rate_limit","server_error","empty_result"]])
    fault_table=table(["Model","Timeout","Permission","Rate limit","Server error","Lost response"],faults,"Task success (benchmark checker pass) at 50% assigned fault probability; all eligible primary episodes")
    # Exact browser data is local and optional; static charts/tables remain complete.
    data_script='<script type="application/json" id="overview-data">'+json.dumps(data,separators=(",",":")).replace("<","\\u003c")+'</script>'
    dose_rows = []
    for m, name in zip(MODELS, NAMES):
        c = next(c for c in cells if c["model"] == m and c["p"] == .5)
        dose_rows.append([name, f'{c["rates"]["success"]["value"]:.1f}%', f'{c["rates"]["unsupported"]["value"]:.1f}%', f'{c["rates"]["cap"]["value"]:.1f}%', c["n"]])
    dose = table(["Model","Checker pass","Failed + success claim","No answer at cap","n"], dose_rows, "50% assigned timeout probability · all eligible episodes")
    # Standalone figures retain accessible SVGs and the complete associated tables.
    (out / "diagrams").mkdir(exist_ok=True)
    for slug, title, content in [
        ("overview-success", "Task outcomes across fault probabilities", success),
        ("overview-reporting", "Task outcome and final report", outcomes),
        ("overview-effort", "Persistence across fault probabilities", effort),
    ]:
        css = """body{background:#f7f5ef;color:#252b29;font:15px/1.6 Arial,sans-serif;margin:32px}h1{font:40px Georgia,serif}svg{display:block;width:100%;min-width:920px}.overview-plot,.mini-plot,.table-scroll{overflow-x:auto;max-width:100%}.mini-plot svg{min-width:392px;max-width:600px}.outcome-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,392px),1fr));gap:24px}.chart-legend{display:flex;gap:20px;flex-wrap:wrap}.chart-legend i{display:inline-block;width:14px;height:14px;margin-right:8px}table{border-collapse:collapse}td,th{padding:12px;border-bottom:1px solid #ced3c8}summary{cursor:pointer;padding:16px 0}caption{text-align:left}"""
        page = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{css}</style></head><body><h1>{title}</h1><p>All eligible primary episodes in each assigned timeout condition. Existing scores and labels; new deterministic presentation aggregates. Nemotron is highlighted. <a href="../index.html">Read the experiment, definitions, and evidence</a>.</p>{content}</body></html>'
        (out / "diagrams" / (slug + ".html")).write_text(page)
    return {"SUCCESS_SWEEP":success,"OUTCOME_SWEEP":outcomes,"EFFORT_SWEEP":effort,"FAULT_SUCCESS":fault_table,"OVERVIEW_DATA":data_script,"DOSE_COMPARISON":dose}
