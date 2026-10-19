"""Render verified presentation extracts; never modify the research package."""
import html
import json
import re


def presentation_blocks(src, out):
    esc = lambda value: html.escape(str(value), quote=True).replace("\n", "&#10;")
    data = json.loads((src / 'examples.json').read_text())
    (out / 'data' / 'examples.json').write_text(json.dumps(data, indent=2) + '\n')
    (out / 'data' / 'episodes').mkdir(exist_ok=True)
    navigation = []
    panels = []
    for i, e in enumerate(data['examples']):
        slug = e['slug']
        (out / 'data' / 'episodes' / (slug + '.json')).write_text(json.dumps(e, indent=2) + '\n')
        short = {'luna-loud':'Luna · acknowledgment','qwen-cap':'Qwen · silence','glm-quiet':'GLM · lost receipt','kimi-acknowledgment':'Kimi · partial acknowledgment','glm-partial':'GLM · partial claim','nemotron-contradicted':'Nemotron · contradiction','nemotron-unverified':'Nemotron · unverified'}[slug]
        navigation.append(f'<a href="#example-{slug}"'+(' aria-current="true"' if i == 0 else '')+f'>{esc(short)}</a>')
        steps = ''.join(f'<li><span class="step-kind">{esc(s["kind"])}</span>{esc(s["text"])}</li>' for s in e['steps'])
        response_class = 'response no-response' if e['response_kind'] == 'absence' else 'response'
        response_tag = 'p' if e['response_kind'] == 'absence' else 'blockquote'
        sources = ''.join(f'<a href="{esc(s["url"])}">{esc(s["label"])} ↗</a>' for s in e['sources'])
        probe = ''
        if 'probe' in e:
            p = e['probe']
            probe_sources = ''.join(f'<a href="{esc(s["url"])}">{esc(s["label"])} ↗</a> ' for s in p['sources'])
            probe = f'''<details class="probe-example"><summary>Follow-up: the same episode, after the cap</summary><p><strong>Stage A · tools available.</strong> {esc(p['stage_a_prompt'])}<br>{esc(p['stage_a_behavior'])}</p><p><strong>Stage B · {esc(p['stage_b_change'])}</strong><br>{esc(p['stage_b_prompt'])}</p><blockquote class="response">{esc(p['stage_b_answer'])}</blockquote><p>Full captured stage-B answer. {esc(p['label'])}. {esc(p['environment'])} {esc(p['qualification'])}</p><p>{probe_sources}</p></details>'''
        panels.append(f'''<details class="episode" id="example-{slug}"{' open' if i == 0 else ''}><summary><span>{esc(e['model'])}</span> {esc(e['title'])}</summary><div class="episode-body"><div class="episode-top"><div><span class="eyebrow">{esc(e['model'])} / {esc(e['condition'])}</span><h3>{esc(e['title'])}</h3><p>{esc(e['population'])}</p></div><span class="episode-badge">{esc(e['behavior'])}</span></div><div class="episode-columns"><div class="trace-block"><p class="eyebrow">01 / THE USER'S REQUEST · VERBATIM</p><p class="request">“{esc(e['request'])}”</p><p class="eyebrow">02 / TOOL SEQUENCE · ABRIDGED SUMMARY</p><ol class="trace-steps">{steps}</ol></div><div class="trace-block"><p class="eyebrow">03 / AGENT RESPONSE · {esc(e['response_kind'])}</p><{response_tag} class="{response_class}">{esc(e['response'])}</{response_tag}><div class="outcome"><strong>04 / Environment outcome</strong>{esc(e['environment'])}</div><p class="published-label"><strong>Published classification</strong><br>{esc(e['label'])}</p><p class="interpretation">{esc(e['interpretation'])}</p></div></div>{probe}<div class="episode-provenance"><p><strong>Reading boundary:</strong> {esc(e['qualification'])}</p><p>Episode <code>{esc(e['id'])}</code></p><a href="data/episodes/{slug}.json">Saved conversation & source records ↗</a>{sources}</div></div></details>''')
    examples = '<div class="example-lab"><nav class="example-nav" aria-label="Choose a real episode">' + ''.join(navigation) + '</nav>' + ''.join(panels) + '</div>'
    walkthrough = (src / 'walkthrough.html').read_text()
    spoken_words = sum(len(t.split()) for t in re.findall(r'<p data-spoken>(.*?)</p>', walkthrough))
    walkthrough = walkthrough.replace('{{SPOKEN_WORDS}}', str(spoken_words))
    return {'EXAMPLES': examples, 'WALKTHROUGH': walkthrough}
