"""Metadatos de la aplicación Django responsable del catálogo de videojuegos."""

from django.apps import AppConfig


class VideojuegosConfig(AppConfig):
    """Define el nombre de la app y el tipo de identificador por defecto."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videojuegos'
