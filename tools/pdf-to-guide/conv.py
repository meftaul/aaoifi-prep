import pymupdf, re, json, html, sys, os

SRC, SLUG, OUTDIR = sys.argv[1], sys.argv[2], sys.argv[3]
SKIP = set(int(x) for x in sys.argv[4].split(',')) if len(sys.argv) > 4 and sys.argv[4] else set()
doc = pymupdf.open(SRC)
os.makedirs(f'{OUTDIR}/img', exist_ok=True)

def foreign(font):
    return 'Bn' in font or 'Naskh' in font or 'NotoAr' in font

def is_sans(font):
    return font.startswith(('GSans', 'NSans', 'Inter', 'BnSans', 'NotoBn')) or 'Sans' in font

def bold(font):
    return 'Bold' in font or 'Semi' in font

LABEL_COLORS = {
    'navy': [0x12365a, 0x1e3a5f], 'research': [0x0f6e64, 0x0f766e], 'bangla': [0x3e6f22, 0x166534],
    'example': [0xa8741a, 0x92400e], 'warn': [0xa12d2d, 0x991b1b], 'tip': [0x5a3d8a, 0x5b21b6],
    'evidence': [0x7a5a12, 0x854d0e], 'neutral': [0x5b6475, 0x374151],
}
def color_kind(c):
    for k, v in LABEL_COLORS.items():
        if c in v: return k
    return None

placeholders = []  # dicts

def ph(kind, page, rect, text):
    pid = f'{kind}{len(placeholders)+1:03d}'
    placeholders.append({'id': pid, 'page': page, 'rect': [round(x, 1) for x in rect], 'garbled': text})
    return f'⟦{pid}⟧'

class Span:
    def __init__(s, d, links):
        s.text = d['text']; s.font = d['font']; s.size = d['size']; s.color = d['color']
        s.bbox = pymupdf.Rect(d['bbox']); s.base = d['origin'][1]
        s.href = None
        for l in links:
            if l.get('uri') and pymupdf.Rect(l['from']).intersects(s.bbox) and (pymupdf.Rect(l['from']) & s.bbox).get_area() > 0.3 * s.bbox.get_area():
                s.href = l['uri']
        s.fg = foreign(s.font)

def make_lines(spans):
    spans = sorted(spans, key=lambda s: (s.base, s.bbox.x0))
    lines = []
    for s in spans:
        for L in lines:
            if abs(L['base'] - s.base) < 3.5 and (s.size < L['size'] * 1.6 and L['size'] < s.size * 1.6):
                L['spans'].append(s); break
        else:
            lines.append({'base': s.base, 'size': s.size, 'spans': [s]})
    for L in lines:
        L['spans'].sort(key=lambda s: s.bbox.x0)
        L['rect'] = pymupdf.Rect(L['spans'][0].bbox)
        for s in L['spans']: L['rect'] |= s.bbox
        main = [s for s in L['spans'] if s.text.strip()]
        L['main'] = max(main, key=lambda s: len(s.text)) if main else L['spans'][0]
        ns = []
        for sp in L['spans']:
            if ns and not ns[-1].fg and not sp.fg and sp.bbox.x0 - ns[-1].bbox.x1 > 12 and ns[-1].text.strip() and sp.text.strip():
                g = Span({'text': ': ' if ('Bold' in ns[-1].font or 'Semi' in ns[-1].font) and not ns[-1].text.rstrip().endswith((':', '.')) else ' ', 'font': 'GSerif', 'size': ns[-1].size, 'color': 0, 'bbox': tuple(ns[-1].bbox), 'origin': (0, ns[-1].base)}, [])
                ns.append(g)
            ns.append(sp)
        L['spans'] = ns
        vis = [x for x in L['spans'] if x.text.strip()]
        L['kv'] = len(vis) > 1 and ('Bold' in vis[0].font or 'Semi' in vis[0].font) and vis[1].bbox.x0 - vis[0].bbox.x1 > 12
        L['text'] = ''.join(s.text for s in L['spans'])
    lines.sort(key=lambda L: (L['base'], L['rect'].x0))
    return lines

