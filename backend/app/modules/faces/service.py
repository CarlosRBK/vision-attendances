from __future__ import annotations

from typing import Any, Dict, List, Optional

import face_recognition
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.app.modules.faces.schemas import PersonIn
from backend.app.utils.img_to_np import img_to_np

from . import repository as repo


async def list_people(
    db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 50
) -> List[Dict[str, Any]]:
    return await repo.list_people(db, skip=skip, limit=limit)


async def get_person(
    db: AsyncIOMotorDatabase, person_id: str
) -> Optional[Dict[str, Any]]:
    return await repo.get_person(db, person_id)


async def create_person(db: AsyncIOMotorDatabase, payload: Dict[str, Any]) -> Dict[str, Any]:
    img_np = img_to_np(payload["image_base64"])
    encs = face_recognition.face_encodings(img_np)
    if not encs:
        raise ValueError("No face encodings found in the provided image.")
    payload["embedings"] = encs[0]
    return await repo.create_person(db, payload)


async def update_person(
    db: AsyncIOMotorDatabase, person_id: str, payload: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    if "image_base64" in payload:
        img_np = img_to_np(payload["image_base64"])
        encs = face_recognition.face_encodings(img_np)
        if not encs:
            raise ValueError("No face encodings found in the provided image.")
        payload["encodings"] = encs[0]
    return await repo.update_person(db, person_id, payload)

async def start_video_face_detection(db: AsyncIOMotorDatabase) -> None:
    pass