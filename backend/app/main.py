from datetime import datetime, timezone
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from .modules.people.router import router as people_router
# from .modules.faces.router import router as faces_router

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

def create_app() -> FastAPI:
    app = FastAPI(
        title="Attendance Backend",
        version=APP_VERSION,
        description=(
            "API del sistema de asistencia por reconocimiento facial.\n\n"
            "Endpoints principales: health, device, people y faces. Documentación autogenerada con Swagger (/docs) y ReDoc (/redoc)."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {"name": "health", "description": "Estado del servicio"},
            {"name": "people", "description": "Gestión de personas (alumnos/docentes)"},
            {
                "name": "faces",
                "description": "Gestión de rostros y embeddings (alta/listado)",
            },
        ],
    )

    # CORS (abierto en dev; ajustar en prod)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Lifespan para DB y uptime
    async def on_startup() -> None:
        from .core.config import settings

        app.state.started_at = datetime.now(timezone.utc)
        app.state.mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
        app.state.db = app.state.mongo_client[settings.DB_NAME]

        # Crear índices mínimos
        await app.state.db["attendances"].create_index("timestamp")
        await app.state.db["attendances"].create_index("person_id")
        await app.state.db["faces"].create_index("person_id")
        await app.state.db["people"].create_index("full_name")

    async def on_shutdown() -> None:
        client: AsyncIOMotorClient = app.state.mongo_client
        client.close()

    app.add_event_handler("startup", on_startup)
    app.add_event_handler("shutdown", on_shutdown)

    # Routers de módulos
    app.include_router(people_router, prefix="/people", tags=["people"])
    # app.include_router(faces_router, prefix="/faces", tags=["faces"])

    # Health
    @app.get(
        "/health",
        tags=["health"],
        summary="Health check",
        description="Devuelve estado, versión y uptime del servicio",
    )
    async def health():
        started_at: datetime = app.state.started_at
        uptime_sec = int((datetime.now(timezone.utc) - started_at).total_seconds())
        return {"status": "ok", "version": APP_VERSION, "uptime_sec": uptime_sec}

    return app


app = create_app()
