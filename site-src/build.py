#!/usr/bin/env python3
"""Build the presentation from the frozen published tables. No model calls or report writes.

Diagram grammar: Diagram Design 2.6.110 (flowchart, bar/dot, line, timeline).
The source reports remain authoritative; this is a presentation-only build.
"""
from pathlib import Path
import hashlib
import html
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'site-src'
OUT = ROOT / 'site'
OUT.mkdir(exist_ok=True)
(OUT / 'diagrams').mkdir(exist_ok=True)
(OUT / 'data').mkdir(exist_ok=True)
COMMIT = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
# Retain a stable research snapshot even after website-only commits.
snapshot_path = SRC / 'research-snapshot.json'
if snapshot_path.exists():
    SNAPSHOT = json.loads(snapshot_path.read_text())
else:
    paths = ['REPORT.md', 'analysis/REMEDIATED_TABLES.md', 'analysis/PROBE_ANALYSIS.md',
             'analysis/REAUDIT.md', 'analysis/PERSISTENCE.md', 'analysis/READBACK.md',
             'docs/TIMELINE.md', 'docs/TRANSPARENCY.md', 'docs/SCOPE_AND_VALIDITY.md',
             'docs/BLIND_SPOTS.md', 'prereg/PREREGISTRATION.md']
    SNAPSHOT = {'commit': COMMIT, 'files': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}
    snapshot_path.write_text(json.dumps(SNAPSHOT, indent=2)+'\n')
for p, sha in SNAPSHOT['files'].items():
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == sha, f'Frozen evidence changed: {p}'
REPO = 'https://github.com/codesagar/silent-failures'
BASE = REPO + '/blob/' + SNAPSHOT['commit'] + '/'
NAMES = ['gpt-6-luna', 'glm-5.3-flash', 'kimi-k3', 'nemotron', 'qwen-ablated']
DISPLAY = ['GPT-6 Luna', 'GLM-5.3 Flash', 'Kimi K3', 'Nemotron', 'Qwen ablated']
C = {'paper':'#f7f5ef', 'white':'#fffefa', 'ink':'#252b29', 'muted':'#626b65',
     'rule':'#d9dcd2', 'accent':'#ad4328', 'tint':'#f3e7de', 'green':'#3c6655'}

def table(path, heading):
    text = (ROOT/path).read_text()
    block = text.split(heading,1)[1].split('\n## ',1)[0]
    return [[c.strip() for c in line.strip().strip('|').split('|')]
            for line in block.splitlines() if line.startswith('|')][2:]

def rate(s):
    m = re.search(r'([\d.]+)% \[([\d.]+),([\d.]+)\]', s)
    if not m: raise ValueError(s)
    n = re.search(r'\(n=(\d+)\)',s)
    boot = re.search(r'boot\[([\d.]+),([\d.]+)\]',s)
    return {'value':float(m[1]),'lo':float(m[2]),'hi':float(m[3]),
            'n':int(n[1]) if n else None,
            'boot':[float(boot[1]),float(boot[2])] if boot else None}

primary='analysis/REMEDIATED_TABLES.md'
conduct_rows=table(primary,'## Conduct on failed DOSED')
conduct={r[0]:{'ack':rate(r[1]),'claim':rate(r[2]),'capped':rate(r[4])} for r in conduct_rows}
curve_rows=table(primary,'## Unsupported success claims vs failure rate')
curves={r[0]:[rate(c) for c in r[1:]] for r in curve_rows}
error_rows=table(primary,'## Error-type sensitivity')
errors={r[0]:[rate(c) for c in r[1:]] for r in error_rows}
repeat_rows=table(primary,'## Repeat-reliability')
repeats={r[0]:{'cells':int(r[1]),'flaky':int(r[2]),**rate(r[3])} for r in repeat_rows}

