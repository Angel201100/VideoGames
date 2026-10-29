# Guía práctica: CRUD de videojuegos con inicio de sesión, Django y MongoDB

**Objetivo:** construir una aplicación web que exija iniciar sesión con una cuenta de usuario y que, una vez dentro, permita registrar, consultar, editar y eliminar videojuegos, además de cerrar la sesión. Se utilizarán Django, Python y MongoDB Atlas.

Esta práctica continúa el trabajo realizado con Django y MongoDB (CRUD de productos). Los aprendices ya conocen las vistas, las URL, los formularios HTML, las operaciones CRUD y la conexión con PyMongo. Ahora aprenderán a proteger las páginas con **autenticación**: solo quien inicie sesión podrá ver y administrar el catálogo.

## ¿Qué vamos a construir?

Una aplicación web de catálogo de videojuegos con cuatro datos por juego:

- Nombre.
- Costo.
- Descripción del juego.
- Cantidad de jugadores.

Las funciones serán:

- **Iniciar sesión:** ingresar con usuario y contraseña.
- **Consultar:** al ingresar, se muestran todos los videojuegos registrados.
- **Crear:** agregar videojuegos nuevos.
- **Editar:** modificar los datos de un videojuego.
- **Eliminar:** borrar un videojuego.
- **Cerrar sesión:** salir de la aplicación de forma segura.

El flujo de uso será:

**Visitante → Página de inicio de sesión → Catálogo de videojuegos → Agregar / Editar / Eliminar → Cerrar sesión**

## 1. Comprender las tecnologías

| Tecnología | Función |
|---|---|
| Python | Lenguaje de programación. |
| Django | Gestiona las URL, las vistas, las plantillas HTML y la autenticación de usuarios. |
| PyMongo | Permite que Python se comunique con MongoDB. |
| MongoDB Atlas | Aloja la base de datos de videojuegos en la nube. |
| HTML | Presenta el inicio de sesión, los formularios y el catálogo en el navegador. |

El funcionamiento será:

**Navegador → Django (URL, autenticación, vista y validación) → PyMongo → MongoDB Atlas**

**Dos lugares de almacenamiento:** en esta práctica los datos se guardan en dos sitios distintos y cada uno cumple una función.

| Dato | Dónde se guarda | Quién lo gestiona |
|---|---|---|
| Videojuegos | MongoDB Atlas (colección `videojuegos`) | PyMongo |
| Cuentas de usuario y sesiones | SQLite (`db.sqlite3`, base interna de Django) | Sistema de autenticación de Django |

Por eso no necesitamos crear un modelo Django para los videojuegos, pero sí ejecutaremos las migraciones de Django: son las que crean las tablas de usuarios y sesiones.

## 2. Preparar el entorno de trabajo

Necesitamos:

- Python instalado.
- Visual Studio Code.
- Un navegador web.
- Una cuenta de MongoDB Atlas.

No necesitamos Docker, una API REST ni Django REST Framework.

### 2.1. Crear la carpeta del proyecto

Abre Visual Studio Code, selecciona **Terminal → Nueva terminal** y ejecuta estos comandos en Windows:

```powershell
mkdir django_videojuegos
cd django_videojuegos
```

### 2.2. Crear y activar el entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Si utilizas CMD en lugar de PowerShell, activa el entorno con:

```bat
venv\Scripts\activate.bat
```

Un entorno virtual permite instalar las dependencias de este proyecto sin mezclarlas con las de otros proyectos de Python. Cuando esté activo, normalmente aparecerá `(venv)` al comienzo de la línea de la terminal.

Si Windows bloquea la activación en PowerShell, puedes seleccionar CMD como terminal de VS Code y utilizar el segundo comando.

### 2.3. Instalar las dependencias

```powershell
python -m pip install django pymongo dnspython python-dotenv
```

- `django`: permite desarrollar la aplicación web y trae incluido el sistema de usuarios.
- `pymongo`: conecta Python con MongoDB.
- `dnspython`: permite resolver los registros DNS utilizados por conexiones `mongodb+srv://`.
- `python-dotenv`: permite leer variables de configuración desde el archivo `.env`.

Comprueba que Django esté instalado:

```powershell
python -m django --version
```

## 3. Crear el proyecto Django

Ejecuta:

```powershell
django-admin startproject config .
python manage.py startapp videojuegos
```

El primer comando crea la configuración general de Django. El segundo crea la aplicación que administrará los videojuegos.

La estructura inicial será parecida a esta:

```text
django_videojuegos/
├── venv/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── videojuegos/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    └── views.py
```

No es necesario modificar todos los archivos. Trabajaremos solamente con los que necesitamos para el CRUD y el inicio de sesión.

## 4. Crear la base de datos en MongoDB Atlas

Utilizaremos MongoDB Atlas para que los aprendices no tengan que instalar y configurar un servidor de base de datos en sus computadores.

### 4.1. Crear la cuenta y el clúster

