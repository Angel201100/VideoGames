"""Comando Django para insertar un catálogo de muestra en MongoDB."""

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from pymongo.errors import PyMongoError

from videojuegos.db import get_collection


# Datos de ejemplo. $setOnInsert preserva el precio y descripción si ya existen.
JUEGOS_DE_MUESTRA = [
    {
        "nombre": "Hades II",
        "costo": 129000,
        "descripcion": "Aventura de acción mitológica con combates rápidos y un mundo que cambia en cada intento.",
        "jugadores": 1,
    },
    {
        "nombre": "Stardew Valley",
        "costo": 42000,
        "descripcion": "Construye una granja, explora el valle y comparte una tranquila aventura cooperativa.",
        "jugadores": 4,
    },
    {
        "nombre": "Hollow Knight",
        "costo": 45000,
        "descripcion": "Explora un vasto reino subterráneo dibujado a mano y enfréntate a criaturas misteriosas.",
        "jugadores": 1,
    },
    {
        "nombre": "Celeste",
        "costo": 32000,
        "descripcion": "Acompaña a Madeline en un desafiante viaje de plataformas hasta la cima de una montaña.",
        "jugadores": 1,
    },
    {
        "nombre": "Portal 2",
        "costo": 21000,
        "descripcion": "Resuelve acertijos espaciales con portales y coopera para superar cámaras de pruebas.",
        "jugadores": 2,
    },
]


class Command(BaseCommand):
    """Carga juegos populares de forma repetible, sin reemplazar documentos previos."""

    help = "Agrega cinco videojuegos de muestra sin duplicar registros existentes."

    def handle(self, *args, **options):
        # Obtener la colección comprueba que la configuración permita construir el cliente.
        try:
            coleccion = get_collection()
        except (ImproperlyConfigured, PyMongoError) as error:
            raise CommandError(
                f"No fue posible conectar con MongoDB para cargar el catálogo: {error}"
            ) from error

        # El filtro por nombre y upsert inserta solo los que todavía no están.
        agregados = 0

        for juego in JUEGOS_DE_MUESTRA:
            try:
                resultado = coleccion.update_one(
                    {"nombre": juego["nombre"]},
                    {"$setOnInsert": juego},
                    upsert=True,
                )
            except PyMongoError as error:
                raise CommandError(
                    f"No fue posible guardar {juego['nombre']} en MongoDB: {error}"
                ) from error
            # MongoDB informa el identificador cuando esta operación hizo una inserción.
            if resultado.upserted_id is not None:
                agregados += 1

        # El resumen permite verificar cuántos juegos se añadieron en esta ejecución.
        self.stdout.write(
            self.style.SUCCESS(
                f"Catálogo de muestra listo: {agregados} agregados, "
                f"{len(JUEGOS_DE_MUESTRA) - agregados} ya existían."
            )
        )