def classify(L, inbox):
    m = L['main']; f, sz = m.font, m.size
    t = L['text'].strip()
    if re.match(r'^(Figure|Fig\.)\s*\d', t): return 'figcap'
    if is_sans(f) and bold(f) and sz >= 18: return 'h1'
    if is_sans(f) and bold(f) and 12.5 <= sz < 18 and not m.fg: return 'h2'
    if m.fg and bold(f) and 12 <= sz < 14: return 'sub'
    if 'NotoBn' in f and 12 <= sz < 14: return 'sub'
    if re.match(r'^(C\s?HAPTER\s*\d+|A\s?PPENDIX|R\s?EFERENCE)$', t) and is_sans(f) and bold(f): return 'eyebrow'
    if is_sans(f) and bold(f) and re.match(r'^Table [A-Z0-9]', t): return 'tcap'
    f0 = next((x for x in L['spans'] if x.text.strip()), m)
    if inbox and is_sans(f0.font) and bold(f0.font) and f0.size < 8.7 and f0.color != 0xffffff and (f0.fg or f0.text == f0.text.upper()): return 'label'
    if is_sans(f) and bold(f) and 9.8 <= sz < 12.5 and not inbox: return 'h3'
    if is_sans(f) and bold(f) and 9.8 <= sz < 12.5 and inbox: return 'h4'
    return 'p'

def inline(spans, page):
    out = []
    i = 0
    n = len(spans)
    while i < n:
        s = spans[i]
        if s.fg:
            j = i; rect = pymupdf.Rect(s.bbox); txt = ''
            while j < n and (spans[j].fg or (not spans[j].text.strip()) or (re.fullmatch(r'[\s()\[\],.:;—–\-?!"\'0-9/%]+', spans[j].text) and j + 1 < n and spans[j+1].fg)):
                rect |= spans[j].bbox; txt += spans[j].text; j += 1
            kind = 'ar' if any('Naskh' in x.font or 'NotoAr' in x.font for x in spans[i:j]) else 'bn'
            lead = ' ' if txt.startswith(' ') else ''
            trail = ' ' if txt.endswith(' ') else ''
            out.append(lead + ph(kind, page, rect, txt.strip()) + trail)
            i = j; continue
        t = html.escape(s.text)
        if 'Bold' in s.font or ('Semi' in s.font and not is_sans(s.font)): t = f'<strong>{t}</strong>' if t.strip() else t
        if 'Italic' in s.font or 'Oblique' in s.font: t = f'<em>{t}</em>' if t.strip() else t
        out.append((t, s))
        i += 1
    # merge links
    res = []
    for o in out:
        if isinstance(o, str): res.append(o); continue
        t, s = o
        href = s.href
        if not href and s.color in (0x1a5aa6, 0x1d4ed8, 0x2563eb, 0x0f5d8a) and re.search(r'[a-z]\.[a-z]', s.text):
            href = None  # handled after merge
        res.append(t if not (s.color in (0x1a5aa6, 0x0f5d8a) or href) else ('\x01' + (href or '') + '\x02' + t + '\x03'))
    h = ''.join(res)
    h = re.sub(r'</strong><strong>', '', h); h = re.sub(r'</em><em>', '', h)
    # merge adjacent link segments
    def linkfix(hh):
        parts = re.split(r'(\x01[^\x02]*\x02.*?\x03)', hh)
        out2 = []; cur = None
        for p in parts:
            m = re.match(r'\x01([^\x02]*)\x02(.*?)\x03$', p, re.S)
            if m:
                if cur and (cur[0] == m.group(1) or not m.group(1) or not cur[0]):
                    cur = (cur[0] or m.group(1), cur[1] + m.group(2))
                else:
                    if cur: out2.append(cur)
                    cur = (m.group(1), m.group(2))
            elif p == '' or (p.isspace() and cur):
                if cur and p: cur = (cur[0], cur[1] + p)
            else:
                if cur: out2.append(cur); cur = None
                out2.append(p)
        if cur: out2.append(cur)
        r = ''
        for o in out2:
            if isinstance(o, tuple):
                href, txt = o
                plain = re.sub(r'<[^>]+>', '', txt).strip()
                if not href:
                    if re.match(r'^[\w.-]+\.[a-z]{2,}(/\S*)?$', plain.replace(' ', '')): href = 'https://' + plain.replace(' ', '')
                if href: r += f'<a href="{html.escape(href)}" target="_blank" rel="noopener">{txt}</a>'
                else: r += txt
            else: r += o
        return r
    return linkfix(h)

