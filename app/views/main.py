from __future__ import annotations

from flask import current_app, Blueprint, make_response, render_template, request
from datetime import date

from ..utils.version_content import CATEGORIES, program_copy
from ..utils.content import hydrate_blocks

from ..models import Event, Page, Program, Review, SiteSetting, Teacher


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


def version_page(template, **values):
    ctx = shared_context()
    ctx.update({
        "program_copy": {p.slug: program_copy(p) for p in ctx["programs"]},
        "categories": CATEGORIES,
        "terms_verified": ctx["settings"].get("program_terms_verified") == "true",
        "selected_program": request.args.get("program", ""),
        "year": date.today().year,
        "today": date.today(),
    })
    ctx.update(values)
    return render_template("version/" + template + ".html", **ctx)


def composed_page(page):
    # Preserve the complete editor contract for custom pages outside the new named layouts.
    return render_template(
        "pages/content_page.html", page=page,
        blocks=hydrate_blocks(page.blocks, shared_context()),
        page_title=page.meta_title or page.title,
        page_description=page.meta_description or page.hero_subtitle,
    )


@bp.app_context_processor
def inject_global_context():
    ctx = shared_context()
    return {
        "site_settings": ctx["settings"],
        "nav_pages": ctx["nav_pages"],
        "programs": ctx["programs"],
        "news": ctx["news"],
        "year": date.today().year,
    }


@bp.route("/")
def home():
    Page.query.filter_by(slug="home", is_published=True).first_or_404()
    return version_page("home", page_title="Детский центр в Сергиевом Посаде", page_description="Занятия, творчество, подготовка к школе и поддержка специалистов в центре Семицветик. Познакомьтесь с программами и педагогами.")


@bp.route("/novosti/")
def news_list():
    posts = Event.query.filter_by(type="news", is_published=True).order_by(Event.created_at.desc()).all()
    return version_page("posts", posts=posts, page_title="Новости центра", page_description="Занятия, события и истории из жизни Семицветика.")


@bp.route("/novosti/<slug>/")
def news_detail(slug):
    post = Event.query.filter_by(slug=slug, type="news", is_published=True).first_or_404()
    return version_page("article", post=post, page_title=post.title, page_description=post.excerpt)


@bp.route("/blog/<slug>/")
def article_detail(slug):
    post = Event.query.filter_by(slug=slug, type="article", is_published=True).first_or_404()
    return version_page("article", post=post, page_title=post.title, page_description=post.excerpt)


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


@bp.route("/<slug>/")
def slug_router(slug):
    if slug in ("privacy-policy", "politika-konfidencialnosti"):
        policy = Page.query.filter_by(slug=slug, is_published=True).first()
        if policy:
            return composed_page(policy)
        return version_page("privacy", page_title="Данные заявки")
    program = Program.query.filter_by(slug=slug, is_published=True).first()
    if program:
        programs = Program.query.filter_by(is_published=True).order_by(Program.sort_order, Program.name).all()
        detail = program_copy(program)
        return version_page("program", program=program, detail=detail, program_index=programs.index(program)+1, selected_program=program.slug, page_title=program.name, page_description=detail["description"])
    page = Page.query.filter_by(slug=slug, is_published=True).first_or_404()
    templates = {"programmy":"catalog", "pedagogi":"teachers", "o-centre":"about", "ceny":"prices", "kontakty":"contacts"}
    if slug == "meropriyatiya":
        posts = Event.query.filter(Event.type.in_(["event", "article"]), Event.is_published.is_(True)).order_by(Event.event_date.desc()).all()
        return version_page("posts", posts=posts, page_title="Мероприятия", page_description="События и встречи в центре. У прошедших мероприятий стоит отметка «Архив».")
    if slug not in templates:
        return composed_page(page)
    return version_page(templates[slug], page=page, page_title=page.title, page_description={"programmy":"Занятия и направления детского центра Семицветик. Выберите программу или обратитесь за помощью с выбором.", "pedagogi":"Педагоги, специалисты и администраторы Семицветика: фотографии, имена и специализации.", "o-centre":"Познакомьтесь с центром Семицветик, его занятиями и командой.", "ceny":"Уточните стоимость, расписание и условия посещения занятий в Семицветике.", "kontakty":"Адрес и контакты центра Семицветик в Сергиевом Посаде. Свяжитесь с администратором и договоритесь о посещении."}.get(slug, page.meta_description or page.hero_subtitle))


@bp.app_errorhandler(404)
def page_not_found(error):
    return version_page("error", page_title="Страница не найдена", page_description="Вернитесь к занятиям и педагогам центра Семицветик."), 404