1. Ingresa a [MongoDB Atlas](https://www.mongodb.com/atlas).
2. Crea una cuenta o inicia sesión.
3. Crea un clúster del nivel gratuito disponible.
4. Crea un usuario de base de datos con contraseña.
5. En el acceso a la red, autoriza la dirección IP pública desde la cual trabajarás.
6. En el clúster, pulsa **Connect** y selecciona la opción de conexión para una aplicación.

No es necesario crear manualmente una colección. MongoDB podrá crearla cuando guardemos el primer videojuego.

**No confundir cuentas:** el usuario de base de datos de Atlas sirve para que Django se conecte a MongoDB. La cuenta con la que se inicia sesión en la aplicación es otra distinta y se crea más adelante con Django.

### 4.2. Obtener la cadena de conexión

Atlas proporcionará una dirección parecida a esta:

```text
mongodb+srv://usuario:contraseña@cluster0.xxxxx.mongodb.net/
```

La dirección real tendrá el nombre de tu clúster. Utiliza la cadena que entrega Atlas, no copies literalmente el ejemplo.

**Importante:** no compartas la contraseña ni publiques la cadena de conexión en GitHub. Si la contraseña contiene caracteres especiales, puede ser necesario codificarlos correctamente en la URL.

## 5. Guardar la conexión de forma segura

Una buena práctica es separar las credenciales de la base de datos del código fuente.

### 5.1. Crear el archivo `.env`

En la raíz del proyecto, al mismo nivel que `manage.py`, crea un archivo llamado `.env`:

```text
django_videojuegos/
├── .env
├── manage.py
├── config/
└── videojuegos/
```

Dentro de `.env`, escribe:

```dotenv
MONGO_URI="PEGA_AQUI_LA_CADENA_DE_ATLAS"
MONGO_DB="tienda_videojuegos"
```

Reemplaza el valor de `MONGO_URI` por tu cadena real de conexión.

### 5.2. Proteger las credenciales

Crea un archivo `.gitignore` en la raíz del proyecto:

```gitignore
venv/
__pycache__/
*.py[cod]
.env
db.sqlite3
```

Esto evita incluir las credenciales y la base de datos de usuarios en los cambios que se suban al repositorio Git.

## 6. Configurar Django

Abre `config/settings.py`.

Al principio del archivo, agrega estos imports. Si `Path` ya está importado, no lo dupliques:

```python
import os
from pathlib import Path
from dotenv import load_dotenv
```

Busca la línea que define `BASE_DIR`:

```python
BASE_DIR = Path(__file__).resolve().parent.parent
```

Inmediatamente después, agrega:

```python
load_dotenv(BASE_DIR / ".env")
```

Al final de `settings.py`, agrega la configuración de MongoDB:

```python
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "tienda_videojuegos")
```

Registra también la aplicación. Busca `INSTALLED_APPS` y agrega `"videojuegos"` sin eliminar las aplicaciones que Django creó automáticamente. Las aplicaciones `auth`, `contenttypes`, `sessions` y `messages` son las que hacen posible el inicio de sesión:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "videojuegos",
]
```

Comprueba que en `MIDDLEWARE` sigan estas líneas, que Django incluye por defecto. No las elimines, porque la autenticación depende de ellas:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

Como las plantillas estarán fuera de la aplicación, configura `TEMPLATES` para buscar en la carpeta `templates` de la raíz del proyecto:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

El procesador `auth` permite usar la variable `user` en cualquier plantilla, por ejemplo para mostrar el nombre de quien inició sesión.

Configura también la carpeta `static` de la raíz para conectar el CSS:

```python
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

Finalmente, indica a Django a dónde enviar al usuario en cada momento del ciclo de sesión. Agrega al final de `settings.py`:

```python
# Página a la que se envía a quien intenta entrar sin haber iniciado sesión.
LOGIN_URL = "login"

# Página que se muestra después de iniciar sesión correctamente.
LOGIN_REDIRECT_URL = "videojuegos:listar"

# Página que se muestra después de cerrar sesión.
LOGOUT_REDIRECT_URL = "login"
```

Estos valores son **nombres de URL** que definiremos más adelante en la sección 10.

## 7. Crear la conexión con MongoDB

Dentro de la carpeta `videojuegos`, crea el archivo `db.py`.

Ruta: `videojuegos/db.py`

```python
from django.conf import settings
from pymongo import MongoClient


if not settings.MONGO_URI:
    raise RuntimeError(
        "Falta configurar MONGO_URI en el archivo .env"
    )


cliente = MongoClient(
    settings.MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = cliente[settings.MONGO_DB]

coleccion_videojuegos = db["videojuegos"]
```

### ¿Qué hace este código?

- `MongoClient()` crea el cliente de conexión.
- `settings.MONGO_URI` obtiene la dirección configurada.
- `settings.MONGO_DB` indica qué base de datos utilizaremos.
- `db["videojuegos"]` selecciona la colección que guardará los videojuegos.

