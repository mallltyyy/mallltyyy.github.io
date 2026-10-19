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
# уменьшенные фото для сетки каталога (t/), полные остаются для карточки товара
os.makedirs('t',exist_ok=True)
for _f in set(IMG.values()):
    _o='t/'+_f
    if os.path.exists(_f) and (not os.path.exists(_o) or os.path.getmtime(_o)<os.path.getmtime(_f)):
        _im=Image.open(_f).convert('RGB'); _im.thumbnail((480,960),Image.LANCZOS); _im.save(_o,'WEBP',quality=74,method=6)
for _f in os.listdir('t'):
    if _f not in set(IMG.values()): os.remove('t/'+_f)
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
import seo_pages
keep=seo_pages.build(P,IMG,ORDER,og_img,slug,fmt,word)
cats={}
for p in P: cats.setdefault(p[1],[]).append(p)
# удалить устаревшие
for d in ('p','c'):
    for f in os.listdir(d):
        if f'{d}/{f}' not in keep: os.remove(f'{d}/{f}')
for f in os.listdir('og'):
    if f not in ('main.jpg','rassrochka.jpg') and f[:-4] not in IMG: os.remove('og/'+f)
print(len(P),'товаров,',len(cats),'разделов')

# ---------- Страница «Рассрочка» (rassrochka.html) ----------
from PIL import ImageDraw, ImageFont
src=open('index.html',encoding='utf-8').read()
LOGO=re.search(r'<a class="brand"[^>]*><img src="(data:[^"]+)"',src).group(1)
ICON=re.search(r'<link rel="icon" href="(data:[^"]+)"',src).group(1)
BRN=json.loads(re.search(r'const BRN=(\{.*?\});',src).group(1)) if 'const BRN=' in src else {}
RSMIN=25000
TMR=re.search(r'<!-- Top.Mail.Ru counter -->.*?<!-- /Yandex.Metrika counter -->',src,re.S).group(0)
def og_rs():
    out='og/rassrochka.jpg'
    W,H=1200,630; im=Image.new('RGB',(W,H),(11,11,12)); d=ImageDraw.Draw(im)
    F='/usr/share/fonts/opentype/inter/Inter-'
    fb=lambda s:ImageFont.truetype(F+'Bold.otf',s); fr=lambda s:ImageFont.truetype(F+'Regular.otf',s)
    # фото товаров справа
    pics=sorted(P,key=lambda x:-x[3])[:3]
    x=W-3*190-30
    for i,p in enumerate(pics):
        t=Image.open(IMG[p[4]]).convert('RGB'); t.thumbnail((180,420),Image.LANCZOS)
        im.paste(t,(x+i*190,(H-t.height)//2))
    g=Image.new('RGB',(W,H),(11,11,12)); mask=Image.linear_gradient('L').rotate(90).resize((W,H))
    mask=mask.point(lambda v:255 if v<110 else max(0,255-(v-110)*3))
    im=Image.composite(g,im,mask); d=ImageDraw.Draw(im)
    gold=(201,164,92)
    d.text((64,120),'Исламская',font=fb(76),fill=(243,241,236))
    d.text((64,205),'рассрочка',font=fb(76),fill=gold)
    d.text((64,318),'до 12 месяцев',font=fr(38),fill=(243,241,236))
    d.text((64,368),'со взносом и без',font=fr(38),fill=(243,241,236))
    d.text((64,418),'на товары от 25 000 ₽',font=fr(38),fill=(161,157,149))
    d.text((64,520),'TEHNOODOM · Грозный',font=fb(30),fill=gold)
    im.save(out,'JPEG',quality=82,optimize=True,progressive=True)
og_rs()
oi=lambda c: ORDER.index(c) if c in ORDER else 999
items=sorted([p for p in P if p[3]>=RSMIN],key=lambda p:(oi(p[1]),p[3]))
e=lambda s: html.escape(s,quote=True)
groups={}
for p in items: groups.setdefault(p[1],[]).append(p)
cards=''.join(f'<h3 class="gh">{e(c)}</h3><div class="grid">'+''.join(
    f'<a class="card" href="./#p={p[4]}"><img src="t/{IMG[p[4]]}" alt="{e(p[0])}" loading="lazy"><span class="nm">{e(p[0])}</span><b>{fmt(p[3])}</b><span class="mo" data-p="{p[3]}"></span></a>'
    for p in ps)+'</div>' for c,ps in groups.items())
lo=min(p[3] for p in items)
open('rassrochka.html','w',encoding='utf-8').write(f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Исламская рассрочка до 12 месяцев — TEHNOODOM</title>
<meta name="description" content="Рассрочка на технику через DIRHAM: 3, 6, 9 или 12 месяцев, со взносом и без. На товары от 25 000 ₽. {len(items)} {word(len(items))}. TEHNOODOM, Грозный.">
<meta property="og:type" content="website"><meta property="og:site_name" content="TEHNOODOM">
<meta property="og:title" content="Исламская рассрочка до 12 месяцев — TEHNOODOM">
<meta property="og:description" content="Со взносом и без. На товары от 25 000 ₽. Нужны паспорт и поручитель, прописка в ЧР.">
<meta property="og:image" content="{BASE}og/rassrochka.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{BASE}rassrochka.html"><meta property="og:locale" content="ru_RU"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0b0c"><link rel="icon" href="{ICON}">
{TMR}
<style>
:root{{--bg:#0b0b0c;--card:#161618;--ink:#f3f1ec;--mute:#a19d95;--line:#2c2b29;--gold:#c9a45c}}
*{{box-sizing:border-box;margin:0}}html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Inter,Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.47}}
a{{color:inherit;text-decoration:none}}.wrap{{max-width:1080px;margin:0 auto;padding:0 16px}}
nav{{position:sticky;top:0;z-index:20;background:rgba(11,11,12,.85);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid var(--line)}}
nav .wrap{{height:56px;display:flex;align-items:center;justify-content:space-between}}
.brand{{display:flex;align-items:center;gap:10px;font-weight:700;letter-spacing:.02em}}.brand img{{width:30px;height:30px;border-radius:8px}}
.nb{{background:var(--gold);color:#17130b;border-radius:980px;padding:8px 18px;font-size:14px;font-weight:700}}
.hero{{text-align:center;padding:56px 0 28px}}
.hero h1{{font-size:clamp(36px,8vw,64px);line-height:1.05;letter-spacing:-.02em;background:linear-gradient(180deg,#fff 30%,#d9c08f);-webkit-background-clip:text;background-clip:text;color:transparent}}
.hero p{{font-size:clamp(17px,3vw,22px);color:var(--mute);margin:14px auto 0;max-width:30ch;line-height:1.3}}
.chips{{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:20px}}.chips span{{border:1px solid var(--line);border-radius:980px;padding:7px 14px;font-size:14px}}.chips b{{color:var(--gold)}}
section{{margin:36px 0}}h2{{font-size:26px;letter-spacing:-.01em;margin-bottom:14px}}
.box{{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:18px}}
.calc{{max-width:560px;margin:0 auto}}
.calc>label{{display:block;font-size:14px;color:var(--mute);margin-bottom:6px}}
.calc>input{{width:100%;border:1px solid var(--line);background:var(--bg);color:var(--ink);font:inherit;font-size:22px;font-weight:700;padding:12px 14px;border-radius:14px;margin-bottom:6px}}
.warn{{font-size:13px;color:#e8a33c;min-height:18px;margin-bottom:8px}}
.steps{{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));counter-reset:s;list-style:none;padding:0}}
.steps li{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px 16px 16px 58px;position:relative;color:var(--mute);font-size:15px}}
.steps li b{{display:block;color:var(--ink);font-size:16px;margin-bottom:2px}}
.steps li::before{{counter-increment:s;content:counter(s);position:absolute;left:16px;top:16px;width:30px;height:30px;border-radius:50%;background:var(--gold);color:#17130b;font-weight:700;display:grid;place-items:center}}
.two{{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}}
.box ul{{list-style:none;padding:0}}.box li{{padding:9px 0;border-bottom:1px solid var(--line);font-size:15px}}.box li:last-child{{border:0}}
.box .tip{{margin-top:10px;font-size:13.5px;color:#e8a33c}}
table{{width:100%;border-collapse:collapse;font-size:15px}}th{{text-align:left;color:var(--mute);font-weight:500;font-size:13px;padding:6px 0}}td{{padding:9px 0;border-top:1px solid var(--line)}}td+td,th+th{{text-align:right}}
.gh{{font-size:17px;margin:22px 0 10px;color:var(--gold)}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}
@media(min-width:700px){{.grid{{grid-template-columns:repeat(4,minmax(0,1fr))}}}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;padding-bottom:12px}}
.card img{{width:100%;aspect-ratio:3/4;object-fit:cover;background:#111}}
.card .nm{{font-size:13.5px;line-height:1.3;padding:10px 12px 4px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.card b{{padding:0 12px;font-size:16px}}.card .mo{{padding:0 12px;font-size:12.5px;color:var(--gold);font-weight:600}}
.cta{{text-align:center;padding:10px 0 40px}}.cta a,.cta button{{display:block;width:100%;max-width:380px;margin:10px auto 0;padding:14px;border-radius:980px;font:inherit;font-size:16px;font-weight:700;cursor:pointer}}
.wa{{background:#25d366;color:#fff;border:0}}.sh{{background:transparent;color:var(--ink);border:1px solid var(--line)}}
footer{{border-top:1px solid var(--line);padding:22px 0 40px;color:var(--mute);font-size:13px;text-align:center}}
.rsseg{{display:grid;grid-template-columns:1fr 1fr;gap:4px;padding:3px;border-radius:12px;background:var(--bg);margin-bottom:10px}}
.rsseg button{{border:0;border-radius:9px;padding:9px;font:inherit;font-size:14px;font-weight:600;background:transparent;color:var(--mute);cursor:pointer}}
.rsseg button.on{{background:#26262a;color:var(--ink)}}
.rsdown{{display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:14px;color:var(--mute);margin:0 0 10px}}
.rsdown input{{width:140px;border:1px solid var(--line);background:var(--bg);color:var(--ink);font:inherit;font-size:16px;font-weight:700;padding:9px 12px;border-radius:12px;text-align:right}}
.rsbody{{display:grid;gap:6px}}
.rsrow{{display:grid;grid-template-columns:64px 1fr auto;align-items:center;gap:8px;width:100%;padding:10px 12px;border:1.5px solid var(--line);border-radius:12px;background:transparent;color:var(--ink);font:inherit;font-size:14.5px;text-align:left;cursor:pointer}}
.rsrow b{{font-size:16px}}.rsrow b small{{font-size:12px;color:var(--mute);font-weight:500}}.rsrow em{{font-style:normal;font-size:13px;color:var(--mute)}}
.rsrow.on{{border-color:var(--gold);background:rgba(201,164,92,.1)}}
.rssum{{font-size:13.5px;color:var(--mute);margin:4px 2px 0;line-height:1.45}}.rssum b{{color:var(--ink)}}
.rsbtn{{display:block;width:100%;margin-top:6px;padding:13px;border-radius:980px;background:var(--gold);color:#17130b;text-align:center;font-size:16px;font-weight:700}}
.rsnote{{display:block;margin-top:10px;font-size:12px;color:var(--mute);line-height:1.45}}.rsnote a{{color:var(--gold)}}
</style></head><body>
<nav><div class="wrap"><a class="brand" href="./"><img src="{LOGO}" alt="">TEHNOODOM</a><a class="nb" href="./#catalog">Каталог</a></div></nav>
<main class="wrap">
<div class="hero"><h1>Исламская рассрочка</h1><p>Покупайте технику сейчас, платите частями. Через компанию DIRHAM.</p>
<div class="chips"><span><b>3–12</b> месяцев</span><span>Со взносом и без</span><span>От <b>25 000 ₽</b></span></div></div>

<section><h2 style="text-align:center">Рассчитайте платёж</h2><div class="box calc">
<label for="pr">Стоимость товара, ₽</label><input id="pr" type="number" inputmode="numeric" min="0" step="500" value="50000">
<div class="warn" id="warn"></div><div id="w"></div></div></section>

<section><h2>Как оформить</h2><ol class="steps">
<li><b>Выберите товар</b>На сайте или в магазине. Рассрочка на товары и заказы от 25 000 ₽.</li>
<li><b>Выберите срок</b>3, 6, 9 или 12 месяцев, со взносом или без, и нажмите «Оформить в рассрочку».</li>
<li><b>Отправьте документы</b>В WhatsApp: фото паспорта и номер телефона, ваши и поручителя.</li>
<li><b>Получите одобрение</b>DIRHAM рассматривает заявку, после одобрения забираете товар.</li>
</ol></section>

<section class="two">
<div class="box"><h2>Что нужно</h2><ul>
<li>Возраст от 20 лет</li><li>Прописка в Чеченской Республике</li><li>Паспорт и номер телефона покупателя</li><li>Паспорт и номер телефона поручителя</li></ul>
<p class="tip">Фотографии должны быть чёткими, без бликов, чтобы были видны обе страницы паспорта.</p></div>
<div class="box"><h2>Наценка</h2><table><tr><th>Срок</th><th>Без взноса</th><th>Со взносом</th></tr>
<tr><td>3 месяца</td><td>12%</td><td>9%</td></tr><tr><td>6 месяцев</td><td>22%</td><td>15%</td></tr>
<tr><td>9 месяцев</td><td>30%</td><td>22%</td></tr><tr><td>12 месяцев</td><td>40%</td><td>30%</td></tr></table>
<p class="tip" style="color:var(--mute)">Фиксированная наценка вместо процентов. Точную сумму и одобрение даёт DIRHAM. <a href="https://dirham95.ru" target="_blank" rel="noopener" style="color:var(--gold)">Калькулятор DIRHAM</a></p></div>
</section>

<section><h2>Товары в рассрочку</h2><p style="color:var(--mute)">{len(items)} {word(len(items))} от {fmt(lo)}. Нажмите на товар, чтобы выбрать срок.</p>
{cards}</section>

<div class="cta"><a class="wa" href="https://wa.me/79280040943?text={html.escape(__import__('urllib.parse').parse.quote('Здравствуйте! Хочу узнать про рассрочку.'))}" target="_blank" rel="noopener">Спросить про рассрочку в WhatsApp</a>
<button class="sh" id="sh">Поделиться страницей</button></div>
</main>
<footer>TEHNOODOM · Грозный, ул. Назарбаева 98 · <a href="tel:+79280040943">+7 928 004-09-43</a></footer>
<script src="rs.js"></script>
<script>
document.querySelectorAll(".mo").forEach(function(s){{s.textContent="от "+RS.fmt(RS.from(+s.dataset.p))+"/мес"}});
var pr=document.getElementById("pr"),warn=document.getElementById("warn");
var w=RS.mount(document.getElementById("w"),{{price:+pr.value,docs:false,getText:function(st){{return "Здравствуйте! Хочу оформить рассрочку на сумму "+RS.fmt(+pr.value)+".\\n"+st.line}}}});
pr.oninput=function(){{var v=+pr.value||0;warn.textContent=v&&v<RS.MIN?"Рассрочка доступна на сумму от 25 000 ₽":"";w.set(Math.max(v,0))}};
document.getElementById("sh").onclick=async function(){{var u="{BASE}rassrochka.html",b=this;
try{{if(navigator.share){{await navigator.share({{title:"Исламская рассрочка — TEHNOODOM",url:u}});return}}}}catch(e){{return}}
try{{await navigator.clipboard.writeText(u);b.textContent="Ссылка скопирована ✓";setTimeout(function(){{b.textContent="Поделиться страницей"}},1500)}}catch(e){{prompt("Ссылка:",u)}}}};
</script></body></html>''')
print('rassrochka.html:',len(items),'товаров')
