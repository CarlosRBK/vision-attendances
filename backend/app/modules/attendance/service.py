from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from . import repository as repo
from ..people.service import get_person

async def record_attendance(
    db: AsyncIOMotorDatabase,
    person_id: str,
    person_name: str,
    confidence: float,
    device_id: str = "default"
) -> Dict[str, Any]:
    """
    Registra una nueva asistencia para una persona.
    
    Args:
        db: Conexión a la base de datos
        person_id: ID de la persona
        person_name: Nombre de la persona
        confidence: Nivel de confianza del reconocimiento (0.0 a 1.0)
        device_id: ID del dispositivo que registra la asistencia
        
    Returns:
        Dict con los datos de la asistencia registrada
    """
    # Verificar si la persona existe (opcional, solo advertir si no existe)
    # Comentado temporalmente para permitir registros sin verificación
    # TODO: Implementar sincronización de person_id entre face-services y backend
    # try:
    #     person = await get_person(db, person_id)
    #     if not person:
    #         print(f"[WARNING] Persona con ID {person_id} no encontrada en la base de datos")
    # except Exception as e:
    #     print(f"[WARNING] Error al verificar persona: {e}")
    
    # Registrar la asistencia
    attendance = await repo.create_attendance(
        db=db,
        person_id=person_id,
        person_name=person_name,
        confidence=confidence,
        device_id=device_id
    )
    
    return attendance

async def get_attendance(
    db: AsyncIOMotorDatabase,
    attendance_id: str
) -> Optional[Dict[str, Any]]:
    """Obtiene un registro de asistencia por su ID"""
    return await repo.get_attendance(db, attendance_id)

async def list_attendances(
    db: AsyncIOMotorDatabase,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    person_id: Optional[str] = None,
    device_id: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """
    Lista registros de asistencia con filtros opcionales
    
    Args:
        db: Conexión a la base de datos
        start_date: Fecha de inicio para filtrar
        end_date: Fecha de fin para filtrar
        person_id: Filtrar por ID de persona
        device_id: Filtrar por ID de dispositivo
        limit: Límite de resultados
        skip: Número de resultados a omitir
        
    Returns:
        Lista de diccionarios con los datos de asistencia
    """
    return await repo.list_attendances(
        db=db,
        start_date=start_date,
        end_date=end_date,
        person_id=person_id,
        device_id=device_id,
        limit=limit,
        skip=skip
    )

async def get_todays_attendances(
    db: AsyncIOMotorDatabase,
    person_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene las asistencias del día actual
    
    Args:
        db: Conexión a la base de datos
        person_id: Opcional, filtrar por ID de persona
        
    Returns:
        Lista de asistencias del día actual
    """
    return await repo.get_todays_attendances(db, person_id=person_id)

async def get_attendance_summary(
    db: AsyncIOMotorDatabase,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    group_by: str = "day"
) -> Dict[str, Any]:
    """
    Obtiene un resumen de asistencias agrupadas por día, semana o mes
    
    Args:
        db: Conexión a la base de datos
        start_date: Fecha de inicio para el resumen
        end_date: Fecha de fin para el resumen
        group_by: Agrupar por 'day', 'week' o 'month'
        
    Returns:
        Diccionario con el resumen de asistencias
    """
    # Configurar fechas por defecto (últimos 30 días)
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Definir el formato de agrupación para MongoDB
    date_format = "%Y-%m-%d"
    if group_by == "month":
        date_format = "%Y-%m"
    elif group_by == "week":
        date_format = "%Y-%W"
    
    # Pipeline de agregación
    pipeline = [
        {
            "$match": {
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": date_format,
                        "date": "$timestamp"
                    }
                },
                "count": {"$sum": 1},
                "people": {"$addToSet": "$person_id"}
            }
        },
        {
            "$project": {
                "date": "$_id",
                "count": 1,
                "unique_people": {"$size": "$people"},
                "_id": 0
            }
        },
        {"$sort": {"date": 1}}
    ]
    
    cursor = db.attendances.aggregate(pipeline)
    results = await cursor.to_list(length=1000)
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "group_by": group_by,
        "data": results
    }
