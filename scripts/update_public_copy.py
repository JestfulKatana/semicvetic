"""Replace known demo phrases without overwriting client-edited copy.

Run with an explicit database path; defaults to preview, --apply writes changes.
Never use on production without a database backup and explicit authorization.
"""
import argparse
import json
import sqlite3
from pathlib import Path

REPLACEMENTS = {
    ('events_grid', 'title'): ('Ближайшие мероприятия', 'Мероприятия центра'),
    ('hero', 'subtitle'): ('События дают быстрые лиды, статьи закрывают SEO-запросы родителей.', 'Праздники, встречи и полезные материалы для родителей.'),
    ('hero', 'eyebrow'): ('Контент-маркетинг', 'Жизнь центра'),
    ('articles_grid', 'title'): ('Статьи для органического трафика', 'Полезное для родителей'),
}


def updated_blocks(blocks):
    result = json.loads(json.dumps(blocks))
    count = 0
    for block in result:
        data = block.get('data', {})
        for (component, field), (old, new) in REPLACEMENTS.items():
            if block.get('component') == component and data.get(field) == old:
                data[field] = new
                count += 1
    for block in result:
        if block.get('component', block.get('type')) != 'credentials_list':
            continue
        for item in block.get('data', block.get('payload', {})).get('items', []):
            old = 'Подтверждённая отметка на\u00a0Яндекс.Картах. Рейтинг без\u00a0цифр\u00a0— только сам бейдж.'
            if item.get('description') == old:
                item['description'] = 'Отметка центра на Яндекс.Картах.'
                count += 1
    return result, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error('Database must already exist')
    with sqlite3.connect(args.database) as connection:
        rows = connection.execute("SELECT id, content_json FROM page WHERE slug IN ('meropriyatiya', 'o-centre')").fetchall()
        count = 0
        for row in rows:
            blocks, changed = updated_blocks(json.loads(row[1]))
            count += changed
            if args.apply and changed:
                connection.execute('UPDATE page SET content_json = ? WHERE id = ?', (json.dumps(blocks, ensure_ascii=False), row[0]))
        print(f'{"Updated" if args.apply else "Would update"} {count} demo phrases')


if __name__ == '__main__':
    main()
