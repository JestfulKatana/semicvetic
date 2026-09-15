from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests
from flask import current_app

from ..extensions import db
from ..models import TelegramDelivery

logger = logging.getLogger(__name__)


def queue_lead_notifications(lead):
    """Called inside the same transaction as the lead; never contacts Telegram."""
    raw = current_app.config.get("TELEGRAM_CHAT_IDS") or current_app.config.get("TELEGRAM_CHAT_ID", "")
    recipients = dict.fromkeys(part.strip() for part in raw.split(",") if part.strip())
    for chat_id in recipients:
        db.session.add(TelegramDelivery(lead=lead, chat_id=chat_id))


def deliver_pending(limit=20):
    """Lease each row so concurrent workers cannot send it simultaneously."""
    token = current_app.config.get("TELEGRAM_BOT_TOKEN")
    if not token:
        return 0
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    ids = db.session.scalars(db.select(TelegramDelivery.id).where(
        TelegramDelivery.sent_at.is_(None), TelegramDelivery.next_attempt_at <= now,
    ).order_by(TelegramDelivery.id).limit(limit)).all()
    sent = 0
    for delivery_id in ids:
        claimed = db.session.execute(db.update(TelegramDelivery).where(
            TelegramDelivery.id == delivery_id, TelegramDelivery.sent_at.is_(None),
            TelegramDelivery.next_attempt_at <= now,
        ).values(next_attempt_at=now + timedelta(minutes=5), attempts=TelegramDelivery.attempts + 1))
        db.session.commit()
        if not claimed.rowcount:
            continue
        delivery = db.session.get(TelegramDelivery, delivery_id)
        lead = delivery.lead
        if lead is None:
            delivery.last_error = "lead_missing"
            delivery.next_attempt_at = now + timedelta(hours=1)
            db.session.commit()
            continue
        created = lead.created_at.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("Europe/Moscow"))
        text = (
            f"Новая заявка №{lead.id}\n"
            f"Телефон: {lead.phone}\n"
            f"Имя: {(lead.name or 'не указано')[:120]}\n"
            f"Возраст ребёнка: {(lead.child_age or 'не указан')[:50]}\n"
            f"Желаемая дата: {lead.preferred_date.strftime('%d.%m.%Y') if lead.preferred_date else 'согласовать по телефону'}\n"
            f"Страница: {(lead.source_page or 'неизвестно')[:255]}\n"
            f"Время: {created:%d.%m.%Y %H:%M} МСК"
        )
        error = None
        try:
            response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                                     json={"chat_id": delivery.chat_id, "text": text}, timeout=(3, 5))
            response.raise_for_status()
            result = response.json()
            if not isinstance(result, dict) or result.get("ok") is not True:
                error = "telegram_rejected"
        except (requests.RequestException, ValueError):
            # Exceptions can contain the bot token, recipient and message. Never log them.
            error = "telegram_unavailable"
        delivery.last_error = error
        if error:
            delivery.next_attempt_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
                seconds=min(3600, 30 * 2 ** min(delivery.attempts, 7)))
            logger.warning("telegram_delivery_failed id=%s", delivery.id)
        else:
            delivery.sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
            sent += 1
        db.session.commit()
    return sent
