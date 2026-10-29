#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Prepara Django y entrega los argumentos a su herramienta de administración."""
    # Indica qué módulo contiene los ajustes que deben cargar los comandos.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        # La importación se pospone para mostrar un error claro si Django no está instalado.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # Solo ejecuta el comando al invocar este archivo directamente desde la terminal.
    main()
