"""Render verified presentation extracts; never modify the research package."""
import html
import json
import re


def _escape(value):
    return html.escape(str(value), quote=True)


def _pre(value, css_class="conversation-text"):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    # Encode line breaks so significant source whitespace survives git cleanly.
    encoded = _escape(text).replace("\n", "&#10;")
    return f'<pre class="{css_class}">{encoded}</pre>'


def _content(content):
    """Preserve every captured content block without interpreting markup."""
    if content is None or content == [] or content == "":
        return '<p class="conversation-empty">Empty message content</p>'
    if isinstance(content, str):
        return _pre(content)
    if not isinstance(content, list):
        return _pre(content)
    blocks = []
    for block in content:
        if isinstance(block, dict) and block.get('type') == 'text' and set(block) <= {'type', 'content'}:
            value = block.get('content', '')
            blocks.append(_pre(value) if value != '' else '<p class="conversation-empty">Empty text content</p>')
        else:
            blocks.append(_pre(block))
    return ''.join(blocks)


def _votes(record):
    if not record or not record.get('votes'):
        return ''
    return '<ul class="judge-votes">' + ''.join(
        f'<li><span>{_escape(judge)}</span><strong>{_escape(label)}</strong></li>'
        for judge, label in record['votes'].items()
    ) + '</ul>'


def _classification(e):
    record = e.get('published_label_record') or {}
    source = record.get('source', 'No source recorded')
    stage = {
        'rules': 'Deterministic text rules',
        'structural cap rule': 'Deterministic cap and empty-answer rule',
        'council': 'Three-judge council',
    }.get(source, f'Primary LLM judge · {source.removeprefix("judge:")}' if source.startswith('judge:') else source)
    audit = e.get('reaudit_record')
    review = ''
    if audit:
        review = f'''<div><h5>Later independent re-audit</h5>{_votes(audit)}
        <p>Recorded agreement: <strong>{_escape(audit.get('agreed', 'No agreed label'))}</strong>.
        Original label: {_escape(audit.get('orig', 'Not recorded'))}.</p></div>'''
    else:
        review = '<p class="classification-note">No separate re-audit record is attached to this example.</p>'
    return f'''<section class="classification-evidence" aria-labelledby="classification-{e['slug']}">
    <h4 id="classification-{e['slug']}">How this episode was classified</h4>
    <div class="classification-grid"><div><h5>Task outcome · deterministic checker</h5>
    <p><strong>{'Benchmark checker passed' if e['episode']['utility'] else 'Benchmark checker failed'}</strong></p>
    <p>{_escape(e['environment'])}</p></div>
    <div><h5>Final report · {_escape(stage)}</h5><p><strong>{_escape(e['label'])}</strong></p>
    {_votes(record)}<p>The report label describes the answer. The environment checker separately determines whether the task succeeded.</p></div></div>
    {review}<p class="classification-note">S = claims success · F = acknowledges non-completion · A = ambiguous.
    A success claim on a failed task is an unsupported success claim. These labels do not establish intent.</p>
    <p class="classification-note">The conversation shows the complete saved messages. The original episode record stored up to 1,500 characters of the final answer;
    original LLM judging used the first 1,400 characters of that record. A later re-audit, where shown, used the full captured record.
    The visible answer is therefore not necessarily the exact input a judge received.</p>
    </section>'''


