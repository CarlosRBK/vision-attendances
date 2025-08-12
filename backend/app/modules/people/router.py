from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, UploadFile, File, Form, Response

from .schemas import PersonIn, PersonOut
from . import service

router = APIRouter()


def get_db(request: Request):
    return request.app.state.db


@router.get(
    "/",
    response_model=List[PersonOut],
    summary="Listar personas",
    description="Retorna una lista paginada de personas registradas.",
)
async def list_people(request: Request, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    db = get_db(request)
    items = await service.list_people(db, skip=skip, limit=limit)
    return items


@router.post(
    "/",
    response_model=PersonOut,
    status_code=201,
    summary="Crear persona",
    description=(
        "Crea una nueva persona. Acepta multipart/form-data con campos y un archivo opcional 'photo' (PNG/JPEG)."
    ),
)
async def create_person(
    request: Request,
    full_name: str = Form(...),
    email: Optional[str] = Form(None),
    grade: Optional[str] = Form(None),
    group: Optional[str] = Form(None),
    photo: UploadFile = File(None),
):
    db = get_db(request)
    data = {
        "full_name": full_name,
        "email": email,
        "grade": grade,
        "group": group,
    }
    try:
        doc = await service.create_person_with_photo(db, data, photo)
        return doc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar la imagen: {e}")


@router.get(
    "/{person_id}",
    response_model=PersonOut,
    summary="Obtener persona",
    description="Obtiene una persona por su ID.",
)
async def get_person(person_id: str, request: Request):
    db = get_db(request)
    doc = await service.get_person(db, person_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return doc


@router.put(
    "/{person_id}",
    response_model=PersonOut,
    summary="Actualizar persona",
    description="Actualiza los datos de una persona.",
)
async def update_person(person_id: str, payload: PersonIn, request: Request):
    db = get_db(request)
    doc = await service.update_person(db, person_id, payload.model_dump(exclude_none=True))
    if not doc:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return doc


@router.put(
    "/{person_id}/photo",
    response_model=PersonOut,
    summary="Actualizar/establecer foto de la persona",
    description=(
        "Sube y reemplaza la foto de una persona. Acepta multipart/form-data con 'photo' (PNG/JPEG). "
        "Si existía una foto anterior, se elimina del disco."
    ),
)
async def set_person_photo(
    person_id: str,
    request: Request,
    photo: UploadFile = File(...),
):
    db = get_db(request)
    try:
        updated = await service.set_person_photo(db, person_id, photo)
        if not updated:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar la imagen: {e}")


@router.delete(
    "/{person_id}/photo",
    response_model=PersonOut,
    summary="Eliminar foto de la persona",
    description="Elimina la foto asociada a la persona y limpia el campo en la base de datos.",
)
async def delete_person_photo(person_id: str, request: Request):
    db = get_db(request)
    updated = await service.delete_person_photo(db, person_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return updated


@router.delete(
    "/{person_id}",
    status_code=204,
    summary="Eliminar persona y su foto",
    description="Elimina la persona y su foto asociada del sistema.",
)
async def delete_person(person_id: str, request: Request):
    db = get_db(request)
    ok = await service.delete_person(db, person_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    # 204 No Content
    return None


@router.delete(
    "/{person_id}",
    status_code=204,
    summary="Eliminar persona",
    description="Elimina la persona y su foto en disco si existiese.",
)
async def delete_person(person_id: str, request: Request):
    db = get_db(request)
    deleted = await service.delete_person(db, person_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return Response(status_code=204)
