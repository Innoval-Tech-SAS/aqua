"""
Container Package - Sistema de Inyección de Dependencias

Este paquete proporciona el sistema de inyección de dependencias del framework Aqua.
Incluye la clase Container que maneja la resolución automática de dependencias.

Exporta:
    Container: Clase principal para resolver dependencias
"""

from .container import Container

__all__ = ["Container"]