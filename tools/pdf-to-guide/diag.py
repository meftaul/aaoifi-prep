"""Extract each figure of a study-guide PDF as vector data (shapes + text) for D3.

Usage: python3 diag.py <pdf> <slug>   (reads out/<slug>.items.json, writes out/<slug>.diagrams.json)
"""
import colorsys, json, re, sys
import pymupdf

SRC, SLUG = sys.argv[1], sys.argv[2]
doc = pymupdf.open(SRC)
items = json.load(open(f'out/{SLUG}.items.json'))['items']


def tone(c):
    """Map a PDF colour to a theme token so diagrams follow light/dark mode."""
    if c is None:
        return None
    if isinstance(c, int):
        c = ((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255)
    h, l, s = colorsys.rgb_to_hls(*c)
    if l > 0.985:
        return 'paper'
    if s < 0.12 or (l < 0.3 and s < 0.25):
        if l > 0.85:
            return 'gray-bg'
        return 'muted' if l > 0.3 else 'ink'
    deg = h * 360
    if deg < 22 or deg >= 330: hue = 'red'
    elif deg < 55: hue = 'amber'
    elif deg < 150: hue = 'green'
    elif deg < 190: hue = 'teal'
    elif deg < 255: hue = 'navy'
    else: hue = 'purple'
    return f'{hue}-bg' if l > 0.8 else hue


def fmt(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


def path_d(dr, ox, oy):
    d = []
    cur = None
    for it in dr['items']:
        kind = it[0]
        if kind == 're':
            r = it[1]
            d.append(f'M{fmt(r.x0-ox)} {fmt(r.y0-oy)}h{fmt(r.width)}v{fmt(r.height)}h{fmt(-r.width)}Z')
            cur = None
            continue
        if kind == 'qu':
            q = it[1]
            pts = [q.ul, q.ur, q.lr, q.ll]
            d.append('M' + 'L'.join(f'{fmt(p.x-ox)} {fmt(p.y-oy)}' for p in pts) + 'Z')
            cur = None
            continue
        pts = it[1:]
        if cur is None or abs(cur.x - pts[0].x) > 0.05 or abs(cur.y - pts[0].y) > 0.05:
            d.append(f'M{fmt(pts[0].x-ox)} {fmt(pts[0].y-oy)}')
        if kind == 'l':
            d.append(f'L{fmt(pts[1].x-ox)} {fmt(pts[1].y-oy)}')
        elif kind == 'c':
            d.append('C' + ' '.join(f'{fmt(p.x-ox)} {fmt(p.y-oy)}' for p in pts[1:]))
        cur = pts[-1]
    if dr.get('closePath'):
        d.append('Z')
    return ''.join(d)


def dashes(dr):
    m = re.findall(r'[\d.]+', (dr.get('dashes') or '').split(']')[0])
    vals = [float(x) for x in m]
    return ' '.join(fmt(v) for v in vals) if vals and any(vals) else None


def bars_spec(page, region):
    """Figure 6.2 is a real bar chart: rebuild it from its numbers."""
    return {
        'type': 'bars',
        'w': round(region.width), 'h': round(region.height),
        'groups': ['BDT 5,000', 'BDT 10,000', 'BDT 20,000', 'BDT 50,000'],
        'series': [
            {'name': 'Flat fee BDT 150 — allowed (4/5/2)', 'tone': 'teal', 'values': [150, 150, 150, 150]},
            {'name': '2% of amount — not allowed', 'tone': 'red', 'values': [100, 200, 400, 1000]},
        ],
        'yLabel': 'Fee (BDT)',
        'xLabel': 'Cash withdrawn (the Qard amount)',
    }


out = {}
for it in items:
    if it['t'] != 'figure':
        continue
    name = it['img'].rsplit('.', 1)[0]
    page = doc[it['pg'] - 1]
    region = pymupdf.Rect(it['rect'])
    if name == 'ss02-p35-1':
        out[name] = bars_spec(page, region)
        continue
    ox, oy = region.x0, region.y0
    shapes = []
    for dr in page.get_drawings():
        r = dr['rect']
        c = pymupdf.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
        if not region.contains(c) or r.width > region.width * 0.97:
            continue
        lineonly = all(i[0] == 'l' for i in dr['items']) and len(dr['items']) == 1
        fill = None if lineonly else tone(dr.get('fill'))
        stroke = tone(dr.get('color')) if dr['type'] in ('s', 'fs') else None
        if not fill and not stroke:
            continue
        s = {'d': path_d(dr, ox, oy)}
        if fill: s['fill'] = fill
        if stroke:
            s['stroke'] = stroke
            s['sw'] = round(dr.get('width') or 1, 2)
            if dashes(dr): s['dash'] = dashes(dr)
        shapes.append(s)
    # text: merge spans that share a baseline and touch horizontally
    spans = []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for sp in l['spans']:
                bb = pymupdf.Rect(sp['bbox'])
                if sp['text'].strip() == '' and not spans: continue
                if region.contains(pymupdf.Point((bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2)):
                    spans.append((sp, bb))
    spans.sort(key=lambda x: (round(x[0]['origin'][1]), x[1].x0))
    lines = []
    for sp, bb in spans:
        base = sp['origin'][1]
        L = next((L for L in lines if abs(L['base'] - base) < 1.5 and bb.x0 - L['x1'] < 4 and bb.x0 >= L['x0'] - 1), None)
        if L is None:
            L = {'base': base, 'x0': bb.x0, 'x1': bb.x1, 'size': sp['size'], 'spans': []}
            lines.append(L)
        gap = bb.x0 - L['x1']
        L['x1'] = max(L['x1'], bb.x1)
        part = {'t': sp['text']}
        if L['spans'] and gap > 1 and not L['spans'][-1]['t'].endswith(' ') and not part['t'].startswith(' '):
            part['t'] = ' ' + part['t']
        if 'Bold' in sp['font'] or 'Semi' in sp['font']: part['b'] = 1
        tn = tone(sp['color'])
        if tn: part['c'] = tn
        L['spans'].append(part)
    texts = []
    for L in lines:
        parts = []
        for p in L['spans']:
            if parts and parts[-1].get('b') == p.get('b') and parts[-1].get('c') == p.get('c'):
                parts[-1]['t'] += p['t']
            else:
                parts.append(dict(p))
        if not ''.join(p['t'] for p in parts).strip(): continue
        parts[0]['t'] = parts[0]['t'].lstrip(); parts[-1]['t'] = parts[-1]['t'].rstrip()
        texts.append({'x': round((L['x0'] + L['x1']) / 2 - ox, 1), 'y': round(L['base'] - oy, 1), 's': round(L['size'], 1), 'p': parts})
    out[name] = {'type': 'vector', 'w': round(region.width, 1), 'h': round(region.height, 1), 'shapes': shapes, 'texts': texts}

json.dump(out, open(f'out/{SLUG}.diagrams.json', 'w'), ensure_ascii=False)
print(SLUG, len(out), 'diagrams', sum(len(v.get('shapes', [])) for v in out.values()), 'shapes')
