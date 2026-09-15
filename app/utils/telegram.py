from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import requests
from flask import current_app

from ..extensions import db
from ..models import Lead, Page, Program, SiteSetting, TelegramDelivery

logger = logging.getLogger(__name__)


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def recipient_ids():
    raw = current_app.config.get("TELEGRAM_CHAT_IDS") or current_app.config.get("TELEGRAM_CHAT_ID", "")
    return list(dict.fromkeys(part.strip() for part in raw.split(",") if part.strip()))


def queue_lead_notifications(lead):
    """Enqueue inside the same transaction as the lead; no network requests."""
    for chat_id in recipient_ids():
        db.session.add(TelegramDelivery(lead=lead, chat_id=chat_id))


def telegram_request(method, payload):
    token = current_app.config.get("TELEGRAM_BOT_TOKEN")
    if not token:
        return None
    try:
        response = requests.post(f"https://api.telegram.org/bot{token}/{method}",
                                 json=payload, timeout=(3, 5))
        data = response.json()
        if isinstance(data, dict):
            if response.status_code < 400 and data.get("ok") is True:
                return data.get("result")
            if method == "editMessageText" and "message is not modified" in str(data.get("description", "")).lower():
                return True
    except (requests.RequestException, ValueError):
        pass
    # URLs/exceptions may contain credentials or phone numbers. Log neither.
    logger.warning("telegram_request_failed method=%s", method)
    return None


def source_title(lead):
    try:
        slug = urlsplit(lead.source_page or "/").path.strip("/") or "home"
    except ValueError:
        return "Сайт «Семицветик»"
    program = db.session.scalar(db.select(Program).where(Program.slug == slug))
    if program:
        return program.name
    page = db.session.scalar(db.select(Page).where(Page.slug == slug))
    return page.title if page else "Сайт «Семицветик»"


def lead_message(lead):
    processed = lead.status == "processed"
    heading = f"{'✅ Обработана' if processed else 'Новая заявка'} №{lead.id}"
    lines = [heading, source_title(lead)[:160], "", f"Телефон: {lead.phone}"]
    if lead.name:
        lines.append(f"Имя: {lead.name[:120]}")
    if lead.child_age:
        lines.append(f"Возраст ребёнка: {lead.child_age[:50]}")
    if lead.preferred_date:
        lines.append(f"Удобный день: {lead.preferred_date:%d.%m.%Y}")
    created = lead.created_at.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("Europe/Moscow"))
    lines.extend(["", f"Получена {created:%d.%m в %H:%M} МСК"])
    text = "\n".join(lines)
    offset = len(text[:text.index(lead.phone)].encode("utf-16-le")) // 2
    return {
        "text": text,
        "entities": [{"type": "bold", "offset": 0, "length": len(heading.encode("utf-16-le")) // 2},
                     {"type": "phone_number", "offset": offset, "length": len(lead.phone)}],
        "reply_markup": {"inline_keyboard": [[
            {"text": "Открыть контакт", "callback_data": f"contact:{lead.id}"},
            {"text": "✅ Обработана" if processed else "⬜ Не обработана", "callback_data": f"{'reopen' if processed else 'processed'}:{lead.id}"},
        ]]},
    }


def deliver_pending(limit=20):
    if not current_app.config.get("TELEGRAM_BOT_TOKEN"):
        return 0
    now = utcnow()
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
        rendered_status = lead.status
        result = telegram_request("sendMessage", {"chat_id": delivery.chat_id, **lead_message(lead)})
        if not isinstance(result, dict) or not isinstance(result.get("message_id"), int):
            delivery.last_error = "telegram_unavailable"
            delivery.next_attempt_at = utcnow() + timedelta(seconds=min(3600, 30 * 2 ** min(delivery.attempts, 7)))
        else:
            delivery.message_id = result["message_id"]
            delivery.rendered_status = rendered_status
            delivery.sent_at = utcnow()
            delivery.last_error = None
            sent += 1
        db.session.commit()
    return sent


def sync_processed_messages():
    rows = db.session.scalars(db.select(TelegramDelivery).join(Lead).where(
        TelegramDelivery.message_id.is_not(None), TelegramDelivery.rendered_status != Lead.status,
        TelegramDelivery.next_attempt_at <= utcnow(),
    ).limit(20)).all()
    for row in rows:
        status = row.lead.status
        result = telegram_request("editMessageText", {
            "chat_id": row.chat_id, "message_id": row.message_id, **lead_message(row.lead),
        })
        if result is not None:
            row.rendered_status = status
            row.last_error = None
        else:
            row.last_error = "telegram_edit_failed"
            row.next_attempt_at = utcnow() + timedelta(minutes=1)
        db.session.commit()


def handle_callback(callback):
    sender = str(callback.get("from", {}).get("id", ""))
    message = callback.get("message", {})
    chat = message.get("chat", {})
    match = re.fullmatch(r"(processed|reopen|contact):(\d{1,12})", callback.get("data", ""))
    delivery = None
    if sender in recipient_ids() and chat.get("type") == "private" and str(chat.get("id")) == sender and match:
        delivery = db.session.scalar(db.select(TelegramDelivery).where(
            TelegramDelivery.lead_id == int(match[2]), TelegramDelivery.chat_id == sender,
            TelegramDelivery.message_id == message.get("message_id"),
        ))
    if not delivery or not delivery.lead:
        telegram_request("answerCallbackQuery", {"callback_query_id": callback["id"], "text": "Нет доступа к этой заявке"})
        return True
    lead = delivery.lead
    if match[1] == "contact":
        if delivery.contact_message_id:
            text = "Контакт уже отправлен в этот чат"
        else:
            result = telegram_request("sendContact", {
                "chat_id": sender, "phone_number": lead.phone,
                "first_name": (lead.name or f"Заявка №{lead.id}")[:120],
            })
            if isinstance(result, dict) and isinstance(result.get("message_id"), int):
                delivery.contact_message_id = result["message_id"]
                db.session.commit()
                text = "Контакт отправлен"
            else:
                text = "Не удалось отправить контакт. Нажмите ещё раз."
    else:
        target_status = "new" if match[1] == "reopen" else "processed"
        if lead.status != target_status:
            lead.status = target_status
            lead.processed_at = utcnow() if target_status == "processed" else None
            lead.processed_by = sender if target_status == "processed" else None
            db.session.execute(db.update(TelegramDelivery).where(TelegramDelivery.lead_id == lead.id).values(next_attempt_at=utcnow()))
            db.session.commit()
        text = "Заявка обработана" if target_status == "processed" else "Заявка не обработана"
    telegram_request("answerCallbackQuery", {"callback_query_id": callback["id"], "text": text})
    return True


def poll_updates():
    cursor = db.session.get(SiteSetting, "telegram_update_offset")
    offset = int(cursor.value) if cursor else 0
    updates = telegram_request("getUpdates", {"offset": offset, "timeout": 0, "limit": 100})
    if not isinstance(updates, list):
        return
    for update in updates:
        callback = update.get("callback_query")
        if callback and not handle_callback(callback):
            break
        if cursor is None:
            cursor = SiteSetting(key="telegram_update_offset", value="0")
            db.session.add(cursor)
        cursor.value = str(update["update_id"] + 1)
        db.session.commit()
