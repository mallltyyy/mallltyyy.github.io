# Генерирует страницы-превью для ссылок (WhatsApp/Telegram):
#   p/<key>.html — товар, c/<slug>.html — раздел, og/*.jpg — картинки превью.
# Запуск: python3 tools/build_previews.py  (из корня репозитория)
import json, os, html
from PIL import Image
BASE='https://tehnoodom.github.io/'
TR=dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя',['a','b','v','g','d','e','e','zh','z','i','y','k','l','m','n','o','p','r','s','t','u','f','h','c','ch','sh','sch','','y','','e','yu','ya']))
import re
def slug(c): s=''.join(TR.get(ch,ch) for ch in c.lower()); return re.sub(r'^-|-$','',re.sub(r'[^a-z0-9]+','-',s))
def fmt(n): return f'{n:,}'.replace(',',' ')+' ₽'
def word(n):
    m,h=n%10,n%100
    return 'товар' if m==1 and h!=11 else 'товара' if 2<=m<=4 and not 12<=h<=14 else 'товаров'
t=open('index.html',encoding='utf-8').read().split('\n')
get=lambda pre,off: json.loads(next(l for l in t if l.startswith(pre))[off:].rstrip(';'))
P=get('const P=',8); IMG=get('const IMG=',10); ORDER=get('const ORDER=',12)
for d in ('p','c','og'): os.makedirs(d,exist_ok=True)
def og_img(key,src):
    out=f'og/{key}.jpg'
    if not os.path.exists(out) or os.path.getmtime(out)<os.path.getmtime(src):
        im=Image.open(src).convert('RGB'); im.thumbnail((480,720),Image.LANCZOS); im.save(out,'JPEG',quality=72,optimize=True,progressive=True)
    return BASE+out
def page(path,title,desc,img,target):
    e=lambda s: html.escape(s,quote=True)
    open(path,'w',encoding='utf-8').write(f'''<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="TEHNOODOM">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{img}"><meta property="og:url" content="{BASE}{path}">
<meta property="og:locale" content="ru_RU"><meta name="twitter:card" content="summary_large_image">
<meta http-equiv="refresh" content="0; url=../{target}">
<script>location.replace("../{target}")</script>
<style>body{{background:#0b0b0c;color:#f3f1ec;font-family:system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0}}a{{color:#c9a45c}}</style>
</head><body><p>Открываем <a href="../{target}">{e(title)}</a>…</p></body></html>''')
keep=set()
for p in P:
    name,cat,spec,price,key=p[:5]
    img=og_img(key,IMG[key])
    desc=spec+' · заказ в WhatsApp · TEHNOODOM, Грозный'
    if len(desc)>200: desc=desc[:197].rsplit(' ',1)[0]+'…'
    page(f'p/{key}.html',name+(' — '+fmt(price) if price else ''),desc,img,f'#p={key}'); keep.add(f'p/{key}.html')
cats={}
for p in P: cats.setdefault(p[1],[]).append(p)
for c,items in cats.items():
    s=slug(c); n=len(items)
    lo=min(x[3] for x in items if x[3]) if any(x[3] for x in items) else 0
    desc=f'{n} {word(n)}'+(f' · от {fmt(lo)}' if lo else '')+' · заказ в WhatsApp · TEHNOODOM, Грозный'
    first=sorted(items,key=lambda x:-x[3])[0]
    page(f'c/{s}.html',f'{c} — TEHNOODOM',desc,BASE+f'og/{first[4]}.jpg',f'#c={s}'); keep.add(f'c/{s}.html')
# удалить устаревшие
for d in ('p','c'):
    for f in os.listdir(d):
        if f'{d}/{f}' not in keep: os.remove(f'{d}/{f}')
for f in os.listdir('og'):
    if f!='main.jpg' and f[:-4] not in IMG: os.remove('og/'+f)
print(len(P),'товаров,',len(cats),'разделов')
