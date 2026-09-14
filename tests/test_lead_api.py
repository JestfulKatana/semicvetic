from __future__ import annotations

import unittest
from unittest.mock import patch

from flask import Flask

from app.extensions import db, limiter
from app.models import Lead, Program
from app.views.api import bp


class LeadAPITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)
        cls.app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI='sqlite://',
                              LEAD_RATE_LIMIT='5 per minute', RATELIMIT_STORAGE_URI='memory://')
        db.init_app(cls.app)
        limiter.init_app(cls.app)
        cls.app.register_blueprint(bp)
        with cls.app.app_context():
            db.create_all()
            db.session.add_all([Program(slug='speech', name='Логопедия'),
                                Program(slug='draft', name='Черновик', is_published=False)])
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def setUp(self):
        self.client = self.app.test_client()
        with self.app.app_context():
            limiter.reset()
            Lead.query.delete()
            db.session.commit()
        self.notify = patch('app.views.api.send_lead_notification', return_value=False).start()
        self.addCleanup(patch.stopall)

    def post(self, **changes):
        data = dict(phone='8 (999) 000-00-00', consent='on', name='Тест')
        data.update(changes)
        return self.client.post('/api/lead', json=data)

    def test_context_survives_submission_and_reaches_notification(self):
        response = self.post(program_slug='speech', preference='После 18:00', child_age='5')
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            lead = Lead.query.one()
            self.assertEqual(lead.phone, '+79990000000')
            self.assertEqual(lead.child_age, '5')
            self.assertIn('Логопедия (speech)', lead.note)
            self.assertIn('После 18:00', lead.note)
            self.assertIn('Согласие', lead.note)
        self.notify.assert_called_once()
        self.assertIn("После 18:00", self.notify.call_args.args[0].note)

    def test_form_data_without_program_is_accepted(self):
        response = self.client.post('/api/lead', data={'phone': '+79990000000', 'consent': 'on'})
        self.assertEqual(response.status_code, 200)

    def test_invalid_input_never_creates_lead(self):
        cases = [dict(program_slug='missing'), dict(program_slug='draft'),
                 dict(phone='letters79990000000'), dict(phone=123), dict(phone='123'),
                 dict(consent=False), dict(preference='x' * 501), dict(name=['bad'])]
        for changes in cases:
            with self.subTest(changes=changes):
                with self.app.app_context():
                    limiter.reset()
                self.assertEqual(self.post(**changes).status_code, 400)
        with self.app.app_context():
            self.assertEqual(Lead.query.count(), 0)
        self.notify.assert_not_called()

    def test_non_object_json_is_rejected(self):
        self.assertEqual(self.client.post('/api/lead', json=['invalid']).status_code, 400)

    def test_honeypot_does_not_create_or_notify(self):
        self.assertEqual(self.post(company='spam').status_code, 200)
        with self.app.app_context():
            self.assertEqual(Lead.query.count(), 0)
        self.notify.assert_not_called()

    def test_existing_rate_limit_returns_actionable_json(self):
        for _ in range(5):
            self.assertEqual(self.post().status_code, 200)
        response = self.post()
        self.assertEqual(response.status_code, 429)
        self.assertFalse(response.get_json()['ok'])
        self.assertEqual(self.notify.call_count, 5)
