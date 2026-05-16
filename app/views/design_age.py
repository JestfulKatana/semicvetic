"""
Designer mockups blueprint — Age-picker redesign.

Live preview for the "С какого года ваш ребёнок?" block.
Mounted at /design/.
Templates extend base.html so real header/footer/CSS apply.

Routes:
    /design/age      — index with 3 thumbs
    /design/age-v1   — Safe: огромный возрастной свитчер
    /design/age-v2   — Evolve: таймлайн взросления
    /design/age-v3   — Bold: JTBD-фрейм («зачем вы пришли»)

Do NOT remove without designer/owner consent.
"""
from __future__ import annotations

from flask import Blueprint, render_template


design_age_bp = Blueprint("design_age", __name__, url_prefix="/design")


@design_age_bp.route("/age")
@design_age_bp.route("/age/")
def age_index():
    return render_template(
        "design/age_index.html",
        page_title="Age picker — варианты на выбор",
    )


@design_age_bp.route("/age-v1")
@design_age_bp.route("/age-v1/")
def age_v1():
    return render_template(
        "design/age_v1.html",
        page_title="Age V1 — Возрастной свитчер",
    )


@design_age_bp.route("/age-v2")
@design_age_bp.route("/age-v2/")
def age_v2():
    return render_template(
        "design/age_v2.html",
        page_title="Age V2 — Таймлайн взросления",
    )


@design_age_bp.route("/age-v3")
@design_age_bp.route("/age-v3/")
def age_v3():
    return render_template(
        "design/age_v3.html",
        page_title="Age V3 — Что нужно ребёнку сейчас",
    )
