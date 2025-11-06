"""
Router System - Sistema de Enrutamiento

Este módulo maneja el registro y gestión de rutas HTTP en el framework Aqua.
Proporciona funciones para agregar rutas y mantener un registro global de todas
las rutas disponibles.

Autor: lyrionlannister
Versión: 1.0.0
"""

from inspect import iscoroutinefunction
from typing import Awaitable, List, Dict
from core.logger.logger import logger


Route = Dict[str, object]

_routes: List[Route] = []


def add_route(method: str, path: str, handler: Awaitable):
    """
    Registra una nueva ruta en el sistema de enrutamiento.
    
    Esta función:
    1. Valida que el handler sea una función asíncrona
    2. Registra la ruta en el sistema global
    3. Registra la operación en los logs
    
    Args:
        method (str): Método HTTP (GET, POST, PUT, DELETE, PATCH, etc.)
        path (str): Ruta del endpoint (ej: "/users", "/users/{id}")
        handler (Awaitable): Función asíncrona que manejará las requests a esta ruta
        
    Raises:
        TypeError: Si el handler no es una función asíncrona (corrutina)
        
    Example:
        ```python
        async def get_users(request):
            return {"users": []}
            
        # Registrar la ruta
        add_route("GET", "/users", get_users)
        ```
        
    Note:
        - El method se convierte automáticamente a mayúsculas
        - Esta función normalmente es llamada internamente por el framework
        - Las rutas se almacenan en orden de registro
    """
    if not iscoroutinefunction(handler):
        raise TypeError(f"El handler para {method.upper()} {path} debe ser async (usa 'async def')")

    logger.info(f"Ruta añadida al router: {method.upper()} {path} -> {handler.__module__}.{handler.__qualname__}")
    _routes.append({
        "method": method.upper(),
        "path": path,
        "handler": handler
    })


def get_routes() -> List[Route]:
    """
    Obtiene todas las rutas registradas en el sistema.
    
    Returns:
        List[Route]: Lista de diccionarios, cada uno representando una ruta con:
                    - method: Método HTTP en mayúsculas
                    - path: Ruta del endpoint
                    - handler: Función que maneja la ruta
                    
    Example:
        ```python
        routes = get_routes()
        for route in routes:
            print(f"{route['method']} {route['path']}")
        
        # Output ejemplo:
        # GET /users
        # POST /users  
        # GET /users/{id}
        ```
        
    Note:
        - Retorna una copia de la lista para evitar modificaciones accidentales
        - Útil para debugging, introspección o generación de documentación
    """
    return _routes