El tiempo de espera de cinco segundos evita que algunas operaciones queden esperando demasiado ante problemas de conexión. `MongoClient` puede reutilizarse; no necesitamos crear un cliente nuevo para cada videojuego.

## 8. Comprender cómo se almacenan los videojuegos

En MongoDB trabajaremos con una colección de documentos. Un videojuego podría almacenarse así:

```json
{
  "_id": "identificador generado por MongoDB",
  "nombre": "Overcooked 2",
  "costo": 70000.0,
  "descripcion": "Juego cooperativo de cocina caótica donde el equipo debe preparar y entregar pedidos a tiempo.",
  "jugadores": 4
}
```

El campo `_id` identifica de manera única el documento. MongoDB normalmente genera un `ObjectId` automáticamente.

| Campo | Tipo | Ejemplo |
|---|---|---|
| `nombre` | Texto | Overcooked 2 |
| `costo` | Número | 70000 |
| `descripcion` | Texto | Juego cooperativo de cocina caótica... |
| `jugadores` | Entero | 4 |

No vamos a crear un modelo de Django para representar los videojuegos. PyMongo trabajará directamente con los documentos de la colección.

## 9. Crear las vistas del CRUD

Abre `videojuegos/views.py` y reemplaza su contenido por este código. Incluye validación en el servidor, mensajes para el usuario, identificación de documentos, manejo de errores de MongoDB y protección de cada vista con `@login_required`.

```python
import math

from bson import ObjectId
from bson.errors import InvalidId

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from pymongo.errors import PyMongoError

from .db import coleccion_videojuegos


def validar_videojuego(datos):
    """Valida los datos recibidos del formulario."""

    nombre = datos.get("nombre", "").strip()
    costo_texto = datos.get("costo", "").strip()
    descripcion = datos.get("descripcion", "").strip()
    jugadores_texto = datos.get("jugadores", "").strip()

    errores = []

    if not nombre:
        errores.append("El nombre es obligatorio.")
    elif len(nombre) > 100:
        errores.append("El nombre no puede superar 100 caracteres.")

    try:
        costo = float(costo_texto)

        if not math.isfinite(costo) or costo < 0:
            errores.append(
                "El costo debe ser un número válido y no negativo."
            )
    except ValueError:
        costo = None
        errores.append("Ingresa un costo válido.")

    if not descripcion:
        errores.append("La descripción es obligatoria.")
    elif len(descripcion) > 500:
        errores.append("La descripción no puede superar 500 caracteres.")

    try:
        jugadores = int(jugadores_texto)

        if jugadores < 1 or jugadores > 100:
            errores.append(
                "La cantidad de jugadores debe estar entre 1 y 100."
            )
    except ValueError:
        jugadores = None
        errores.append("La cantidad de jugadores debe ser un número entero.")

    videojuego = {
        "nombre": nombre,
        "costo": costo,
        "descripcion": descripcion,
        "jugadores": jugadores,
    }

    return videojuego, errores


@login_required
def listar(request):
    """Consulta y muestra todos los videojuegos."""

    try:
        datos = list(
            coleccion_videojuegos.find().sort("nombre", 1)
        )
        for videojuego in datos:
            # Django bloquea el acceso a claves que comienzan con "_".
            # La plantilla usa "id", con el mismo identificador convertido a texto.
            videojuego["id"] = str(videojuego["_id"])

        return render(
            request,
            "videojuegos/lista.html",
            {"videojuegos": datos},
        )

    except PyMongoError:
        messages.error(
            request,
            "No fue posible consultar los videojuegos. "
            "Verifica la conexión con MongoDB."
        )

        return render(
            request,
            "videojuegos/lista.html",
            {"videojuegos": []},
        )


@login_required
def crear(request):
    """Registra un videojuego."""

    if request.method == "POST":
        videojuego, errores = validar_videojuego(request.POST)

        if errores:
            for error in errores:
                messages.error(request, error)

            return render(
                request,
                "videojuegos/formulario.html",
                {"videojuego": videojuego, "editando": False},
            )

        try:
            coleccion_videojuegos.insert_one(videojuego)

            messages.success(
                request,
                "Videojuego registrado correctamente."
            )

            return redirect("videojuegos:listar")

        except PyMongoError:
            messages.error(
                request,
                "No fue posible guardar el videojuego."
            )

            return render(
                request,
                "videojuegos/formulario.html",
                {"videojuego": videojuego, "editando": False},
            )

    return render(
        request,
        "videojuegos/formulario.html",
        {"editando": False},
    )


@login_required
def editar(request, id):
    """Actualiza un videojuego existente."""

    try:
        identificador = ObjectId(id)
    except (InvalidId, TypeError):
        messages.error(request, "El identificador no es válido.")
        return redirect("videojuegos:listar")

    try:
        videojuego_actual = coleccion_videojuegos.find_one(
            {"_id": identificador}
        )

        if videojuego_actual is None:
            messages.error(request, "El videojuego no existe.")
            return redirect("videojuegos:listar")

        if request.method == "POST":
            videojuego, errores = validar_videojuego(request.POST)

            if errores:
                for error in errores:
                    messages.error(request, error)

                return render(
                    request,
                    "videojuegos/formulario.html",
                    {"videojuego": videojuego, "editando": True},
                )

            resultado = coleccion_videojuegos.update_one(
                {"_id": identificador},
                {"$set": videojuego},
            )

            if resultado.matched_count == 0:
                messages.error(request, "El videojuego ya no existe.")
            else:
                messages.success(
                    request,
                    "Videojuego actualizado correctamente."
                )

            return redirect("videojuegos:listar")

        return render(
            request,
            "videojuegos/formulario.html",
            {"videojuego": videojuego_actual, "editando": True},
        )

    except PyMongoError:
        messages.error(
            request,
            "No fue posible consultar o actualizar el videojuego."
        )

        return redirect("videojuegos:listar")


@login_required
def eliminar(request, id):
    """Elimina un videojuego mediante POST."""

    if request.method != "POST":
        messages.error(
            request,
            "La eliminación requiere enviar el formulario."
        )
        return redirect("videojuegos:listar")

    try:
        identificador = ObjectId(id)
    except (InvalidId, TypeError):
        messages.error(request, "El identificador no es válido.")
        return redirect("videojuegos:listar")

    try:
        resultado = coleccion_videojuegos.delete_one(
            {"_id": identificador}
        )

        if resultado.deleted_count == 1:
            messages.success(
                request,
                "Videojuego eliminado correctamente."
            )
        else:
            messages.error(
                request,
                "El videojuego no existe o ya fue eliminado."
            )

    except PyMongoError:
        messages.error(
            request,
            "No fue posible eliminar el videojuego."
        )

    return redirect("videojuegos:listar")
```

