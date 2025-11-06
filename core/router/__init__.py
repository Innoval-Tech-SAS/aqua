"""
Router Package - Sistema de Enrutamiento

Este paquete maneja el registro y gestión de rutas HTTP.
Proporciona funciones para agregar y consultar rutas registradas.

Exporta:
    add_route: Función para registrar nuevas rutas
    get_routes: Función para obtener todas las rutas registradas
"""

from .router import add_route, get_routes

__all__ = ["add_route", "get_routes"]