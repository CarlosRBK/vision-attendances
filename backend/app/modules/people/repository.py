from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...utils.face_detector import Face

COLLECTION = "people"


def _ensure_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception as e:
        raise ValueError("Invalid ObjectId") from e


def _serialize(doc: Dict[str, Any], include_embeds: bool = False) -> Dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "full_name": doc.get("full_name"),
        "photo": doc.get("photo"),
        "face_encodings": doc.get("face_encodings") if include_embeds else None,
        "email": doc.get("email"),
        "grade": doc.get("grade"),
        "group": doc.get("group"),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }


async def list_people(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 50, include_embeds: bool = False) -> List[Dict[str, Any]]:
    cursor = (
        db[COLLECTION]
        .find({})
        .sort("created_at", -1)
        .skip(int(skip))
        .limit(int(limit))
    )
    return [_serialize(d, include_embeds) async for d in cursor]


async def get_person(db: AsyncIOMotorDatabase, person_id: str) -> Optional[Dict[str, Any]]:
    oid = _ensure_object_id(person_id)
    doc = await db[COLLECTION].find_one({"_id": oid})
    return _serialize(doc) if doc else None


async def get_person_raw(db: AsyncIOMotorDatabase, person_id: str) -> Optional[Dict[str, Any]]:
    oid = _ensure_object_id(person_id)
    return await db[COLLECTION].find_one({"_id": oid})


async def create_person(db: AsyncIOMotorDatabase, data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    doc = {
        "full_name": data.get("full_name"),
        "email": data.get("email"),
        "grade": data.get("grade"),
        "group": data.get("group"),
        "face_encodings": data.get("face_encodings"),
        "photo": data.get("photo"),
        "created_at": now,
        "updated_at": None,
    }
    res = await db[COLLECTION].insert_one(doc)
    created = await db[COLLECTION].find_one({"_id": res.inserted_id})
    if not created:
        raise RuntimeError("Failed to retrieve created document")
    return _serialize(created)


async def update_person(db: AsyncIOMotorDatabase, person_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    oid = _ensure_object_id(person_id)
    set_fields: Dict[str, Any] = {k: v for k, v in data.items() if v is not None}
    unset_fields: Dict[str, int] = {k: 1 for k, v in data.items() if v is None}
    set_fields["updated_at"] = datetime.now(timezone.utc)

    update_ops: Dict[str, Any] = {"$set": set_fields}
    if unset_fields:
        update_ops["$unset"] = unset_fields

    await db[COLLECTION].update_one({"_id": oid}, update_ops)
    fresh = await db[COLLECTION].find_one({"_id": oid})
    return _serialize(fresh) if fresh else None


async def delete_person(db: AsyncIOMotorDatabase, person_id: str) -> bool:
    """Delete a person document by id. Returns True if a document was deleted."""
    oid = _ensure_object_id(person_id)
    res = await db[COLLECTION].delete_one({"_id": oid})
    return res.deleted_count > 0


async def get_faces(db: AsyncIOMotorDatabase) -> List[Face]:
    cursor = db[COLLECTION].find({"face_encodings": {"$exists": True}})
    return [Face(d["id"], d["name"], d["face_encodings"]) async for d in cursor]