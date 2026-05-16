from __future__ import annotations

from datetime import date, datetime

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from ..extensions import db
from ..models import Event
from ..utils.content import sanitize_html
from ..utils.slug import ensure_unique_slug, slugify


bp = Blueprint("news_admin", __name__, url_prefix="/admin/news")


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None


@bp.get("/")
@login_required
def index():
    pinned = (
        Event.query.filter_by(type="news", is_pinned=True)
        .order_by(Event.event_date.desc().nullslast(), Event.created_at.desc())
        .all()
    )
    rest = (
        Event.query.filter_by(type="news", is_pinned=False)
        .order_by(Event.event_date.desc().nullslast(), Event.created_at.desc())
        .all()
    )
    return render_template(
        "admin/news/list.html",
        pinned=pinned,
        posts=rest,
    )


@bp.get("/new")
@login_required
def new():
    today_str = date.today().isoformat()
    return render_template(
        "admin/news/form.html",
        post=None,
        form_action=url_for("news_admin.create"),
        today_str=today_str,
    )


@bp.post("/new")
@login_required
def create():
    post = Event(type="news")
    _apply_form(post, request.form, is_new=True)
    db.session.add(post)
    db.session.commit()
    flash("Новость создана", "success")
    return redirect(url_for("news_admin.edit", post_id=post.id))


@bp.get("/<int:post_id>/edit")
@login_required
def edit(post_id: int):
    post = Event.query.filter_by(id=post_id, type="news").first_or_404()
    return render_template(
        "admin/news/form.html",
        post=post,
        form_action=url_for("news_admin.update", post_id=post.id),
        today_str=date.today().isoformat(),
    )


@bp.post("/<int:post_id>/edit")
@login_required
def update(post_id: int):
    post = Event.query.filter_by(id=post_id, type="news").first_or_404()
    _apply_form(post, request.form, is_new=False)
    db.session.commit()
    flash("Изменения сохранены", "success")
    return redirect(url_for("news_admin.edit", post_id=post.id))


@bp.post("/<int:post_id>/delete")
@login_required
def delete(post_id: int):
    post = Event.query.filter_by(id=post_id, type="news").first_or_404()
    db.session.delete(post)
    db.session.commit()
    flash("Новость удалена", "success")
    return redirect(url_for("news_admin.index"))


def _apply_form(post: Event, form, *, is_new: bool) -> None:
    title = (form.get("title") or "").strip()
    if not title:
        abort(400, "Заголовок обязателен")
    post.title = title

    slug_input = (form.get("slug") or "").strip()
    base_slug = slugify(slug_input or title)
    post.slug = ensure_unique_slug(base_slug, Event, exclude_id=None if is_new else post.id)

    post.excerpt = (form.get("excerpt") or "").strip() or None
    post.body_html = sanitize_html(form.get("body_html") or "") or None
    post.image_url = (form.get("image_url") or "").strip() or None
    post.event_date = _parse_date(form.get("event_date"))
    post.category = (form.get("category") or "").strip() or None
    post.is_published = bool(form.get("is_published"))
    post.is_pinned = bool(form.get("is_pinned"))
    # Зеркалим в content для обратной совместимости /blog/<slug>/ и пр.,
    # храним plain-fallback вырезая теги.
    if post.body_html:
        from html import unescape
        import re as _re

        plain = _re.sub(r"<[^>]+>", "", post.body_html)
        post.content = unescape(plain).strip() or None
