"""
Container - Sistema de Inyección de Dependencias

Este módulo implementa un contenedor de inyección de dependencias para el framework Aqua.
Permite la resolución automática de dependencias usando type hints y decoradores.

Autor: lyrionlannister
Versión: 1.0.0
"""

import inspect


class Container:
    """
    Contenedor de inyección de dependencias para el framework Aqua.
    
    Este contenedor:
    - Resuelve dependencias automáticamente usando type hints
    - Mantiene un cache de instancias (singleton por defecto)
    - Soporta inyección manual usando el decorador @Inject
    - Valida que las clases estén marcadas con @Injectable
    
    Attributes:
        _instances (dict): Cache de instancias ya creadas para evitar recreación.
        
    Example:
        ```python
        container = Container()
        
        @Injectable
        class MyService:
            pass
            
        @Injectable
        class MyController:
            def __init__(self, service: MyService):
                self.service = service
                
        # Resolverá automáticamente MyService e inyectará en MyController
        controller = await container.resolve(MyController)
        ```
    """
    
    def __init__(self):
        """
        Inicializa un nuevo contenedor de inyección de dependencias.
        """
        self._instances = {}

    async def resolve(self, cls):
        """
        Resuelve una clase y todas sus dependencias recursivamente.
        
        Este método:
        1. Verifica que la clase esté marcada con @Injectable
        2. Retorna la instancia cacheada si existe
        3. Analiza las dependencias del constructor
        4. Resuelve recursivamente todas las dependencias
        5. Crea la instancia y la cachea
        
        Args:
            cls (type): Clase a resolver (debe estar decorada con @Injectable)
            
        Returns:
            object: Instancia de la clase con todas sus dependencias inyectadas
            
        Raises:
            Exception: Si la clase no está marcada con @Injectable
            Exception: Si alguna dependencia no está anotada correctamente
            
        Example:
            ```python
            @Injectable
            class UserService:
                def __init__(self, repo: UserRepository):
                    self.repo = repo
                    
            service = await container.resolve(UserService)
            ```
        """
        if not getattr(cls, "_injectable", False):
            raise Exception(f"{cls.__name__} debe estar decorado con @Injectable")

        if cls in self._instances:
            return self._instances[cls]

        sig = inspect.signature(cls.__init__)
        params = list(sig.parameters.values())[1:]

        overrides = getattr(cls, "_inject_overrides", {})
        deps = []

        for param in params:
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue

            dep_cls = overrides.get(param.name, param.annotation)

            if dep_cls is inspect.Parameter.empty:
                raise Exception(f"Debe anotar o inyectar la dependencia '{param.name}' en {cls.__name__}")

            dep_instance = await self.resolve(dep_cls)
            deps.append(dep_instance)

        instance = cls(*deps)
        self._instances[cls] = instance
        return instance