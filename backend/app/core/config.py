from functools import lru_cache
from pydantic import BaseModel
import os
from dotenv import load_dotenv, find_dotenv

# Cargar .env lo antes posible para que os.getenv vea los valores durante la definición de la clase.
# 1) Busca .env desde el CWD hacia arriba (proyectos que lo ponen en la raíz)
load_dotenv(find_dotenv(), override=False)
# 2) Intenta también backend/.env relativo a este archivo (proyectos que lo ponen en backend/.env)
_backend_env = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(_backend_env, override=False)


class Settings(BaseModel):
    # Soporta MONGODB_URI (preferido) y MONGO_URI (compatibilidad)
    MONGODB_URI: str = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or "mongodb://localhost:27017"
    DB_NAME: str = os.getenv("DB_NAME", "attendance_db")
    # Ruta base para archivos estáticos/subidos (por defecto: app/static)
    MEDIA_ROOT: str = os.getenv(
        "MEDIA_ROOT",
        os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "static")
        ),
    )

    # Defaults de dispositivo
    DEVICE_ID: str = os.getenv("DEVICE_ID", "default")
    DEVICE_TYPE: str = os.getenv("DEVICE_TYPE", "webcam")  # webcam | rtsp
    DEVICE_WIDTH: int = int(os.getenv("DEVICE_WIDTH", "640"))
    DEVICE_HEIGHT: int = int(os.getenv("DEVICE_HEIGHT", "480"))
    DEVICE_FPS: int = int(os.getenv("DEVICE_FPS", "30"))
    DEBOUNCE_SECONDS: int = int(os.getenv("DEBOUNCE_SECONDS", "300"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
