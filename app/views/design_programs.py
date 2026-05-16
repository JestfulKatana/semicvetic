"""
Designer mockups blueprint — «Программы центра» (главная).

Live preview для 3 вариантов редизайна блока программ.
Шаблоны extendят base.html, поэтому шапка/футер/шрифты/палитра реальные.
Прод-главная (`/`) НЕ тронута; данные программ замоканы внутри view.

Не удалять без согласия дизайнера/владельца — URL расшарены для ревью.
"""
from __future__ import annotations

from flask import Blueprint, render_template


design_programs_bp = Blueprint("design_programs", __name__, url_prefix="/design")


# ------------------------------------------------------------------
# Мок-данные программ (5 шт., как на проде главной)
# ------------------------------------------------------------------
_PROGRAMS = [
    {
        "slug": "anglijskij-yazyk",
        "name": "Английский язык",
        "tagline": "Заговорит на английском без зубрёжки — через игры и сказки",
        "benefit": "Заговорит без страха",
        "age_label": "3–12 лет",
        "age_min": 3,
        "age_max": 12,
        "duration_min": 45,
        "frequency": "2 раза в неделю",
        "format": "Группа до 6 детей",
        "price_label": "от 4 800 ₽",
        "price_unit": "мес",
        "color": "#4c83f1",
        "color_soft": "#dde9fd",
        "icon": "ABC",
        "emoji": "🇬🇧",
        "category": "english",
    },
    {
        "slug": "vmeste-s-mamoj",
        "name": "Вместе с мамой",
        "tagline": "Развиваем малыша в безопасной паре — мама рядом, педагог направляет",
        "benefit": "Малыш привыкнет к занятиям",
        "age_label": "1–3 года",
        "age_min": 1,
        "age_max": 3,
        "duration_min": 40,
        "frequency": "2 раза в неделю",
        "format": "Пара мама + ребёнок",
        "price_label": "от 3 600 ₽",
        "price_unit": "мес",
        "color": "#ed7735",
        "color_soft": "#fbe1cf",
        "icon": "1+1",
        "emoji": "🧸",
        "category": "early",
    },
    {
        "slug": "izostudiya-i-lepka",
        "name": "Изостудия и Лепка",
        "tagline": "Творчество в живой студии: краски, глина, бумага — а не один планшет",
        "benefit": "Раскроет творческие способности",
        "age_label": "4–10 лет",
        "age_min": 4,
        "age_max": 10,
        "duration_min": 60,
        "frequency": "1–2 раза в неделю",
        "format": "Группа до 8 детей",
        "price_label": "от 4 200 ₽",
        "price_unit": "мес",
        "color": "#db5eb4",
        "color_soft": "#fadcef",
        "icon": "ART",
        "emoji": "🎨",
        "category": "art",
    },
    {
        "slug": "programma-otlichnik",
        "name": "Программа «Отличник»",
        "tagline": "Подготовка к школе: чтение, счёт, письмо, психолог рядом",
        "benefit": "Пойдёт в школу спокойно",
        "age_label": "5–7 лет",
        "age_min": 5,
        "age_max": 7,
        "duration_min": 50,
        "frequency": "3 раза в неделю",
        "format": "Группа до 8 детей",
        "price_label": "от 5 400 ₽",
        "price_unit": "мес",
        "color": "#6359c2",
        "color_soft": "#e2dffa",
        "icon": "1кл",
        "emoji": "📚",
        "category": "school",
    },
    {
        "slug": "detskij-lager",
        "name": "Детский лагерь",
        "tagline": "Летние и весенние смены: каждый день — новое приключение",
        "benefit": "Не заскучает на каникулах",
        "age_label": "5–12 лет",
        "age_min": 5,
        "age_max": 12,
        "duration_min": 480,
        "frequency": "Пн–Пт, 9:00–18:00",
        "format": "Смена 5 дней",
        "price_label": "от 14 900 ₽",
        "price_unit": "смена",
        "color": "#00b43c",
        "color_soft": "#d2f1d8",
        "icon": "5дн",
        "emoji": "⛺",
        "category": "camp",
    },
]


def _ctx():
    return {
        "programs": _PROGRAMS,
    }


@design_programs_bp.route("/programs")
@design_programs_bp.route("/programs/")
def programs_index():
    return render_template(
        "design/programs_index.html",
        page_title="Программы — варианты на выбор",
    )


@design_programs_bp.route("/programs-v1")
@design_programs_bp.route("/programs-v1/")
def programs_v1():
    return render_template(
        "design/programs_v1.html",
        page_title="Программы V1 — Возраст во главе",
        **_ctx(),
    )


@design_programs_bp.route("/programs-v2")
@design_programs_bp.route("/programs-v2/")
def programs_v2():
    return render_template(
        "design/programs_v2.html",
        page_title="Программы V2 — Список-сравнение",
        **_ctx(),
    )


@design_programs_bp.route("/programs-v3")
@design_programs_bp.route("/programs-v3/")
def programs_v3():
    return render_template(
        "design/programs_v3.html",
        page_title="Программы V3 — Цветные плитки",
        **_ctx(),
    )
