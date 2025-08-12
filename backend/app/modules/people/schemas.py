from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PersonBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200, description="Nombre completo")
    email: Optional[str] = Field(None, description="Email (opcional)")
    grade: Optional[str] = Field(None, description="Grado/Curso (opcional)")
    group: Optional[str] = Field(None, description="División/Grupo (opcional)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "full_name": "Juan Pérez",
                    "email": "juan.perez@escuela.edu",
                    "grade": "5to",
                    "group": "A",
                }
            ]
        }
    }


class PersonIn(PersonBase):
    pass


class PersonOut(PersonBase):
    id: str = Field(..., description="ID del documento")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    has_photo: bool = Field(False, description="Indica si la persona tiene una foto almacenada")
    photo_url: Optional[str] = Field(None, description="URL relativa para acceder a la foto (/static/...) si existe")
