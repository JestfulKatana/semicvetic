from __future__ import annotations

from flask import redirect, request, url_for
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms import PasswordField, TextAreaField

from .extensions import admin, db
from .models import (
    AdminUser,
    Event,
    Lead,
    Page,
    Program,
    ProgramSubject,
    Review,
    ScheduleSlot,
    SiteSetting,
    Teacher,
)


class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))


class SecureModelView(ModelView):
    can_view_details = True
    create_modal = False
    edit_modal = False
    page_size = 50

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login", next=request.url))


class AdminUserView(SecureModelView):
    column_list = ("username",)
    form_excluded_columns = ("password_hash",)
    form_extra_fields = {"password": PasswordField("Новый пароль")}

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)


class JsonModelView(SecureModelView):
    form_overrides = {
        "content_json": TextAreaField,
        "landing_json": TextAreaField,
        "description": TextAreaField,
        "bio": TextAreaField,
        "content": TextAreaField,
        "excerpt": TextAreaField,
        "note": TextAreaField,
    }


def init_admin() -> None:
    if any(getattr(view, "name", "") == "Настройки" for view in admin._views):
        return
    admin.add_view(JsonModelView(SiteSetting, db.session, name="Настройки"))
    admin.add_view(JsonModelView(Page, db.session, name="Страницы"))
    admin.add_view(JsonModelView(Program, db.session, name="Программы"))
    admin.add_view(SecureModelView(ScheduleSlot, db.session, name="Расписание"))
    admin.add_view(SecureModelView(ProgramSubject, db.session, name="Предметы"))
    admin.add_view(JsonModelView(Teacher, db.session, name="Педагоги"))
    admin.add_view(JsonModelView(Review, db.session, name="Отзывы"))
    admin.add_view(JsonModelView(Event, db.session, name="События и статьи"))
    admin.add_view(JsonModelView(Lead, db.session, name="Заявки"))
    admin.add_view(AdminUserView(AdminUser, db.session, name="Админы"))
