from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PersonBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200, description="Nombre completo")
    photo: Optional[str] = Field(None, description="Imagen en base64 (opcional)")
    face_encodings: Optional[List[float]] = Field(None, description="Face encodings (opcional)")
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
    photo: Optional[str] = Field(None, description="Imagen en base64 (opcional)")
