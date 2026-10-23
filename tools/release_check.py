#!/usr/bin/env python3
"""Контроль перед публикацией TEHNOODOM. Ничего не сливает, не публикует и не меняет.

Запуск из корня репозитория (в рабочей ветке):
    python3 tools/release_check.py [--base main] [--md отчёт.md]

Что делает:
 1. Сравнивает каталог текущей ветки с веткой base (по умолчанию main):
    количество товаров и разделов, пропавшие/новые товары, изменённые цены и названия,
    номер WhatsApp, телефон, адрес.
 2. Запускает tools/check_catalog.py.
 3. Если установлен Playwright — проверяет в браузере на 320 и 390 px:
    поиск, открытие карточки, корзину и сумму, формирование заказа в WhatsApp,
    ошибки JavaScript и горизонтальную прокрутку.
Код выхода 1 — есть проблемы, которые нужно разобрать до публикации.
"""
import functools, http.server, json, os, re, subprocess, sys, threading, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import check_catalog  # noqa: E402


def parse(s):
    def get(n, d=None):
        m = re.search(r'const ' + n + r'=(.*?);\n', s, re.S)
        return json.loads(m.group(1)) if m else d
    P = get('P', [])
    return {
        'P': {p[4]: p for p in P}, 'order': get('ORDER', []),
        'wa': sorted(set(re.findall(r'wa\.me/(\d+)', s))), 'tel': sorted(set(re.findall(r'tel:([+\d]+)', s))),
        'addr': sorted(set(re.findall(r'(?:ул\.|улица)\s*[А-ЯЁа-яё]+\s*\d+', s))),
    }


def compare(base):
    cur = parse(open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read())
    try:
        old_s = subprocess.check_output(['git', 'show', f'{base}:index.html'], cwd=ROOT).decode('utf-8')
    except subprocess.CalledProcessError:
        return [f'Не удалось прочитать {base}:index.html'], [], {}
    old = parse(old_s)
    E, I = [], []
    gone = sorted(set(old['P']) - set(cur['P']))
    new = sorted(set(cur['P']) - set(old['P']))
    if gone:
        E.append(f'Пропали товары ({len(gone)}): {", ".join(gone)}')
    if new:
        I.append(f'Новые товары ({len(new)}): {", ".join(new)}')
    for k in sorted(set(old['P']) & set(cur['P'])):
        a, b = old['P'][k], cur['P'][k]
        if a[3] != b[3]:
            I.append(f'Цена изменена [{k}]: {a[3]} → {b[3]}')
        if a[0] != b[0]:
            I.append(f'Название изменено [{k}]: «{a[0]}» → «{b[0]}»')
        if a[1] != b[1]:
            I.append(f'Раздел изменён [{k}]: {a[1]} → {b[1]}')
    lost_cats = [c for c in old['order'] if c not in cur['order']]
    if lost_cats:
        E.append(f'Пропали разделы: {lost_cats}')
    for f, label in (('wa', 'номер WhatsApp'), ('tel', 'телефон'), ('addr', 'адрес')):
        if old[f] != cur[f]:
            E.append(f'Изменился {label}: {old[f]} → {cur[f]}')
    stats = {'товаров было': len(old['P']), 'товаров стало': len(cur['P']),
             'разделов было': len(old['order']) - 1, 'разделов стало': len(cur['order']) - 1}
    return E, I, stats


