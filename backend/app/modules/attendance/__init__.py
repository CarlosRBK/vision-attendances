"""
Módulo para la gestión de asistencias.

Este módulo proporciona funcionalidades para registrar y consultar asistencias
de personas en el sistema de reconocimiento facial.
"""

from . import repository, service, schemas, router

# Hacer disponibles los nombres principales para facilitar las importaciones
__all__ = ["repository", "service", "schemas", "router"]