def esc(s): return html.escape(str(s),quote=True)
def txt(x,y,s,size=12,fill=None,anchor='start',weight=400,family='sans'):
    fam = "'Instrument Serif',Georgia,serif" if family=='serif' else "'Geist',Arial,sans-serif"
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill or C["ink"]}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}">{esc(s)}</text>'
def line(x1,y1,x2,y2,color=None,width=1,dash=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or C["rule"]}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def rect(x,y,w,h,fill=None,stroke=None,rx=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill or C["white"]}" stroke="{stroke or C["rule"]}"/>'
def dot(x,y,r=4,color=None): return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color or C["ink"]}"/>'
def svg(slug,w,h,title,desc,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{slug}-title {slug}-desc" style="--diagram-width:{w}px"><title id="{slug}-title">{esc(title)}</title><desc id="{slug}-desc">{esc(desc)}</desc>{body}</svg>'
DIAGRAMS={}
def register(slug,w,h,title,desc,body):
    value=svg(slug,w,h,title,desc,body)
    DIAGRAMS[slug]=value
    standalone=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · Silent Failures</title><style>body{{margin:0;padding:24px;background:{C['paper']};color:{C['ink']};font-family:Arial,sans-serif}}h1{{font:32px Georgia,serif}}p{{max-width:75ch;line-height:1.6}}.diagram-container{{width:100%;overflow-x:auto}}svg{{display:block;width:100%;min-width:{w}px}}@media print{{svg{{min-width:0}}.diagram-container{{overflow:visible}}}}</style><h1>{esc(title)}</h1><p>{esc(desc)}</p><div class="diagram-container">{value}</div><p>Silent Failures · Frozen research snapshot {SNAPSHOT['commit'][:7]} · Diagram Design 2.6.110 · Editorial fit preset. Values are from the published analysis; intervals and population definitions accompany the figure on the website.</p></html>'''
    (OUT/'diagrams'/f'{slug}.html').write_text(standalone)
    return value

# Five model rows, exact rates; task-cluster intervals carry repeated-task uncertainty.
for metric,title in [('ack','Acknowledges non-completion'),('claim','Unsupported success claim'),('capped','Capped without output')]:
    body=txt(24,32,title,16,weight=600)
    body+=txt(24,54,'% of failed, dosed episodes',11,fill=C['muted'])
    left,right=144,280
    for tick in [0,50,100]:
        x=left+(right-left)*tick/100
        body+=line(x,72,x,312)+txt(x,336,str(tick)+'%',10,fill=C['muted'],anchor='middle')
    for i,(m,name) in enumerate(zip(NAMES,DISPLAY)):
        r=conduct[m][metric]; y=100+i*48; x=left+(right-left)*r['value']/100
        lo,hi=r['boot']; a=left+(right-left)*lo/100;b=left+(right-left)*hi/100
        col=C['accent'] if m=='qwen-ablated' else C['green']
        body+=txt(24,y-4,name,11,weight=600)+txt(24,y+12,f"n = {r['n']}",10,fill=C['muted'])
        body+=line(a,y,b,y,col,2)+line(a,y-4,a,y+4,col)+line(b,y-4,b,y+4,col)+dot(x,y,4,col)
        body+=txt(312,y+4,f"{r['value']:.1f}",11,anchor='end',weight=600)
    body+=txt(24,368,'Dots: rate · whiskers: task-cluster 95% interval',10,fill=C['muted'])
    register('conduct-'+metric,336,392,title,'Failed timeout episodes with at least one realized injection, assigned probability 75% or 100%; primary r0–r3 sample; hidden reruns excluded.',body)

# Small multiples: baseline separated from the connected injected series.
ps=[0,.1,.25,.5,.75,1]
for model,name in zip(NAMES,DISPLAY):
    rs=curves[model]; body=txt(32,32,name,16,weight=600)
    x0,y0,pw,ph=44,64,264,176
    for tick in [0,50,100]:
        y=y0+ph-ph*tick/100
        body+=line(x0,y,x0+pw,y)+txt(x0-8,y+4,str(tick),10,fill=C['muted'],anchor='end')
    pts=[(x0+pw*p,y0+ph-ph*r['value']/100) for p,r in zip(ps,rs)]
    body+='<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts[1:])+f'" fill="none" stroke="{C["accent"]}" stroke-width="2"/>'
    for j,((x,y),r) in enumerate(zip(pts,rs)):
        lo=y0+ph-ph*r['lo']/100; hi=y0+ph-ph*r['hi']/100
        body+=line(x,hi,x,lo,C['muted'])+line(x-3,hi,x+3,hi,C['muted'])+line(x-3,lo,x+3,lo,C['muted'])
        body+=(rect(x-4,y-4,8,8,C['white'],C['ink'],0) if j==0 else dot(x,y,3,C['accent']))
    for p,label in [(0,'0'),(.5,'50'),(1,'100%')]:body+=txt(x0+pw*p,260,label,10,fill=C['muted'],anchor='middle')
    body+=txt(44,284,'Assigned timeout probability',11,fill=C['muted'])
    body+=txt(32,312,f"Baseline: {rs[0]['value']:.1f}% · n = {rs[0]['n']}",12,weight=600)
    register('claims-'+model,344,336,name+' · unsupported claims','Percent of failed episodes with success claims. Open square: uninjected baseline; connected dots: actually dosed timeout episodes. Whiskers: published Jeffreys 95% intervals.',body)

# Method flowchart: no conflation of message labels and environment truth.
def node(x,y,w,h,title,sub,focal=False):
    return rect(x,y,w,h,C['tint'] if focal else C['white'],C['accent'] if focal else C['rule'])+txt(x+16,y+28,title,16,weight=600)+txt(x+16,y+52,sub,12,fill=C['muted'])
def path(d,color=None):return f'<path d="{d}" fill="none" stroke="{color or C["muted"]}" stroke-width="1.5" marker-end="url(#method-arrow)"/>'
arrow=f'<defs><marker id="method-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{C["muted"]}"/></marker></defs>'
body=arrow
body+=path('M244 108 H292')+path('M520 108 H568')
body+=path('M688 148 V172 Q688 180 680 180 H304 Q296 180 296 188 V224')
body+=path('M712 148 V224')
body+=path('M296 304 V328 Q296 336 304 336 H456 Q464 336 464 344 V368')
body+=path('M712 304 V328 Q712 336 704 336 H592 Q584 336 584 344 V368')
body+=node(40,68,204,80,'A benign user task','97 tasks · four domains')
body+=node(292,68,228,80,'An agent uses tools','Five models · one scaffold')
body+=node(568,68,264,80,'Inject a tool failure','Seeded per-call probability',True)
body+=node(160,224,272,80,'Check environment state','Did the whole task succeed?')
body+=node(568,224,272,80,'Label the final response','What does the message claim?')
body+=node(392,368,272,80,'Compare outcome & claim','Measure behavior under failure',True)
body+=txt(40,504,'Two measurements. The judge labels language; the environment checker scores task utility.',12,fill=C['muted'])
register('method',896,536,'Measure outcomes and claims separately','The tool-use episode produces environment state and a final response, which are evaluated separately and then compared.',body)

# Probe flowchart focused on Qwen, because its clean subset has the largest sample.
arrow=arrow.replace('method-arrow','probe-arrow')
def pp(d):return path(d).replace('method-arrow','probe-arrow')
body=arrow+pp('M196 112 V152')+pp('M196 232 V272')+pp('M324 192 H392')+pp('M196 352 V392')+pp('M324 432 H392')
body+=node(40,32,312,80,'819 capped episodes','Qwen · injected, hidden-rerun excluded')
body+=node(40,152,284,80,'A. Ask for a status update','Tools remain available · outage continues')
body+=node(392,152,248,80,'259 respond','31.6% give a user-facing answer')
body+=node(40,272,284,80,'560 resume tool use','68.4% still give no answer',True)
body+=node(40,392,284,80,'B. Remove tools; ask again','559 answered · 1 length artifact')
body+=node(392,392,248,80,'531 acknowledge','95.0% of 559 stage-B answers',True)
body+=txt(40,520,'Stage B is a selected subset, not all capped episodes. Original labels are retained.',12,fill=C['muted'])
register('probe',688,552,'After silence, ask again','Qwen’s clean injected subset shows that failure to report within the original budget does not establish inability to acknowledge non-completion.',body)

# A mobile composition preserves the entire branch selection without shrinking text.
body=arrow.replace('probe-arrow','probe-mobile-arrow')
for a,b in [(112,152),(312,352),(432,472)]:
    body+=pp(f'M172 {a} V{b}').replace('probe-arrow','probe-mobile-arrow')
body+=node(20,32,304,80,'819 capped episodes','Qwen · clean injected subset')
body+=rect(20,152,304,160,C['white'],C['rule'])
body+=txt(36,180,'A. Ask for a status update',16,weight=600)+txt(36,204,'Tools stay available; outage continues.',12,fill=C['muted'])
body+=line(36,224,308,224)+txt(36,248,'259 respond',16,weight=600)+txt(36,272,'560 resume tool use without answering',12,fill=C['accent'])+txt(36,296,'Only these nonresponders reach B.',12,fill=C['muted'])
body+=node(20,352,304,80,'B. Remove tools; ask again','559 answered · 1 length artifact')
body+=node(20,472,304,80,'531 acknowledge non-completion','95.0% of 559 stage-B answers',True)
body+=txt(20,588,'Selected subset; original episode labels retained.',12,fill=C['muted'])
register('probe-mobile',344,616,'After silence, ask again','Qwen: 819 clean injected capped episodes; 259 answer the nudge, 560 do not. Of the latter, 559 answer the tools-off question and 531 acknowledge non-completion.',body)

# Failure-channel comparison uses a numerical table with in-cell bars, not decorative heat.
error_labels=['Timeout','Permission','Rate limit','Server error','Lost response']
body=txt(40,36,'The error channel changes the outcome',28,family='serif')
for j,name in enumerate(error_labels):body+=txt(236+j*136,84,name,12,weight=600,anchor='middle')
for i,(m,name) in enumerate(zip(NAMES,DISPLAY)):
    y=112+i*64;body+=txt(40,y+24,name,12,weight=600)
    for j,r in enumerate(errors[m]):
        x=184+j*136
        body+=rect(x,y,112,48,C['white'],C['rule'])
        body+=f'<rect x="{x+8}" y="{y+36}" width="{96*r["value"]/100:.2f}" height="4" fill="{C["accent"] if j==4 else C["muted"]}"/>'
        body+=txt(x+56,y+24,f"{r['value']:.1f}%",12,anchor='middle',weight=600)
body+=txt(40,468,'Unsupported success claims · failed, dosed episodes · assigned probability 50%',12,fill=C['muted'])
body+=txt(40,492,'Bars share a 0–100% scale. Lost responses are highest in 4 of 5 models; GLM is the exception.',12,fill=C['muted'])
register('channels',904,524,'Failure channel comparison','At assigned failure probability 50%, lost tool responses yield the highest unsupported-claim rate for four of the five models; GLM peaks on rate limits.',body)

def data_table(headers,rows,caption):
    return '<div class="table-scroll" tabindex="0" role="region" aria-label="'+esc(caption)+'"><table><caption>'+esc(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+esc(c)+'</th>' for c in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row">' if i==0 else '<td>')+esc(c)+('</th>' if i==0 else '</td>') for i,c in enumerate(row))+'</tr>' for row in rows)+'</tbody></table></div>'
def figure(slug,caption=''):
    return '<div class="diagram-container" tabindex="0" role="region" aria-label="Scrollable '+esc(slug.replace('-',' '))+' diagram">'+DIAGRAMS[slug]+'</div>'+(f'<p class="figure-note">{caption}</p>' if caption else '')
def source(p,label='Source table ↗'): return '<a class="source-link" href="'+BASE+p+'">'+label+'</a>'

blocks={
 'METHOD':'<p class="scroll-hint">Scroll sideways to follow the complete diagram →</p>'+figure('method'),
 'CONDUCT':'<div class="conduct-grid">'+''.join(figure('conduct-'+k) for k in ['ack','claim','capped'])+'</div>',
 'CURVES':'<div class="curve-grid">'+''.join(figure('claims-'+m) for m in NAMES)+'<div class="curve-key"><span class="eyebrow">READING THE FIGURE</span><h3>What changes<br>is the denominator.</h3><p>□ At 0%: ordinary failures, with no injection.<br>● Above 0%: failed episodes where at least one timeout was actually injected.</p><p>Lines connect observed conditions, not a fitted curve. Whiskers show 95% Jeffreys intervals.</p></div></div>',
 'CHANNELS':'<p class="scroll-hint">Scroll sideways to compare all five failure channels →</p>'+figure('channels'),
 'PROBE':'<div class="wide-diagram">'+figure('probe')+'</div><div class="narrow-diagram">'+figure('probe-mobile')+'</div>',
 'CONDUCT_TABLE':data_table(['Model','Acknowledges','Unsupported claim','Capped without output'],[[r[0],r[1],r[2],r[4]] for r in conduct_rows],'Published primary conduct rates and intervals'),
 'CURVE_TABLE':data_table(['Model','Baseline 0%','10%','25%','50%','75%','100%'],curve_rows,'Published unsupported-claim rates; zi counts excluded zero-injection episodes'),
 'ERROR_TABLE':data_table(['Model']+error_labels,error_rows,'Published error-channel rates with denominators and 95% intervals'),
 'PROBE_TABLE':data_table(['Model','Clean injected n','Resumes tool use after nudge','Forced acknowledgment'],[
 ['GLM-5.3 Flash','67','36/67 = 53.7%','35/36 = 97.2%'],['Kimi K3','106','60/106 = 56.6%','59/60 = 98.3%'],['Qwen ablated','819','560/819 = 68.4%','531/559 = 95.0%'],['Nemotron','3','1/3 (descriptive only)','1/1 (descriptive only)'],['GPT-6 Luna','5','0/5 (descriptive only)','No stage-B cases']], 'Probe main slice; stage B includes only stage-A nonresponders who answered stage B'),
 'REPEAT_TABLE':data_table(['Model','Mixed-outcome task cells','Rate'],[[r[0],r[2]+'/97',r[3]] for r in repeat_rows],'Uninjected repeat reliability, r0–r3; retained cells have at least two repetitions'),
 'PERSISTENCE_TABLE':data_table(['Model','n','Mean retries','Max retry streak','Mean distinct tools','Mean tool calls'],table('analysis/PERSISTENCE.md','## Micro-metrics'),'Persistence on failed, dosed timeout episodes at p ≥ 0.75'),
}
from redesign_charts import build_charts
from presentation import presentation_blocks
from overview_data import overview_data
from overview_render import overview_blocks
blocks.update(build_charts(register, txt, line, rect, dot, C, conduct, errors, NAMES, DISPLAY))
blocks.update(presentation_blocks(SRC, OUT))
blocks.update(overview_blocks(overview_data(ROOT, OUT), OUT))
blocks["NEMOTRON_BRIEF"] = (SRC / "nemotron-brief.html").read_text()
blocks["BEHAVIOR_DEFINITIONS"] = (SRC / "behavior-definitions.html").read_text()

payload={'snapshot':SNAPSHOT,'conduct':conduct,'unsupported_claim_curves':curves,'error_channels':errors,'repeat_reliability':repeats,
         'notes':'Presentation extracts from published tables. No experiments or classifications rerun.'}
(OUT/'data'/'findings.json').write_text(json.dumps(payload,indent=2)+'\n')
(OUT/'data'/'research-snapshot.json').write_text(json.dumps(SNAPSHOT,indent=2)+'\n')
for page in ['index','methodology']:
    text=(SRC/(page+'.html')).read_text()
    for key,value in blocks.items(): text=text.replace('{{'+key+'}}',value)
    text=text.replace('{{SOURCE}}',BASE).replace('{{COMMIT}}',SNAPSHOT['commit'][:7]).replace('{{FULL_COMMIT}}',SNAPSHOT['commit']).replace('{{REPO}}',REPO)
    assert not re.search(r'\{\{[A-Z_]+\}\}',text), 'Unresolved template token'
    (OUT/(page+'.html')).write_text(text)
for name in ['styles.css','app.js','favicon.svg','overview.css','overview.js','conversations.css','conversations.js']:
    shutil.copyfile(SRC/name,OUT/name)
(OUT/'.nojekyll').touch()
print(f'Built 2 pages, {len(DIAGRAMS)+3} standalone infographics, and source data; frozen research {SNAPSHOT["commit"][:7]}.')
