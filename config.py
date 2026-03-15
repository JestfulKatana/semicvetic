from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def normalize_database_url(raw_url: str | None) -> str:
    if not raw_url:
        return f"sqlite:///{(BASE_DIR / 'data' / 'semicvetik.db').as_posix()}"
    if raw_url.startswith("sqlite:///") and not raw_url.startswith("sqlite:////"):
        relative_path = raw_url.removeprefix("sqlite:///")
        return f"sqlite:///{(BASE_DIR / relative_path).as_posix()}"
    return raw_url


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = normalize_database_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:5000").rstrip("/")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    YANDEX_METRIKA_ID = os.getenv("YANDEX_METRIKA_ID", "")
    AUTO_SEED = os.getenv("AUTO_SEED", "true").lower() == "true"
    LEAD_RATE_LIMIT = os.getenv("LEAD_RATE_LIMIT", "5 per minute")
    RATELIMIT_STORAGE_URI = "memory://"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
