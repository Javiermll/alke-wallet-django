# core/urls.py

from django.contrib import admin  # Importa el panel de administración de Django
from django.contrib.auth import views as auth_views # Importa las vistas de login y logout que trae django.contrib.auth
from django.urls import path, include  # path crea una ruta; include conecta las rutas de otra app
from django.contrib.auth.decorators import login_not_required# Marca una vista como pública: el middleware de login obligatorio no la bloquea
from gestion.views import RegistroView, salud# Vista de registro de la app


# Lista de rutas del proyecto; Django las revisa de arriba hacia abajo
urlpatterns = [
    path('admin/', admin.site.urls),# Todo lo que empiece con admin/ lo atiende el panel de administración
    path('acceso/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),# Iniciar sesión; usa el template registration/login.html. redirect_authenticated_user=True envía al inicio a quien ya tiene sesión
    path('acceso/logout/', auth_views.LogoutView.as_view(), name='logout'),# Cerrar sesión; solo acepta POST (por seguridad), así que se usa desde un formulario
    path('salud/', login_not_required(salud), name='salud'),# Comprobación de que el servicio está activo (pública, sin datos)
    path('registro/', login_not_required(RegistroView.as_view()), name='registro'),# Registro público de clientes (login_not_required lo deja pasar sin sesión)
    path('', include('gestion.urls')),# Cualquier otra dirección se entrega a las rutas de la app gestion
]

# Vistas previas de las páginas de error en desarrollo: con DEBUG = True Django muestra su página técnica en lugar de
# 404.html y 500.html, así que estas rutas (solo existen cuando DEBUG es True) permiten ver los diseños
from django.conf import settings
from django.views.generic import TemplateView

if settings.DEBUG:
    for numero in (403, 404, 500):
        urlpatterns.insert(0, path(f'vista-{numero}/', login_not_required(TemplateView.as_view(template_name=f'{numero}.html')), name=f'vista_{numero}'))
