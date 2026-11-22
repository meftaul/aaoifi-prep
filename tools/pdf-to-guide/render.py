import json, re, sys, html, os

SLUG, OUT, FIXES = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(f'out/{SLUG}.items.json'))['items']
phs = {p['id']: p for p in json.load(open(f'out/{SLUG}.ph.json'))}
fixes = json.load(open(FIXES)) if os.path.exists(FIXES) else {}
missing = []

def subst(h):
    def rep(m):
        pid = m.group(1)
        g = phs[pid]['garbled']
        if g in fixes:
            v = fixes[g]
            if v.startswith('!'): return v[1:]
            lang = 'ar' if pid.startswith('ar') else 'bn'
            return f'<span lang="{lang}"{" dir=\"rtl\"" if lang == "ar" else ""}>{v}</span>'
        missing.append(pid)
        return f'<span class="garbled" title="{pid}">[{pid}] {html.escape(phs[pid]["garbled"])}</span>'
    h = h.replace('⟧·⟦', '⟧⟦')
    return re.sub(r'⟦(\w+)⟧', rep, h)

def strip_strong(h):
    return re.sub(r'</?strong>', '', h)

END = re.compile(r'([.?!:;)"”\]]|</a>|</strong>\.|⟧)\s*$')

def merge(items):
    out = []
    for it in items:
        if it['t'] == 'box':
            if it['items'] and all(x['t'] in ('h1','h2','h3','sub','eyebrow') for x in it['items']):
                for x in it['items']:
                    if it.get('pagestart'): x['pagestart'] = True
                out.extend(it['items']); continue
            it['items'] = merge(it['items'])
        if out and it.get('pagestart'):
            prev = out[-1]
            if it['t'] == 'p' and prev['t'] == 'p' and not END.search(prev['html']) and abs(prev['size'] - it['size']) < 1 and not it.get('list') and not re.match(r'<strong>\d{1,2}\. ', it['html']):
                prev['html'] += ' ' + it['html']; continue
            if it['t'] == 'box' and prev['t'] == 'box' and (not it['items'] or it['items'][0]['t'] != 'label') and (it.get('kind') in (None, prev.get('kind'))):
                a, b = prev['items'], it['items']
                if a and b and a[-1]['t'] == 'p' and b[0]['t'] == 'p' and not END.search(a[-1]['html']) and not b[0].get('list'):
                    a[-1]['html'] += ' ' + b[0]['html']; b = b[1:]
                a += b; continue
            if it['t'] == 'table' and prev['t'] == 'table':
                rows = it['rows']
                newhead = rows and rows[0] and rows[0][0][0]
                samehead = newhead and prev['rows'] and [c[1] for c in rows[0]] == [c[1] for c in prev['rows'][0]]
                if not newhead or samehead:
                    if samehead: rows = rows[1:]
                    prev['rows'] += rows; continue
        out.append(it)
    return out

def slugify(t):
    t = html.unescape(re.sub(r'<[^>]+>', '', t)).replace("'", '')
    t = re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
    return t[:60]

toc = []
ids = set()
def hid(t):
    base = slugify(t) or 'sec'
    i = base; n = 2
    while i in ids: i = f'{base}-{n}'; n += 1
    ids.add(i); return i

def table(rows):
    h = '<div class="table-wrap"><table>'
    for ri, row in enumerate(rows):
        if not row: continue
        head = all(c[0] for c in row) and ri == 0
        tag = 'th' if head else 'td'
        if head: h += '<thead>'
        h += '<tr>' + ''.join(f'<{tag}>{subst(c[1])}</{tag}>' for c in row) + '</tr>'
        if head: h += '</thead>'
    return h + '</table></div>'

def render(items, inbox=False):
    h = ''
    i = 0
    while i < len(items):
        it = items[i]; t = it['t']
        if it.get('list'):
            kind = it['list']
            h += f'<{kind}>'
            while i < len(items) and items[i].get('list') == kind:
                h += f'<li>{subst(items[i]["html"])}</li>'; i += 1
            h += f'</{kind}>'
            continue
        if t == 'h1':
            txt = strip_strong(it['html']); idd = hid(txt)
            toc.append((1, idd, html.unescape(re.sub(r'<[^>]+>', '', txt))))
            h += f'<h2 id="{idd}" class="chapter-title">{subst(txt)}</h2>'
        elif t == 'h2':
            txt = strip_strong(it['html']); idd = hid(txt)
            if not inbox: toc.append((2, idd, html.unescape(re.sub(r'<[^>]+>', '', txt))))
            h += f'<h3 id="{idd}">{subst(txt)}</h3>'
        elif t == 'h3': h += f'<h4>{subst(strip_strong(it["html"]))}</h4>'
        elif t == 'h4': h += f'<h5>{subst(strip_strong(it["html"]))}</h5>'
        elif t == 'sub': h += f'<p class="subtitle">{subst(strip_strong(it["html"]))}</p>'
        elif t == 'eyebrow': h += f'<p class="eyebrow">{subst(strip_strong(it["html"])).replace("C HAPTER", "CHAPTER").replace("A PPENDIX", "APPENDIX").replace("R EFERENCE", "REFERENCE")}</p>'
        elif t == 'label': h += f'<div class="box-label">{subst(strip_strong(it["html"]))}</div>'
        elif t == 'tcap': h += f'<p class="table-caption">{subst(strip_strong(it["html"]))}</p>'
        elif t == 'figcap': h += f'<p class="figcaption">{subst(it["html"])}</p>'
        elif t == 'figure':
            name = it['img'].rsplit('.', 1)[0]
            cap = next((x for x in items[i + 1:i + 2] if x['t'] == 'figcap'), None)
            label = html.escape(re.sub(r'<[^>]+>', '', cap['html'])) if cap else ''
            h += f'<figure class="diagram" data-diagram="{name}" role="img" aria-label="{label}"></figure>'
        elif t == 'table': h += table(it['rows'])
        elif t == 'box':
            if not it['items']: i += 1; continue
            h += f'<aside class="box box-{it.get("kind") or "plain"}">{render(it["items"], True)}</aside>'
        else:
            h += f'<p>{subst(it["html"])}</p>'
        i += 1
    return h

items = merge(d)
body = render(items)
body = body.replace('&#x27;', "'")
diagrams = json.load(open(f'out/{SLUG}.diagrams.json'))
json.dump({'toc': toc, 'html': body, 'diagrams': diagrams}, open(OUT, 'w'), ensure_ascii=False)
print('missing', len(set(missing)), 'len', len(body))
