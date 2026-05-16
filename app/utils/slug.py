from __future__ import annotations

import re


_TRANSLIT_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def slugify(value: str, max_length: int = 80) -> str:
    if not value:
        return ""
    value = value.strip().lower()
    out = []
    for ch in value:
        if ch in _TRANSLIT_MAP:
            out.append(_TRANSLIT_MAP[ch])
        elif ch.isascii() and (ch.isalnum() or ch in "-_"):
            out.append(ch)
        elif ch.isspace() or ch in "—–_/\\":
            out.append("-")
        # прочие символы — выкидываем
    slug = "".join(out)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:max_length].rstrip("-")


def ensure_unique_slug(base_slug: str, model, exclude_id: int | None = None) -> str:
    candidate = base_slug or "post"
    suffix = 2
    while True:
        query = model.query.filter_by(slug=candidate)
        if exclude_id is not None:
            query = query.filter(model.id != exclude_id)
        if not query.first():
            return candidate
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
