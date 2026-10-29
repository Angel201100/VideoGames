"""Crea y reutiliza el acceso a la colección de videojuegos en MongoDB."""

from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pymongo import MongoClient


@lru_cache(maxsize=4)
def _cliente(uri):
    """Reutiliza un cliente por URI y limita el tiempo de espera al conectar."""
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def get_collection():
    """Devuelve la colección del catálogo o informa que falta configurar la URI."""
    if not settings.MONGO_URI:
        raise ImproperlyConfigured(
            "Falta configurar MONGO_URI en el archivo .env. "
            "Copia .env.example a .env y agrega la cadena de MongoDB Atlas."
        )
    # MongoDB crea la base y la colección al insertar el primer documento.
    return _cliente(settings.MONGO_URI)[settings.MONGO_DB]["videojuegos"]
