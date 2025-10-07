from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION = "attendances"

def _ensure_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception as e:
        raise ValueError("Invalid ObjectId") from e

async def create_attendance(
    db: AsyncIOMotorDatabase,
    person_id: str,
    person_name: str,
    confidence: float,
    device_id: str = "default"
) -> Dict[str, Any]:
    """Crea un nuevo registro de asistencia"""
    attendance_data = {
        "person_id": person_id,
        "person_name": person_name,
        "confidence": confidence,
        "device_id": device_id,
        "timestamp": datetime.utcnow()
    }
    
    result = await db[COLLECTION].insert_one(attendance_data)
    return {
        "id": str(result.inserted_id),
        **attendance_data
    }

async def get_attendance(
    db: AsyncIOMotorDatabase,
    attendance_id: str
) -> Optional[Dict[str, Any]]:
    """Obtiene un registro de asistencia por su ID"""
    oid = _ensure_object_id(attendance_id)
    doc = await db[COLLECTION].find_one({"_id": oid})
    if not doc:
        return None
    return {
        "id": str(doc["_id"]),
        "person_id": doc.get("person_id"),
        "person_name": doc.get("person_name"),
        "confidence": doc.get("confidence"),
        "device_id": doc.get("device_id", "default"),
        "timestamp": doc.get("timestamp")
    }

async def list_attendances(
    db: AsyncIOMotorDatabase,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    person_id: Optional[str] = None,
    device_id: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """Lista registros de asistencia con filtros opcionales"""
    query = {}
    
    # Filtro por rango de fechas
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = start_date
        if end_date:
            # Añadir 1 día para incluir todo el día final
            query["timestamp"]["$lt"] = end_date + timedelta(days=1)
    
    # Filtro por persona
    if person_id:
        query["person_id"] = person_id
    
    # Filtro por dispositivo
    if device_id:
        query["device_id"] = device_id
    
    cursor = (
        db[COLLECTION]
        .find(query)
        .sort("timestamp", -1)
        .skip(skip)
        .limit(limit)
    )
    
    return [{
        "id": str(doc["_id"]),
        "person_id": doc.get("person_id"),
        "person_name": doc.get("person_name"),
        "confidence": doc.get("confidence"),
        "device_id": doc.get("device_id", "default"),
        "timestamp": doc.get("timestamp")
    } async for doc in cursor]

async def get_todays_attendances(
    db: AsyncIOMotorDatabase,
    person_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Obtiene las asistencias del día actual"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    query = {"timestamp": {"$gte": today, "$lt": tomorrow}}
    if person_id:
        query["person_id"] = person_id
    
    cursor = db[COLLECTION].find(query).sort("timestamp", -1)
    
    return [{
        "id": str(doc["_id"]),
        "person_id": doc.get("person_id"),
        "person_name": doc.get("person_name"),
        "confidence": doc.get("confidence"),
        "device_id": doc.get("device_id", "default"),
        "timestamp": doc.get("timestamp")
    } async for doc in cursor]
