from __future__ import annotations

import secrets
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, url_for
from flask_login import login_required
from PIL import Image, UnidentifiedImageError


bp = Blueprint("admin_media", __name__, url_prefix="/admin/media")

# SVG умышленно НЕ разрешён — векторные файлы могут содержать <script>,
# и при открытии напрямую (/static/uploads/news/x.svg) выполнят JS
# в origin сайта. Нужны векторы — заводи отдельный санитайзер.
_ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
_ALLOWED_MIMETYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB на одиночный файл


def _upload_dir() -> Path:
    static_root = Path(current_app.root_path) / "static" / "uploads" / "news"
    static_root.mkdir(parents=True, exist_ok=True)
    return static_root


@bp.post("/upload")
@login_required
def upload_image():
    file = request.files.get("file") or request.files.get("upload")
    if not file or not file.filename:
        return jsonify({"ok": False, "error": "Файл не получен"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in _ALLOWED_EXTENSIONS:
        return jsonify({"ok": False, "error": "Допустимы JPG, PNG, WEBP, GIF"}), 400

    if file.mimetype not in _ALLOWED_MIMETYPES:
        return jsonify({"ok": False, "error": "Тип файла не поддерживается"}), 400

    file.stream.seek(0, 2)
    size = file.stream.tell()
    file.stream.seek(0)
    if size > _MAX_BYTES:
        return jsonify({"ok": False, "error": "Файл больше 10 МБ"}), 400
    if size == 0:
        return jsonify({"ok": False, "error": "Пустой файл"}), 400

    # Pillow.verify() парсит заголовок и убеждается, что файл — реальная картинка,
    # а не html/php/exe с подменённым расширением. После verify() поток нужно
    # перемотать для последующего file.save().
    try:
        with Image.open(file.stream) as img:
            img.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        return jsonify({"ok": False, "error": "Файл не является корректной картинкой"}), 400
    file.stream.seek(0)

    name = f"{secrets.token_hex(8)}.{ext}"
    dest = _upload_dir() / name
    file.save(dest)

    url = url_for("static", filename=f"uploads/news/{name}")
    # Quill / CKEditor общий контракт ответа.
    return jsonify({"ok": True, "url": url, "location": url})
