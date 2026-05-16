"""
Designer mockups blueprint.

Live preview for CTA redesign variants. Mounted at /design/.
These templates extend base.html so that real header/footer/CSS apply.
Lead forms reuse `data-lead-form` and POST to the production lead endpoint.

Do NOT remove without designer/owner consent — these URLs are shared for review.
"""
from __future__ import annotations

from flask import Blueprint, render_template


bp = Blueprint("design", __name__, url_prefix="/design")


@bp.route("/all")
@bp.route("/all/")
@bp.route("/overview")
@bp.route("/overview/")
def overview():
    return render_template(
        "design/overview.html",
        page_title="Все варианты редизайна",
    )


@bp.route("/cta")
@bp.route("/cta/")
def cta_index():
    return render_template("design/cta_index.html", page_title="CTA — варианты на выбор")


@bp.route("/cta-v1")
@bp.route("/cta-v1/")
def cta_v1():
    return render_template(
        "design/cta_v1.html",
        page_title="CTA V1 — Тёплый разговор",
    )


@bp.route("/cta-v2")
@bp.route("/cta-v2/")
def cta_v2():
    return render_template(
        "design/cta_v2.html",
        page_title="CTA V2 — Пробное за 1 клик",
    )


@bp.route("/cta-v3")
@bp.route("/cta-v3/")
def cta_v3():
    return render_template(
        "design/cta_v3.html",
        page_title="CTA V3 — Голос родителя",
    )
