# gestion/management/commands/crear_superusuario.py
# Crea el superusuario desde variables de entorno, sin pedir nada por consola.
# Render gratuito no ofrece terminal, así que build.sh ejecuta este comando en cada despliegue.

import os  # os lee las variables de entorno

from django.contrib.auth import get_user_model  # Devuelve el modelo de usuario del proyecto
from django.core.management.base import BaseCommand  # Clase base de los comandos de manage.py


class Command(BaseCommand):
    help = 'Crea el superusuario con DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL y DJANGO_SUPERUSER_PASSWORD (si no existe)'

    def handle(self, *args, **options):
        nombre = os.environ.get('DJANGO_SUPERUSER_USERNAME')  # Usuario
        correo = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')  # Correo (opcional)
        clave = os.environ.get('DJANGO_SUPERUSER_PASSWORD')  # Contraseña; nunca se escribe en pantalla

        # Sin usuario o sin clave no se hace nada: así el comando no falla en local, donde esas variables no existen
        if not nombre or not clave:
            self.stdout.write('Variables DJANGO_SUPERUSER_* sin definir: no se crea ningún superusuario.')
            return

        Usuario = get_user_model()
        # Si ya existe no se toca: así repetir el despliegue no cambia la clave que se haya puesto después
        if Usuario.objects.filter(username=nombre).exists():
            self.stdout.write(f'El superusuario "{nombre}" ya existe: no se modifica.')
            return

        Usuario.objects.create_superuser(username=nombre, email=correo, password=clave)
        self.stdout.write(f'Superusuario "{nombre}" creado.')
