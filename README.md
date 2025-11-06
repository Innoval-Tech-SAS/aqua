# 🌊 Aqua Framework

**Un framework web moderno para Python que hace que crear APIs sea tan simple como escribir funciones.**

¿Cansado de configurar manualmente cada dependencia en tu aplicación? ¿Quieres crear APIs web sin la complejidad de frameworks pesados? Aqua es la solución perfecta: combina la simplicidad de escribir código Python limpio con características avanzadas que normalmente requieren configuración compleja.

## 🎯 ¿Por qué Aqua?

### 🚀 **Desarrollo Rápido**
Crea una API completa en minutos, no horas. Solo escribe tus funciones y Aqua se encarga del resto.

### 🧩 **Inyección Automática**
Olvídate de crear manualmente todas las instancias. Aqua conecta automáticamente tus servicios y dependencias.

### � **Organización Natural**
Estructura tu código como módulos independientes que se pueden reutilizar y mantener fácilmente.

### ⚡ **Rendimiento Real**
Construido sobre tecnología asíncrona moderna para manejar miles de usuarios simultáneos.

## ✨ Lo que hace especial a Aqua

- 🎨 **Sintaxis Familiar**: Si sabes Python, ya sabes usar Aqua
- 🔌 **Conecta Todo Solo**: Las dependencias se resuelven automáticamente
- 🏗️ **Modular**: Organiza tu aplicación en piezas pequeñas y reutilizables  
- 🚀 **Asíncrono**: Diseñado para aplicaciones modernas de alto rendimiento
- 🪶 **Ligero**: Sin configuraciones complejas ni archivos XML gigantes
- 🎯 **Parámetros Tipados**: URLs con tipos automáticos como `<int:id>` y `<str:slug>`
- 🔄 **Flexible**: Usa `request` solo cuando lo necesites, como Flask/FastAPI

## 🌟 Tu Primera API en 5 Minutos

### Paso 1: Crea un Servicio

```python
from core.decorators.di_decorators import Injectable

@Injectable  # Esto dice "Aqua, maneja esta clase automáticamente"
class GreetingService:
    def get_welcome_message(self, name):
        return f"¡Hola {name}! Bienvenido a Aqua 🌊"
```

### Paso 2: Crea un Controlador

```python
from core.controller import Controller, Get
from core.decorators.di_decorators import Injectable, Inject

@Injectable
@Controller("/api")  # Todas las rutas empezarán con /api
@Inject(greeting_service=GreetingService)  # Aqua inyecta el servicio automáticamente
class WelcomeController:
    def __init__(self, greeting_service):
        self.greeting_service = greeting_service
    
    @Get("/welcome/<str:name>")  # GET /api/welcome/Juan - parámetro tipado
    async def welcome_user(self, name: str):  # ¡Sin request! Solo el parámetro
        message = self.greeting_service.get_welcome_message(name)
        return {"message": message}
    
    @Get("/users/<int:user_id>")  # GET /api/users/123 - entero automático
    async def get_user(self, user_id: int):  # user_id ya es int, no string
        return {
            "user_id": user_id,
            "name": f"Usuario {user_id}",
            "type": type(user_id).__name__  # Confirma que es 'int'
        }
```

### Paso 3: Ensambla tu Aplicación

```python
from core import Aqua
from core.module import Module

# Junta todo en un módulo
AppModule = Module(
    controllers=[WelcomeController],  # Tus controladores
    providers=[GreetingService]       # Tus servicios
)

# Crea la aplicación
app = Aqua(AppModule)

# ¡Listo para ejecutar!
if __name__ == "__main__":
    app.run()
```

### 🎉 ¡Ya tienes una API funcionando!

Ejecuta `python main.py` y visita:
- `http://localhost:4200/api/welcome/Juan` → `{"message": "¡Hola Juan! Bienvenido a Aqua 🌊"}`
- `http://localhost:4200/api/users/123` → `{"user_id": 123, "name": "Usuario 123", "type": "int"}`

## 🎯 Parámetros URL Tipados - La Magia de Aqua

Una de las características más poderosas de Aqua es su sistema de parámetros URL tipados. Olvídate de convertir strings manualmente:

### 🔢 Tipos Soportados

