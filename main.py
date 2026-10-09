"""
Aplicación principal del framework Aqua.

Este archivo contiene la configuración principal de la aplicación, incluyendo
servicios, controladores y la definición del módulo raíz.

Ejemplo de uso:
    python main.py

Autor: lyrionlannister
Versión: 1.0.0
"""

from core import Aqua, Controller, Get, Post, Injectable, Inject, Module


@Injectable
class UserService:
    """
    Servicio de ejemplo que demuestra la inyección de dependencias.
    
    Este servicio proporciona funcionalidades básicas y puede ser
    inyectado en controladores u otros servicios.
    
    Attributes:
        Ningún atributo específico en esta implementación básica.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa el servicio.
        
        Args:
            *args: Argumentos posicionales (para compatibilidad con DI)
            **kwargs: Argumentos nombrados (para compatibilidad con DI)
        """
        pass
    
    async def do_work(self):
        """
        Realiza algún trabajo asíncrono.
        
        Returns:
            str: Mensaje indicando que el trabajo fue completado.
            
        Example:
            ```python
            service = UserService()
            result = await service.do_work()
            print(result)  # "Trabajo hecho"
            ```
        """
        return "Trabajo hecho"






@Injectable
@Controller("/users")
@Inject(my_service=UserService)
class UserController:
    """
    Controlador para manejar operaciones relacionadas con usuarios.
    
    Este controlador demuestra:
    - Inyección de dependencias usando @Inject
    - Definición de rutas usando decoradores
    - Integración con servicios
    
    Attributes:
        my_service (UserService): Servicio inyectado para lógica de negocio.
    """
    
    def __init__(self, my_service: UserService):
        """
        Inicializa el controlador con las dependencias inyectadas.
        
        Args:
            my_service (UserService): Instancia del servicio de usuarios.
        """
        self.my_service = my_service

    @Get("/")
    async def list_users(self):
        """
        Endpoint para listar usuarios.
        
        Returns:
            dict: Respuesta JSON con el resultado del servicio y lista de usuarios.
            
        Example:
            GET /users/
            
            Response:
            ```json
            {
                "message": "Trabajo hecho",
                "users": [{"id": 1, "name": "Alice"}]
            }
            ```
        """
        resultado = await self.my_service.do_work()
        return {"message": resultado, "users": [{"id":1,"name":"Alice"}]}

    @Get("/<int:user_id>")
    async def get_user(self, user_id: int):
        """
        Endpoint para obtener un usuario específico por ID.
        
        Args:
            user_id (int): ID del usuario (recibido como entero automáticamente)
            
        Returns:
            dict: Información del usuario solicitado
        """
        resultado = await self.my_service.do_work()
        return {
            "user": {"id": user_id, "name": f"Usuario {user_id}"}, 
            "message": resultado,
            "type_of_id": type(user_id).__name__  # Mostrará 'int'
        }

    @Get("/<int:user_id>/posts/<str:slug>")
    async def get_user_post(self, user_id: int, slug: str):
        """
        Endpoint para obtener un post específico de un usuario por slug.
        
        Args:
            user_id (int): ID del usuario (entero)
            slug (str): Slug del post (string)
            
        Returns:
            dict: Información del post del usuario
        """
        resultado = await self.my_service.do_work()
        return {
            "user_id": user_id,
            "slug": slug,
            "post": {"title": f"Post '{slug}' del Usuario {user_id}"},
            "message": resultado,
            "types": {
                "user_id": type(user_id).__name__,  # 'int'
                "slug": type(slug).__name__          # 'str'
            }
        }

    @Post("/<int:user_id>/update", allow_raw_request=True)
    async def update_user(self, request, user_id: int):
        """
        Endpoint para actualizar un usuario - ejemplo con request y parámetros.
        
        Args:
            request (Request): Objeto request HTTP (para acceder al body)
            user_id (int): ID del usuario a actualizar
            
        Returns:
            dict: Resultado de la actualización
        """
        try:
            body = await request.json()
        except:
            body = {}
            
        resultado = await self.my_service.do_work()
        return {
            "user_id": user_id,
            "updated_data": body,
            "message": resultado,
            "method": request.method
        }



@Module(
    controllers=[UserController],
    providers=[UserService],
)
class UserModule:
    """
    Módulo de usuarios que agrupa controladores y servicios relacionados con usuarios.
    
    Este módulo actúa como contenedor para todas las funcionalidades
    relacionadas con la gestión de usuarios en la aplicación.
    
    Attributes:
        controllers (list): Lista de controladores a registrar.
        providers (list): Lista de servicios/proveedores a registrar.
        imports (list): Lista de módulos importados para composición modular.
    """
    pass


@Module(
    imports=[UserModule],  
)

class AppModule:
    """
    Módulo raíz de la aplicación Aqua.
    
    Este módulo configura los controladores y servicios principales
    que componen la aplicación. Actúa como punto de entrada para
    la configuración del contenedor de inyección de dependencias
    y el enrutamiento HTTP.
    
    Attributes:
        controllers (list): Lista de controladores a registrar.
        providers (list): Lista de servicios/proveedores a registrar.
        imports (list): Lista de módulos importados para composición modular.
    """
    pass


app = Aqua(AppModule)

if __name__ == "__main__":
    app.run(app_import_string="main:app")
