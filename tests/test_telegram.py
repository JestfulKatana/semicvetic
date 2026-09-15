import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import requests

from app import create_app
from app.extensions import db, limiter
from app.models import Lead, TelegramDelivery
from app.utils.telegram import deliver_pending
from config import Config


class TelegramTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(Config, 'SQLALCHEMY_DATABASE_URI', 'sqlite://'), patch.object(Config, 'AUTO_SEED', False):
            cls.app = create_app()
        cls.app.config.update(TESTING=True, MAINTENANCE_MODE=False, RATELIMIT_ENABLED=False,
                              TELEGRAM_BOT_TOKEN='test-token', TELEGRAM_CHAT_IDS='111,222,111')

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def setUp(self):
        self.ctx = self.app.app_context()
        self.ctx.push()
        limiter.reset()
        db.session.query(TelegramDelivery).delete()
        db.session.query(Lead).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        self.ctx.pop()

    def submit(self):
        return self.app.test_client().post('/api/lead', json={'phone': '+79990000000', 'name': 'Тест', 'source_page': '/anglijskij/'})

    @patch('app.utils.telegram.requests.post')
    def test_missing_lead_does_not_crash_worker(self, post):
        self.submit()
        db.session.query(Lead).delete()
        db.session.commit()
        self.assertEqual(deliver_pending(), 0)
        self.assertEqual(db.session.query(TelegramDelivery).filter_by(last_error="lead_missing").count(), 2)
        post.assert_not_called()

    def test_lead_admin_preserves_records_and_delivery_is_read_only(self):
        from app.extensions import admin
        lead_view = next(view for view in admin._views if getattr(view, "model", None) is Lead)
        self.assertFalse(lead_view.can_delete)
        delivery_view = next(view for view in admin._views if getattr(view, "model", None) is TelegramDelivery)
        self.assertFalse(delivery_view.can_create)
        self.assertFalse(delivery_view.can_edit)
        self.assertFalse(delivery_view.can_delete)

    @patch('app.utils.telegram.requests.post')
    def test_request_saves_lead_and_two_deliveries_without_network(self, post):
        self.assertEqual(self.submit().status_code, 200)
        self.assertEqual(db.session.query(Lead).count(), 1)
        self.assertEqual(db.session.query(TelegramDelivery).count(), 2)
        post.assert_not_called()

    @patch('app.utils.telegram.requests.post')
    def test_partial_failure_retries_only_unsent_and_redacts_errors(self, post):
        self.submit()
        post.side_effect = [requests.ConnectionError('test-token +79990000000'), Mock(json=lambda: {'ok': True})]
        with self.assertLogs('app.utils.telegram', level='WARNING') as logs:
            self.assertEqual(deliver_pending(), 1)
        self.assertNotIn('test-token', ''.join(logs.output))
        self.assertNotIn('+79990000000', ''.join(logs.output))
        rows = db.session.query(TelegramDelivery).order_by(TelegramDelivery.id).all()
        self.assertIsNone(rows[0].sent_at)
        self.assertIsNotNone(rows[1].sent_at)
        self.assertGreater(rows[0].next_attempt_at, datetime.utcnow())
        rows[0].next_attempt_at = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()
        post.reset_mock(side_effect=True)
        post.return_value = Mock(json=lambda: {'ok': True})
        self.assertEqual(deliver_pending(), 1)
        self.assertEqual(post.call_count, 1)
        self.assertEqual(post.call_args.kwargs['json']['chat_id'], '111')
        self.assertEqual(deliver_pending(), 0)

    @patch('app.utils.telegram.requests.post')
    def test_api_rejection_is_not_success_and_future_lease_is_skipped(self, post):
        self.submit()
        post.return_value = Mock(json=lambda: {'ok': False})
        self.assertEqual(deliver_pending(), 0)
        self.assertEqual(db.session.query(TelegramDelivery).filter(TelegramDelivery.sent_at.is_not(None)).count(), 0)
        post.reset_mock()
        self.assertEqual(deliver_pending(), 0)
        post.assert_not_called()

    @patch('app.utils.telegram.requests.post')
    def test_validation_and_failed_transaction_leave_no_orphan_delivery(self, post):
        response = self.app.test_client().post('/api/lead', json={'phone': 'bad'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(db.session.query(TelegramDelivery).count(), 0)
        with patch('app.views.api.db.session.commit', side_effect=RuntimeError('db unavailable')):
            with self.assertRaises(RuntimeError):
                self.submit()
        db.session.rollback()
        self.assertEqual(db.session.query(Lead).count(), 0)
        self.assertEqual(db.session.query(TelegramDelivery).count(), 0)


class DeliveryMigrationTest(unittest.TestCase):
    def test_upgrade_preserves_existing_leads_and_is_repeatable(self):
        import importlib.util
        from pathlib import Path
        import sqlalchemy as sa
        from alembic.migration import MigrationContext
        from alembic.operations import Operations
        path = Path(__file__).resolve().parents[1] / 'migrations/versions/20260915_telegram_delivery.py'
        spec = importlib.util.spec_from_file_location('delivery_migration', path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        engine = sa.create_engine('sqlite://')
        try:
            with engine.begin() as connection:
                connection.exec_driver_sql('CREATE TABLE lead (id INTEGER PRIMARY KEY, phone TEXT)')
                connection.exec_driver_sql("INSERT INTO lead VALUES (1, 'test-value')")
                migration.op = Operations(MigrationContext.configure(connection))
                migration.upgrade()
                migration.upgrade()
                self.assertTrue(sa.inspect(connection).has_table('telegram_delivery'))
                self.assertEqual(connection.exec_driver_sql('SELECT phone FROM lead').scalar(), 'test-value')
        finally:
            engine.dispose()
