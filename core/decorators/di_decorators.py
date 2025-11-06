"""
Dependency Injection Decorators

Este módulo proporciona decoradores para el sistema de inyección de dependencias
del framework Aqua. Permite marcar clases como inyectables y configurar 
inyecciones manuales de dependencias.

Autor: lyrionlannister
Versión: 1.0.0
"""


def Injectable(cls):
    """
    Decorador para marcar una clase como inyectable en el contenedor de DI.
    
    Las clases marcadas con @Injectable pueden ser:
    - Resueltas automáticamente por el contenedor
    - Inyectadas como dependencias en otras clases
    - Cacheadas como singletons
    
    Args:
        cls (type): Clase a marcar como inyectable
        
    Returns:
        type: La misma clase con metadatos de inyección agregados
        
    Example:
        ```python
        @Injectable
        class UserService:
            def __init__(self, repo: UserRepository):
                self.repo = repo
                
        @Injectable  
        class UserRepository:
            def __init__(self):
                pass
                
        # Ambas clases pueden ser resueltas por el contenedor
        container = Container()
        service = await container.resolve(UserService)  # UserRepository se inyecta automáticamente
        ```
        
    Note:
        - Todas las clases que serán manejadas por el contenedor DEBEN tener este decorador
        - Sin este decorador, el contenedor lanzará una excepción al intentar resolver la clase
    """
    cls._injectable = True
    return cls


def Inject(**kwargs):
    """
    Decorador para especificar inyecciones manuales de dependencias.
    
    Permite override manual de dependencias cuando los type hints no son suficientes
    o cuando se necesita inyectar una implementación específica.
    
    Args:
        **kwargs: Mapeo de nombre_parametro=ClaseAInyectar
        
    Returns:
        function: Decorador que agrega metadatos de inyección manual a la clase
        
    Example:
        ```python
        @Injectable
        class EmailService:
            pass
            
        @Injectable  
        class SMSService:
            pass
            
        @Injectable
        @Inject(notification_service=EmailService)  # Forzar EmailService en lugar del type hint
        class UserController:
            def __init__(self, notification_service):  # Sin type hint, usa el @Inject
                self.notification_service = notification_service
                
        # O con type hint diferente:
        @Injectable
        @Inject(notification_service=SMSService)  # Override del type hint
        class AdminController:
            def __init__(self, notification_service: EmailService):  # Type hint dice EmailService
                self.notification_service = notification_service  # Pero se inyecta SMSService
        ```
        
    Note:
        - Los valores en @Inject tienen prioridad sobre los type hints
        - Útil para casos donde necesitas inyectar diferentes implementaciones de una interfaz
        - Los nombres de los parámetros deben coincidir exactamente con los del constructor
    """
    def wrapper(cls):
        cls._inject_overrides = kwargs
        return cls
    return wrapper