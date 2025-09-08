from __future__ import annotations

from typing import Any, Dict, List, Optional

import cv2
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson.objectid import ObjectId
import numpy as np

from ...utils.face_utils import crop_face, get_face_encodings, numpy_to_base64

from . import repository as repo
from fastapi import UploadFile


async def _add_face_encodings_and_crop_from_file(data: Dict[str, Any], photo: UploadFile) -> Dict[str, Any]:
    if not photo.filename:
        raise ValueError("No file uploaded.")

    # Check file type
    if not photo.filename.endswith(('.jpg', '.jpeg', '.png')):
        raise ValueError("Invalid file type. Only .jpg, .jpeg, and .png are allowed.")
    
    # Read the image file
    image_data = await photo.read()
    
    # Convert bytes to a NumPy array
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Decodifica la imagen

    if image is None:
        raise ValueError("Error loading image: image could not be decoded.")
    
    # Get face encodings
    encodings = get_face_encodings(image)

    # Get cropped image
    cropped_face = crop_face(image)

    # Add to data
    data["photo"] = numpy_to_base64(cropped_face)
    data["face_encodings"] = encodings.tolist() # Convert to list for MongoDB compatibility

    return data


async def list_people(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
    items = await repo.list_people(db, skip=skip, limit=limit)
    return items


async def get_person(db: AsyncIOMotorDatabase, person_id: str) -> Optional[Dict[str, Any]]:
    doc = await repo.get_person(db, person_id)
    return doc


async def get_person_raw(db: AsyncIOMotorDatabase, person_id: str) -> Optional[Dict[str, Any]]:
    # Internal helper used by router to manage photo files on disk
    return await repo.get_person_raw(db, person_id)


async def update_person(db: AsyncIOMotorDatabase, person_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    updated = await repo.update_person(db, person_id, payload)
    return updated


async def create_person(
    db: AsyncIOMotorDatabase,
    data: Dict[str, Any],
    photo: Optional[UploadFile],
) -> Dict[str, Any]:
    person_id = str(ObjectId())
    data["_id"] = person_id
    
    if photo:
        data = await _add_face_encodings_and_crop_from_file(data, photo)

    created = await repo.create_person(db, data)

    return created


async def set_person_photo(
    db: AsyncIOMotorDatabase,
    person_id: str,
    photo: UploadFile,
) -> Optional[Dict[str, Any]]:
    # Ensure exists
    found = await repo.get_person_raw(db, person_id)
    if not found:
        return None
    
    updated_data = await _add_face_encodings_and_crop_from_file(found, photo)

    updated = await repo.update_person(db, person_id, updated_data)
    return updated


async def delete_person_photo(db: AsyncIOMotorDatabase, person_id: str) -> Optional[Dict[str, Any]]:
    existing = await repo.get_person_raw(db, person_id)
    if not existing:
        return None
    updated = await repo.update_person(db, person_id, {"photo_path": None})
    return updated


async def delete_person(db: AsyncIOMotorDatabase, person_id: str) -> bool:
    """Delete person and associated photo file if present.
    Returns True if the person was deleted, False if not found.
    """
    existing = await repo.get_person_raw(db, person_id)
    if not existing:
        return False
    return await repo.delete_person(db, person_id)
