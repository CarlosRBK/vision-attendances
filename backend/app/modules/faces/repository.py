from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION = "faces"


def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "person_id": doc.get("person_id"),
        "embedding_dim": doc.get("embedding_dim", len(doc.get("embedding", []) or [])),
        "created_at": doc.get("created_at"),
    }


async def insert_face(db: AsyncIOMotorDatabase, person_id: str, embedding: List[float]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    doc: Dict[str, Any] = {
        "person_id": person_id,
        "embedding": embedding,
        "embedding_dim": len(embedding),
        "created_at": now,
    }
    res = await db[COLLECTION].insert_one(doc)
    fresh = await db[COLLECTION].find_one({"_id": res.inserted_id})
    return _serialize(fresh)


async def list_faces(
    db: AsyncIOMotorDatabase, person_id: Optional[str] = None, skip: int = 0, limit: int = 50
) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if person_id:
        filt["person_id"] = person_id
    cursor = (
        db[COLLECTION]
        .find(filt, projection={"embedding": 0})
        .sort("created_at", -1)
        .skip(int(skip))
        .limit(int(limit))
    )
    return [_serialize(d) async for d in cursor]
