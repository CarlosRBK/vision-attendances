from datetime import datetime
from typing import Optional

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
    pass


class PersonOut(PersonBase):
    id: str = Field(..., description="ID del documento")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