```python
@Get("/productos/<int:product_id>")           # Enteros
async def get_product(self, product_id: int): 
    return {"id": product_id}  # product_id ya es int

@Get("/usuarios/<str:username>")              # Strings  
async def get_user(self, username: str):
    return {"username": username}

@Get("/precios/<float:price>")                # Números decimales
async def get_price(self, price: float):
    return {"precio": price}  # price ya es float

@Get("/configs/<uuid:config_id>")             # UUIDs
async def get_config(self, config_id: UUID):
    return {"config": str(config_id)}  # config_id ya es UUID
```

### 🎪 Múltiples Parámetros

```python
@Get("/tienda/<int:store_id>/productos/<str:category>/precio/<float:max_price>")
async def search_products(self, store_id: int, category: str, max_price: float):
    return {
        "tienda": store_id,      # int automáticamente
        "categoria": category,   # str automáticamente  
        "precio_max": max_price, # float automáticamente
        "tipos": {
            "store_id": type(store_id).__name__,    # 'int'
            "category": type(category).__name__,    # 'str'
            "max_price": type(max_price).__name__   # 'float'
        }
    }

# Llamada: GET /tienda/42/productos/electronicos/precio/999.99
# Resultado: {"tienda": 42, "categoria": "electronicos", "precio_max": 999.99, ...}
```

### 🔄 Flexibilidad Total - Con o Sin Request

```python
# ✅ Estilo Flask/FastAPI - Solo parámetros URL
@Get("/simple/<int:id>")
async def simple_endpoint(self, id: int):
    return {"id": id}

# ✅ Con acceso al request cuando lo necesites
@Post("/advanced/<int:user_id>")  
async def advanced_endpoint(self, request, user_id: int):
    body = await request.json()
    return {
        "user_id": user_id,
        "data": body,
        "method": request.method,
        "headers": dict(request.headers)
    }
```

## 🎪 Ejemplos del Mundo Real

### 📚 Sistema de Biblioteca

```python
# Servicio de base de datos
@Injectable
class BookDatabase:
    def __init__(self):
        self.books = [
            {"id": 1, "title": "El Quijote", "author": "Cervantes"},
            {"id": 2, "title": "Cien años de soledad", "author": "García Márquez"}
        ]
    
    def find_all_books(self):
        return self.books
    
    def find_book_by_id(self, book_id):
        return next((book for book in self.books if book["id"] == book_id), None)

# Servicio de lógica de negocio
@Injectable  
class BookService:
    def __init__(self, database: BookDatabase):  # ← Inyección automática por tipo
        self.db = database
    
    async def get_all_books(self):
        return {"books": self.db.find_all_books(), "total": len(self.db.books)}
    
    async def get_book_details(self, book_id):
        book = self.db.find_book_by_id(int(book_id))
        if book:
            return {"book": book, "status": "found"}
        return {"error": "Libro no encontrado", "status": "not_found"}

# Controlador de API
@Injectable
@Controller("/biblioteca")
class BookController:
    def __init__(self, book_service: BookService):  # ← Inyección automática
        self.book_service = book_service
    
    @Get("/libros")
    async def list_books(self):
        return await self.book_service.get_all_books()
    
    @Get("/libros/<int:book_id>")
    async def get_book(self, book_id: int):  # book_id ya es int!
        return await self.book_service.get_book_details(book_id)
```

### 🛒 E-commerce Simple

```python
@Injectable
class PaymentService:
    async def process_payment(self, amount, currency="USD"):
        # Aquí iría tu lógica de pago real
        return {"transaction_id": "TX123", "status": "approved", "amount": amount}

@Injectable
class OrderService:
    def __init__(self, payment_service: PaymentService):
        self.payment = payment_service
    
    async def create_order(self, items, customer_email):
        total = sum(item["price"] for item in items)
        payment_result = await self.payment.process_payment(total)
        
        return {
            "order_id": "ORD456",
            "items": items,
            "total": total,
            "customer": customer_email,
            "payment": payment_result
        }

@Injectable
@Controller("/tienda")
class ShopController:
    def __init__(self, order_service: OrderService):
        self.orders = order_service
    
    @Post("/pedidos")
    async def create_order(self, request):  # POST necesita request para el body
        data = await request.json()
        result = await self.orders.create_order(
            items=data["items"],
            customer_email=data["customer_email"]
        )
        return result
```

## 🔧 Instalación y Configuración

