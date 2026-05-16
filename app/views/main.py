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
    news = (
        Event.query.filter_by(type="news", is_published=True)
        .order_by(Event.is_pinned.desc(), Event.event_date.desc().nullslast(), Event.created_at.desc())
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
        "news": news,
        "nav_pages": nav_pages,
        "current_program": current_program,
    }


@bp.app_context_processor
def inject_global_context():
    ctx = shared_context()
    return {
        "site_settings": ctx["settings"],
        "nav_pages": ctx["nav_pages"],
        "programs": ctx["programs"],
        "news": ctx["news"],
    }


@bp.route("/")
def home():
    page = Page.query.filter_by(slug="home", is_published=True).first_or_404()
    ctx = shared_context()
    return render_template(
        "pages/home.html",
        page=page,
        blocks=hydrate_blocks(page.blocks, ctx),
        page_title=page.meta_title or page.title,
        page_description=page.meta_description or page.hero_subtitle,
        page_schema=build_org_schema(ctx["settings"]),
    )


@bp.route("/novosti/")
def news_list():
    ctx = shared_context()
    return render_template(
        "pages/news_list.html",
        news=ctx["news"],
        page_title="Новости центра «Семицветик»",
        page_description="Что происходит в центре: события, наборы, поздравления и новости из жизни наших ребят.",
    )


@bp.route("/novosti/<slug>/")
def news_detail(slug: str):
    post = Event.query.filter_by(slug=slug, type="news", is_published=True).first_or_404()
    ctx = shared_context()
    related = [n for n in ctx["news"] if n.id != post.id][:3]
    site_url = current_app.config["SITE_URL"].rstrip("/")
    image_abs = (
        (site_url + post.image_url)
        if post.image_url and post.image_url.startswith("/")
        else post.image_url
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": post.title,
        "description": post.excerpt,
        "datePublished": (post.event_date or post.created_at.date()).isoformat(),
    }
    if image_abs:
        schema["image"] = image_abs
    return render_template(
        "pages/news_detail.html",
        post=post,
        related=related,
        page_title=post.title,
        page_description=post.excerpt or (post.title + " — новости центра Семицветик"),
        og_image=image_abs,
        og_type="article",
        page_schema=schema,
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
    news = Event.query.filter_by(is_published=True, type="news").all()
    response = make_response(
        render_template(
            "sitemap.xml",
            pages=pages,
            programs=programs,
            articles=articles,
            news=news,
        )
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


# Slug -> название включаемого шаблона компонента из templates/components/program_landing/
# для специальных продакт-лендингов (E-варианты из handoff 2026-05-09).
PROGRAM_LANDING_E = {
    "podgotovka-k-shkole": "school",
    "anglijskij": "english",
    "logoped": "speech",
    "rannee-razvitie": "early",
}


@bp.route("/<slug>/")
def slug_router(slug: str):
    program = Program.query.filter_by(slug=slug, is_published=True).first()
    if program:
        ctx = shared_context(current_program=program)
        landing_e = PROGRAM_LANDING_E.get(slug)
        if landing_e:
            return render_template(
                "pages/program_landing_e.html",
                page=program,
                program_landing_e=landing_e,
                page_title=program.name,
                page_description=program.tagline,
                page_schema=build_course_schema(program),
            )
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