### 9.1. Comprender las vistas

La función `validar_videojuego()` centraliza la validación de los datos. Así evitamos duplicar las mismas comprobaciones al crear y editar.

| Operación | Instrucción | Significado |
|---|---|---|
| Crear | `insert_one(videojuego)` | Inserta un documento. |
| Consultar | `find()` | Recupera documentos. |
| Editar | `update_one(filtro, cambios)` | Modifica un documento. |
| Eliminar | `delete_one(filtro)` | Borra un documento. |

En las operaciones de edición y eliminación, el filtro utiliza `_id`. Así actuamos sobre un videojuego específico, en lugar de modificar o borrar toda la colección.

### 9.2. Comprender `@login_required`

El decorador `@login_required` se escribe justo encima de cada vista que debe estar protegida. Funciona así:

1. Si el usuario **ya inició sesión**, la vista se ejecuta con normalidad.
2. Si el usuario **no ha iniciado sesión**, Django lo redirige a la dirección definida en `LOGIN_URL` y recuerda la página que quería visitar (`/login/?next=/`).
3. Después de ingresar con sus credenciales, Django lo devuelve a esa página.

Todas las vistas llevan el decorador, incluida `eliminar`. Si solo protegiéramos la lista, alguien que conozca la dirección `/crear/` podría registrar videojuegos sin haber iniciado sesión.

### 9.3. Diferencias con la guía de productos

| Cambio | Motivo |
|---|---|
| Variable `editando` en el contexto | El título del formulario depende de ella. Si se usara `{% if videojuego %}`, al fallar la validación al **crear** aparecería el título «Editar», porque en ese caso también se devuelve un diccionario con los datos escritos. |
| Campo `descripcion` | Es un texto largo con límite de 500 caracteres. |
| Campo `jugadores` | Es un entero entre 1 y 100. |
| `@login_required` en cada vista | Impide el acceso sin cuenta. |

## 10. Crear las URL de la aplicación

Crea `videojuegos/urls.py`:

```python
from django.urls import path
from . import views


app_name = "videojuegos"

urlpatterns = [
    path("", views.listar, name="listar"),
    path("crear/", views.crear, name="crear"),
    path("editar/<str:id>/", views.editar, name="editar"),
    path("eliminar/<str:id>/", views.eliminar, name="eliminar"),
]
```

Ahora abre `config/urls.py` y reemplaza su contenido por el siguiente. Aquí se agregan las rutas de **inicio** y **cierre de sesión**, que Django ya trae programadas:

```python
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),

    # Inicio de sesión. Si ya hay sesión activa, redirige al catálogo.
    path(
        "login/",
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name="login",
    ),

    # Cierre de sesión. Solo acepta peticiones POST.
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("", include("videojuegos.urls")),
]
```

Las URL indican qué vista debe ejecutarse cuando el usuario visita una dirección o envía un formulario.

**No necesitamos escribir las vistas de login ni de logout.** `LoginView` valida el usuario y la contraseña, crea la sesión y redirige a `LOGIN_REDIRECT_URL`. `LogoutView` destruye la sesión y redirige a `LOGOUT_REDIRECT_URL`.