def paragraphs(lines, page, inbox):
    blocks = []
    prev = None
    for L in lines:
        k = classify(L, inbox)
        t = L['text'].strip()
        if not t: continue
        bullet = re.match(r'^(•|·|–|\d{1,2}\.|\([a-z0-9]\)|[a-z]\))\s', t + ' ') and L['spans'][0].text.strip() in ('•', '·', '–') or re.match(r'^\d{1,2}\.$', L['spans'][0].text.strip())
        newp = True
        vis0 = next((x for x in L['spans'] if x.text.strip()), None)
        qstart = vis0 is not None and 'Bold' in vis0.font and re.match(r'^\d{1,2}\.\s', vis0.text.strip() + ' ') and prev is not None and not any('Bold' in x.font for x in prev['lines'][-1]['spans'][-1:])
        if prev is not None and k == prev['k'] and not bullet and not L.get('kv') and not qstart:
            gap = L['base'] - prev['last']
            if k in ('p', 'h1', 'h2', 'h3', 'sub', 'label', 'h4', 'figcap', 'tcap') and gap < L['size'] * 1.75 and abs(L['size'] - prev['size']) < 1.2:
                # continuation of list item must be indented at/after item text
                newp = False
        if newp:
            prev = {'k': k, 'lines': [L], 'last': L['base'], 'size': L['size'], 'bullet': bool(bullet), 'x0': L['rect'].x0}
            blocks.append(prev)
        else:
            prev['lines'].append(L); prev['last'] = L['base']
    out = []
    for b in blocks:
        spans = []
        for L in b['lines']:
            if spans and not spans[-1].text.endswith((' ', '-', '—', '/')) and not L['spans'][0].text.startswith(' '):
                sp = Span({'text': ' ', 'font': spans[-1].font, 'size': spans[-1].size, 'color': spans[-1].color, 'bbox': spans[-1].bbox, 'origin': (0, spans[-1].base)}, [])
                sp.fg = spans[-1].fg and L['spans'][0].fg
                spans.append(sp)
            spans.extend(L['spans'])
        marker = None
        if b['bullet']:
            first = spans[0].text.strip()
            marker = 'ol' if re.match(r'^\d', first) else 'ul'
            spans = spans[1:]
            while spans and not spans[0].text.strip(): spans = spans[1:]
        rect = pymupdf.Rect(b['lines'][0]['rect'])
        for L in b['lines']: rect |= L['rect']
        fgchars = sum(len(s.text.strip()) for s in spans if s.fg)
        allchars = sum(len(s.text.strip()) for s in spans) or 1
        if fgchars / allchars > 0.45 and b['k'] in ('p', 'sub', 'label', 'h4'):
            kind = 'ar' if any('Naskh' in x.font or 'NotoAr' in x.font for x in spans) else 'bn'
            content = ph(kind, page, rect, ''.join(s.text for s in spans))
        else:
            content = inline(spans, page)
        out.append({'t': b['k'], 'html': content.strip(), 'list': marker, 'y': rect.y0, 'x': rect.x0, 'size': b['size'], 'page': page})
    return out

def fill_light(f):
    return f and min(f) > 0.84 and not all(x > 0.995 for x in f)

