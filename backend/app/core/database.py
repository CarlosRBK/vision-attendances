"""Database connection and session management."""
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Request

def get_database(request: Request) -> AsyncIOMotorDatabase:
    """
    Dependency para obtener la conexión a la base de datos desde el estado de la app.
    
    Args:
        request: Request de FastAPI que contiene el estado de la aplicación
        
    Returns:
        AsyncIOMotorDatabase: Conexión a la base de datos MongoDB
    """
    return request.app.state.db
