from __future__ import annotations

from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from . import repository as repo


def _ensure_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception as e:
        raise ValueError("Invalid ObjectId") from e


async def _ensure_person_exists(db: AsyncIOMotorDatabase, person_id: str) -> None:
    oid = _ensure_object_id(person_id)
    person = await db["people"].find_one({"_id": oid})
    if not person:
        raise ValueError("Persona no existe")


def _compute_embedding(image_bytes: bytes) -> List[float]:
    try:
        import numpy as np
        import cv2
        import face_recognition as fr
    except Exception as e:
        raise RuntimeError(
            "Faltan dependencias para embeddings (numpy/opencv/face_recognition). Asegúrate de instalarlas en el entorno."
        ) from e

    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise RuntimeError("Imagen inválida o no soportada")

    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    boxes = fr.face_locations(rgb, model="hog")  # CPU-friendly
    if len(boxes) != 1:
        raise RuntimeError(f"Se requiere exactamente 1 rostro (encontrados: {len(boxes)})")

    encs = fr.face_encodings(rgb, boxes)
    if not encs:
        raise RuntimeError("No se pudo calcular el embedding del rostro")

    return [float(x) for x in encs[0]]


async def add_face(db: AsyncIOMotorDatabase, person_id: str, image_bytes: bytes) -> Dict[str, Any]:
    await _ensure_person_exists(db, person_id)
    embedding = _compute_embedding(image_bytes)
    return await repo.insert_face(db, person_id=person_id, embedding=embedding)


async def list_faces(
    db: AsyncIOMotorDatabase, person_id: Optional[str] = None, skip: int = 0, limit: int = 50
) -> List[Dict[str, Any]]:
    return await repo.list_faces(db, person_id=person_id, skip=skip, limit=limit)
