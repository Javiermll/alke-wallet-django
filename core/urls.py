# core/urls.py

from django.contrib import admin  # Importa el panel de administración de Django
from django.contrib.auth import views as auth_views # Importa las vistas de login y logout que trae django.contrib.auth
from django.urls import path, include  # path crea una ruta; include conecta las rutas de otra app
from django.contrib.auth.decorators import login_not_required# Marca una vista como pública: el middleware de login obligatorio no la bloquea
from gestion.views import RegistroView# Vista de registro de la app


# Lista de rutas del proyecto; Django las revisa de arriba hacia abajo
urlpatterns = [
    path('admin/', admin.site.urls),# Todo lo que empiece con admin/ lo atiende el panel de administración
    path('acceso/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),# Iniciar sesión; usa el template registration/login.html. redirect_authenticated_user=True envía al inicio a quien ya tiene sesión
    path('acceso/logout/', auth_views.LogoutView.as_view(), name='logout'),# Cerrar sesión; solo acepta POST (por seguridad), así que se usa desde un formulario
    path('registro/', login_not_required(RegistroView.as_view()), name='registro'),# Registro público de clientes (login_not_required lo deja pasar sin sesión)
    path('', include('gestion.urls')),# Cualquier otra dirección se entrega a las rutas de la app gestion
]