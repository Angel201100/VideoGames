"""Expone la aplicación Django en el estándar ASGI para servidores compatibles."""

import os

from django.core.asgi import get_asgi_application

# Selecciona la configuración del proyecto y construye el punto de entrada ASGI.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
