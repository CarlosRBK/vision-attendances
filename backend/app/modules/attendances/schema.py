
from datetime import datetime
from pydantic import BaseModel, Field


class AttendanceBase(BaseModel):
    user_id: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "person_id": "niabvbruiahvfdaopvhuaeh",
                }
            ]
        }
    }

class AttendanceIn(AttendanceBase):
    pass

class AttendanceOut(AttendanceBase):
    id: str = Field(..., description="ID del documento")
    person_id: str = Field(..., description="ID de la persona")
    attendance_time: datetime = Field(..., description="Momento en que se registró la asistencia")