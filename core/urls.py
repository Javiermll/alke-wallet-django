# core/urls.py

from django.contrib import admin  # Importa el panel de administración de Django
from django.urls import path, include  # path crea una ruta; include conecta las rutas de otra app

# Lista de rutas del proyecto; Django las revisa de arriba hacia abajo
urlpatterns = [
    path('admin/', admin.site.urls),  # Todo lo que empiece con admin/ lo atiende el panel de administración
    path('', include('gestion.urls')),  # Cualquier otra dirección se entrega a las rutas de la app gestion
]