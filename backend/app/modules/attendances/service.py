from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorDatabase

from . import repository as repo
from .face_detector import face_detector


async def list_attendances(
    db: AsyncIOMotorDatabase,
    skip: int = 0,
    limit: int = 50,
    person_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> List[Dict[str, Any]]:
    items = await repo.list_attendances(
        db,
        skip=skip,
        limit=limit,
        person_id=person_id,
        start_time=start_time,
        end_time=end_time,
    )
    return items


async def start_registration(db: AsyncIOMotorDatabase):
    async def _marcar_asistencia(faces: List[Tuple[int, int, int, int, str, str]]):
        for face in faces:
            X, Y, W, H, name, color = face
            # TODO: debe ser el id de la persona, no el nombre
            await repo.create_attendance(db, name)

    face_detector.on_detected_faces(lambda faces: _marcar_asistencia(faces))
    face_detector.start_detection()


async def stop_registration():
    face_detector.stop_detection()


async def remove_attendance(db: AsyncIOMotorDatabase, attendance_id: str):
    return await repo.remove_attendance(db, attendance_id)
