#!/usr/bin/env python3
"""Presentation integrity checks. Never runs experiments or edits evidence."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT/'site'
class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.ids=set(); self.links=[]; self.svg=[]; self.path=path
        self.feed(path.read_text())
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate ID {a["id"]} in {self.path}'
            self.ids.add(a['id'])
        if tag=='a' and a.get('href'): self.links.append(a['href'])
        if tag in ['script','link']:
            ref=a.get('src') or a.get('href')
            if ref:self.links.append(ref)
        if tag=='svg':self.svg.append(a)

docs={p:Document(p) for p in SITE.rglob('*.html')}
for p,d in docs.items():
    for s in d.svg:
        assert s.get('role')=='img' and s.get('aria-labelledby'),f'Inaccessible SVG: {p}'
        assert all(i in d.ids for i in s['aria-labelledby'].split()),f'Missing SVG label: {p}'
    for href in d.links:
        u=urlsplit(href)
        if u.scheme or u.netloc:
            if u.netloc=='github.com' and '/silent-failures/' in u.path and ('/blob/' in u.path or '/tree/' in u.path):
                parts=unquote(u.path.split('/silent-failures/',1)[1]).split('/',2)
                suffix=parts[2] if len(parts)>2 else '.'
                assert (ROOT/suffix).exists(), f'Missing evidence source: {href}'
            continue
        target=(p.parent/unquote(u.path)).resolve() if u.path else p
        if target.is_dir():target=target/'index.html'
        assert target.exists(),f'Broken local link from {p}: {href}'
        if u.fragment and target in docs:assert u.fragment in docs[target].ids,f'Broken anchor: {href}'
    assert not re.search(r'\{\{[A-Z_]+\}\}',p.read_text()),f'Unresolved template: {p}'

snap=json.loads((SITE/'data/research-snapshot.json').read_text())
for p,sha in snap['files'].items():
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha,f'Evidence modified: {p}'
data=json.loads((SITE/'data/findings.json').read_text())
assert len(data['conduct'])==5
assert data['conduct']['qwen-ablated']['capped']['value']==91.5
assert data['conduct']['qwen-ablated']['capped']['n']==574
assert data['conduct']['gpt-6-luna']['ack']['value']==99.3
assert all(len(v)==6 and v[-1]['value']==0 for v in data['unsupported_claim_curves'].values())
assert sum(1 for v in data['error_channels'].values() if v[-1]['value']==max(x['value'] for x in v))==4
assert 19380-1920-(901-93)-3==16649
for font in ['geist','instrument-serif','instrument-serif-italic']:
    assert (SITE/'fonts'/f'{font}.woff2').read_bytes()[:4]==b'wOF2'
print(f'PASS: {len(docs)} HTML documents; local links, source paths, SVG labels, frozen evidence hashes, chart anchors, and fonts.')

# Verify displayed examples against frozen source-line records, not self-asserted metadata.
examples=json.loads((SITE/'data/examples.json').read_text())
assert examples['research_commit']==snap['commit']
assert examples['archive_sha256'] in (ROOT/'data/TRANSCRIPTS_SHA256').read_text()
assert len(examples['examples'])==7
assert {e['episode']['model'] for e in examples['examples']}==set(data['conduct'])
def source_record(sources,label):
    url=next(s['url'] for s in sources if s['label']==label)
    u=urlsplit(url)
    prefix='/codesagar/silent-failures/blob/'+snap['commit']+'/'
    assert u.path.startswith(prefix), 'Unpinned example source'
    path=ROOT/u.path[len(prefix):]
    assert re.fullmatch(r'L\d+',u.fragment), 'Expected exact source line'
    return json.loads(path.read_text().splitlines()[int(u.fragment[1:])-1])
for e in examples['examples']:
    original=source_record(e['sources'],'Episode record')
    assert e['episode']==original and e['id']==original['run_id']
    assert original['rep']<=3 and not original['harness_error']
    assert original['tool_calls_total']<=original['tool_msgs']
    assert not (original['final_empty'] and original['assistant_turns']<16)
    assert original['injected_failures']>=1
    assert e['trace_excerpt']['utility']==original['utility']
    assert sum(m['role']=='tool' for m in e['trace_excerpt']['messages'])==original['tool_msgs']
    if e['response_kind']!='absence':assert e['response'] in original['final_message']
    else:assert original['final_empty'] and not original['final_message']
    if e['published_label_record'] is not None and e['response_kind']!='absence':
        assert e['published_label_record']==source_record(e['sources'],'Published label')
    if e['reaudit_record'] is not None:
        assert e['reaudit_record']==source_record(e['sources'],'Independent label re-audit')
    if 'probe' in e:
        p=e['probe']
        assert p['record']==source_record(p['sources'],'Probe episode')
        assert p['stage_b_answer']==p['record']['stageB_answer']
    assert json.loads((SITE/'data/episodes'/(e['slug']+'.json')).read_text())==e
print('PASS: seven primary examples, five-model coverage, exact source-line records, quoted responses, archive pin, and selected probe answer.')
