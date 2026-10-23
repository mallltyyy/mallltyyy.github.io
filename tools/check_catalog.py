#!/usr/bin/env python3
"""Проверка каталога TEHNOODOM. Только читает файлы, ничего не меняет.

Запуск из корня репозитория:  python3 tools/check_catalog.py [--md отчёт.md]
Код выхода 1 — есть ошибки, 0 — ошибок нет (предупреждения допустимы).
"""
import json, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WA = '79280040943'


def load(path='index.html'):
    s = open(os.path.join(ROOT, path), encoding='utf-8').read()
    def get(name, default=None):
        m = re.search(r'const ' + name + r'=(.*?);\n', s, re.S)
        return json.loads(m.group(1)) if m else default
    return s, get


def fmt(n):
    return f'{n:,}'.replace(',', ' ') + ' ₽'


def models(name):
    """Номера моделей из названия: токены с цифрами длиной от 3 символов."""
    out = set()
    for t in re.findall(r'[A-Za-zА-Яа-я0-9][A-Za-zА-Яа-я0-9\-‑./]*', name):
        c = re.sub(r'[\-‑./]', '', t).lower()
        if re.search(r'\d', c) and len(c) >= 3 and not re.fullmatch(r'\d+(л|вт|мм|см|гб|мач)?', c):
            out.add(c)
    return out


