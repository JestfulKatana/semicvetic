"""Apply the client-confirmed roster. Dry run by default; backs up before --apply."""
import argparse
import datetime
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
ROSTER = json.loads(Path(__file__).with_name('teachers_20260914.json').read_text())
DEMO_NAMES = {'Ольга Савельева', 'Екатерина Морозова', 'Анна Карпова', 'Наталья Кузнецова', 'Светлана Иванова', 'Дарья Николаева', 'Марина Лебедева', 'Татьяна Орлова', 'Юлия Васильева', 'Алёна Сорокина'}

def update(connection):
    for row in connection.execute('SELECT id, name FROM teacher').fetchall():
        if row[1] in DEMO_NAMES:
            connection.execute('UPDATE program SET teacher_id = NULL WHERE teacher_id = ?', (row[0],))
            connection.execute('DELETE FROM teacher WHERE id = ?', (row[0],))
    for order, person in enumerate(ROSTER, 1):
        existing = connection.execute("SELECT id FROM teacher WHERE replace(name, 'ё', 'е') = ?", (person['name'].replace('ё', 'е'),)).fetchone()
        if existing:
            teacher_id = existing[0]
        else:
            teacher_id = connection.execute("INSERT INTO teacher(name, role, sort_order, created_at, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)", (person['name'], person['role'], order)).lastrowid
        connection.execute('''UPDATE teacher SET name=?, role=?, category=?, photo_url=?, sort_order=?,
            specialization=NULL, bio=NULL, emoji=NULL, experience_years=NULL, at_center_since=NULL,
            education=NULL, awards=NULL, category_rank=NULL, quote=NULL, works_with_ages=NULL,
            updated_at=CURRENT_TIMESTAMP WHERE id=?''',
            (person['name'], person['role'], person['category'], '/static/uploads/teachers/20260914/' + person['photo'], order, teacher_id))
    for page_id, content in connection.execute('SELECT id, content_json FROM page').fetchall():
        blocks = json.loads(content)
        updated = []
        for block in blocks:
            kind = block.get('component', block.get('type'))
            if kind == 'team_stats':
                continue  # Unconfirmed demo statistics and attributed quotations.
            if kind == 'teachers_grid':
                data = block.get('data', block.get('payload', {}))
                data.pop('team_stats', None)
                data['title'] = 'Педагоги и специалисты центра'
                data['subtitle'] = 'Знакомьтесь с командой «Семицветика».'
                if data.get('limit'):
                    data['limit'] = 4
            updated.append(block)
        if updated != json.loads(content):
            connection.execute('UPDATE page SET content_json=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', (json.dumps(updated, ensure_ascii=False), page_id))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, default=ROOT / 'data/semicvetik.db')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    connection = sqlite3.connect(f'file:{args.database}?mode=rw', uri=True)
    if args.apply:
        for person in ROSTER:
            if not (ROOT / 'app/static/uploads/teachers/20260914' / person['photo']).is_file():
                raise SystemExit('Missing photo: ' + person['photo'])
        backup = args.database.with_name(args.database.name + '.backup-teachers-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
        with sqlite3.connect(backup) as target:
            connection.backup(target)
        print('Timestamped database backup created')
    connection.execute('BEGIN')
    try:
        update(connection)
        print('Confirmed roster:')
        for name, role in connection.execute('SELECT name, role FROM teacher ORDER BY sort_order'):
            print(name + ' — ' + role)
        if args.apply:
            connection.commit()
        else:
            connection.rollback()
            print('Dry run: rolled back')
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()
