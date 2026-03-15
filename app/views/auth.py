from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..models import AdminUser


bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_url = request.args.get("next")
            return redirect(next_url or url_for("admin.index"))
        flash("Неверный логин или пароль", "error")

    return render_template("auth_login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))