def check():
    s, get = load()
    P, IMG, SZ = get('P', []), get('IMG', {}), get('SZ', {})
    ORDER, GROUPS, BR, ADDED = get('ORDER', []), get('GROUPS', []), get('BR', []), get('ADDED', {})
    E, W = [], []
    keys = [p[4] if len(p) > 4 else None for p in P]
    stale = []

    # 1. Идентификаторы
    seen = defaultdict(list)
    for i, k in enumerate(keys):
        seen[k].append(i)
    for k, idx in seen.items():
        if len(idx) > 1:
            E.append(f'Ключ «{k}» повторяется {len(idx)} раз (строки {idx})')
    for i, p in enumerate(P):
        k = keys[i]
        tag = f'[{k}]'
        if len(p) < 6:
            E.append(f'{tag} в строке {len(p)} полей, нужно минимум 6'); continue
        name, cat, spec, price, _, wa = p[:6]
        if not k or not re.fullmatch(r'[a-z0-9]+', str(k)):
            E.append(f'{tag} ключ должен состоять из латиницы в нижнем регистре и цифр')
        # 2. Название, раздел, характеристики
        if not str(name).strip():
            E.append(f'{tag} пустое название')
        if cat not in ORDER:
            E.append(f'{tag} раздел «{cat}» отсутствует в ORDER')
        if not str(spec).strip():
            W.append(f'{tag} нет характеристик')
        # 3. Цена
        if not isinstance(price, int) or isinstance(price, bool):
            E.append(f'{tag} цена не целое число: {price!r}')
        elif price <= 0:
            E.append(f'{tag} цена {price} — недопустимое значение')
        elif price < 100 or price > 1_000_000:
            W.append(f'{tag} подозрительная цена {fmt(price)}')
        else:
            nums = [int(re.sub(r'\D', '', x)) for x in re.findall(r'(\d[\d\s]*)\s*₽', str(wa))]
            if nums and price not in nums:
                stale.append(k)
        # 4. Фото и страницы
        img = IMG.get(k)
        if not img:
            E.append(f'{tag} нет записи в IMG')
        else:
            for path in (img, 't/' + img):
                if not os.path.exists(os.path.join(ROOT, path)):
                    E.append(f'{tag} нет файла {path}')
            if k not in SZ:
                W.append(f'{tag} нет размеров в SZ')
            else:
                try:
                    from PIL import Image
                    real = list(Image.open(os.path.join(ROOT, img)).size)
                    if real != SZ[k]:
                        W.append(f'{tag} SZ {SZ[k]} не совпадает с размером фото {real}')
                except Exception:
                    pass
        for path in (f'p/{k}.html', f'og/{k}.jpg'):
            if not os.path.exists(os.path.join(ROOT, path)):
                W.append(f'{tag} нет {path} (запустите tools/build_previews.py)')
        if k not in ADDED:
            W.append(f'{tag} нет даты в ADDED (запустите tools/build_previews.py)')
        # 5. Ссылка на обзор
        if len(p) > 6 and p[6] and not re.fullmatch(r'https://(www\.)?instagram\.com/(reel|p)/[A-Za-z0-9_-]+/?', p[6]):
            W.append(f'{tag} необычная ссылка на обзор: {p[6]}')

    if stale:
        W.append(f'Старая цена в 6-м поле (запасной текст WhatsApp) у {len(stale)} товаров: {", ".join(stale)}. '
                 'Сайт это поле не использует — заказ собирается из названия и актуальной цены, покупатель не пострадает.')

    # 6. Возможные дубли: одинаковый номер модели у разных ключей
    by_model = defaultdict(set)
    for p in P:
        for m in models(p[0]):
            by_model[m].add(p[4])
    for m, ks in sorted(by_model.items()):
        if len(ks) > 1:
            W.append(f'Возможный дубль: модель «{m}» у ключей {sorted(ks)} — проверьте, это разные товары или цвета')
    names = defaultdict(list)
    for p in P:
        names[re.sub(r'[\s‑-]+', ' ', p[0].lower()).strip()].append(p[4])
    for n, ks in names.items():
        if len(ks) > 1:
            E.append(f'Одинаковое название у ключей {ks}: «{n}»')

    # 7. Разделы и группы
    used = {p[1] for p in P}
    for c in ORDER[1:]:
        if c not in used:
            E.append(f'Раздел «{c}» пустой — приведёт к пустой странице')
    in_groups = {c for _, cs in GROUPS for c in cs}
    for c in used - in_groups:
        W.append(f'Раздел «{c}» не входит ни в одну группу GROUPS')
    if len(set(BR)) != len(BR):
        W.append('В списке брендов BR есть повторы')

    # 8. Ссылки на странице
    html = re.sub(r'<script.*?</script>', '', s, flags=re.S)
    ids = set(re.findall(r'id="([^"]+)"', s))
    for a in sorted(set(re.findall(r'href="#([A-Za-z][\w-]*)"', html))):
        if a not in ids:
            E.append(f'Ссылка на #{a} ведёт в никуда')
    for f in sorted(set(re.findall(r'(?:href|src)="([\w./-]+\.(?:html|js|css|jpg|png|webp))"', html))):
        if not f.startswith(('http', '//')) and not os.path.exists(os.path.join(ROOT, f)):
            E.append(f'Файл по ссылке не найден: {f}')
    nums = set(re.findall(r'wa\.me/(\d+)', s))
    if nums != {WA}:
        E.append(f'Номера WhatsApp на странице: {sorted(nums)} (ожидается только {WA})')
    sm = os.path.join(ROOT, 'sitemap.xml')
    if os.path.exists(sm):
        for u in re.findall(r'<loc>https://tehnoodom\.github\.io/([^<]*)</loc>', open(sm, encoding='utf-8').read()):
            f = u or 'index.html'
            if not os.path.exists(os.path.join(ROOT, f)):
                E.append(f'sitemap.xml: файла нет — {u}')

    stats = {'товаров': len(P), 'разделов': len(used), 'брендов': len(BR)}
    return E, W, stats


def report(E, W, stats):
    lines = ['# Проверка каталога TEHNOODOM', '',
             ' · '.join(f'{k}: {v}' for k, v in stats.items()), '',
             f'## Ошибки: {len(E)}'] + [f'- {e}' for e in E] + ['', f'## Предупреждения: {len(W)}'] + [f'- {w}' for w in W]
    lines += ['', 'Итог: ' + ('ЕСТЬ ОШИБКИ — публиковать нельзя, пока не исправлены.' if E else 'ошибок нет.'),
              'Скрипт ничего не исправляет и не удаляет — только сообщает.']
    return '\n'.join(lines)


if __name__ == '__main__':
    E, W, stats = check()
    text = report(E, W, stats)
    print(text)
    if '--md' in sys.argv:
        open(sys.argv[sys.argv.index('--md') + 1], 'w', encoding='utf-8').write(text + '\n')
    sys.exit(1 if E else 0)
