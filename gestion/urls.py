# gestion/urls.py

from django.urls import path  # path crea una ruta
from . import views   # Importa las vistas de esta misma app

# app_name agrupa los nombres de las rutas; se usan como 'gestion:inicio'
app_name = 'gestion'

# Lista de rutas de la app
urlpatterns = [
    # La ruta vacía es la raíz del sitio (http://127.0.0.1:8000/)
    # as_view() convierte la clase en una vista que Django puede ejecutar
    path('', views.InicioView.as_view(), name='inicio'),
]