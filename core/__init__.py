"""
Aqua Framework - Core Module

Este módulo contiene la clase principal Aqua que actúa como el framework web ASGI.
Proporciona funcionalidades de inyección de dependencias, enrutamiento y manejo del ciclo de vida.

Autor: lyrionlannister
Versión: 1.0.0
"""

import inspect
from uvicorn import run
from core.container import Container
from core.router import add_route
from core.router.url_params import find_matching_route
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import Scope, Receive, Send
from core.logger.logger import logger


class Aqua:
    """
    Clase principal del framework Aqua que implementa la interfaz ASGI.
    
    Esta clase es responsable de:
    - Configurar el contenedor de inyección de dependencias
    - Registrar controladores y sus rutas
    - Manejar requests HTTP
    - Gestionar el ciclo de vida de la aplicación (startup/shutdown)
    
    Attributes:
        container (Container): Contenedor de inyección de dependencias
        root_module: Módulo raíz que contiene controladores y proveedores
        routes (list): Lista de rutas registradas en la aplicación
    
    Example:
        ```python
        from core import Aqua
        from core.module import Module
        
        app_module = Module(
            controllers=[UserController],
            providers=[UserService]
        )
        app = Aqua(app_module)
        app.run()
        ```
    """
    
    def __init__(self, root_module):
        """
        Inicializa una nueva instancia del framework Aqua.
        
        Args:
            root_module: Módulo que contiene los controladores y proveedores
                        de la aplicación. Debe tener atributos 'controllers' y 'providers'.
        """
        self.container = Container()
        self.root_module = root_module
        self.routes = []

    async def startup(self):
        """
        Método de inicialización de la aplicación.
        
        Se ejecuta durante el evento lifespan.startup de ASGI.
        Configura todos los componentes necesarios antes de que la aplicación
        esté lista para recibir requests.
        
        Raises:
            Exception: Si hay algún error durante la configuración inicial.
        """
        await self._setup(self.root_module)

    async def _setup(self, module_cls):
        config = getattr(module_cls, "_module_config", None)
        if config is None:
            raise Exception(f"{module_cls.__name__} no está decorado con @Module")

        for imported_module in config.get("imports", []):
            await self._setup(imported_module)

        for provider in config.get("exports", []):
            await self.container.resolve(provider)
        await self._resolve_providers(config.get("providers", []))
        await self._register_controllers(config.get("controllers", []))


    async def _resolve_providers(self, providers):
        """
        Resuelve todos los proveedores del módulo.
        
        Los proveedores incluyen servicios, repositorios y otras dependencias
        que pueden ser inyectadas en los controladores.
        
        Args:
            providers (list): Lista de clases marcadas con @Injectable
            
        Raises:
            Exception: Si hay algún error al resolver algún proveedor.
        """
        for provider in providers:
            logger.debug(f"Resolviendo proveedor: {provider.__name__}")
            await self.container.resolve(provider)

    async def _register_controllers(self, controllers):
        """
        Registra todas las rutas de todos los controladores.
        
        Para cada controlador:
        1. Lo resuelve usando el contenedor de DI
        2. Registra todas sus rutas decoradas
        
        Args:
            controllers (list): Lista de clases controladoras marcadas con @Controller
            
        Raises:
            Exception: Si hay algún error al registrar algún controlador.
        """
        for controller_cls in controllers:
            logger.info(f"Configurando controlador: {controller_cls.__name__}")
            controller_instance = await self.container.resolve(controller_cls)
            await self._register_controller_routes(controller_cls, controller_instance)

    async def _register_controller_routes(self, controller_cls, controller_instance):
        """
        Registra las rutas de un controlador específico.
        
        Busca todos los métodos del controlador que tengan información de ruta
        (decorados con @Get, @Post, etc.) y los registra en el sistema de enrutamiento.
        
        Args:
            controller_cls (type): Clase del controlador
            controller_instance: Instancia del controlador ya resuelta
            
        Note:
            Solo registra métodos que sean corrutinas y tengan el atributo '_route_info'.
        """
        prefix = getattr(controller_cls, "_route_prefix", "")
        
        route_methods = [
            (name, method) for name, method in inspect.getmembers(
                controller_instance, 
                predicate=inspect.iscoroutinefunction
            ) if hasattr(method, "_route_info")
        ]
        
        for name, method in route_methods:
            route_info = method._route_info
            full_path = prefix.rstrip("/") + route_info["path"]
            
            logger.info(f"Registrando ruta: {route_info['method'].upper()} {full_path} -> {controller_cls.__name__}.{method.__name__}")
            
            self.routes.append({
                "method": route_info["method"],
                "path": full_path,
                "handler": method
            })
            add_route(route_info["method"], full_path, method)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """
        Punto de entrada principal para requests ASGI.
        
        Este método implementa la interfaz ASGI y maneja:
        - Eventos de ciclo de vida (lifespan)
        - Requests HTTP
        - Otros tipos de scope (con error 500)
        
        Args:
            scope (dict): Información sobre la conexión/request
            receive (callable): Función para recibir mensajes ASGI
            send (callable): Función para enviar mensajes ASGI
            
        Returns:
            None: Responde directamente a través de la función send
        """
        if scope["type"] == "lifespan":
            await self._lifespan(scope, receive, send)
            return

        if scope["type"] != "http":
            response = Response("Unsupported scope type", status_code=500)
            await response(scope, receive, send)
            return

        req = Request(scope, receive)
        method = req.method.upper()
        path = req.url.path

        # Buscar ruta con parámetros tipados
        route, enhanced_handler = find_matching_route(self.routes, method, path)
        
        if route and enhanced_handler:
            result = await enhanced_handler(req)
            if isinstance(result, Response):
                await result(scope, receive, send)
            else:
                await JSONResponse(result)(scope, receive, send)
        else:
            await JSONResponse({"error": "Not Found"}, status_code=404)(scope, receive, send)

    async def _lifespan(self, scope, receive, send):
        """
        Maneja los eventos de ciclo de vida de la aplicación ASGI.
        
        Gestiona los eventos:
        - lifespan.startup: Inicializa la aplicación
        - lifespan.shutdown: Limpia recursos antes del cierre
        
        Args:
            scope (dict): Información del scope de lifespan
            receive (callable): Función para recibir mensajes
            send (callable): Función para enviar respuestas
            
        Note:
            Incluye manejo de errores para ambos eventos de ciclo de vida.
        """
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                try:
                    await self.startup()
                    await send({"type": "lifespan.startup.complete"})
                except Exception as e:
                    await send({"type": "lifespan.startup.failed", "message": str(e)})
            elif message["type"] == "lifespan.shutdown":
                try:
                    await send({"type": "lifespan.shutdown.complete"})
                except Exception as e:
                    await send({"type": "lifespan.shutdown.failed", "message": str(e)})
                break

    def run(self, *, host="localhost", port=4200, reload=True):
        """
        Inicia el servidor de desarrollo usando Uvicorn.
        
        Args:
            host (str, optional): Dirección IP donde escuchar. Por defecto "localhost".
            port (int, optional): Puerto donde escuchar. Por defecto 4200.
            reload (bool, optional): Si habilitar auto-reload en desarrollo. Por defecto True.
            
        Example:
            ```python
            app = Aqua(AppModule)
            app.run(host="0.0.0.0", port=8000, reload=False)
            ```
            
        Note:
            Este método está diseñado para desarrollo. En producción usa un servidor ASGI
            como Uvicorn, Gunicorn + Uvicorn workers, o similar.
        """
        run("main:app", host=host, port=port, reload=reload, log_level="critical")
