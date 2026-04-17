from __future__ import annotations

from copy import deepcopy

from markdown import markdown


def render_markdown(value: str | None) -> str:
    if not value:
        return ""
    return markdown(value, extensions=["extra", "sane_lists"])


def phone_href(phone: str | None) -> str:
    if not phone:
        return ""
    return "".join(ch for ch in phone if ch.isdigit() or ch == "+")


def hydrate_blocks(blocks: list[dict], shared: dict) -> list[dict]:
    hydrated = []
    for block in blocks:
        clone = deepcopy(block)
        # Новые блоки (audit 2026-04-17) приходят в контракте {type, payload}.
        # Приводим к существующему {component, data}, чтобы render_block.html
        # не дублировать — фронт-агент пишет ветки через block.component.
        if clone.get("type") and "component" not in clone:
            clone["component"] = clone["type"]
        if "payload" in clone and "data" not in clone:
            clone["data"] = clone["payload"]
        data = clone.setdefault("data", {})
        source = data.get("source")
        if source == "all_programs":
            data["programs"] = shared["programs"]
        elif source == "featured_programs":
            data["programs"] = shared["programs"][: data.get("limit", 3)]
        elif source == "all_teachers":
            teachers = shared["teachers"]
            limit = data.get("limit")
            data["teachers"] = teachers[:limit] if limit else teachers
        elif source == "featured_reviews":
            data["reviews"] = shared["reviews"][: data.get("limit", 3)]
        elif source == "program_reviews":
            current_program = shared.get("current_program")
            data["reviews"] = (
                [review for review in shared["reviews"] if review.program_id == current_program.id]
                if current_program
                else []
            )
        elif source == "all_events":
            data["events"] = shared["events"]
        elif source == "all_articles":
            data["articles"] = shared["articles"]
        elif source == "upcoming_events":
            limit = data.get("limit", 3)
            data["events"] = shared["events"][:limit]
        elif source == "recent_articles":
            limit = data.get("limit", 3)
            data["articles"] = shared["articles"][:limit]
        elif source == "all_prices":
            data["programs"] = shared["programs"]
        elif source == "contact_data":
            data["settings"] = shared["settings"]
        elif source == "current_program" and shared.get("current_program"):
            program = shared["current_program"]
            data.setdefault("title", program.name)
            data.setdefault("subtitle", program.tagline)
            data.setdefault("cta_text", "Записаться на пробное занятие")
            data.setdefault(
                "stats",
                [
                    {"value": program.age_label, "label": "Возраст"},
                    {"value": f"{program.duration_min} мин", "label": "Занятие"},
                    {"value": program.price_label, "label": "Стоимость"},
                ],
            )
        elif source == "program_schedule" and shared.get("current_program"):
            program = shared["current_program"]
            groups: dict[str, list] = {}
            for slot in program.schedule_slots:
                key = slot.group_name or "Группа"
                groups.setdefault(key, []).append({
                    "day": slot.day_of_week,
                    "time": f"{slot.time_start}–{slot.time_end}",
                })
            data["groups"] = [
                {"title": title, "slots": slots}
                for title, slots in groups.items()
            ]
            data.setdefault("program", program)
        hydrated.append(clone)
    return hydrated
