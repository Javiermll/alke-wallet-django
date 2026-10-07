#!/usr/bin/env bash
# Script de construcción para Render: se ejecuta en cada despliegue, antes de iniciar la aplicación.
# set -o errexit detiene todo si cualquier comando falla, para no publicar una versión a medias.
set -o errexit

# 1. Instala las librerías del proyecto
pip install -r requirements.txt

# 2. Reúne los archivos estáticos (CSS, JS, imágenes) en staticfiles/ para que WhiteNoise los sirva
python manage.py collectstatic --no-input

# 3. Crea o actualiza las tablas de la base de datos (Neon)
python manage.py migrate --no-input

# 4. Crea el superusuario si no existe (usa las variables DJANGO_SUPERUSER_* del panel de Render)
python manage.py crear_superusuario

# 5. Carga los datos de demostración; se puede repetir sin duplicar y no cambia las claves de usuarios que ya existen
python manage.py poblar_datos
