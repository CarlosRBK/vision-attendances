from datetime import datetime, timezone
from typing import Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorDatabase


COLLECTION_NAME = "device"


async def get_device(db: AsyncIOMotorDatabase, device_id: str) -> Optional[Dict[str, Any]]:
    return await db[COLLECTION_NAME].find_one({"device_id": device_id})


async def upsert_device(db: AsyncIOMotorDatabase, doc: Dict[str, Any]) -> Dict[str, Any]:
    device_id = doc["device_id"]
    doc["updated_at"] = datetime.now(timezone.utc)
    await db[COLLECTION_NAME].update_one(
        {"device_id": device_id},
        {"$set": doc},
        upsert=True,
    )
    # return the fresh doc
    return await get_device(db, device_id)
