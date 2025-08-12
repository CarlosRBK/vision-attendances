from __future__ import annotations

import os
from typing import Optional
from uuid import uuid4

from fastapi import UploadFile

from ...core.config import settings

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}


def ensure_media_dir() -> None:
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    os.makedirs(os.path.join(settings.MEDIA_ROOT, "people_photos"), exist_ok=True)


def _ext_from_content_type(ct: str) -> str:
    ct = (ct or "").lower()
    if ct == "image/png":
        return ".png"
    # default to ".jpg" for jpeg/jpg
    return ".jpg"


async def save_person_photo(file: UploadFile) -> str:
    """
    Save uploaded file under MEDIA_ROOT/people_photos and return relative path (unix-style).
    """
    if (file.content_type or "").lower() not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Invalid content type. Use PNG or JPEG.")

    ensure_media_dir()
    rel_dir = "people_photos"
    abs_dir = os.path.join(settings.MEDIA_ROOT, rel_dir)

    ext = _ext_from_content_type(file.content_type or "")
    filename = f"{uuid4().hex}{ext}"
    abs_path = os.path.join(abs_dir, filename)

    data = await file.read()
    with open(abs_path, "wb") as f:
        f.write(data)

    return os.path.join(rel_dir, filename).replace("\\", "/")


def delete_person_photo(rel_path: Optional[str]) -> None:
    if not rel_path:
        return
    abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    try:
        if os.path.exists(abs_path):
            os.remove(abs_path)
    except Exception:
        # silent best-effort
        pass
