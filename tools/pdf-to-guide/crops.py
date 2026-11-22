import json,pymupdf,os
from PIL import Image,ImageDraw,ImageFont
fp='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(fp,22) if os.path.exists(fp) else ImageFont.load_default()
for slug,src in [('ss02','s02.pdf'),('ss03','s03.pdf')]:
  d=pymupdf.open(src); phs=json.load(open(f'out/{slug}.ph.json'))
  seen={}; uniq=[]
  for p in phs:
    if p['garbled'] in seen: continue
    seen[p['garbled']]=p['id']; uniq.append(p)
  dup={p['id']:seen[p['garbled']] for p in phs}
  json.dump(dup,open(f'out/{slug}.dup.json','w'))
  ims=[]
  for p in uniq:
    r=pymupdf.Rect(p['rect']); r=pymupdf.Rect(r.x0-3,r.y0-2,r.x1+3,r.y1+2)
    pix=d[p['page']-1].get_pixmap(clip=r,dpi=150)
    ims.append((p['id'],Image.frombytes('RGB',(pix.width,pix.height),pix.samples)))
  sheets=[[]];h=0
  for pid,im in ims:
    if h+im.height>1500: sheets.append([]);h=0
    sheets[-1].append((pid,im));h+=im.height+14
  for n,sheet in enumerate(sheets,1):
    W=max(i.width for _,i in sheet)+130; H=sum(i.height+14 for _,i in sheet)
    c=Image.new('RGB',(W,H),'white');dr=ImageDraw.Draw(c);y=0
    for pid,i in sheet:
      dr.text((4,y+4),pid,fill='red',font=font);c.paste(i,(125,y));y+=i.height+14
      dr.line((0,y-7,W,y-7),fill='#ccc')
    c.save(f'crops/{slug}-{n:02d}.png')
  print(slug,len(phs),'unique',len(uniq),'sheets',len(sheets))