**Importante:** desde Django 5.0, `LogoutView` solo acepta el método POST. Por eso el botón **Cerrar sesión** será un formulario y no un enlace simple. Esto evita que una página externa cierre la sesión del usuario sin que él lo sepa.

## 11. Crear las plantillas y los estilos

El mismo formulario servirá para crear y editar videojuegos, evitando mantener dos archivos casi iguales.

Crea estas carpetas en la raíz del proyecto, al mismo nivel que `manage.py`. Las plantillas quedan fuera de `videojuegos` y los estilos en un archivo CSS independiente:

```text
videojuegos/
├── db.py
├── urls.py
└── views.py

templates/
├── registration/
│   └── login.html
└── videojuegos/
    ├── formulario.html
    └── lista.html

static/
└── css/
    └── videojuegos.css
```

La plantilla de inicio de sesión debe estar en `templates/registration/login.html`, porque es la ruta donde `LoginView` la busca por defecto.

En cada plantilla carga la etiqueta `static` y enlaza la hoja CSS en `<head>`. Esto mantiene el HTML separado de su presentación:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/videojuegos.css' %}">
```

Crea `static/css/videojuegos.css`. Este ejemplo muestra estilos compartidos y comentarios que explican cada grupo de reglas:

```css
/* Estilo general compartido por las páginas. */
body {
    margin: 0;
    padding: 24px;
    font-family: system-ui, sans-serif;
    color: #172033;
    background: #f3f6fb;
}

/* Limita el ancho del contenido y lo centra. */
.contenedor {
    max-width: 800px;
    margin: 0 auto;
}

/* Barra superior con el título y los datos de la sesión. */
.barra {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}

.usuario-sesion {
    display: flex;
    gap: 12px;
    align-items: center;
}

