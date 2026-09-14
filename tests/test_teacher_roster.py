import json
import sqlite3
import unittest

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import sqlite

from app.models import Teacher, Page, Program
from scripts.update_teachers_20260914 import ROSTER, update


class TeacherRosterTest(unittest.TestCase):
    def test_update_preserves_real_ids_and_unrelated_content_and_is_repeatable(self):
        connection = sqlite3.connect(':memory:')
        self.addCleanup(connection.close)
        for model in (Teacher, Page, Program):
            connection.execute(str(CreateTable(model.__table__).compile(dialect=sqlite.dialect())))
        connection.execute("INSERT INTO teacher(id,name,role,sort_order,experience_years,created_at,updated_at) VALUES (14,'Дёмина Ирина Александровна','Психолог',2,12,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP),(3,'Ольга Савельева','Демо',3,9,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)")
        connection.execute("INSERT INTO program(id,slug,name,landing_json,sort_order,has_landing,is_published,teacher_id,created_at,updated_at) VALUES(1,'early','Early','[]',1,1,1,3,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)")
        blocks = [{'component':'hero','data':{'title':'Keep me'}}, {'component':'teachers_grid','data':{'source':'all_teachers','limit':2,'team_stats':{'quote':'demo'}}}]
        connection.execute('INSERT INTO page(slug,title,content_json,is_published,sort_order,created_at,updated_at) VALUES(?,?,?,?,?,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)', ('home','Home',json.dumps(blocks),1,1))
        update(connection)
        first = connection.execute('SELECT id,name,role,photo_url FROM teacher ORDER BY sort_order').fetchall()
        update(connection)
        self.assertEqual(first, connection.execute('SELECT id,name,role,photo_url FROM teacher ORDER BY sort_order').fetchall())
        self.assertEqual(len(first), 10)
        self.assertEqual([r[1] for r in first], [p['name'] for p in ROSTER])
        self.assertEqual(connection.execute('SELECT name,experience_years FROM teacher WHERE id=14').fetchone(), ('Демина Ирина Александровна',None))
        self.assertIsNone(connection.execute('SELECT teacher_id FROM program').fetchone()[0])
        changed = json.loads(connection.execute('SELECT content_json FROM page').fetchone()[0])
        self.assertEqual(changed[0], blocks[0])
        self.assertNotIn('team_stats', changed[1]['data'])
