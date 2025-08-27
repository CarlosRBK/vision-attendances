from __future__ import annotations

from typing import Any, Dict, List, Optional
import os

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson.objectid import ObjectId

from . import repository as repo
from fastapi import UploadFile
from .storage import save_person_photo, delete_person_photo as storage_delete_photo
from ...core.config import settings


async def list_people(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
    items = await repo.list_people(db, skip=skip, limit=limit)
    return [_present_person(it) for it in items]


async def get_person(db: AsyncIOMotorDatabase, person_id: str) -> Optional[Dict[str, Any]]:
    doc = await repo.get_person(db, person_id)
    return _present_person(doc) if doc else None


async def get_person_raw(db: AsyncIOMotorDatabase, person_id: str) -> Optional[Dict[str, Any]]:
    # Internal helper used by router to manage photo files on disk
    return await repo.get_person_raw(db, person_id)


async def create_person(db: AsyncIOMotorDatabase, payload: Dict[str, Any]) -> Dict[str, Any]:
    # Photo is saved on disk; payload may include only 'photo_path'.
    created = await repo.create_person(db, payload)
    return _present_person(created)


async def update_person(db: AsyncIOMotorDatabase, person_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    updated = await repo.update_person(db, person_id, payload)
    return _present_person(updated) if updated else None


async def create_person_with_photo(
    db: AsyncIOMotorDatabase,
    data: Dict[str, Any],
    photo: Optional[UploadFile],
) -> Dict[str, Any]:
    person_id = str(ObjectId())
    data = {**data, "_id": person_id, "photo_path": None}  # Ensure id is set
    if photo is not None:
        rel_path = await save_person_photo(photo, person_id)
        data = {**data, "photo_path": rel_path}
    created = await repo.create_person(db, data)
    return _present_person(created)


async def set_person_photo(
    db: AsyncIOMotorDatabase,
    person_id: str,
    photo: UploadFile,
) -> Optional[Dict[str, Any]]:
    # Ensure exists
    existing = await repo.get_person_raw(db, person_id)
    if not existing:
        return None

    # delete previous if any
    prev_rel = existing.get("photo_path")
    if prev_rel:
        storage_delete_photo(prev_rel)

    rel_path = await save_person_photo(photo, person_id)
    updated = await repo.update_person(db, person_id, {"photo_path": rel_path})
    return _present_person(updated) if updated else None


async def delete_person_photo(db: AsyncIOMotorDatabase, person_id: str) -> Optional[Dict[str, Any]]:
    existing = await repo.get_person_raw(db, person_id)
    if not existing:
        return None
    prev_rel = existing.get("photo_path")
    if prev_rel:
        storage_delete_photo(prev_rel)
    updated = await repo.update_person(db, person_id, {"photo_path": None})
    return _present_person(updated) if updated else None


async def delete_person(db: AsyncIOMotorDatabase, person_id: str) -> bool:
    """Delete person and associated photo file if present.
    Returns True if the person was deleted, False if not found.
    """
    existing = await repo.get_person_raw(db, person_id)
    if not existing:
        return False
    prev_rel = existing.get("photo_path")
    if prev_rel:
        storage_delete_photo(prev_rel)
    return await repo.delete_person(db, person_id)


def _present_person(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Map repository document to API shape, computing has_photo and photo_url.
    Removes internal photo_path from outward responses.
    """
    if not doc:
        return doc
    photo_path = doc.get("photo_path")
    presented = {**doc}
    presented.pop("photo_path", None)
    # Validate file existence to avoid broken links when the file was removed manually
    exists = bool(photo_path) and os.path.exists(os.path.join(settings.MEDIA_ROOT, photo_path))
    presented["has_photo"] = bool(exists)
    presented["photo_url"] = f"/static/{photo_path}" if exists else None
    return presented
