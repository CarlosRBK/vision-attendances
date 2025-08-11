from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class PersonBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Nombre")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Juan Pérez",
                }
            ]
        }
    }


class PersonIn(PersonBase):
    image_base64: str = Field(
        ..., description="Imagen codificada en base64, sin el prefijo data:image/…"
    )
    pass


class PersonOut(PersonBase):
    id: str = Field(..., description="ID del documento")
    encodings: List[List[float]] = Field(
        ..., description="Lista de vectores de características"
    )
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(
        None, description="Fecha de última actualización"
    )
