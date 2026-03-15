from __future__ import annotations

from flask import current_app, Blueprint, abort, make_response, render_template

from ..models import Event, Page, Program, Review, SiteSetting, Teacher
from ..utils.content import hydrate_blocks
from ..utils.seo import build_course_schema, build_org_schema


bp = Blueprint("main", __name__)


def shared_context(current_program=None) -> dict:
    settings = SiteSetting.get_map()
    settings.setdefault("site_name", "Семицветик")
    settings.setdefault("site_url", current_app.config["SITE_URL"])
    programs = Program.query.filter_by(is_published=True).order_by(Program.sort_order, Program.name).all()
    teachers = Teacher.query.order_by(Teacher.sort_order, Teacher.name).all()
    reviews = Review.query.filter_by(is_published=True).all()
    events = (
        Event.query.filter_by(type="event", is_published=True)
        .order_by(Event.event_date.asc(), Event.created_at.desc())
        .all()
    )
    articles = (
        Event.query.filter_by(type="article", is_published=True)
        .order_by(Event.created_at.desc())
        .all()
    )
    nav_pages = (
        Page.query.filter(Page.is_published.is_(True), Page.slug != "home")
        .order_by(Page.sort_order, Page.title)
        .all()
    )
    return {
        "settings": settings,
        "programs": programs,
        "teachers": teachers,
        "reviews": reviews,
        "events": events,
        "articles": articles,
        "nav_pages": nav_pages,
        "current_program": current_program,
    }


@bp.app_context_processor
def inject_global_context():
    ctx = shared_context()
    return {"site_settings": ctx["settings"], "nav_pages": ctx["nav_pages"]}


@bp.route("/")
def home():
    page = Page.query.filter_by(slug="home", is_published=True).first_or_404()
    ctx = shared_context()
    return render_template(
        "pages/content_page.html",
        page=page,
        blocks=hydrate_blocks(page.blocks, ctx),
        page_title=page.meta_title or page.title,
        page_description=page.meta_description or page.hero_subtitle,
        page_schema=build_org_schema(ctx["settings"]),
    )


@bp.route("/blog/<slug>/")
def article_detail(slug: str):
    article = Event.query.filter_by(slug=slug, type="article", is_published=True).first_or_404()
    ctx = shared_context()
    return render_template(
        "pages/article_detail.html",
        article=article,
        page_title=article.title,
        page_description=article.excerpt,
        page_schema={
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": article.title,
            "description": article.excerpt,
        },
        **ctx,
    )


@bp.route("/sitemap.xml")
def sitemap():
    pages = Page.query.filter_by(is_published=True).all()
    programs = Program.query.filter_by(is_published=True).all()
    articles = Event.query.filter_by(is_published=True, type="article").all()
    response = make_response(
        render_template("sitemap.xml", pages=pages, programs=programs, articles=articles)
    )
    response.headers["Content-Type"] = "application/xml"
    return response


@bp.route("/robots.txt")
def robots():
    response = make_response(
        "User-agent: *\nAllow: /\nSitemap: " + current_app.config["SITE_URL"] + "/sitemap.xml\n"
    )
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response


@bp.route("/health")
def health():
    return {"ok": True}


@bp.route("/<slug>/")
def slug_router(slug: str):
    program = Program.query.filter_by(slug=slug, is_published=True).first()
    if program:
        ctx = shared_context(current_program=program)
        return render_template(
            "pages/content_page.html",
            page=program,
            blocks=hydrate_blocks(program.landing_blocks, ctx),
            page_title=program.name,
            page_description=program.tagline,
            page_schema=build_course_schema(program),
        )

    page = Page.query.filter_by(slug=slug, is_published=True).first()
    if page:
        ctx = shared_context()
        return render_template(
            "pages/content_page.html",
            page=page,
            blocks=hydrate_blocks(page.blocks, ctx),
            page_title=page.meta_title or page.title,
            page_description=page.meta_description or page.hero_subtitle,
            page_schema=build_org_schema(ctx["settings"]),
        )

    abort(404)