class Row:
    def __init__(s, cells): s.cells = cells
class Tab:
    def __init__(s, bbox, rows, head): s.bbox = bbox; s.rows = rows; s.head = head

def cluster(vals, tol):
    vals = sorted(vals); out = []
    for v in vals:
        if out and v - out[-1][-1] <= tol: out[-1].append(v)
        else: out.append([v])
    return [sum(c) / len(c) for c in out]

def detect_tables(drawings, raw):
    segs = []; darks = []
    for d in drawings:
        f = d.get('fill'); r = pymupdf.Rect(d['rect'])
        if f and max(f) < 0.45 and 10 < r.height < 70 and r.width > 15: darks.append(r)
        if d['type'] == 's':
            for it in d['items']:
                if it[0] == 'l':
                    p1, p2 = it[1], it[2]
                    if abs(p1.y - p2.y) < 0.6 and abs(p1.x - p2.x) > 15:
                        segs.append((min(p1.x, p2.x), max(p1.x, p2.x), p1.y))
    ys = cluster([s[2] for s in segs], 1.0)
    groups = []
    for y in ys:
        ss = [s for s in segs if abs(s[2] - y) <= 1.2]
        groups.append({'y': y, 'x0': min(s[0] for s in ss), 'x1': max(s[1] for s in ss), 'xs': [v for s in ss for v in (s[0], s[1])]})
    tabs = []; cur = []
    for g in groups:
        newhead = bool(cur) and sum(r.width for r in darks if r.y0 > cur[-1]['y'] - 1 and r.y1 <= g['y'] + 2.5) > 0.6 * (g['x1'] - g['x0'])
        if cur and not newhead and g['y'] - cur[-1]['y'] < 140 and abs(g['x0'] - cur[-1]['x0']) < 4 and abs(g['x1'] - cur[-1]['x1']) < 4:
            cur.append(g)
        else:
            if cur: tabs.append(cur)
            cur = [g]
    if cur: tabs.append(cur)
    out = []
    for t in tabs:
        x0, x1 = t[0]['x0'], t[0]['x1']
        ly = [g['y'] for g in t]
        hd = [r for r in darks if ly[0] - 70 < r.y1 < ly[0] + 2.5 and r.x0 >= x0 - 3 and r.x1 <= x1 + 3]
        if hd and sum(r.width for r in hd) < 0.6 * (x1 - x0): hd = []
        if hd:
            top = min(r.y0 for r in hd); head = True
            hb = max(r.y1 for r in hd)
            if hb < ly[0] - 2.5: ly = [hb] + ly
        else:
            if len(t) < 2: continue
            gaps = [b - a for a, b in zip(ly, ly[1:])]
            top = ly[0] - min(gaps); head = False
            ly = ly
        if len(t) < 2 and not hd: continue
        bounds = [top] + ly
        cx0 = [x0] + [c for c in cluster([v for g in t for v in g['xs']] + [v for r in hd for v in (r.x0, r.x1)], 2.5) if x0 + 4 < c < x1 - 4]
        below = sorted([sp for sp in raw if sp.text.strip() and sp.bbox.y0 > ly[-1] - 1 and sp.bbox.x0 >= x0 and sp.bbox.x1 <= x1 + 2], key=lambda sp: sp.bbox.y0)
        if len(cx0) > 1 and below and below[0].bbox.y0 - ly[-1] < 14:
            first = [sp for sp in below if abs(sp.base - below[0].base) < 2]
            starts = [any(abs(sp.bbox.x0 - (c + 6)) < 6 for sp in first) for c in cx0[:2]]
            if all(starts):
                bot = ly[-1]
                for sp in below:
                    if sp.bbox.y0 - bot < 9 or sp.bbox.y0 < bot: bot = max(bot, sp.bbox.y1)
                    else: break
                bounds.append(bot + 2); ly = ly + [bot + 2]
        xs = [v for g in t for v in g['xs']] + [v for r in hd for v in (r.x0, r.x1)]
        cols = [c for c in cluster(xs, 2.5) if x0 + 4 < c < x1 - 4]
        cx = [x0] + cols + [x1]
        rows = []
        for a, b in zip(bounds, bounds[1:]):
            rows.append(Row([pymupdf.Rect(cx[i], a, cx[i + 1], b) for i in range(len(cx) - 1)]))
        def hastext(rr): return any(sp.size >= 7.9 and rr.contains(pymupdf.Point((sp.bbox.x0+sp.bbox.x1)/2, (sp.bbox.y0+sp.bbox.y1)/2)) for sp in raw)
        full = pymupdf.Rect(x0, top, x1, ly[-1])
        if sum(1 for r in rows if hastext(pymupdf.Rect(x0, r.cells[0].y0, x1, r.cells[0].y1))) < max(1, len(rows) * 0.6): continue
        out.append(Tab(full, rows, head))
    return out

