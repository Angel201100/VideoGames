"""Asocia las rutas globales con el acceso y la aplicación de videojuegos."""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

# El login y logout usan vistas integradas de Django; las rutas del CRUD se delegan
# a videojuegos.urls para mantener separada la configuración de cada aplicación.
urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'login/',
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('videojuegos.urls')),
]
