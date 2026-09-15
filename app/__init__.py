from __future__ import annotations

import logging
import os

import structlog
from flask import Flask, jsonify, make_response, render_template, request
from flask_login import current_user
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

from .admin import SecureAdminIndexView, init_admin
from .demo_seed import seed_database
from .extensions import admin, csrf, db, limiter, login_manager, metrics, migrate
from .models import AdminUser
from .views import admin_media, api, auth, design, main, news_admin
from .views.design_age import design_age_bp
from .views.design_programs import design_programs_bp
from .views.design_teachers import design_teachers_bp


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
    csrf.init_app(app)

    from .telegram_worker import telegram_worker
    app.cli.add_command(telegram_worker)

    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin_media.bp)
    app.register_blueprint(news_admin.bp)
    app.register_blueprint(design.bp)
    app.register_blueprint(design_teachers_bp)
    app.register_blueprint(design_programs_bp)
    app.register_blueprint(design_age_bp)

    # /api/lead — публичная форма заявки. Прокидывать токен через JS-фронт
    # сложнее, чем обеспечить SameSite=Lax + honeypot + rate-limit, поэтому
    # именно этот blueprint оставляем без CSRF. Exempt после register, чтобы
    # Flask-WTF корректно зарегистрировал имена endpoints.
    csrf.exempt(api.bp)

    login_manager.login_view = "auth.login"

    @app.before_request
    def maintenance_mode():
        if not app.config["MAINTENANCE_MODE"]:
            return None

        path = request.path
        if (
            path in {"/health", "/login", "/logout", "/metrics", "/admin"}
            or path.startswith(("/static/", "/admin/"))
        ):
            return None
        if path == "/robots.txt":
            response = make_response("User-agent: *\nDisallow: /\n")
            response.headers["Content-Type"] = "text/plain; charset=utf-8"
            return response
        if path.startswith("/api/"):
            return jsonify({"ok": False, "message": "Сайт временно обновляется"}), 503

        if current_user.is_authenticated:
            return None

        response = make_response(render_template("maintenance.html"), 503)
        response.headers["Retry-After"] = "3600"
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response

    @app.after_request
    def protect_maintenance_preview(response):
        if app.config["MAINTENANCE_MODE"]:
            response.headers["Cache-Control"] = "no-store, max-age=0"
            response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response

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
        from sqlalchemy import inspect
        fresh_database = not inspect(db.engine).has_table("lead")
        db.metadata.create_all(db.engine, tables=[
            table for table in db.metadata.sorted_tables
            if fresh_database or table.name != "telegram_delivery"
        ])
        from .utils.db_migrations import ensure_runtime_schema

        ensure_runtime_schema(db)
        if app.config["AUTO_SEED"]:
            seed_database()

    return app
