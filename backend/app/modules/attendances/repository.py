from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION = "attendances"


def _ensure_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception as e:
        raise ValueError("Invalid ObjectId") from e


def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "person_id": doc.get("person_id"),
        "assistance_time": doc.get("assistance_time"),
    }


async def list_attendances(
    db: AsyncIOMotorDatabase,
    skip: int = 0,
    limit: int = 50,
    person_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> List[Dict[str, Any]]:
    query = {}
    if person_id:
        query["person_id"] = person_id
    if start_time or end_time:
        time_query = {}
        if start_time:
            time_query["$gte"] = start_time
        if end_time:
            time_query["$lte"] = end_time
        query["assistance_time"] = time_query

    cursor = (
        db[COLLECTION]
        .find(query)
        .sort("created_at", -1)
        .skip(int(skip))
        .limit(int(limit))
    )
    return [_serialize(d) async for d in cursor]


async def create_attendance(
    db: AsyncIOMotorDatabase,
    person_id: str,
) -> Dict[str, Any]:
    """Registra la asistencia de una persona. Si ya existe una asistencia para esa persona en el día actual, no se registra de nuevo."""
    # TODO: Se requiere algún tipo de cache ya que se llama con mucha frecuencia
    # como una lista limitada a 10, cuando llega a 10 se elimina el más antiguo (FIFO)
    # de esa forma los mas frecuentes estarán en cache y no se consultará a la base de datos
    found_person_in_date = await db[COLLECTION].find_one(
        {
            "person_id": person_id,
            "assistance_time": {
                "$gte": datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            },
        }
    )
    if found_person_in_date:
        return _serialize(found_person_in_date)

    document = {
        "person_id": person_id,
        "attendance_time": datetime.now(timezone.utc),
    }

    result = await db[COLLECTION].insert_one(document)
    created = await db[COLLECTION].find_one({"_id": result.inserted_id})
    if not created:
        raise ValueError("Failed to create attendance record")
    return _serialize(created)


async def remove_attendance(
    db: AsyncIOMotorDatabase,
    attendance_id: str,
) -> Dict[str, Any]:
    """Elimina un registro de asistencia."""
    object_id = _ensure_object_id(attendance_id)
    result = await db[COLLECTION].find_one_and_delete({"_id": object_id})
    if not result:
        raise ValueError("Attendance record not found")
    return _serialize(result)
