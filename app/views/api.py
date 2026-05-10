from __future__ import annotations

import re

from flask import Blueprint, current_app, jsonify, request
from prometheus_client import Counter

from ..extensions import db, limiter
from ..models import Lead
from ..utils.telegram import send_lead_notification


bp = Blueprint("api", __name__, url_prefix="/api")

leads_total = Counter("semicvetik_leads_total", "Total leads", ["source_page", "source_block"])
telegram_total = Counter("semicvetik_leads_telegram_sent_total", "Telegram notifications sent")


def normalize_phone(raw_phone: str) -> str:
    digits = re.sub(r"\D", "", raw_phone or "")
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    if len(digits) == 11 and digits.startswith("7"):
        return f"+{digits}"
    raise ValueError("Введите корректный номер телефона — 11 цифр, например: +7 (999) 123-45-67")


@bp.post("/lead")
@limiter.limit(lambda: current_app.config["LEAD_RATE_LIMIT"])
def create_lead():
    payload = request.get_json(silent=True) or request.form

    def _s(key, fallback=""):
        value = payload.get(key)
        if value is None or value == "":
            value = fallback
        if value is None:
            return ""
        return str(value).strip()

    honeypot = _s("company")
    if honeypot:
        return jsonify({"ok": True}), 200

    try:
        phone = normalize_phone(_s("phone"))
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

    child_age_raw = _s("child_age")
    if child_age_raw:
        digits = re.sub(r"\D", "", child_age_raw)
        if not digits or int(digits) <= 0 or int(digits) > 99:
            return jsonify({"ok": False, "message": "Возраст ребёнка указан некорректно"}), 400
        child_age_value = child_age_raw
    else:
        child_age_value = None

    lead = Lead(
        phone=phone,
        name=_s("name") or None,
        child_age=child_age_value,
        source_page=_s("source_page", request.referrer or "") or None,
        source_block=_s("source_block") or None,
        utm_source=_s("utm_source", request.args.get("utm_source") or "") or None,
        utm_medium=_s("utm_medium", request.args.get("utm_medium") or "") or None,
        utm_campaign=_s("utm_campaign", request.args.get("utm_campaign") or "") or None,
    )
    db.session.add(lead)
    db.session.commit()

    leads_total.labels(lead.source_page or "unknown", lead.source_block or "unknown").inc()
    if send_lead_notification(lead):
        telegram_total.inc()

    return jsonify({"ok": True, "message": "Спасибо, перезвоним в ближайшее время"})
