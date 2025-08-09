from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FaceOut(BaseModel):
    id: str = Field(..., description="ID del documento")
    person_id: str = Field(..., description="ID de la persona a la que pertenece el rostro")
    embedding_dim: int = Field(..., description="Dimensión del vector de embedding almacenado")
    created_at: datetime = Field(..., description="Fecha de creación")


class FaceListParams(BaseModel):
    person_id: Optional[str] = Field(None, description="Filtrar por person_id")
