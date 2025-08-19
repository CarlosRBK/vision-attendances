from __future__ import annotations

from typing import Any, List, Optional

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
    Response,
)

from . import service
from .schema import AttendanceOut



router = APIRouter()


def get_db(request: Request):
    return request.app.state.db


@router.post(
    "/start",
    response_model=Any,
    status_code=201,
    summary="Detección facial",
    description="Inicia el proceso de detección facial, abre la ventana de la cámara.",
)
async def start_registration(request: Request):
    db = get_db(request)
    await service.start_registration(db)
    return Response(status_code=200)


@router.post(
    "/stop",
    response_model=Any,
    status_code=201,
    summary="Finaliza detección facial",
    description=("Finaliza el proceso de detección facial, cierra la ventana."),
)
async def stop_registration():
    await service.stop_registration()
    return Response(status_code=200)

@router.get(
    "/",
    response_model=List[AttendanceOut],
    summary="Listar asistencias",
    description="Retorna la lista de asistencias registradas en el día. Acepta parámetros de paginación, rango de fechas y nombre de alumno.",
)
async def list_attendances(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    person_id: Optional[str] = Query(
        None, description="Id de la persona para filtrar asistencias"
    ),
    start_time: Optional[str] = Query(
        None, description="Fecha de inicio en formato YYYY-MM-DD:HH:MM:SS"
    ),
    end_time: Optional[str] = Query(
        None, description="Fecha de fin en formato YYYY-MM-DD:HH:MM:SS"
    ),
):
    db = get_db(request)

    items = await service.list_attendances(
        db,
        skip=skip,
        limit=limit,
        person_id=person_id,
        start_time=start_time,
        end_time=end_time,
    )
    return items


@router.delete(
    "/{attendance_id}",
    response_model=Any,
    summary="Eliminar asistencia",
    description="Elimina una asistencia registrada por su ID.",
)
async def remove_attendance(
    request: Request,
    attendance_id: str,
):
    db = get_db(request)
    result = await service.remove_attendance(db, attendance_id)
    if not result:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    return Response(status_code=204)
