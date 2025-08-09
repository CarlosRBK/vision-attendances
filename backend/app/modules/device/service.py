from datetime import datetime, timezone
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorDatabase

from . import repository
from .schemas import DeviceConfigIn
from ...core.config import settings


DEFAULT_DOC: Dict[str, Any] = {
    "device_id": settings.DEVICE_ID,
    "type": settings.DEVICE_TYPE,
    "params": {
        "index": 0,
        "url": None,
        "width": settings.DEVICE_WIDTH,
        "height": settings.DEVICE_HEIGHT,
        "fps": settings.DEVICE_FPS,
        "debounce_seconds": settings.DEBOUNCE_SECONDS,
        "rtsp_transport": None,
        "reconnect_secs": 5,
    },
}


async def get_or_init(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    existing = await repository.get_device(db, settings.DEVICE_ID)
    if existing:
        return existing
    return await repository.upsert_device(db, DEFAULT_DOC.copy())


async def update(db: AsyncIOMotorDatabase, payload: DeviceConfigIn) -> Dict[str, Any]:
    doc: Dict[str, Any] = {
        "device_id": settings.DEVICE_ID,
        "type": payload.type,
        "params": payload.params.model_dump(),
    }
    return await repository.upsert_device(db, doc)
