from __future__ import annotations

import unittest
from unittest.mock import patch

from app import create_app
from app.extensions import db
from config import Config


class MaintenanceModeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (
            patch.object(Config, "SQLALCHEMY_DATABASE_URI", "sqlite://"),
            patch.object(Config, "AUTO_SEED", False),
        ):
            cls.app = create_app()
        cls.app.config.update(TESTING=True, MAINTENANCE_MODE=True)
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def test_public_page_returns_maintenance_screen(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 503)
        self.assertIn("Ведётся разработка нового сайта", response.get_data(as_text=True))
        self.assertEqual(response.headers["Retry-After"], "3600")
        self.assertEqual(response.headers["X-Robots-Tag"], "noindex, nofollow, noarchive")

    def test_operational_and_admin_routes_remain_available(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/login").status_code, 200)
        self.assertEqual(self.client.get("/admin/").status_code, 302)
        with self.client.get("/static/img/maintenance-shiba.webp") as response:
            self.assertEqual(response.status_code, 200)

    def test_robots_disallows_crawling(self):
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "User-agent: *\nDisallow: /\n")

    def test_lead_api_is_disabled(self):
        response = self.client.post("/api/lead", json={"phone": "+79990000000"})

        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.get_json()["ok"])

    def test_mode_can_be_disabled(self):
        self.app.config["MAINTENANCE_MODE"] = False
        try:
            response = self.client.get("/robots.txt")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Allow: /", response.get_data(as_text=True))
        finally:
            self.app.config["MAINTENANCE_MODE"] = True


if __name__ == "__main__":
    unittest.main()
