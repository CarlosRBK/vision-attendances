from datetime import datetime
from fastapi import APIRouter, Depends, Request

from .schemas import DeviceConfigIn, DeviceConfigOut
from . import service

router = APIRouter()


def get_db(request: Request):
    return request.app.state.db


@router.get(
    "/",
    response_model=DeviceConfigOut,
    summary="Obtener configuración del dispositivo",
    description="Devuelve la configuración actual del dispositivo. Si no existe, se inicializa con valores por defecto.",
)
async def get_device(request: Request):
    db = get_db(request)
    doc = await service.get_or_init(db)
    return {
        "device_id": doc["device_id"],
        "type": doc["type"],
        "params": doc["params"],
        "updated_at": doc.get("updated_at"),
    }


@router.put(
    "/",
    response_model=DeviceConfigOut,
    summary="Actualizar configuración del dispositivo",
    description="Guarda la configuración del dispositivo (tipo y parámetros).",
)
async def put_device(payload: DeviceConfigIn, request: Request):
    db = get_db(request)
    doc = await service.update(db, payload)
    return {
        "device_id": doc["device_id"],
        "type": doc["type"],
        "params": doc["params"],
        "updated_at": doc.get("updated_at"),
    }