def process_page(pno):
    page = doc[pno]
    links = page.get_links()
    raw = []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                sp = Span(s, links)
                if sp.bbox.y0 < 44 or sp.bbox.y0 > 795: continue
                raw.append(sp)
    drawings = page.get_drawings()
    tables = detect_tables(drawings, raw)
    tbboxes = []
    # figures
    figs = []
    caps = [s for s in raw if re.match(r'^(Figure|Fig\.)\s*\d', s.text.strip()) and s.size < 9.5]
    for c in caps:
        top = c.bbox.y0
        region = None
        def isfig(d):
            n = len(d['items'])
            if d['type'] == 'fs': return True
            if d['type'] == 'f' and n in (3, 8): return True
            if d['type'] == 's':
                r = d['rect']; return not (r.height < 0.6 and r.width > 60)
            return False
        tbs0 = [t.bbox for t in tables]
        cands = [pymupdf.Rect(d['rect']) for d in drawings if (isfig(d) or (d['type'] == 'f' and d['rect'].width < 470 and not any(tb.intersects(d['rect']) for tb in tbs0))) and d['rect'].y1 <= c.bbox.y0 + 1]
        items = sorted(cands, key=lambda r: -r.y1)
        cur_top = top
        for r in items:
            if r.y1 >= cur_top - 45 and r.y0 < cur_top:
                region = [r.x0, r.y0, r.x1, r.y1] if region is None else [min(region[0], r.x0), min(region[1], r.y0), max(region[2], r.x1), max(region[3], r.y1)]
                cur_top = min(cur_top, r.y0)
        if region:
            y0, y1 = region[1], region[3]
            for s2 in sorted(raw, key=lambda q: -q.bbox.y0):
                cy = (s2.bbox.y0 + s2.bbox.y1) / 2
                if y0 - 4 <= cy <= c.bbox.y0 - 1 or (is_sans(s2.font) and s2.size < 9.5 and y0 - 22 <= cy < y0 and s2.bbox.y1 < c.bbox.y0):
                    y0 = min(y0, s2.bbox.y0); y1 = max(y1, s2.bbox.y1)
            region = pymupdf.Rect(page.rect.x0 + 46, y0, page.rect.x1 - 46, y1)
        if region:
            region = pymupdf.Rect(region.x0 - 6, region.y0 - 6, region.x1 + 6, region.y1 + 4)
            figs.append((region, c))
    figrects = [f[0] for f in figs]
    tables = [t for t in tables if not any((fr & t.bbox).get_area() > 0.3 * t.bbox.get_area() for fr in figrects)]
    tbboxes = [pymupdf.Rect(t.bbox) for t in tables]
    # boxes
    boxes = []
    for d in drawings:
        f = d.get('fill'); r = pymupdf.Rect(d['rect'])
        if fill_light(f) and (r.width > 300 and r.height > 18 or r.width > 150 and r.height > 30) and not any(tb.contains(r) or (tb & r).get_area() > 0.8 * r.get_area() for tb in tbboxes) and not any(fr.contains(r) for fr in figrects):
            if not any(abs(b.x0 - r.x0) < 2 and abs(b.y0 - r.y0) < 2 and abs(b.y1 - r.y1) < 2 for b in boxes):
                boxes.append(r)
    # drop boxes that are contained in other boxes (keep outer)
    boxes = [b for b in boxes if not any(o != b and o.contains(b) for o in boxes)]
    # assign spans
    def center(s): return pymupdf.Point((s.bbox.x0 + s.bbox.x1) / 2, (s.bbox.y0 + s.bbox.y1) / 2)
    used = set()
    figitems = []
    for i, (r, c) in enumerate(figs):
        name = f'{SLUG}-p{pno+1:02d}-{i+1}.png'
        pix = page.get_pixmap(clip=r, dpi=200)
        pix.save(f'{OUTDIR}/img/{name}')
        for s in raw:
            if r.contains(center(s)): used.add(id(s))
        figitems.append({'r': r, 'img': name, 'w': round(r.width), 'h': round(r.height)})
    def table_html(t, spans_avail):
        rows = []
        for ri, row in enumerate(t.rows):
            cells = []
            for cb in row.cells:
                if cb is None: continue
                cr = pymupdf.Rect(cb)
                inside = [s for s in spans_avail if cr.contains(center(s)) and id(s) not in used]
                for s in inside: used.add(id(s))
                ps = paragraphs(make_lines(inside), pno + 1, True)
                cell = ''
                for p in ps:
                    if p['list']: cell += f'<div class="li">{p["html"]}</div>'
                    else: cell += (f'<p>{p["html"]}</p>' if len(ps) > 1 else p['html'])
                head = ri == 0 and t.head
                cells.append((head, cell, cr.width))
            rows.append(cells)
        return rows
    def build(container_rect, inbox):
        items = []
        for ti, t in enumerate(tables):
            tb = tbboxes[ti]
            if container_rect.contains(pymupdf.Point(tb.x0 + 2, tb.y0 + 2)) and (inbox or not any(b.contains(tb) for b in boxes)):
                items.append({'t': 'table', 'rows': table_html(t, raw), 'y': tb.y0})
        for f in figitems:
            if container_rect.contains(pymupdf.Point(f['r'].x0 + 8, f['r'].y0 + 8)) and (inbox or not any(b.contains(f['r']) for b in boxes)):
                items.append({'t': 'figure', 'img': f['img'], 'y': f['r'].y0, 'w': f['w'], 'h': f['h'], 'rect': list(f['r'])})
        if not inbox:
            for b in boxes:
                sub = build(b, True)
                lab = next((x for x in sub if x['t'] == 'label'), None)
                kind = None
                if True:
                    for s in raw:
                        if b.contains(center(s)) and is_sans(s.font) and bold(s.font) and s.size < 8.7 and s.color != 0xffffff and color_kind(s.color):
                            kind = color_kind(s.color); break
                items.append({'t': 'box', 'kind': kind, 'items': sub, 'y': b.y0, 'rect': list(b)})
        sp = [s for s in raw if id(s) not in used and container_rect.contains(center(s)) and (inbox or not any(b.contains(center(s)) for b in boxes))]
        for s in sp: used.add(id(s))
        items += paragraphs(make_lines(sp), pno + 1, inbox)
        items.sort(key=lambda x: x['y'])
        return items
    return build(page.rect, False)

allitems = []
for pno in range(len(doc)):
    if pno + 1 in SKIP: continue
    its = process_page(pno)
    if its: its[0]['pagestart'] = True
    for it in its: it['pg'] = pno + 1
    allitems += its

json.dump({'items': allitems}, open(f'{OUTDIR}/{SLUG}.items.json', 'w'), ensure_ascii=False, indent=0)
json.dump(placeholders, open(f'{OUTDIR}/{SLUG}.ph.json', 'w'), ensure_ascii=False, indent=1)
print(len(allitems), 'items', len(placeholders), 'placeholders')
