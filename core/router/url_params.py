"""
URL Parameter System

Este módulo implementa un sistema de parámetros URL tipados,
donde puedes especificar tipos de datos en la ruta y recibirlos
como parámetros tipados en el handler.

Ejemplos:
    /users/<int:user_id>        -> user_id será un int
    /posts/<str:slug>           -> slug será un str  
    /articles/<float:price>     -> price será un float
    /users/<user_id>            -> user_id será un str (por defecto)

Autor: lyrionlannister
Versión: 1.0.0
"""

import re
import inspect
from typing import Dict, Any, Tuple, Callable, Optional


class ParameterConverter:
    """
    Clase base para convertidores de parámetros URL.
    """
    
    def convert(self, value: str) -> Any:
        """Convierte el string a su tipo correspondiente"""
        raise NotImplementedError
    
    def regex_pattern(self) -> str:
        """Retorna el patrón regex para este tipo"""
        raise NotImplementedError


class StringConverter(ParameterConverter):
    """Convertidor para parámetros string (por defecto)"""
    
    def convert(self, value: str) -> str:
        return value
    
    def regex_pattern(self) -> str:
        return r'[^/]+'


class IntConverter(ParameterConverter):
    """Convertidor para parámetros enteros"""
    
    def convert(self, value: str) -> int:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"No se puede convertir '{value}' a entero")
    
    def regex_pattern(self) -> str:
        return r'\d+'


class FloatConverter(ParameterConverter):
    """Convertidor para parámetros flotantes"""
    
    def convert(self, value: str) -> float:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"No se puede convertir '{value}' a float")
    
    def regex_pattern(self) -> str:
        return r'\d+(\.\d+)?'


class UUIDConverter(ParameterConverter):
    """Convertidor para parámetros UUID"""
    
    def convert(self, value: str) -> str:
        # Validación básica de UUID
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        if not uuid_pattern.match(value):
            raise ValueError(f"'{value}' no es un UUID válido")
        return value
    
    def regex_pattern(self) -> str:
        return r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'


# Registry de convertidores disponibles
CONVERTERS = {
    'str': StringConverter(),
    'int': IntConverter(), 
    'float': FloatConverter(),
    'uuid': UUIDConverter(),
}


class RoutePattern:
    """
    Representa un patrón de ruta con parámetros tipados.
    """
    
    def __init__(self, route_path: str):
        self.original_path = route_path
        self.regex_pattern, self.param_specs = self._parse_route(route_path)
        self.compiled_regex = re.compile(f'^{self.regex_pattern}$')
    
    def _parse_route(self, route_path: str) -> Tuple[str, Dict[str, ParameterConverter]]:
        """
        Parsea una ruta con parámetros tipados y genera regex + especificaciones.
        
        Args:
            route_path: Ruta como "/users/<int:user_id>/posts/<str:slug>"
            
        Returns:
            Tupla con (patrón_regex, diccionario_especificaciones_parámetros)
        """
        param_pattern = re.compile(r'<(?:([^:>]+):)?([^>]+)>')
        param_specs = {}
        
        def replace_param(match):
            param_type = match.group(1) or 'str'  # str por defecto
            param_name = match.group(2)
            
            if param_type not in CONVERTERS:
                raise ValueError(f"Tipo de parámetro desconocido: {param_type}")
            
            converter = CONVERTERS[param_type]
            param_specs[param_name] = converter
            
            return f'(?P<{param_name}>{converter.regex_pattern()})'
        
        escaped_path = re.escape(route_path)
        escaped_path = escaped_path.replace(r'\<', '<').replace(r'\>', '>')
        regex_pattern = param_pattern.sub(replace_param, escaped_path)
        
        return regex_pattern, param_specs
    
    def match(self, url_path: str) -> Optional[Dict[str, Any]]:
        """
        Intenta hacer match de la URL con este patrón.
        
        Args:
            url_path: URL a verificar
            
        Returns:
            Diccionario con parámetros convertidos o None si no hace match
        """
        match = self.compiled_regex.match(url_path)
        if not match:
            return None
        
        converted_params = {}
        for param_name, converter in self.param_specs.items():
            raw_value = match.group(param_name)
            try:
                converted_params[param_name] = converter.convert(raw_value)
            except ValueError as e:
                return None
        
        return converted_params


def inject_route_params(handler: Callable, params: Dict[str, Any]) -> Callable:
    """
    Crea una versión del handler que recibe los parámetros como argumentos.
    
    Solo pasa el objeto request si el handler lo tiene como parámetro.
    Esto hace que sea más consistente con Flask/FastAPI.
    
    Args:
        handler: Función handler original
        params: Diccionario de parámetros extraídos de la URL
        
    Returns:
        Función wrapper que inyecta los parámetros
    """
    sig = inspect.signature(handler)
    handler_params = list(sig.parameters.keys())
    
    # Filtrar parámetros que el handler realmente acepta
    injectable_params = {}
    for param_name, param_value in params.items():
        if param_name in handler_params:
            injectable_params[param_name] = param_value
    
    # Verificar si el handler acepta 'request' como parámetro
    accepts_request = 'request' in handler_params
    
    async def wrapper(request):
        if 'self' in handler_params:
            # Es un método de clase
            if accepts_request:
                return await handler(request, **injectable_params)
            else:
                # Solo pasar self y los parámetros de URL
                return await handler(**injectable_params)
        else:
            # Es una función standalone
            if accepts_request:
                return await handler(request, **injectable_params)
            else:
                # Solo pasar los parámetros de URL
                return await handler(**injectable_params)
    
    return wrapper


def find_matching_route(routes: list, method: str, url_path: str) -> Tuple[Optional[dict], Optional[Callable]]:
    """
    Busca una ruta que haga match con el método y URL dados.
    
    Args:
        routes: Lista de rutas registradas
        method: Método HTTP (GET, POST, etc.)
        url_path: URL de la request
        
    Returns:
        Tupla con (ruta_encontrada, handler_con_parámetros_inyectados)
    """
    for route in routes:
        if route["method"] != method:
            continue
        
        route_pattern = RoutePattern(route["path"])
        params = route_pattern.match(url_path)
        
        if params is not None:
            enhanced_handler = inject_route_params(route["handler"], params)
            return route, enhanced_handler
    
    return None, None
