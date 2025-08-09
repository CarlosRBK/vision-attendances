from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile

from .schemas import FaceOut
from . import service

router = APIRouter()


def get_db(request: Request):
    return request.app.state.db


@router.get(
    "/",
    response_model=List[FaceOut],
    summary="Listar rostros",
    description="Lista rostros almacenados. Permite filtrar por person_id y paginar.",
)
async def list_faces(
    request: Request,
    person_id: Optional[str] = Query(None, description="Filtrar por person_id"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    db = get_db(request)
    items = await service.list_faces(db, person_id=person_id, skip=skip, limit=limit)
    return items


@router.post(
    "/",
    response_model=FaceOut,
    status_code=201,
    summary="Subir rostro y generar embedding",
    description=(
        "Sube una imagen con exactamente 1 rostro, calcula el embedding y lo guarda. "
        "Usar multipart/form-data con campo 'image' y query 'person_id'."
    ),
)
async def upload_face(
    request: Request,
    person_id: str = Query(..., description="ID de la persona"),
    image: UploadFile = File(..., description="Imagen (jpg/png)")
):
    db = get_db(request)
    try:
        content = await image.read()
        doc = await service.add_face(db, person_id=person_id, image_bytes=content)
        return doc
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=400, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno procesando el rostro")
