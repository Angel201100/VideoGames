"""Expone la aplicación Django en el estándar WSGI para servidores compatibles."""

import os

from django.core.wsgi import get_wsgi_application

# Selecciona la configuración del proyecto y construye el punto de entrada WSGI.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
