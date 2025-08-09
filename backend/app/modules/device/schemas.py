from datetime import datetime
from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel, Field


class DeviceParams(BaseModel):
    # Parámetros genéricos según tipo de dispositivo
    index: Optional[int] = Field(default=0, description="Índice de cámara para webcam")
    url: Optional[str] = Field(default=None, description="URL RTSP para cámaras IP")
    width: int = 640
    height: int = 480
    fps: int = 30
    debounce_seconds: int = 300
    rtsp_transport: Optional[Literal["tcp", "udp"]] = None
    reconnect_secs: Optional[int] = 5


class DeviceConfigIn(BaseModel):
    type: Literal["webcam", "rtsp"]
    params: DeviceParams


class DeviceConfigOut(BaseModel):
    device_id: str
    type: Literal["webcam", "rtsp"]
    params: DeviceParams
    updated_at: datetime
