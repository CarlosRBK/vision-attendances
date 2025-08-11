from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION = "people"


def _ensure_object_id(id_str: str) -> ObjectId:
    """Ensure the string is a valid ObjectId."""
    try:
        return ObjectId(id_str)
    except Exception as e:
        raise ValueError("Invalid ObjectId") from e


def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "name": doc.get("name"),
        "embedings": doc.get("embedings"),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }


async def list_people(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
    cursor = (
        db[COLLECTION]
        .find({})
        .sort("created_at", -1)
        .skip(int(skip))
        .limit(int(limit))
    )
    return [_serialize(d) async for d in cursor]


async def get_person(db: AsyncIOMotorDatabase, person_id: str) -> Optional[Dict[str, Any]]:
    oid = _ensure_object_id(person_id)
    doc = await db[COLLECTION].find_one({"_id": oid})
    return _serialize(doc) if doc else None


async def create_person(db: AsyncIOMotorDatabase, data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    doc = {
        "name": data["name"],
        "created_at": now,
        "updated_at": None,
    }
    await db[COLLECTION].insert_one(doc)
    return _serialize(doc)


async def update_person(db: AsyncIOMotorDatabase, person_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    oid = _ensure_object_id(person_id)
    update_doc: Dict[str, Any] = {k: v for k, v in data.items() if v is not None}
    update_doc["updated_at"] = datetime.now(timezone.utc)
    await db[COLLECTION].update_one({"_id": oid}, {"$set": update_doc})
    fresh = await db[COLLECTION].find_one({"_id": oid})
    return _serialize(fresh) if fresh else None
