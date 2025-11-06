"""
Controller Decorators - Sistema de Enrutamiento

Este módulo proporciona decoradores para definir controladores y rutas HTTP
en el framework Aqua. Sigue un patrón similar a frameworks como NestJS o FastAPI.

Autor: lyrionlannister
Versión: 1.0.0
"""
def Controller(prefix: str = ""):
    """
    Decorador para marcar una clase como controlador y definir un prefijo de ruta.
    
    Args:
        prefix (str, optional): Prefijo que se agregará a todas las rutas del controlador.
                               Por defecto "". Ejemplo: "/api/v1"
    
    Returns:
        function: Decorador que modifica la clase agregando metadatos de ruta.
        
    Example:
        ```python
        @Controller("/users")
        class UserController:
            @Get("/")
            async def list_users(self, request):
                return {"users": []}
                
        # Resultará en la ruta: GET /users/
        ```
        
    Note:
        El prefijo se combina con las rutas individuales definidas en los métodos.
        Si el prefijo es "/api" y el método tiene ruta "/users", la ruta final será "/api/users".
    """
    def decorator(cls):
        cls._route_prefix = prefix
        return cls
    return decorator


def Get(path: str):
    """
    Decorador para definir una ruta HTTP GET.
    
    Args:
        path (str): Ruta relativa para este endpoint. Ejemplo: "/", "/users", "/users/{id}"
        
    Returns:
        function: Decorador que agrega metadatos de ruta al método.
        
    Example:
        ```python
        @Get("/users")
        async def get_users(self, request):
            return {"users": []}
            
        @Get("/users/{user_id}")
        async def get_user(self, request):
            user_id = request.path_params["user_id"]
            return {"user": user_id}
        ```
    """
    def decorator(func):
        setattr(func, "_route_info", {"method": "GET", "path": path})
        return func
    return decorator


def Post(path: str):
    """
    Decorador para definir una ruta HTTP POST.
    
    Args:
        path (str): Ruta relativa para este endpoint.
        
    Returns:
        function: Decorador que agrega metadatos de ruta al método.
        
    Example:
        ```python
        @Post("/users")
        async def create_user(self, request):
            data = await request.json()
            # Lógica para crear usuario
            return {"created": True}
        ```
    """
    def decorator(func):
        setattr(func, "_route_info", {"method": "POST", "path": path})
        return func
    return decorator


def Put(path: str):
    """
    Decorador para definir una ruta HTTP PUT.
    
    Args:
        path (str): Ruta relativa para este endpoint.
        
    Returns:
        function: Decorador que agrega metadatos de ruta al método.
        
    Example:
        ```python
        @Put("/users/{user_id}")
        async def update_user(self, request):
            user_id = request.path_params["user_id"]
            data = await request.json()
            # Lógica para actualizar usuario
            return {"updated": True}
        ```
    """
    def decorator(func):
        setattr(func, "_route_info", {"method": "PUT", "path": path})
        return func
    return decorator


def Delete(path: str):
    """
    Decorador para definir una ruta HTTP DELETE.
    
    Args:
        path (str): Ruta relativa para este endpoint.
        
    Returns:
        function: Decorador que agrega metadatos de ruta al método.
        
    Example:
        ```python
        @Delete("/users/{user_id}")
        async def delete_user(self, request):
            user_id = request.path_params["user_id"]
            # Lógica para eliminar usuario
            return {"deleted": True}
        ```
    """
    def decorator(func):
        setattr(func, "_route_info", {"method": "DELETE", "path": path})
        return func
    return decorator


def Patch(path: str):
    """
    Decorador para definir una ruta HTTP PATCH.
    
    Args:
        path (str): Ruta relativa para este endpoint.
        
    Returns:
        function: Decorador que agrega metadatos de ruta al método.
        
    Example:
        ```python
        @Patch("/users/{user_id}")
        async def patch_user(self, request):
            user_id = request.path_params["user_id"]
            data = await request.json()
            # Lógica para actualización parcial
            return {"patched": True}
        ```
    """
    def decorator(func):
        setattr(func, "_route_info", {"method": "PATCH", "path": path})
        return func
    return decorator