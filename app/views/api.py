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
    raise ValueError("Укажите телефон в формате +7")


@bp.post("/lead")
@limiter.limit(lambda: current_app.config["LEAD_RATE_LIMIT"])
def create_lead():
    payload = request.get_json(silent=True) or request.form
    honeypot = (payload.get("company") or "").strip()
    if honeypot:
        return jsonify({"ok": True}), 200

    try:
        phone = normalize_phone(payload.get("phone", ""))
    except ValueError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 400

    lead = Lead(
        phone=phone,
        name=(payload.get("name") or "").strip() or None,
        child_age=(payload.get("child_age") or "").strip() or None,
        source_page=(payload.get("source_page") or request.referrer or "").strip() or None,
        source_block=(payload.get("source_block") or "").strip() or None,
        utm_source=(payload.get("utm_source") or request.args.get("utm_source") or "").strip() or None,
        utm_medium=(payload.get("utm_medium") or request.args.get("utm_medium") or "").strip() or None,
        utm_campaign=(payload.get("utm_campaign") or request.args.get("utm_campaign") or "").strip() or None,
    )
    db.session.add(lead)
    db.session.commit()

    leads_total.labels(lead.source_page or "unknown", lead.source_block or "unknown").inc()
    if send_lead_notification(lead):
        telegram_total.inc()

    return jsonify({"ok": True, "message": "Спасибо, перезвоним в ближайшее время"})
