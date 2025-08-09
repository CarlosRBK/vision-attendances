from __future__ import annotations

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from . import repository as repo


async def list_people(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
    return await repo.list_people(db, skip=skip, limit=limit)


async def get_person(db: AsyncIOMotorDatabase, person_id: str) -> Optional[Dict[str, Any]]:
    return await repo.get_person(db, person_id)


async def create_person(db: AsyncIOMotorDatabase, payload: Dict[str, Any]) -> Dict[str, Any]:
    return await repo.create_person(db, payload)


async def update_person(db: AsyncIOMotorDatabase, person_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return await repo.update_person(db, person_id, payload)