/* La tarjeta destaca cada bloque sobre el fondo. */
.card {
    margin-bottom: 16px;
    padding: 24px;
    border-radius: 16px;
    background: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Los campos ocupan el ancho disponible. */
input,
textarea {
    box-sizing: border-box;
    width: 100%;
    padding: 12px;
    font: inherit;
}

/* Botones y enlaces con apariencia de botón. */
button,
.boton {
    display: inline-block;
    padding: 10px 16px;
    border: 0;
    border-radius: 8px;
    background: #2f5bea;
    color: #fff;
    font: inherit;
    text-decoration: none;
    cursor: pointer;
}

.boton-peligro {
    background: #d92d20;
}

.boton-secundario {
    background: #5b6475;
}

/* Agrupa los botones de editar y eliminar. */
.acciones {
    display: flex;
    gap: 8px;
    align-items: center;
}

.acciones form,
.usuario-sesion form {
    margin: 0;
}

/* Mensajes de éxito y de error. */
.mensaje {
    padding: 12px;
    border-radius: 8px;
    background: #e8eefc;
}

.mensaje.success {
    background: #e6f6ec;
}

.mensaje.error {
    background: #fde8e8;
}
```

## 12. Crear la página de inicio de sesión

Abre `templates/registration/login.html` y copia:

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <!-- Metadatos de la página y conexión con el CSS externo. -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar sesión</title>
    <link rel="stylesheet" href="{% static 'css/videojuegos.css' %}">
</head>
<body>

    <div class="contenedor">

        <h1>Catálogo de videojuegos</h1>

        <div class="card">
            <h2>Iniciar sesión</h2>

            {% if messages %}
                {% for message in messages %}
                    <p class="mensaje {{ message.tags }}">{{ message }}</p>
                {% endfor %}
            {% endif %}

            <form method="POST">
                {% csrf_token %}

                {{ form.as_p }}

                <input type="hidden" name="next" value="{{ next }}">

                <button type="submit">Ingresar</button>
            </form>
        </div>

    </div>

</body>
</html>
```

### 12.1. Comprender el formulario de acceso

- `form` lo entrega `LoginView`; contiene los campos de usuario y contraseña.
- `{{ form.as_p }}` dibuja los campos y muestra automáticamente el error si las credenciales son incorrectas.
- `next` conserva la página que el usuario quería visitar antes de ser redirigido al inicio de sesión.
- `{% csrf_token %}` incorpora la protección CSRF de Django.

## 13. Crear el formulario de videojuegos

Abre `templates/videojuegos/formulario.html` y copia:

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <!-- Metadatos de la página y conexión con el CSS externo. -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Formulario de videojuegos</title>
    <link rel="stylesheet" href="{% static 'css/videojuegos.css' %}">
</head>
<body>

    <div class="contenedor">

        <h1>
            {% if editando %}
                Editar videojuego
            {% else %}
                Registrar videojuego
            {% endif %}
        </h1>

        {% if messages %}
            {% for message in messages %}
                <p class="mensaje {{ message.tags }}">{{ message }}</p>
            {% endfor %}
        {% endif %}

        <div class="card">
            <form method="POST">
                {% csrf_token %}

                <p>
                    <label for="nombre">Nombre del videojuego:</label><br>
                    <input
                        id="nombre"
                        type="text"
                        name="nombre"
                        maxlength="100"
                        value="{{ videojuego.nombre|default:'' }}"
                        required
                    >
                </p>

                <p>
                    <label for="costo">Costo:</label><br>
                    <input
                        id="costo"
                        type="number"
                        name="costo"
                        min="0"
                        step="0.01"
                        value="{{ videojuego.costo|default_if_none:'' }}"
                        required
                    >
                </p>

                <p>
                    <label for="descripcion">Descripción del juego:</label><br>
                    <textarea
                        id="descripcion"
                        name="descripcion"
                        rows="4"
                        maxlength="500"
                        required
                    >{{ videojuego.descripcion|default:'' }}</textarea>
                </p>

                <p>
                    <label for="jugadores">Cantidad de jugadores:</label><br>
                    <input
                        id="jugadores"
                        type="number"
                        name="jugadores"
                        min="1"
                        max="100"
                        step="1"
                        value="{{ videojuego.jugadores|default_if_none:'' }}"
                        required
                    >
                </p>

                <div class="acciones">
                    <button type="submit">Guardar videojuego</button>
                    <a class="boton boton-secundario" href="{% url 'videojuegos:listar' %}">
                        Cancelar
                    </a>
                </div>
            </form>
        </div>

    </div>

</body>
</html>
```

### 13.1. Comprender el formulario

- `method="POST"` envía los datos al servidor.
- `{% csrf_token %}` incorpora la protección CSRF de Django.
- `{% if editando %}` cambia el título según se esté creando o editando.
- `value="{{ videojuego.nombre|default:'' }}"` muestra el valor actual al editar y deja el campo vacío al crear.
- En `costo` y `jugadores` se usa `default_if_none:''` en lugar de `default:''`. Así un juego **gratuito** (costo `0`) se muestra como `0` y no como un campo vacío, ya que `default` trataría el cero como si no tuviera valor.
- El valor de `descripcion` se escribe **entre** las etiquetas `<textarea>` y no en un atributo `value`. Deja la etiqueta de cierre pegada al contenido para no agregar espacios en blanco.
- `required`, `min`, `max` y `step` ayudan al usuario, pero no reemplazan la validación en Python.

## 14. Crear el catálogo de videojuegos

Abre `templates/videojuegos/lista.html` y copia:

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <!-- Carga la presentación desde static/css/videojuegos.css. -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo de videojuegos</title>
    <link rel="stylesheet" href="{% static 'css/videojuegos.css' %}">
</head>
<body>

    <div class="contenedor">

        <header class="barra">
            <h1>Catálogo de videojuegos</h1>

            <div class="usuario-sesion">
                <span>Hola, <strong>{{ user.username }}</strong></span>

                <!-- Cerrar sesión se envía por POST. -->
                <form method="POST" action="{% url 'logout' %}">
                    {% csrf_token %}
                    <button type="submit" class="boton-secundario">
                        Cerrar sesión
                    </button>
                </form>
            </div>
        </header>

        {% if messages %}
            {% for message in messages %}
                <p class="mensaje {{ message.tags }}">{{ message }}</p>
            {% endfor %}
        {% endif %}

        <p>
            <a class="boton" href="{% url 'videojuegos:crear' %}">
                Agregar videojuego
            </a>
        </p>

        {% for videojuego in videojuegos %}

            <article class="card">

                <h2>{{ videojuego.nombre }}</h2>

                <p>
                    <strong>Costo:</strong>
                    ${{ videojuego.costo }}
                </p>

                <p>
                    <strong>Cantidad de jugadores:</strong>
                    {{ videojuego.jugadores }}
                </p>

                <p>
                    <strong>Descripción:</strong><br>
                    {{ videojuego.descripcion|linebreaksbr }}
                </p>

                <div class="acciones">
                    <a class="boton" href="{% url 'videojuegos:editar' videojuego.id %}">
                        Editar
                    </a>

                    <form
                        method="POST"
                        action="{% url 'videojuegos:eliminar' videojuego.id %}"
                    >
                        {% csrf_token %}

                        <button
                            type="submit"
                            class="boton-peligro"
                            onclick="return confirm('¿Deseas eliminar este videojuego?')"
                        >
                            Eliminar
                        </button>
                    </form>
                </div>

            </article>

        {% empty %}

            <p>No hay videojuegos registrados.</p>

        {% endfor %}

    </div>

</body>
</html>
```

**Importante:** PyMongo devuelve el identificador como `_id`, pero Django no permite acceder desde una plantilla a atributos que comiencen con guion bajo. Por eso, la vista agrega `id` al contexto del videojuego con `_id` convertido a texto. Utilizamos `videojuego.id` en los enlaces de edición y eliminación. Este valor sirve para presentar la página y no se guarda como campo adicional en MongoDB.

### 14.1. Comprender el cierre de sesión

- `{{ user.username }}` muestra el nombre de quien inició sesión. La variable `user` está disponible gracias al procesador de contexto `auth` configurado en `TEMPLATES`.
- El botón **Cerrar sesión** está dentro de un `<form method="POST">` que apunta a `{% url 'logout' %}`.
- Al enviarlo, `LogoutView` borra la sesión y redirige a la página de inicio de sesión.

## 15. Ejecutar las migraciones y crear la cuenta de usuario

Aunque los videojuegos se guardarán en MongoDB, Django guarda en su base SQLite las **cuentas de usuario** y las **sesiones**. Ejecuta:

```powershell
python manage.py migrate
```

Este comando crea las tablas internas de Django, entre ellas la de usuarios. **No crea la colección de videojuegos en MongoDB.** La colección aparecerá cuando se inserte el primer documento.

No necesitas ejecutar `makemigrations`, porque no hemos creado modelos Django propios.

Ahora crea tu cuenta de acceso:

```powershell
python manage.py createsuperuser
```

Django te pedirá un nombre de usuario, un correo electrónico (puede dejarse vacío) y una contraseña. Escríbelos y recuérdalos: los usarás para iniciar sesión en la aplicación.

Mientras escribes la contraseña, la terminal no mostrará ningún carácter. Es el comportamiento normal por seguridad.

## 16. Comprobar la configuración y ejecutar

Primero ejecuta:

```powershell
python manage.py check
```

Si no hay errores, inicia el servidor:

```powershell
python manage.py runserver
```

Abre el navegador en:

http://127.0.0.1:8000/

Como todavía no has iniciado sesión, Django te enviará automáticamente a la página de inicio de sesión (`/login/?next=/`).

## 17. Probar la aplicación

### Proteger el acceso

Con la sesión cerrada, intenta entrar directamente a http://127.0.0.1:8000/crear/. La aplicación debe llevarte a la página de inicio de sesión y no mostrar el formulario.

### Iniciar sesión

1. Escribe el usuario y la contraseña que creaste con `createsuperuser`.
2. Pulsa **Ingresar**.
3. Comprueba que aparezca el catálogo, vacío al comienzo, con tu nombre de usuario en la parte superior.

Prueba también con una contraseña incorrecta. La aplicación debe mostrar un error y no permitir el acceso.

### Crear

Pulsa **Agregar videojuego** y registra un juego con estos datos:

- Nombre: Overcooked 2.
- Costo: 70000.
- Descripción: Juego cooperativo de cocina caótica donde el equipo debe preparar y entregar pedidos a tiempo.
- Cantidad de jugadores: 4.

Guarda el formulario y comprueba que aparezca en el catálogo.

### Consultar

Registra dos o tres videojuegos más y verifica que todos se muestren con su costo, cantidad de jugadores y descripción, ordenados por nombre.

### Editar

Pulsa **Editar** en Overcooked 2, cambia el costo de 70000 a 55000 y guarda los cambios.

Comprueba que el catálogo muestre el nuevo costo.

### Eliminar

Pulsa **Eliminar** y confirma la acción si el navegador lo solicita.

Comprueba que el videojuego desaparezca de la lista.

### Validar

Intenta registrar un videojuego con alguno de estos errores. La aplicación debe rechazar los datos que no cumplan las reglas de validación:

- Un costo negativo.
- Una cantidad de jugadores igual a 0 o con decimales.
- Una descripción vacía.

Registra también un videojuego con costo `0` y comprueba que al editarlo el campo siga mostrando `0`.

### Cerrar sesión

Pulsa **Cerrar sesión**. Debes volver a la página de inicio de sesión. Luego intenta entrar a http://127.0.0.1:8000/: la aplicación debe pedirte las credenciales de nuevo.

### Verificar persistencia

Detén el servidor con `Ctrl + C`, vuelve a iniciarlo, ingresa con tu cuenta y comprueba que los videojuegos que no eliminaste sigan guardados.

## 18. Verificar los datos en MongoDB Atlas

Después de registrar un videojuego:

1. Ingresa a MongoDB Atlas.
2. Abre tu clúster.
3. Entra a **Browse Collections** o al explorador de datos.
4. Busca la base de datos `tienda_videojuegos`.
5. Abre la colección `videojuegos`.

Deberás encontrar documentos con una estructura similar a esta:

```json
{
  "_id": "ObjectId generado por MongoDB",
  "nombre": "Overcooked 2",
  "costo": 70000.0,
  "descripcion": "Juego cooperativo de cocina caótica donde el equipo debe preparar y entregar pedidos a tiempo.",
  "jugadores": 4
}
```

El valor de `_id` que aparece en Atlas será un identificador real de tipo `ObjectId`, no el texto ilustrativo del ejemplo.

En Atlas **no** encontrarás las cuentas de usuario: esas se guardan en el archivo `db.sqlite3` de tu proyecto.

## 19. Solución de problemas frecuentes

| Problema | Posible causa | Solución |
|---|---|---|
| `Falta configurar MONGO_URI` | El archivo `.env` no existe o está en otra carpeta. | Colócalo junto a `manage.py` y revisa que la variable tenga valor. |
| La lista muestra «Verifica la conexión con MongoDB» | La IP no está autorizada en Atlas o la cadena es incorrecta. | Revisa **Network Access** en Atlas y la contraseña de la cadena. |
| `TemplateDoesNotExist: registration/login.html` | La plantilla de acceso está en otra ruta. | Debe estar en `templates/registration/login.html` y `DIRS` debe apuntar a `templates`. |
| `no such table: django_session` o `auth_user` | No se ejecutaron las migraciones. | Ejecuta `python manage.py migrate`. |
| El enlace de cerrar sesión muestra «Method Not Allowed» (405) | Se está usando un enlace `<a>` en lugar de un formulario. | Usa el formulario con `method="POST"` de la sección 14. |
| Después de iniciar sesión vuelve a pedir credenciales | Faltan `SessionMiddleware` o `AuthenticationMiddleware`. | Revisa la lista `MIDDLEWARE` de la sección 6. |
| No carga el CSS | La carpeta `static` no existe o falta `STATICFILES_DIRS`. | Crea `static/css/videojuegos.css` y revisa `settings.py`. |
| No recuerdo la contraseña | — | Ejecuta `python manage.py changepassword nombre_de_usuario`. |

## 20. Buenas prácticas aplicadas

| Buena práctica | ¿Por qué importa? |
|---|---|
| Entorno virtual | Aísla las dependencias. |
| Archivo `.env` | Separa las credenciales del código. |
| `.gitignore` | Evita subir secretos y la base de usuarios al repositorio. |
| Autenticación de Django | Reutiliza un sistema probado en lugar de programar las contraseñas manualmente. |
| `@login_required` en todas las vistas | Impide consultar o modificar datos sin haber iniciado sesión. |
| Cierre de sesión por POST | Evita que otro sitio cierre la sesión del usuario sin su intención. |
| Validación en el servidor | Impide aceptar datos inválidos enviados directamente al servidor. |
| Función `validar_videojuego()` | Evita duplicar las reglas de validación. |
| Archivo `db.py` | Centraliza la conexión con MongoDB. |
| Identificación mediante `_id` | Permite seleccionar el documento correcto. |
| Protección CSRF | Protege los formularios POST de Django. |
| Manejo de errores | Permite responder a fallos comunes de conexión. |
| Consultas con filtros | Limita las actualizaciones y eliminaciones al documento correspondiente. |

Esta aplicación es adecuada como práctica académica. Ten presente que **todos los usuarios con cuenta ven y administran el mismo catálogo**. Para producción todavía habría que reforzar los permisos por rol, el registro de usuarios, las pruebas y la configuración de despliegue (`DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS` y HTTPS).

## 21. Reto para los aprendices

Una vez que el CRUD y el inicio de sesión funcionen, realiza estos cambios:

1. Agrega un campo `plataforma` (por ejemplo: PC, PlayStation, Xbox o Nintendo Switch).
2. Muestra la plataforma en el catálogo.
3. Permite modificarla desde el formulario.
4. Comprueba que también se guarde en MongoDB.

**Condición:** el nuevo campo debe funcionar al crear, consultar y editar videojuegos. No basta con agregarlo al HTML; también debe incorporarse en la validación del servidor.

**Reto adicional:** crea una página de registro (`/registro/`) con `UserCreationForm` para que cualquier persona pueda crear su cuenta sin usar `createsuperuser`. Al registrarse, el usuario debe quedar con la sesión iniciada.

## 22. ¿Qué aprendimos?

En la práctica anterior trabajamos el CRUD con MongoDB a través de PyMongo. En esta práctica agregamos una capa de seguridad: el sistema de autenticación de Django decide quién puede entrar a la aplicación, mientras que PyMongo sigue encargándose de los documentos almacenados en MongoDB.

Las operaciones esenciales sobre los datos son:

```python
# Crear
coleccion_videojuegos.insert_one(videojuego)

# Consultar
coleccion_videojuegos.find()

# Editar
coleccion_videojuegos.update_one(
    {"_id": identificador},
    {"$set": videojuego}
)

# Eliminar
coleccion_videojuegos.delete_one(
    {"_id": identificador}
)
```

Y la protección de las vistas se logra con una sola línea:

```python
@login_required
def listar(request):
    ...
```

La idea principal es que **Django gestiona la aplicación web y las cuentas de usuario, y PyMongo permite trabajar con documentos almacenados en MongoDB**. Cada herramienta resuelve una parte distinta del problema, y por eso pueden combinarse sin que una interfiera con la otra.