### Requisitos Mínimos
- Python 3.8+
- Ganas de crear cosas increíbles 🚀

### Instalación

```bash
# Clona el proyecto
git clone https://github.com/tu-usuario/aqua.git
cd aqua

# Instala las dependencias (recomendamos uv)
uv sync

# O si prefieres pip
pip install -r requirements.txt
```

### Primera Ejecución

```bash
# Modo desarrollo (con auto-recarga)
python main.py

# Tu API estará disponible en http://localhost:4200
```

## 🏗️ Conceptos Clave

### 🎭 **Decoradores Mágicos**

- `@Injectable`: "Esta clase puede ser manejada automáticamente"
- `@Controller("/ruta")`: "Esta clase maneja requests HTTP"  
- `@Get("/<int:id>")`, `@Post("/<str:slug>")`: "Este método responde a HTTP con parámetros tipados"
- `@Inject(servicio=ClaseServicio)`: "Usa esta clase específica"

### 🧩 **Inyección de Dependencias**

```python
# ❌ Forma tradicional (tediosa)
database = Database()
email_service = EmailService()
user_service = UserService(database, email_service)
controller = UserController(user_service)

# ✅ Con Aqua (automática)
@Injectable
class UserController:
    def __init__(self, user_service: UserService):  # ← Aqua conecta todo
        self.service = user_service
```

### 🎯 **Parámetros URL - Antes vs Ahora**

```python
# ❌ Forma tradicional (conversión manual)
@Get("/users/{user_id}")
async def get_user(self, request):
    user_id = int(request.path_params["user_id"])  # ¡Conversión manual!
    if user_id <= 0:  # ¡Validación manual!
        return {"error": "ID inválido"}
    return {"user": user_id}

# ✅ Con Aqua (automático)
@Get("/users/<int:user_id>")
async def get_user(self, user_id: int):  # ¡Ya es int y validado!
    return {"user": user_id}  # Si no es int válido, Aqua devuelve 404
```

### 📦 **Módulos Organizados**

```python
# Módulo de usuarios
UserModule = Module(
    controllers=[UserController, UserAdminController],
    providers=[UserService, UserRepository, EmailService]
)

# Módulo de productos  
ProductModule = Module(
    controllers=[ProductController],
    providers=[ProductService, InventoryService]
)

# Aplicación completa
AppModule = Module(
    controllers=[*UserModule.controllers, *ProductModule.controllers],
    providers=[*UserModule.providers, *ProductModule.providers]
)
```

## 🚀 Despliegue en Producción

### Con Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Con Uvicorn Directo

```bash
# Instalación
pip install uvicorn[standard]

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🤔 ¿Cuándo Usar Aqua?

### ✅ **Perfecto Para:**
- APIs REST y microservicios
- Prototipos rápidos que necesitan escalar
- Aplicaciones con lógica de negocio compleja
- Equipos que valoran código limpio y mantenible
- Proyectos que necesitan inyección de dependencias sin complejidad

### 🤷‍♂️ **Quizás No Es Para Ti Si:**
- Solo necesitas servir archivos estáticos
- Prefieres frameworks más establecidos como Django/Flask
- Tu proyecto es principalmente front-end

## 🌈 Lo Que Viene

- 🔐 Autenticación y autorización integrada
- 📊 Métricas y monitoreo automático  
- �️ Integración con ORMs populares
- 📚 Generación automática de documentación
- 🧪 Herramientas de testing integradas

## 🤝 Únete a la Comunidad

¿Tienes ideas? ¿Encontraste un bug? ¿Quieres contribuir?

1. 🍴 Fork el proyecto
2. 🌿 Crea tu rama (`git checkout -b mi-nueva-funcionalidad`)
3. 💾 Confirma tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. 📤 Sube tu rama (`git push origin mi-nueva-funcionalidad`)
5. 🔃 Abre un Pull Request

## � Licencia

Licencia MIT - úsalo, modifícalo, compártelo. Solo pedimos que menciones que usas Aqua 🌊

---

**¿Listo para sumergirte?** Empieza con `git clone` y en 5 minutos tendrás tu primera API funcionando. 

**¿Preguntas?** Abre un [issue](https://github.com/tu-usuario/aqua/issues) - estamos aquí para ayudar.

*¡El futuro de las APIs es simple, elegante y poderoso. Bienvenido a Aqua! 🌊*