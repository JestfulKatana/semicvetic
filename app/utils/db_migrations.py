from __future__ import annotations

from sqlalchemy import inspect, text


# Лёгкие идемпотентные миграции для случаев, когда в проекте используется
# db.create_all() без Alembic. Каждая запись — (таблица, колонка, DDL для ALTER).
# Все выражения должны быть совместимы с SQLite и PostgreSQL.
_ADDITIVE_COLUMNS: list[tuple[str, str, str]] = [
    ("event", "body_html", "ALTER TABLE event ADD COLUMN body_html TEXT"),
    (
        "event",
        "is_pinned",
        "ALTER TABLE event ADD COLUMN is_pinned BOOLEAN NOT NULL DEFAULT 0",
    ),
]


def ensure_runtime_schema(db) -> None:
    engine = db.engine
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        for table_name, column_name, ddl in _ADDITIVE_COLUMNS:
            if table_name not in existing_tables:
                continue
            columns = {col["name"] for col in inspector.get_columns(table_name)}
            if column_name in columns:
                continue
            conn.execute(text(ddl))
