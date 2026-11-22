import json,sys,os
slug=sys.argv[1]; src=sys.argv[2]
phs={p['id']:p for p in json.load(open(f'out/{slug}.ph.json'))}
fn=f'fixes-{slug}.json'
fx=json.load(open(fn)) if os.path.exists(fn) else {}
new=json.load(open(src))
for k,v in new.items():
    fx[phs[k]['garbled']]=v
json.dump(fx,open(fn,'w'),ensure_ascii=False,indent=1)
print(len(fx))
