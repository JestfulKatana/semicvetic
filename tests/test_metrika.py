import unittest
from flask import Flask
from app.views.main import metrika_counter


class MetrikaTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(MAINTENANCE_MODE=False, YANDEX_METRIKA_ID='')

    def test_config_and_database_counter_are_supported(self):
        with self.app.test_request_context('/', base_url='https://cvetik.example'):
            self.assertEqual(metrika_counter({'yandex_metrika_id': '12345'}), 12345)
            self.app.config['YANDEX_METRIKA_ID'] = '67890'
            self.assertEqual(metrika_counter({'yandex_metrika_id': '12345'}), 67890)

    def test_invalid_counter_is_not_embedded_in_script(self):
        with self.app.test_request_context('/', base_url='https://cvetik.example'):
            for value in ['', '0', '-1', '123;alert(1)', '１２３', '1' * 20]:
                self.assertIsNone(metrika_counter({'yandex_metrika_id': value}))

    def test_local_admin_and_maintenance_do_not_track(self):
        for origin, path in [('http://localhost:5096','/'), ('http://127.0.0.1:5096','/'), ('http://[::1]','/'), ('https://cvetik.example','/login'), ('https://cvetik.example','/admin/')]:
            with self.app.test_request_context(path, base_url=origin):
                self.assertIsNone(metrika_counter({'yandex_metrika_id':'12345'}))
        self.app.config['MAINTENANCE_MODE'] = True
        with self.app.test_request_context('/',base_url='https://cvetik.example'):
            self.assertIsNone(metrika_counter({'yandex_metrika_id':'12345'}))
