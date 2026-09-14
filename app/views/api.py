from __future__ import annotations

import re

from flask import Blueprint, current_app, jsonify, render_template, request
from prometheus_client import Counter

from ..extensions import db, limiter
from ..models import Lead, Program
from ..utils.telegram import send_lead_notification


bp = Blueprint("api", __name__, url_prefix="/api")

leads_total = Counter("semicvetik_leads_total", "Total leads", ["source_page", "source_block"])
telegram_total = Counter("semicvetik_leads_telegram_sent_total", "Telegram notifications sent")


def normalize_phone(raw_phone: str) -> str:
    if not isinstance(raw_phone, str) or not re.fullmatch(r"[+0-9()\s-]{1,40}", raw_phone):
        raise ValueError("Укажите телефон в формате +7")
    digits = re.sub(r"\D", "", raw_phone)
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    if len(digits) == 11 and digits.startswith("7"):
        return f"+{digits}"
    raise ValueError("Укажите телефон в формате +7")


def lead_response(ok: bool, message: str, status: int = 200):
    wants_html = (
        not request.is_json
        and request.accept_mimetypes["text/html"] > request.accept_mimetypes["application/json"]
    )
    if wants_html:
        return render_template("version/submission.html", submitted=ok, message=message), status
    return jsonify({"ok": ok, "message": message}), status


@bp.post("/lead")
@limiter.limit(lambda: current_app.config["LEAD_RATE_LIMIT"])
def create_lead():
    payload = request.get_json(silent=True) if request.is_json else request.form
    if not isinstance(payload, dict):
        return lead_response(False, "Не удалось прочитать заявку", 400)

    def field(key, limit, fallback=""):
        value = payload.get(key, fallback)
        if value is None:
            return ""
        if not isinstance(value, str) or len(value) > limit:
            raise ValueError("Проверьте заполнение полей заявки")
        return value.strip()

    try:
        if field("company", 255):
            return lead_response(True, "Спасибо! Заявка получена.")
        phone = normalize_phone(payload.get("phone", ""))
        if payload.get("consent") not in (True, "on", "1", "true"):
            raise ValueError("Подтвердите согласие на обработку персональных данных")
        program_slug = field("program_slug", 120)
        program = None
        if program_slug:
            program = Program.query.filter_by(slug=program_slug, is_published=True).first()
            if program is None:
                raise ValueError("Выберите программу из списка или оставьте поле пустым")
        preference = field("preference", 500)
        notes = ["Согласие на обработку персональных данных: подтверждено при отправке."]
        if program:
            notes.append(f"Программа: {program.name} ({program.slug})")
        if preference:
            notes.append(f"Пожелание по времени (не запись на занятие): {preference}")
        lead = Lead(
            phone=phone,
            name=field("name", 120) or None,
            child_age=field("child_age", 50) or None,
            source_page=field("source_page", 255, request.referrer or "") or None,
            source_block=field("source_block", 120) or None,
            utm_source=field("utm_source", 120, request.args.get("utm_source", "")) or None,
            utm_medium=field("utm_medium", 120, request.args.get("utm_medium", "")) or None,
            utm_campaign=field("utm_campaign", 120, request.args.get("utm_campaign", "")) or None,
            note="\n".join(notes),
        )
    except ValueError as exc:
        return lead_response(False, str(exc), 400)

    db.session.add(lead)
    db.session.commit()

    leads_total.labels(lead.source_page or "unknown", lead.source_block or "unknown").inc()
    if send_lead_notification(lead):
        telegram_total.inc()

    return lead_response(True, "Спасибо! Заявка получена. Мы свяжемся с вами, чтобы обсудить занятия.")


@bp.errorhandler(429)
def lead_rate_limit_exceeded(error):
    return lead_response(False, "Слишком много попыток. Подождите минуту и попробуйте ещё раз", 429)
