"""Run alongside the web server; pending deliveries survive worker restarts."""
import time

import click
from flask import current_app
from flask.cli import with_appcontext

from .extensions import db
from .utils.telegram import deliver_pending, poll_updates, sync_processed_messages, telegram_request


@click.command("telegram-worker")
@click.option("--once", is_flag=True, help="Process one batch, then exit.")
@with_appcontext
def telegram_worker(once):
    if not current_app.config.get("TELEGRAM_BOT_TOKEN"):
        raise click.ClickException("TELEGRAM_BOT_TOKEN is not configured")
    webhook = telegram_request("getWebhookInfo", {})
    if webhook is None:
        raise click.ClickException("Cannot check Telegram webhook")
    if webhook.get("url"):
        raise click.ClickException("An existing Telegram webhook is active; left unchanged")
    while True:
        try:
            poll_updates()
            sync_processed_messages()
            sent = deliver_pending(limit=1)
        finally:
            db.session.remove()
        if once:
            click.echo(f"Delivered: {sent}")
            return
        time.sleep(5)
