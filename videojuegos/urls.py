"""Rutas del catálogo y sus operaciones de creación, edición y eliminación."""

from django.urls import path

from . import views

# El espacio de nombres permite referir estas URL sin colisiones con otras apps.
app_name = "videojuegos"

# Cada ruta envía la solicitud a una vista con autenticación obligatoria.
urlpatterns = [
    path("", views.listar, name="listar"),
    path("crear/", views.crear, name="crear"),
    path("editar/<str:id>/", views.editar, name="editar"),
    path("eliminar/<str:id>/", views.eliminar, name="eliminar"),
]
