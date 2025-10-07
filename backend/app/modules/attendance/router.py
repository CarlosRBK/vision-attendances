from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...core.database import get_database
from . import service
from .schemas import AttendanceOut, AttendanceIn

router = APIRouter(
    prefix="/attendances",
    tags=["attendance"],  # Cambiado a singular para consistencia
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=AttendanceOut, status_code=201)
async def record_attendance(
    attendance: AttendanceIn,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Registra una nueva asistencia.
    """
    try:
        result = await service.record_attendance(
            db=db,
            person_id=attendance.person_id,
            person_name=attendance.person_name,
            confidence=attendance.confidence,
            device_id=attendance.device_id
        )
        print(result)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al registrar la asistencia")

@router.get("/{attendance_id}", response_model=AttendanceOut)
async def get_attendance(
    attendance_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Obtiene un registro de asistencia por su ID.
    """
    attendance = await service.get_attendance(db, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    return attendance

@router.get("/", response_model=List[AttendanceOut])
async def list_attendances(
    start_date: Optional[datetime] = Query(
        None, 
        description="Fecha de inicio para filtrar (formato ISO 8601, ej: 2025-10-01T00:00:00Z)"
    ),
    end_date: Optional[datetime] = Query(
        None, 
        description="Fecha de fin para filtrar (formato ISO 8601, ej: 2025-10-31T23:59:59Z)"
    ),
    person_id: Optional[str] = Query(
        None, 
        description="Filtrar por ID de persona"
    ),
    device_id: Optional[str] = Query(
        None, 
        description="Filtrar por ID de dispositivo"
    ),
    limit: int = Query(
        100, 
        ge=1, 
        le=1000, 
        description="Número máximo de resultados"
    ),
    skip: int = Query(
        0, 
        ge=0, 
        description="Número de resultados a omitir"
    ),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Lista registros de asistencia con filtros opcionales.
    """
    return await service.list_attendances(
        db=db,
        start_date=start_date,
        end_date=end_date,
        person_id=person_id,
        device_id=device_id,
        limit=limit,
        skip=skip
    )

@router.get("/today/", response_model=List[AttendanceOut])
async def get_todays_attendances(
    person_id: Optional[str] = Query(
        None, 
        description="Filtrar por ID de persona"
    ),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Obtiene las asistencias del día actual.
    """
    return await service.get_todays_attendances(db, person_id=person_id)

@router.get("/summary/")
async def get_attendance_summary(
    start_date: Optional[datetime] = Query(
        None, 
        description="Fecha de inicio para el resumen (por defecto: hace 30 días)"
    ),
    end_date: Optional[datetime] = Query(
        None, 
        description="Fecha de fin para el resumen (por defecto: hoy)"
    ),
    group_by: str = Query(
        "day", 
        regex="^(day|week|month)$",
        description="Agrupar por 'day', 'week' o 'month'"
    ),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Obtiene un resumen de asistencias agrupadas por día, semana o mes.
    """
    return await service.get_attendance_summary(
        db=db,
        start_date=start_date,
        end_date=end_date,
        group_by=group_by
    )