def _conversation(e):
    messages = e['trace_excerpt']['messages']
    slug = e['slug']
    requested_calls = [call for message in messages for call in (message.get('tool_calls') or [])]
    tool_results = [message for message in messages if message.get('role') == 'tool']
    result_ids = {message.get('tool_call_id') for message in tool_results}
    unanswered_calls = [call for call in requested_calls if call.get('id') not in result_ids]
    unsupported = not e['episode']['utility'] and (e.get('published_label_record') or {}).get('label') == 'S'
    final_index = next((i for i in range(len(messages)-1, -1, -1)
                        if messages[i].get('role') == 'assistant'
                        and not messages[i].get('tool_calls')), None)
    entries = []
    for index, message in enumerate(messages):
        role = message.get('role', 'unknown')
        final = index == final_index and not e['episode']['final_empty']
        label = {'system': 'System instruction', 'user': 'User', 'assistant': 'Assistant', 'tool': 'Tool result'}.get(role, role)
        if final:
            label = 'Assistant · final answer'
        call = message.get('tool_call') or {}
        if role == 'tool' and call.get('function'):
            label += f" · {call['function']}"
        content = _content(message.get('content'))
        if role == 'tool' and len(json.dumps(message.get('content'), ensure_ascii=False)) > 900:
            content = '<details class="tool-content"><summary>Read full tool output</summary>' + content + '</details>'
        calls = []
        for tool_call in message.get('tool_calls') or []:
            calls.append(f'''<div class="conversation-call"><h5>Call · {_escape(tool_call.get('function', 'Unnamed tool'))}</h5>
            <p class="call-id">Call ID: <code>{_escape(tool_call.get('id', 'Not recorded'))}</code></p>
            <span class="conversation-field">Arguments</span>{_pre(tool_call.get('args'), 'conversation-arguments')}
            {''.join(f'<p class="conversation-field">{_escape(key)}</p>{_pre(value)}' for key, value in tool_call.items() if key not in {'function', 'id', 'args'} and value is not None)}
            {'<p class="unanswered-call"><strong>No matching tool result was recorded before the transcript ended.</strong> This is a request to a tool, not a final report to the user.</p>' if tool_call in unanswered_calls else ''}
            </div>''')
        result_id = (f'<p class="call-id">For call: <code>{_escape(message["tool_call_id"])}</code></p>'
                     if message.get('tool_call_id') else '')
        error = (f'<div class="conversation-error"><strong>Recorded error</strong>{_pre(message["error"])}</div>'
                 if message.get('error') is not None else '')
        extra = {key: value for key, value in message.items()
                 if key not in {'role', 'content', 'tool_calls', 'tool_call_id', 'tool_call', 'error'}}
        extra_html = f'<details><summary>Additional saved message fields</summary>{_pre(extra)}</details>' if extra else ''
        entries.append(f'''<li class="conversation-message role-{_escape(role)}{' final-message' if final else ''}{' unsupported-final' if final and unsupported else ''}"
        id="message-{slug}-{index+1}" data-message-index="{index}">
        <div class="message-heading"><strong>{_escape(label)}</strong><a href="#message-{slug}-{index+1}" aria-label="Link to message {index+1}">#{index+1}</a></div>
        {result_id}{content}{''.join(calls)}{error}{extra_html}
        {'<p class="final-label">This is the final recorded answer associated with the report classification. See the classification input limits below.</p>' if final else ''}</li>''')
    absent = ''
    if e['episode']['final_empty']:
        absent = f'''<div class="conversation-ending" id="ending-{slug}"><h4>No final answer was recorded</h4>
        <p>The saved conversation ends with {'a tool request that has no recorded result' if unanswered_calls else 'the tool exchange above'}. The episode reached the configured loop limit.
        Its empty final answer is classified structurally; it is not an LLM judgment of a missing statement.</p></div>'''
    target = f'message-{slug}-{final_index+1}' if not e['episode']['final_empty'] and final_index is not None else f'ending-{slug}'
    return f'''<section class="full-conversation" aria-labelledby="conversation-{slug}">
    <div class="conversation-intro"><div><p class="eyebrow">COMPLETE SAVED CONVERSATION</p>
    <h4 id="conversation-{slug}">Follow every message and tool call</h4>
    <p>{len(messages)} saved messages · {len(requested_calls)} requested tool calls · {len(tool_results)} recorded tool results.
    Messages appear in their recorded order. Long tool outputs can be expanded in full.</p></div>
    <a class="text-link" href="#{target}">Jump to the final behavior ↓</a></div>
    <ol class="conversation-thread">{''.join(entries)}</ol>{absent}{_classification(e)}
    </section>'''


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
            probe = f'''<details class="probe-example"><summary>Follow-up: the same episode, after the cap</summary><p><strong>Stage A · tools available.</strong> {esc(p['stage_a_prompt'])}<br>{esc(p['stage_a_behavior'])}</p><p><strong>Stage B · {esc(p['stage_b_change'])}</strong><br>{esc(p['stage_b_prompt'])}</p><blockquote class="response">{esc(p['stage_b_answer'])}</blockquote><p>Full captured stage-B answer. {esc(p['label'])}. {esc(p['environment'])} {esc(p['qualification'])}</p><h5>Stage B · saved re-audit votes</h5>{_votes(p.get('reaudit_record'))}<p>This follow-up excerpt is separate from the complete original conversation above; a full continuation transcript is not included here.</p><p>{probe_sources}</p></details>'''
        panels.append(f'''<details class="episode" id="example-{slug}"{' open' if i == 0 else ''}><summary><span>{esc(e['model'])}</span> {esc(e['title'])}</summary><div class="episode-body"><div class="episode-top"><div><span class="eyebrow">{esc(e['model'])} / {esc(e['condition'])}</span><h3>{esc(e['title'])}</h3><p>{esc(e['population'])}</p></div><span class="episode-badge">{esc(e['behavior'])}</span></div><p class="conversation-shortcut"><a href="#conversation-{slug}">Read the complete conversation ↓</a> · <a href="#classification-{slug}">Inspect the recorded classification ↓</a></p><div class="episode-columns"><div class="trace-block"><p class="eyebrow">01 / THE USER'S REQUEST · VERBATIM</p><p class="request">“{esc(e['request'])}”</p><p class="eyebrow">02 / TOOL SEQUENCE · ABRIDGED SUMMARY</p><ol class="trace-steps">{steps}</ol></div><div class="trace-block"><p class="eyebrow">03 / AGENT RESPONSE · {esc(e['response_kind'])}</p><{response_tag} class="{response_class}">{esc(e['response'])}</{response_tag}><div class="outcome"><strong>04 / Environment outcome</strong>{esc(e['environment'])}</div><p class="published-label"><strong>Published classification</strong><br>{esc(e['label'])}</p><p class="interpretation">{esc(e['interpretation'])}</p></div></div>{_conversation(e)}{probe}<div class="episode-provenance"><p><strong>Reading boundary:</strong> {esc(e['qualification'])}</p><p>Episode <code>{esc(e['id'])}</code></p><a href="data/episodes/{slug}.json">Download saved conversation & source records ↗</a>{sources}</div></div></details>''')
    examples = '<div class="example-lab"><nav class="example-nav" aria-label="Choose a real episode">' + ''.join(navigation) + '</nav>' + ''.join(panels) + '</div>'
    examples = re.sub(r'[ \t]+\n', '\n', examples)
    walkthrough = (src / 'walkthrough.html').read_text()
    spoken_words = sum(len(t.split()) for t in re.findall(r'<p data-spoken>(.*?)</p>', walkthrough))
    walkthrough = walkthrough.replace('{{SPOKEN_WORDS}}', str(spoken_words))
    return {'EXAMPLES': examples, 'WALKTHROUGH': walkthrough}
