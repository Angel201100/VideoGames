"""Vistas autenticadas del CRUD, con validación y persistencia en MongoDB."""

import logging
import math

from bson import ObjectId
from bson.errors import InvalidId
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from pymongo.errors import PyMongoError

from .db import get_collection

logger = logging.getLogger(__name__)


def validar_videojuego(datos):
    """Normaliza y valida los cuatro campos enviados por el formulario."""
    # Se eliminan espacios alrededor de los textos antes de validar o guardar.
    nombre = datos.get("nombre", "").strip()
    costo_texto = datos.get("costo", "").strip()
    descripcion = datos.get("descripcion", "").strip()
    jugadores_texto = datos.get("jugadores", "").strip()
    errores = []

    # Nombre requerido y acotado para mantener tarjetas y documentos legibles.
    if not nombre:
        errores.append("El nombre es obligatorio.")
    elif len(nombre) > 100:
        errores.append("El nombre no puede superar 100 caracteres.")

    # Se rechazan infinitos, NaN y valores negativos además de cadenas inválidas.
    try:
        costo = float(costo_texto)
        if not math.isfinite(costo) or costo < 0:
            errores.append("El costo debe ser un número válido y no negativo.")
    except ValueError:
        costo = None
        errores.append("Ingresa un costo válido.")

    # La descripción es texto plano con límite para evitar documentos excesivos.
    if not descripcion:
        errores.append("La descripción es obligatoria.")
    elif len(descripcion) > 500:
        errores.append("La descripción no puede superar 500 caracteres.")

    # La cantidad de jugadores debe ser un entero dentro del rango de la interfaz.
    try:
        jugadores = int(jugadores_texto)
        if not 1 <= jugadores <= 100:
            errores.append("La cantidad de jugadores debe estar entre 1 y 100.")
    except ValueError:
        jugadores = None
        errores.append("La cantidad de jugadores debe ser un número entero.")

    # Se devuelven los valores convertidos y los errores; el llamador decide si guarda.
    return {
        "nombre": nombre,
        "costo": costo,
        "descripcion": descripcion,
        "jugadores": jugadores,
    }, errores


def _avisar_error_base_datos(request, error, mensaje):
    """Muestra un error de configuración o registra un fallo de MongoDB."""
    if isinstance(error, ImproperlyConfigured):
        messages.error(request, str(error))
    else:
        logger.exception("Error al comunicarse con MongoDB")
        messages.error(request, mensaje)


# LECTURA: lista los documentos por nombre. Todas las rutas del CRUD requieren sesión.
@login_required
def listar(request):
    try:
        videojuegos = list(get_collection().find().sort("nombre", 1))
    except (ImproperlyConfigured, PyMongoError) as error:
        _avisar_error_base_datos(
            request,
            error,
            "No fue posible consultar los videojuegos. Verifica la conexión con MongoDB.",
        )
        videojuegos = []

    # Django no permite acceder a claves que comienzan con "_"; se agrega un alias
    # de texto para usar el ObjectId de MongoDB de forma segura en las plantillas.
    for videojuego in videojuegos:
        videojuego["id"] = str(videojuego["_id"])

    return render(request, "videojuegos/lista.html", {"videojuegos": videojuegos})


# CREACIÓN: valida los datos antes de insertarlos y conserva los valores si hay errores.
@login_required
def crear(request):
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

        # La escritura solo se ejecuta después de pasar todas las reglas de validación.
        try:
            get_collection().insert_one(videojuego)
        except (ImproperlyConfigured, PyMongoError) as error:
            _avisar_error_base_datos(
                request, error, "No fue posible guardar el videojuego."
            )
            return render(
                request,
                "videojuegos/formulario.html",
                {"videojuego": videojuego, "editando": False},
            )

        messages.success(request, "Videojuego registrado correctamente.")
        return redirect("videojuegos:listar")

    return render(request, "videojuegos/formulario.html", {"editando": False})


# ACTUALIZACIÓN: convierte el identificador, carga el documento y modifica sus campos.
@login_required
def editar(request, id):
    # Un ObjectId mal formado se rechaza antes de consultar la base de datos.
    try:
        identificador = ObjectId(id)
    except (InvalidId, TypeError):
        messages.error(request, "El identificador no es válido.")
        return redirect("videojuegos:listar")

    try:
        coleccion = get_collection()
        videojuego_actual = coleccion.find_one({"_id": identificador})
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

            # $set cambia los campos validados y el filtro limita la edición a un juego.
            resultado = coleccion.update_one(
                {"_id": identificador},
                {"$set": videojuego},
            )
            if resultado.matched_count == 0:
                messages.error(request, "El videojuego ya no existe.")
            else:
                messages.success(request, "Videojuego actualizado correctamente.")
            return redirect("videojuegos:listar")

        return render(
            request,
            "videojuegos/formulario.html",
            {"videojuego": videojuego_actual, "editando": True},
        )
    except (ImproperlyConfigured, PyMongoError) as error:
        _avisar_error_base_datos(
            request,
            error,
            "No fue posible consultar o actualizar el videojuego.",
        )
        return redirect("videojuegos:listar")


# ELIMINACIÓN: se exige POST para evitar borrar datos al abrir un enlace o página.
@login_required
def eliminar(request, id):
    if request.method != "POST":
        messages.error(request, "La eliminación requiere enviar el formulario.")
        return redirect("videojuegos:listar")

    # Solo se elimina el documento cuyo ObjectId coincide con el de la URL.
    try:
        identificador = ObjectId(id)
    except (InvalidId, TypeError):
        messages.error(request, "El identificador no es válido.")
        return redirect("videojuegos:listar")

    try:
        resultado = get_collection().delete_one({"_id": identificador})
    except (ImproperlyConfigured, PyMongoError) as error:
        _avisar_error_base_datos(
            request, error, "No fue posible eliminar el videojuego."
        )
        return redirect("videojuegos:listar")

    if resultado.deleted_count == 1:
        messages.success(request, "Videojuego eliminado correctamente.")
    else:
        messages.error(request, "El videojuego no existe o ya fue eliminado.")
    return redirect("videojuegos:listar")
