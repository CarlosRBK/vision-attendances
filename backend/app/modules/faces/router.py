from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Query, Request

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
    description="Crea una nueva persona.",
)
async def create_person(payload: PersonIn, request: Request):
    db = get_db(request)
    doc = await service.create_person(db, payload.model_dump(exclude_none=True))

    # TODO: 

    return doc


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
