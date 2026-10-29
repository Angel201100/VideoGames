# CRUD de videojuegos

Aplicación Django con inicio de sesión y operaciones CRUD para videojuegos. Las cuentas y sesiones se guardan en SQLite; el catálogo se guarda en MongoDB Atlas.

## Preparación

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y reemplaza `MONGO_URI` por la cadena de conexión de tu clúster Atlas. No compartas ni subas ese archivo.

Para cargar cinco juegos de ejemplo en el catálogo, ejecuta una vez:

```powershell
python manage.py seed_videojuegos
```

El comando no reemplaza juegos existentes con el mismo nombre.

## Ejecutar

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py check
python manage.py runserver
```

Abre <http://127.0.0.1:8000/> e inicia sesión con la cuenta creada.

## Pruebas

```powershell
python manage.py test videojuegos
```

Las pruebas del CRUD usan una colección simulada, por lo que pueden ejecutarse sin credenciales ni conexión a MongoDB.

## Mapa del código

- `manage.py`: punto de entrada para los comandos de Django.
- `config/settings.py`: idioma, seguridad, plantillas, archivos estáticos, SQLite y variables de MongoDB.
- `config/urls.py`: rutas globales de acceso, salida y catálogo.
- `config/asgi.py` y `config/wsgi.py`: puntos de entrada para servidores compatibles.
- `videojuegos/db.py`: cliente MongoDB reutilizable y selección de la colección.
- `videojuegos/urls.py`: rutas de consulta, alta, edición y eliminación.
- `videojuegos/views.py`: validación del formulario, vistas protegidas y operaciones CRUD.
- `videojuegos/management/commands/seed_videojuegos.py`: inserción repetible de los cinco juegos de muestra.
- `videojuegos/tests.py`: pruebas de autenticación, validación, operaciones CRUD y carga de muestra.
- `templates/`: páginas HTML para iniciar sesión, mostrar el catálogo y editar videojuegos.
- `static/css/videojuegos.css`: paleta oscura, tarjetas, portada visual y diseño adaptable.

## Flujo de una solicitud

1. Django recibe la ruta y la resuelve mediante `config/urls.py` y `videojuegos/urls.py`.
2. `@login_required` confirma que el usuario tenga una sesión activa antes de ejecutar el CRUD.
3. La vista valida los datos recibidos y obtiene la colección a través de `videojuegos/db.py`.
4. PyMongo lee o modifica los documentos de MongoDB; Django renderiza la respuesta con una plantilla.
5. Las cuentas y las sesiones siguen en SQLite, independientes de los documentos del catálogo.

Los comentarios del código están organizados alrededor de estas secciones para explicar las responsabilidades sin repetir cada instrucción.
