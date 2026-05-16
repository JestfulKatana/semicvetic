from __future__ import annotations

from datetime import date, datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

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


def _ru_plural(n: int, forms: tuple[str, str, str]) -> str:
    n = abs(n) % 100
    n1 = n % 10
    if 10 < n < 20:
        return forms[2]
    if 1 < n1 < 5:
        return forms[1]
    if n1 == 1:
        return forms[0]
    return forms[2]


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
    total = len(pinned) + len(rest)
    count_label = f"{total} {_ru_plural(total, ('материал', 'материала', 'материалов'))}"
    return render_template(
        "admin/news/list.html",
        pinned=pinned,
        posts=rest,
        count_label=count_label,
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
        form_data=None,
    )


@bp.post("/new")
@login_required
def create():
    cleaned, error = _validate_form(request.form)
    if error:
        flash(error, "error")
        return render_template(
            "admin/news/form.html",
            post=None,
            form_action=url_for("news_admin.create"),
            today_str=date.today().isoformat(),
            form_data=cleaned,
        )

    post = Event(type="news")
    _apply_cleaned(post, cleaned, is_new=True)
    db.session.add(post)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Не удалось сохранить — slug уже занят, попробуйте другой.", "error")
        return render_template(
            "admin/news/form.html",
            post=None,
            form_action=url_for("news_admin.create"),
            today_str=date.today().isoformat(),
            form_data=cleaned,
        )
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
        form_data=None,
    )


@bp.post("/<int:post_id>/edit")
@login_required
def update(post_id: int):
    post = Event.query.filter_by(id=post_id, type="news").first_or_404()
    cleaned, error = _validate_form(request.form)
    if error:
        flash(error, "error")
        return render_template(
            "admin/news/form.html",
            post=post,
            form_action=url_for("news_admin.update", post_id=post.id),
            today_str=date.today().isoformat(),
            form_data=cleaned,
        )

    _apply_cleaned(post, cleaned, is_new=False)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Не удалось сохранить — slug уже занят, попробуйте другой.", "error")
        return render_template(
            "admin/news/form.html",
            post=post,
            form_action=url_for("news_admin.update", post_id=post.id),
            today_str=date.today().isoformat(),
            form_data=cleaned,
        )
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


def _validate_form(form) -> tuple[dict, str | None]:
    title = (form.get("title") or "").strip()
    cleaned = {
        "title": title,
        "slug": (form.get("slug") or "").strip(),
        "excerpt": (form.get("excerpt") or "").strip(),
        "body_html": form.get("body_html") or "",
        "image_url": (form.get("image_url") or "").strip(),
        "event_date_raw": form.get("event_date") or "",
        "category": (form.get("category") or "").strip(),
        "is_published": bool(form.get("is_published")),
        "is_pinned": bool(form.get("is_pinned")),
    }
    if not title:
        return cleaned, "Заголовок обязателен."
    if len(title) > 255:
        return cleaned, "Заголовок слишком длинный (максимум 255 символов)."
    return cleaned, None


def _apply_cleaned(post: Event, cleaned: dict, *, is_new: bool) -> None:
    post.title = cleaned["title"]
    base_slug = slugify(cleaned["slug"] or cleaned["title"])
    post.slug = ensure_unique_slug(base_slug, Event, exclude_id=None if is_new else post.id)
    post.excerpt = cleaned["excerpt"] or None
    post.body_html = sanitize_html(cleaned["body_html"]) or None
    post.image_url = cleaned["image_url"] or None
    post.event_date = _parse_date(cleaned["event_date_raw"]) or date.today()
    post.category = cleaned["category"] or None
    post.is_published = cleaned["is_published"]
    post.is_pinned = cleaned["is_pinned"]
    # В content не зеркалим — это поле обслуживает /blog/<slug>/ через markdown,
    # смешивать форматы вредно. news_detail.html читает body_html напрямую.
