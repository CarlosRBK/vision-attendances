from __future__ import annotations

import os
import re
from typing import Optional

import cv2
from fastapi import UploadFile

from ...core.config import settings
from ...utils.face_utils import detect_faces

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}


def ensure_media_dir():
    abs_dir = os.path.join(settings.MEDIA_ROOT, "people_photos")
    os.makedirs(abs_dir, exist_ok=True)
    return abs_dir


def _ext_from_content_type(ct: str) -> str:
    ct = (ct or "").lower()
    if ct == "image/png":
        return ".png"
    # default to ".jpg" for jpeg/jpg
    return ".jpg"

def normalize_filename(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9_\-]", "", name)
    return name


async def save_person_photo(file: UploadFile, full_name: str) -> str:
    """
    Guarda una foto de persona, procesa el rostro y devuelve la ruta relativa optimizada.
    """
    if (file.content_type or "").lower() not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Invalid content type. Use PNG or JPEG.")

    abs_dir = ensure_media_dir()

    # Forzamos a JPG optimizado
    ext = ".jpg"
    filename = normalize_filename(full_name) + ext
    abs_path = os.path.join(abs_dir, filename)

    temp_path = abs_path + ".tmp"
    data = await file.read()
    with open(temp_path, "wb") as f:
        f.write(data)

    image = cv2.imread(temp_path)
    if image is None:
        os.remove(temp_path)
        raise ValueError("Error al leer la imagen.")

    faces = detect_faces(image)
    if len(faces) == 0:
        os.remove(temp_path)
        raise ValueError("No se detectó ningún rostro en la imagen.")

    # Usamos la primera cara
    (x, y, w, h) = faces[0]
    face = image[y:y+h, x:x+w]
    face = cv2.resize(face, (150, 150))

    cv2.imwrite(abs_path, face)
    os.remove(temp_path)

    return os.path.join("people_photos", filename).replace("\\", "/")

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
