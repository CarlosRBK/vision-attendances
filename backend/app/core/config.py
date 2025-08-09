from functools import lru_cache
from pydantic import BaseModel
import os
from dotenv import load_dotenv


class Settings(BaseModel):
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "attendance_db")

    # Defaults de dispositivo
    DEVICE_ID: str = os.getenv("DEVICE_ID", "default")
    DEVICE_TYPE: str = os.getenv("DEVICE_TYPE", "webcam")  # webcam | rtsp
    DEVICE_WIDTH: int = int(os.getenv("DEVICE_WIDTH", "640"))
    DEVICE_HEIGHT: int = int(os.getenv("DEVICE_HEIGHT", "480"))
    DEVICE_FPS: int = int(os.getenv("DEVICE_FPS", "30"))
    DEBOUNCE_SECONDS: int = int(os.getenv("DEBOUNCE_SECONDS", "300"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Carga variables de entorno desde .env si existe
    load_dotenv()
    return Settings()


settings = get_settings()
