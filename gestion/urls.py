# gestion/urls.py
# Rutas de la app gestion: clientes, cuentas y transacciones

from django.urls import path # path crea una ruta
from . import views # Importa las vistas de esta misma app

app_name = 'gestion'# app_name agrupa los nombres de las rutas; se usan como 'gestion:inicio'

# Lista de rutas de la app
urlpatterns = [
    # La ruta vacía es la raíz del sitio (http://127.0.0.1:8000/)
    # as_view() convierte la clase en una vista que Django puede ejecutar
    path('', views.InicioView.as_view(), name='inicio'),

    # ---------- Clientes ----------
  
    path('clientes/', views.ClienteListView.as_view(), name='cliente_lista'),  # Listado de clientes
    path('clientes/nuevo/', views.ClienteCreateView.as_view(), name='cliente_nuevo'),  # Formulario para crear un cliente
    path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detalle'), # <int:pk> es una parte variable de la dirección: el número (pk) del cliente
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_editar'),  # Formulario para editar el cliente con ese pk
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_eliminar'), # Confirmación para eliminar el cliente con ese pk

        # ---------- Cuentas ----------
    
    path('cuentas/', views.CuentaListView.as_view(), name='cuenta_lista'),# Listado de cuentas
    path('cuentas/nueva/', views.CuentaCreateView.as_view(), name='cuenta_nueva'), # Formulario para crear una cuenta
    path('cuentas/<int:pk>/', views.CuentaDetailView.as_view(), name='cuenta_detalle'),# Ficha de la cuenta con ese pk
    path('cuentas/<int:pk>/editar/', views.CuentaUpdateView.as_view(), name='cuenta_editar'), # Formulario para editar la cuenta con ese pk
    path('cuentas/<int:pk>/eliminar/', views.CuentaDeleteView.as_view(), name='cuenta_eliminar'), # Confirmación para eliminar la cuenta con ese pk
]