def browser_tests():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, ['Playwright не установлен — проверки в браузере пропущены (pip install playwright)']
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=ROOT)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{srv.server_address[1]}/'
    R = []
    def ok(name, cond, info=''):
        R.append((bool(cond), name, info))
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w, h in ((320, 640), (390, 844)):
            ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=True, has_touch=True)
            pg = ctx.new_page()
            for host in ('mc.yandex.ru', 'top-fwz1.mail.ru'):
                pg.route(f'**/{host}/**', lambda r: r.abort())
            err = []
            pg.on('pageerror', lambda e: err.append(str(e)))
            pg.add_init_script("window.__wa=[];window.open=u=>{__wa.push(u);return null}")
            t = f'[{w}px] '
            pg.goto(url); pg.wait_for_timeout(1200)
            n = pg.evaluate('P.length')
            ok(t + 'страница открывается, товары загружены', n > 0, f'{n} товаров')
            ok(t + 'нет горизонтальной прокрутки', not pg.evaluate('document.documentElement.scrollWidth>innerWidth'))
            first = pg.evaluate('P[0][0]')
            model = re.findall(r'[A-Za-z]+[\w‑-]*\d[\w‑-]*', first)
            q = model[0] if model else first.split()[0]
            pg.fill('#q', q); pg.wait_for_timeout(300)
            ok(t + f'поиск «{q}» находит товар', pg.locator('#grid .card').count() > 0)
            pg.fill('#q', 'zzzzqqq'); pg.wait_for_timeout(300)
            ok(t + 'пустой поиск показывает подсказку', pg.locator('.empty').count() == 1)
            pg.fill('#q', ''); pg.wait_for_timeout(300)
            pg.locator('#grid .card').first.click(position={'x': 30, 'y': 30}); pg.wait_for_timeout(700)
            ok(t + 'карточка товара открывается', pg.evaluate("document.getElementById('pv').classList.contains('open')"))
            ok(t + 'кнопка WhatsApp в карточке ведёт на верный номер',
               pg.evaluate("document.getElementById('pvwa').href").startswith('https://wa.me/79280040943'))
            pg.click('#pvx'); pg.wait_for_timeout(400)
            adds = pg.locator('#grid .card .add')
            adds.nth(0).click(); adds.nth(1).click(); adds.nth(1).click(); pg.wait_for_timeout(300)
            exp = pg.evaluate('Object.entries(cart).reduce((a,[i,n])=>a+P[i][3]*n,0)')
            pg.evaluate("document.getElementById('ov').classList.add('open')"); pg.wait_for_timeout(400)
            got = int(re.sub(r'\D', '', pg.text_content('#sum')) or 0)
            ok(t + 'сумма корзины верная', got == exp, f'{got}')
            pg.check('input[name=dm][value=ship]'); pg.click('#send'); pg.wait_for_timeout(200)
            ok(t + 'без адреса заказ не отправляется', pg.evaluate('__wa.length') == 0)
            pg.fill('#addr', 'Тестовый адрес 1'); pg.click('#send'); pg.wait_for_timeout(200)
            u = pg.evaluate("__wa[0]||''")
            text = urllib.parse.parse_qs(urllib.parse.urlparse(u).query).get('text', [''])[0]
            ok(t + 'сообщение заказа: номер, товары, количество, итог, адрес',
               u.startswith('https://wa.me/79280040943') and 'заявка' in text and '×' in text and 'Итого' in text and 'Тестовый адрес' in text)
            while pg.locator('#items .cdel').count():
                pg.locator('#items .cdel').first.click(); pg.wait_for_timeout(450)
            ok(t + 'товары удаляются, корзина пустеет', pg.evaluate('Object.keys(cart).length') == 0)
            ok(t + 'нет ошибок JavaScript', not err, '; '.join(err)[:200])
            ctx.close()
        b.close()
    srv.shutdown()
    return R, []


def main():
    base = sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else 'main'
    branch = subprocess.run(['git', 'branch', '--show-current'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    out = [f'# Контроль публикации TEHNOODOM', '', f'Ветка: {branch} · сравнение с: {base}', '']
    bad = False
    E, I, stats = compare(base)
    out.append('## 1. Сравнение каталога')
    out.append(' · '.join(f'{k}: {v}' for k, v in stats.items()))
    out += [f'- ОШИБКА: {e}' for e in E] + [f'- {i}' for i in I] or ['- изменений в товарах нет']
    if not E and not I:
        out.append('- товары, цены, разделы, контакты не изменились')
    bad |= bool(E)
    CE, CW, cstats = check_catalog.check()
    out += ['', f'## 2. Проверка каталога: ошибок {len(CE)}, предупреждений {len(CW)}']
    out += [f'- ОШИБКА: {e}' for e in CE] + [f'- {w}' for w in CW]
    bad |= bool(CE)
    R, notes = browser_tests()
    out += ['', '## 3. Проверка в браузере (Chromium)']
    out += [f'- {n}' for n in notes]
    if R:
        out += [f'- {"OK  " if r[0] else "СБОЙ"} {r[1]}' + (f' ({r[2]})' if r[2] else '') for r in R]
        bad |= not all(r[0] for r in R)
    out += ['', '## Ограничения',
            '- Проверка идёт в Chromium; Safari на iPhone нужно проверить вручную.',
            '- Открытие WhatsApp перехватывается: проверяется ссылка и текст, сообщение не отправляется.',
            '- Скрипт не сливает ветки и не публикует сайт. Решение о публикации принимает владелец.',
            '', 'ИТОГ: ' + ('ЕСТЬ ПРОБЛЕМЫ — публиковать нельзя, пока не разобраны.' if bad else 'проблем не найдено, можно показывать владельцу для решения о публикации.')]
    text = '\n'.join(out)
    print(text)
    if '--md' in sys.argv:
        open(sys.argv[sys.argv.index('--md') + 1], 'w', encoding='utf-8').write(text + '\n')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
