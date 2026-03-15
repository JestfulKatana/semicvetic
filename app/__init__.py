from __future__ import annotations

import logging
import os

import structlog
from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

from .admin import SecureAdminIndexView, init_admin
from .demo_seed import seed_database
from .extensions import admin, db, limiter, login_manager, metrics, migrate
from .models import AdminUser
from .views import api, auth, main


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    )


def create_app() -> Flask:
    load_dotenv()
    configure_logging()

    app = Flask(__name__)
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    os.makedirs("data", exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    metrics.init_app(app)
    admin.init_app(app, index_view=SecureAdminIndexView())
    init_admin()

    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(auth.bp)

    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id: str):
        return AdminUser.query.get(int(user_id))

    @app.template_filter("markdown")
    def markdown_filter(value):
        from .utils.content import render_markdown

        return render_markdown(value)

    @app.template_filter("phone_href")
    def phone_href_filter(value):
        from .utils.content import phone_href

        return phone_href(value)

    with app.app_context():
        db.create_all()
        if app.config["AUTO_SEED"]:
            seed_database()

    return app
