"""
Designer mockups blueprint — TEACHERS BLOCK on homepage.

Live preview for 3 redesign variants of «Педагоги, которые знают школьные требования».
Mounted at /design/. Templates extend base.html so the real header/footer/CSS apply.

URLs:
    /design/teachers      — index page with 3 variants
    /design/teachers-v1   — Safe: «Команда у входа» (директор + 3 учителя)
    /design/teachers-v2   — Evolve: «Анатомия команды» (роли + коллаж)
    /design/teachers-v3   — Bold: «Лента действующих учителей» (горизонтальная карусель)

Do NOT remove without designer/owner consent — links are shared for review.
Register this blueprint in app/__init__.py as `design_teachers_bp`.
"""
from __future__ import annotations

from flask import Blueprint, render_template


design_teachers_bp = Blueprint("design_teachers", __name__, url_prefix="/design")


@design_teachers_bp.route("/teachers")
@design_teachers_bp.route("/teachers/")
def teachers_index():
    return render_template(
        "design/teachers_index.html",
        page_title="Педагоги — варианты на выбор",
    )


@design_teachers_bp.route("/teachers-v1")
@design_teachers_bp.route("/teachers-v1/")
def teachers_v1():
    return render_template(
        "design/teachers_v1.html",
        page_title="Педагоги V1 — Команда у входа",
    )


@design_teachers_bp.route("/teachers-v2")
@design_teachers_bp.route("/teachers-v2/")
def teachers_v2():
    return render_template(
        "design/teachers_v2.html",
        page_title="Педагоги V2 — Анатомия команды",
    )


@design_teachers_bp.route("/teachers-v3")
@design_teachers_bp.route("/teachers-v3/")
def teachers_v3():
    return render_template(
        "design/teachers_v3.html",
        page_title="Педагоги V3 — Лента учителей",
    )
