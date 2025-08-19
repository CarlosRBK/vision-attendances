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
    return []


async def start_registration(db: AsyncIOMotorDatabase):
    pass


async def stop_registration():
    pass


async def remove_attendance(db: AsyncIOMotorDatabase, attendance_id: str):
    return attendance_id
