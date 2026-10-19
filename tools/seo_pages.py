# Полноценные страницы для поисковиков и ссылок:
#   p/<key>.html — товар, c/<slug>.html — раздел, sitemap.xml, robots.txt, logo.jpg, pg.css
#   и блок ссылок на разделы в подвале index.html (между <!--cats--> и <!--/cats-->).
# Все данные берутся из каталога в index.html, ничего не придумывается.
import json, os, re, html, base64, datetime
from urllib.parse import quote

BASE = 'https://tehnoodom.github.io/'
WA = 'https://wa.me/79280040943?text='
PHONE = '+79280040943'
PHONE_H = '+7 928 004-09-43'
ADDR = 'г. Грозный, ул. Назарбаева 98'
RSMIN = 25000
BIG = {"Холодильники и морозильники", "Стиральные машины", "Плиты"}
e = lambda s: html.escape(str(s), quote=True)


def rs_from(pr):  # как RS.from в rs.js: 12 мес. без взноса, +40%, вниз до 50 ₽
    return int(pr * 1.40 / 12 // 50 * 50)


CSS = """:root{--bg:#0b0b0c;--card:#161618;--card2:#1d1d20;--ink:#f3f1ec;--mute:#a19d95;--line:#2c2b29;--gold:#c9a45c;--red:#d71920}
*{box-sizing:border-box;margin:0}html{-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Inter,Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.47;padding-bottom:env(safe-area-inset-bottom,0)}
a{color:inherit;text-decoration:none}img{display:block;max-width:100%}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
.top{position:sticky;top:0;z-index:20;background:rgba(11,11,12,.86);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid var(--line)}
.top .wrap{height:56px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;letter-spacing:.02em}.brand img{width:30px;height:30px;border-radius:8px}
.nb{background:var(--gold);color:#17130b;border-radius:980px;padding:8px 18px;font-size:14px;font-weight:700;white-space:nowrap}
.bc{display:flex;flex-wrap:wrap;gap:4px 8px;font-size:13px;color:var(--mute);padding:14px 0 6px;list-style:none}
.bc li+li::before{content:"›";margin-right:8px;color:var(--line)}.bc a{color:var(--mute)}.bc a:hover{color:var(--ink)}
.pp{display:grid;gap:22px;padding:8px 0 10px}
@media(min-width:820px){.pp{grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:start;gap:40px}.ph{position:sticky;top:76px}}
.ph{background:var(--card);border:1px solid var(--line);border-radius:22px;overflow:hidden}
.ph img{width:100%;height:auto;max-height:78vh;object-fit:contain;margin:0 auto}
.pc{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--gold);font-weight:600}
h1{font-size:clamp(24px,5.4vw,34px);line-height:1.15;letter-spacing:-.01em;margin:6px 0 10px}
.pr{font-size:clamp(28px,6vw,38px);font-weight:700;letter-spacing:-.01em}
.rs{display:inline-block;margin-top:4px;color:var(--gold);font-weight:600;font-size:15px}
.btns{display:grid;gap:10px;margin:18px 0 6px}
.btn{display:flex;align-items:center;justify-content:center;gap:8px;min-height:52px;padding:12px 18px;border-radius:980px;font-size:16.5px;font-weight:700;text-align:center;border:0;cursor:pointer}
.btn.wa{background:#25d366;color:#fff}.btn.gold{background:var(--gold);color:#17130b}.btn.out{border:1px solid var(--line);color:var(--ink)}
.btn svg{width:20px;height:20px;flex:none}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.box{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px 18px;margin-top:14px}
.box h2{font-size:18px;margin-bottom:8px}
.box ul{list-style:none;padding:0}.box li{padding:8px 0;border-bottom:1px solid var(--line);font-size:15px}.box li:last-child{border:0}
.box p{font-size:15px;color:var(--mute)}.box p+p{margin-top:6px}.box a{color:var(--gold)}
.sec{margin:34px 0}.sec h2{font-size:clamp(21px,4.4vw,26px);letter-spacing:-.01em;margin-bottom:12px}
.lead{color:var(--mute);font-size:16px;max-width:60ch}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
@media(min-width:700px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(min-width:960px){.grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;padding-bottom:12px;transition:border-color .2s}
.card:hover{border-color:#4a4740}
.card img{width:100%;height:auto;aspect-ratio:3/4;object-fit:cover;background:#111}
.card .cb{font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--gold);padding:10px 12px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card .nm{font-size:14px;line-height:1.3;padding:0 12px;margin:4px 0 8px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;min-height:3.9em}
.card b{padding:0 12px;font-size:17px;margin-top:auto}.card .mo{padding:2px 12px 0;font-size:12.5px;color:var(--gold);font-weight:600}
.chips{display:flex;flex-wrap:wrap;gap:8px}.chips a{border:1px solid var(--line);border-radius:980px;padding:8px 14px;font-size:14px;color:var(--mute)}.chips a:hover{color:var(--ink);border-color:#4a4740}
.chips a[aria-current]{background:var(--gold);color:#17130b;border-color:var(--gold);font-weight:600}
.hero{padding:10px 0 4px}.hero h1{font-size:clamp(28px,6.4vw,44px)}
.foot{border-top:1px solid var(--line);margin-top:40px;padding:24px 0 40px;color:var(--mute);font-size:14px}
.foot .wrap{display:grid;gap:8px}.foot b{color:var(--ink)}.foot a{color:var(--gold)}
"""

ICON_WA = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.2c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.9s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.4.6-.3.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.3 2.4 1.5.3.1.5.1.6-.1l.9-1c.2-.3.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.2.1.7-.1 1.3z"/></svg>'
ICON_CART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.6 12.4a2 2 0 0 0 2 1.6h8.2a2 2 0 0 0 2-1.5L21.5 8H6"/></svg>'


def build(P, IMG, ORDER, og_img, slug, fmt, word):
    src = open('index.html', encoding='utf-8').read()
    BR = json.loads(re.search(r'const BR=(\[.*?\]);', src).group(1))
    BRN = json.loads(re.search(r'const BRN=(\{.*?\});', src).group(1))
    SZ = json.loads(re.search(r'const SZ=(\{.*?\});', src).group(1))
    TMR = re.search(r'<!-- Top.Mail.Ru counter -->.*?<!-- /Yandex.Metrika counter -->', src, re.S).group(0)
    ICON = re.search(r'<link rel="icon" href="(data:[^"]+)"', src).group(1)
    logo = re.search(r'<a class="brand"[^>]*><img src="data:image/(\w+);base64,([^"]+)"', src)
    open('logo.jpg', 'wb').write(base64.b64decode(logo.group(2)))
    open('pg.css', 'w', encoding='utf-8').write(CSS)

    def brand(n):
        for b in BR:
            if re.search(r'(^|[^A-Za-z])' + re.escape(b) + r'(?![A-Za-z])', n, re.I):
                return BRN.get(b, b)
        return ''

    oi = lambda c: ORDER.index(c) if c in ORDER else 999
    cats = {}
    for p in P:
        cats.setdefault(p[1], []).append(p)
    corder = sorted(cats, key=oi)
    today = datetime.date.today().isoformat()

    def head(title, desc, url, img, extra=''):
        return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="TEHNOODOM">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{img}"><meta property="og:url" content="{url}">
<meta property="og:locale" content="ru_RU"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0b0c"><link rel="icon" href="{ICON}">
<link rel="stylesheet" href="../pg.css">
{extra}
{TMR}
</head><body>
<header class="top"><div class="wrap"><a class="brand" href="../"><img src="../logo.jpg" alt="TEHNOODOM" width="30" height="30">TEHNOODOM</a><a class="nb" href="../#catalog">Каталог</a></div></header>
'''

    def foot():
        links = ''.join(f'<a href="../c/{slug(c)}.html">{e(c)}</a>' for c in corder)
        return f'''<footer class="foot"><div class="wrap">
<div><b>TEHNOODOM</b> — бытовая техника, электроника и аксессуары оптом и в розницу.</div>
<div>{ADDR} · <a href="tel:{PHONE}">{PHONE_H}</a> · ежедневно 9:00–20:00</div>
<div class="chips" style="margin-top:8px">{links}</div>
</div></footer>
</body></html>'''

    def card(p):
        name, cat, spec, price, key = p[:5]
        b = brand(name)
        mo = f'<span class="mo">Рассрочка от {fmt(rs_from(price))}/мес</span>' if price >= RSMIN else ''
        return (f'<a class="card" href="../p/{key}.html"><img src="../t/{IMG[key]}" alt="{e(name)}" loading="lazy" width="480" height="640">'
                f'<span class="cb">{e(b or cat)}</span><span class="nm">{e(name)}</span>'
                f'<b>{fmt(price) if price else "Цена по запросу"}</b>{mo}</a>')

    def ld(obj):
        return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'

    keep = set()
    # ---------- товары ----------
    for p in P:
        name, cat, spec, price, key = p[:5]
        cs = slug(cat)
        b = brand(name)
        url = f'{BASE}p/{key}.html'
        og = og_img(key, IMG[key])
        specs = [x.strip() for x in spec.split(' · ') if x.strip()]
        title = f'{name} — {fmt(price)} купить в Грозном' if price else f'{name} — купить в Грозном'
        desc = f'{name}: ' + ', '.join(specs)
        if len(desc) > 150:
            desc = desc[:147].rsplit(' ', 1)[0].rstrip(',') + '…'
        desc += ' Заказ в WhatsApp, доставка по Чечне.'
        w, h = SZ.get(key, [720, 960])
        wa = WA + quote(f'Здравствуйте! Хочу заказать:\n{name}' + (f' — {fmt(price)}' if price else '') + f'\n{url}')
        prod = {"@context": "https://schema.org", "@type": "Product", "name": name, "image": BASE + IMG[key],
                "description": ', '.join(specs), "category": cat, "url": url}
        if b:
            prod["brand"] = {"@type": "Brand", "name": b}
        if price:
            prod["offers"] = {"@type": "Offer", "price": price, "priceCurrency": "RUB", "url": url,
                              "seller": {"@type": "Organization", "name": "TEHNOODOM"}}
        crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Каталог", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": cat, "item": f'{BASE}c/{cs}.html'},
            {"@type": "ListItem", "position": 3, "name": name, "item": url}]}
        rs = (f'<a class="rs" href="../rassrochka.html">Рассрочка от {fmt(rs_from(price))}/мес · 3–12 месяцев</a>'
              if price >= RSMIN else '')
        dl = 'Доставка по Грозному 1 000 ₽.' if cat in BIG else 'Доставка по Грозному от 350 ₽.'
        sim = sorted([x for x in cats[cat] if x[4] != key], key=lambda x: abs(x[3] - price))[:8]
        simh = (f'<section class="sec"><h2>Похожие товары</h2><div class="grid">{"".join(card(x) for x in sim)}</div></section>'
                if sim else '')
        vid = (f'<a class="btn out" href="{e(p[6])}" target="_blank" rel="noopener">Смотреть видеообзор</a>' if len(p) > 6 and p[6] else '')
        body = f'''<main class="wrap">
<ol class="bc"><li><a href="../">Каталог</a></li><li><a href="../c/{cs}.html">{e(cat)}</a></li><li aria-current="page">{e(b or name[:40])}</li></ol>
<article class="pp">
<div class="ph"><img src="../{IMG[key]}" alt="{e(name)}" width="{w}" height="{h}" fetchpriority="high"></div>
<div>
<div class="pc">{e(b + " · " if b else "")}{e(cat)}</div>
<h1>{e(name)}</h1>
<div class="pr">{fmt(price) if price else "Цена по запросу"}</div>
{rs}
<div class="btns">
<a class="btn wa buy" href="{wa}" target="_blank" rel="noopener">{ICON_WA}Заказать в WhatsApp</a>
{vid}
<div class="row2"><a class="btn gold add" href="../#add={key}">{ICON_CART}В корзину</a><a class="btn out" href="tel:{PHONE}">Позвонить</a></div>
</div>
<section class="box"><h2>Характеристики</h2><ul>{"".join(f"<li>{e(x)}</li>" for x in specs)}</ul></section>
<section class="box"><h2>Доставка и гарантия</h2>
<p>{dl} По Чечне и в другие регионы — по тарифам. <a href="../#delivery">Все тарифы</a></p>
<p>Гарантия магазина 14 дней. На оригинальную технику мировых брендов — гарантия сервиса 1 год.</p>
<p>Самовывоз: {ADDR}.</p></section>
<section class="box"><h2>Оптом</h2><p>Нужно несколько штук? <a href="{WA + quote(f"Здравствуйте! Интересует оптовая закупка: {name}. Подскажите цену и наличие.")}" target="_blank" rel="noopener">Уточните оптовую цену в WhatsApp</a>.</p></section>
</div>
</article>
{simh}
</main>
'''
        open(f'p/{key}.html', 'w', encoding='utf-8').write(head(title, desc, url, og, ld(prod) + ld(crumbs)) + body + foot())
        keep.add(f'p/{key}.html')

    # ---------- разделы ----------
    for c in corder:
        items = cats[c]
        s = slug(c)
        n = len(items)
        url = f'{BASE}c/{s}.html'
        priced = [x[3] for x in items if x[3]]
        lo = min(priced) if priced else 0
        brands = []
        for x in items:
            b = brand(x[0])
            if b and b not in brands:
                brands.append(b)
        title = f'{c} в Грозном — {n} {word(n)}' + (f' от {fmt(lo)}' if lo else '') + ' | TEHNOODOM'
        desc = (f'{c}: {n} {word(n)}' + (f' от {fmt(lo)}' if lo else '') +
                (f', бренды {", ".join(brands[:5])}' if brands else '') +
                '. Цены на сайте, заказ в WhatsApp, доставка по Чечне. TEHNOODOM, Грозный.')
        first = sorted(items, key=lambda x: -x[3])[0]
        lead = (f'{n} {word(n)}' + (f' от {fmt(lo)}' if lo else '') + '. Цены указаны на сайте. '
                'Выберите товар и закажите в WhatsApp или добавьте в корзину.'
                + (' На товары от 25 000 ₽ — исламская рассрочка через DIRHAM.' if any(x[3] >= RSMIN for x in items) else ''))
        brl = f'<p class="lead" style="margin-top:6px">Бренды: {e(", ".join(brands))}.</p>' if brands else ''
        lst = {"@context": "https://schema.org", "@type": "ItemList", "name": c, "numberOfItems": n,
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f'{BASE}p/{x[4]}.html', "name": x[0]}
                                   for i, x in enumerate(items)]}
        crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Каталог", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": c, "item": url}]}
        others = ''.join(f'<a href="../c/{slug(o)}.html"' + (' aria-current="page"' if o == c else '') + f'>{e(o)}</a>' for o in corder)
        body = f'''<main class="wrap">
<ol class="bc"><li><a href="../">Каталог</a></li><li aria-current="page">{e(c)}</li></ol>
<div class="hero"><h1>{e(c)} в Грозном</h1><p class="lead">{e(lead)}</p>{brl}
<div class="btns" style="max-width:420px"><a class="btn out" href="../#c={s}">Открыть в каталоге: поиск и фильтры</a></div></div>
<section class="sec"><div class="grid">{"".join(card(x) for x in items)}</div></section>
<section class="box"><h2>Не нашли нужную модель?</h2><p>Напишите нам — подберём и привезём. Оптовым клиентам уточним цены и наличие.</p>
<div class="btns" style="max-width:420px"><a class="btn wa" href="{WA + quote(f"Здравствуйте! Подберите, пожалуйста: {c.lower()}.")}" target="_blank" rel="noopener">{ICON_WA}Написать в WhatsApp</a></div></section>
<section class="sec"><h2>Другие разделы</h2><div class="chips">{others}</div></section>
</main>
'''
        open(f'c/{s}.html', 'w', encoding='utf-8').write(head(title, desc, url, BASE + f'og/{first[4]}.jpg', ld(lst) + ld(crumbs)) + body + foot())
        keep.add(f'c/{s}.html')

    # ---------- sitemap и robots ----------
    urls = [BASE, BASE + 'rassrochka.html'] + [f'{BASE}c/{slug(c)}.html' for c in corder] + [f'{BASE}p/{p[4]}.html' for p in P]
    open('sitemap.xml', 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'<url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls) + '</urlset>\n')
    open('robots.txt', 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n')

    # ---------- ссылки на разделы в подвале главной ----------
    links = ''.join(f'<a href="c/{slug(c)}.html">{e(c)}</a>' for c in corder)
    block = f'<!--cats--><div class="fcats" aria-label="Разделы каталога">{links}</div><!--/cats-->'
    if '<!--cats-->' in src:
        src = re.sub(r'<!--cats-->.*?<!--/cats-->', lambda m: block, src, flags=re.S)
        open('index.html', 'w', encoding='utf-8').write(src)
    print('SEO:', len(P), 'товаров,', len(corder), 'разделов, sitemap', len(urls), 'адресов')
    return keep
