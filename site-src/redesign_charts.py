"""Presentation-only figures from frozen tables; no research mutations.

Diagram Design stacked-bar and paired-dot grammar, plus a selection flow.
Desktop and narrow compositions encode identical data at readable sizes.
"""


def build_charts(register, txt, line, rect, dot, C, conduct, errors, NAMES, DISPLAY):
    def pair(wide, narrow, label):
        return ('<div class="chart-wide diagram-container" tabindex="0" role="region" aria-label="' + label + '">' + wide + '</div>'
                '<div class="chart-narrow diagram-container" tabindex="0" role="region" aria-label="' + label + '">' + narrow + '</div>')

    # Independently checked against result records and final cascade label files.
    counts = {
        'gpt-6-luna': (680, 3, 2, 0),
        'glm-5.3-flash': (378, 26, 7, 0),
        'kimi-k3': (408, 52, 8, 5),
        'nemotron': (370, 3, 16, 0),
        'qwen-ablated': (38, 525, 11, 0),
    }
    colors = [C['green'], C['accent'], C['ink'], C['rule']]
    labels = ['Acknowledges', 'No answer at cap', 'Claims success', 'Ambiguous']

    def conduct_svg(narrow):
        w, h = (336, 572) if narrow else (640, 440)
        b = txt(16 if narrow else 24, 28, 'What the user hears after failure', 16, weight=600)
        b += txt(16 if narrow else 24, 49, 'Failed, dosed timeout episodes · p ≥ 75%', 11, fill=C['muted'])
        for i, (model, name) in enumerate(zip(NAMES, DISPLAY)):
            y = 80 + i * (84 if narrow else 60)
            rates = conduct[model]
            n = rates['ack']['n']
            assert sum(counts[model]) == n
            for j, metric in [(0, 'ack'), (1, 'capped'), (2, 'claim')]:
                assert abs(100 * counts[model][j] / n - rates[metric]['value']) <= .051
            x = 16 if narrow else 184
            width = 304 if narrow else 432
            bar_y = y + 12 if narrow else y - 12
            b += txt(16 if narrow else 24, y, name, 13, weight=600)
            b += txt(320 if narrow else 24, y if narrow else y + 18,
                     f'n = {n}', 11, fill=C['muted'], anchor='end' if narrow else 'start')
            cursor = x
            for count, color in zip(counts[model], colors):
                segment = width * count / n
                if count:
                    b += rect(cursor, bar_y, segment, 20, color, color, 0)
                    cursor += segment
            note = (f"Ack {rates['ack']['value']:.1f}% · cap {rates['capped']['value']:.1f}%"
                    f" · claim {rates['claim']['value']:.1f}%")
            b += txt(x, bar_y + 38, note, 11, fill=C['muted'])
            if counts[model][3]:
                b += txt(x, bar_y + 53, 'Ambiguous: 5/473 = 1.1%', 10, fill=C['muted'])
        legend_y = 512 if narrow else 396
        b += line(16 if narrow else 24, legend_y - 20, w - 16, legend_y - 20)
        for i, (label, color) in enumerate(zip(labels, colors)):
            x = (16 + (i % 2) * 164) if narrow else (24 + i * 152)
            y = legend_y + (i // 2) * 24 if narrow else legend_y
            b += rect(x, y - 9, 10, 10, color, color, 0)
            b += txt(x + 16, y, label, 10, fill=C['muted'])
        b += txt(16 if narrow else 24, h - 12,
                 'Bars use counts; rounded rates may not sum to 100%.', 10, fill=C['muted'])
        return register('conduct-overview' + ('-mobile' if narrow else ''), w, h,
                        'Reporting conduct after severe tool failure',
                        'Five models differ in acknowledgment, cap silence, unsupported success claims, and ambiguity among failed dosed timeout episodes in the primary sample.', b)

    def marker(x, y, quiet):
        return (f'<circle cx="{x:.3f}" cy="{y}" r="4" '
                f'fill="{C["accent"] if quiet else C["white"]}" '
                f'stroke="{C["ink"] if quiet else C["muted"]}" stroke-width="1.5"/>')

    def quiet_svg(narrow):
        w, h = (336, 612) if narrow else (640, 456)
        b = txt(16 if narrow else 24, 28, 'Success claims on incomplete tasks', 16, weight=600)
        b += txt(16 if narrow else 24, 49, 'Failed, dosed episodes · assigned p = 50%', 11, fill=C['muted'])
        # Hollow and solid marks preserve the series distinction in greyscale.
        b += marker(24, 70, False) + txt(36, 74, 'Explicit timeout', 11, fill=C['muted'])
        b += marker(188, 70, True) + txt(200, 74, 'Lost response', 11, fill=C['muted'])
        left, right = (24, 312) if narrow else (184, 608)
        top, bottom = (116, 532) if narrow else (108, 376)
        for tick in [0, 25, 50, 75, 100]:
            x = left + (right - left) * tick / 100
            b += line(x, top, x, bottom)
            b += txt(x, bottom + 24, str(tick) + '%', 10, fill=C['muted'], anchor='middle')
        for i, (model, name) in enumerate(zip(NAMES, DISPLAY)):
            y = (132 + i * 88) if narrow else (120 + i * 56)
            b += txt(16 if narrow else 24, y - 26 if narrow else y + 4, name, 13, weight=600)
            a, q = errors[model][0], errors[model][4]
            for r, quiet, offset in [(a, False, -6), (q, True, 8)]:
                cy = y + offset
                color = C['accent'] if quiet else C['muted']
                lo = left + (right - left) * r['lo'] / 100
                hi = left + (right - left) * r['hi'] / 100
                x = left + (right - left) * r['value'] / 100
                b += line(lo, cy, hi, cy, color, 1.5)
                b += line(lo, cy - 3, lo, cy + 3, color)
                b += line(hi, cy - 3, hi, cy + 3, color)
                b += marker(x, cy, quiet)
            b += txt(16 if narrow else 184, y + 34 if narrow else y + 30,
                     f"Timeout {a['value']:.1f}% (n={a['n']})", 11, fill=C['muted'])
            b += txt(320 if narrow else 608, y + 34 if narrow else y + 30,
                     f"Lost {q['value']:.1f}% (n={q['n']})", 11,
                     fill=C['accent'], anchor='end')
        b += txt(16 if narrow else 24, h - 28, 'Whiskers: published 95% Jeffreys intervals.', 11, fill=C['muted'])
        b += txt(16 if narrow else 24, h - 10, 'Model order matches the conduct chart.', 10, fill=C['muted'])
        return register('quiet-comparison' + ('-mobile' if narrow else ''), w, h,
                        'Explicit timeouts versus lost tool responses',
                        'Lost responses have higher observed unsupported-claim rates than timeouts for four of five models, with GLM the exception; intervals and differing failed-episode denominators are shown.', b)

    def probe_svg(narrow):
        w, h = (336, 600) if narrow else (640, 344)
        slug = 'probe-compact' + ('-mobile' if narrow else '')
        b = txt(16 if narrow else 24, 28, 'After silence: ask for an answer', 16, weight=600)
        b += txt(16 if narrow else 24, 49, 'Qwen ablated · clean injected probe subset', 11, fill=C['muted'])
        def node(x, y, width, height, head, sub, focal=False):
            return (rect(x, y, width, height, C['tint'] if focal else C['white'],
                         C['accent'] if focal else C['rule'], 4)
                    + txt(x + 12, y + 25, head, 16, weight=600)
                    + txt(x + 12, y + 46, sub, 11, fill=C['muted']))
        def route(d):
            return f'<path d="{d}" fill="none" stroke="{C["muted"]}" stroke-width="1.5"/>'
        if narrow:
            # Explicitly selected branch; connector widths encode no quantity.
            b += line(168, 136, 168, 168, C['muted'])
            b += line(168, 328, 168, 364, C['muted'])
            b += line(168, 432, 168, 468, C['muted'])
            b += node(16, 72, 304, 64, '819 capped episodes', 'A. User nudge; tools remain available')
            b += rect(16, 168, 304, 160, C['white'], C['rule'], 4)
            b += txt(28, 196, '259 answer the user', 16, weight=600)
            b += txt(28, 216, '31.6% leave the nonresponder branch', 11, fill=C['muted'])
            b += line(28, 232, 308, 232)
            b += txt(28, 260, '560 still give no answer', 16, fill=C['accent'], weight=600)
            b += txt(28, 282, '68.4% resume tool use', 12, fill=C['muted'])
            b += txt(28, 306, 'Only these nonresponders reach stage B.', 11, fill=C['muted'])
            b += node(16, 364, 304, 68, 'B. Tools off; ask directly', '559 answers · 1 length-limit artifact')
            b += node(16, 468, 304, 84, '531 acknowledge non-completion', '95.0% of 559 · 95% interval 92.9–96.6%', True)
            b += txt(16, 578, 'Post-hoc probe; original labels are retained.', 11, fill=C['muted'])
        else:
            # Separate ports: no shared connector segments or hidden traversal.
            b += route('M180 112 H204 Q212 112 212 104 V100 Q212 92 220 92 H240')
            b += route('M180 136 H196 Q204 136 204 144 V200 Q204 208 212 208 H240')
            b += line(412, 208, 448, 208, C['muted'])
            b += line(532, 240, 532, 264, C['muted'])
            b += node(24, 88, 156, 80, '819 capped', 'A. Nudge; tools stay on')
            b += node(240, 64, 172, 64, '259 answer', '31.6% respond to the nudge')
            b += node(240, 176, 172, 64, '560 do not', '68.4% resume tool use', True)
            b += txt(240, 160, 'ONLY NONRESPONDERS CONTINUE', 10, fill=C['muted'])
            b += node(448, 176, 168, 64, 'B. Tools off', '559 answers · 1 artifact')
            b += rect(320, 264, 296, 64, C['tint'], C['accent'], 4)
            b += txt(332, 289, '531 acknowledge non-completion', 16, weight=600)
            b += txt(332, 312, '95.0% of 559 · 95% interval 92.9–96.6%', 11, fill=C['muted'])
            b += txt(24, 292, 'Post-hoc probe.', 11, fill=C['muted'])
            b += txt(24, 310, 'Original labels retained.', 11, fill=C['muted'])
        return register(slug, w, h, 'Silence does not establish inability to report',
                        'Of 819 clean injected Qwen capped episodes, 560 did not answer a user nudge; 559 of those answered with tools removed, including 531 acknowledgments of non-completion.', b)

    return {
        'CONDUCT_OVERVIEW': pair(conduct_svg(False), conduct_svg(True), 'Reporting conduct comparison'),
        'QUIET_COMPARISON': pair(quiet_svg(False), quiet_svg(True), 'Timeout and lost-response comparison'),
        'PROBE_COMPACT': pair(probe_svg(False), probe_svg(True), 'Selected follow-up probe flow'),
    }
