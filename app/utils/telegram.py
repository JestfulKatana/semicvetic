from __future__ import annotations

import logging

import requests
from flask import current_app


logger = logging.getLogger(__name__)


def send_lead_notification(lead) -> bool:
    token = current_app.config.get("TELEGRAM_BOT_TOKEN")
    chat_id = current_app.config.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False

    text = (
        "Новая заявка с сайта\n"
        f"Телефон: {lead.phone}\n"
        f"Имя: {lead.name or 'не указано'}\n"
        f"Возраст ребёнка: {lead.child_age or 'не указан'}\n"
        f"Страница: {lead.source_page or 'неизвестно'}\n"
        f"Блок: {lead.source_block or 'неизвестно'}\n"
        f"Время: {lead.created_at:%d.%m.%Y %H:%M}"
    )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        logger.warning("telegram_send_failed", exc_info=exc)
        return False
