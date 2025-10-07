from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class AttendanceBase(BaseModel):
    person_id: str = Field(..., description="ID de la persona")
    person_name: str = Field(..., description="Nombre de la persona")
    confidence: float = Field(..., description="Nivel de confianza del reconocimiento")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Fecha y hora de la asistencia")
    device_id: str = Field(default="default", description="ID del dispositivo que registró la asistencia")
    
    class Config:
        json_schema_extra = {
            "example": {
                "person_id": "507f1f77bcf86cd799439011",
                "person_name": "Juan Pérez",
                "confidence": 0.92,
                "timestamp": "2025-10-03T18:30:00Z",
                "device_id": "camara_principal"
            }
        }

class AttendanceIn(AttendanceBase):
    pass

class AttendanceOut(AttendanceBase):
    id: str = Field(..., description="ID del registro de asistencia")
