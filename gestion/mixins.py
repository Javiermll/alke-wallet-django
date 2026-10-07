#gestion/mixins.py
# Mezclas (mixins) para las vistas de la app gestion

# UserPassesTestMixin ejecuta un test antes de mostrar la pantalla; si falla, responde 403
from django.contrib.auth.mixins import UserPassesTestMixin


# Pantallas reservadas al personal (usuarios con is_staff)
class SoloPersonalMixin(UserPassesTestMixin):
    # Django ejecuta este método primero; si devuelve False, la persona recibe un 403
    def test_func(self):
        return self.request.user.is_staff  # Solo pasa quien pertenece al personal


# Pantallas para el personal y para los clientes (usuarios que tienen un Cliente asociado)
class PersonalOClienteMixin(UserPassesTestMixin):
    # Django ejecuta este método primero; si devuelve False, la persona recibe un 403
    def test_func(self):
        usuario = self.request.user # Usuario que hace la petición
        return usuario.is_staff or hasattr(usuario, 'cliente')# hasattr devuelve False si el usuario no tiene un Cliente asociado (relación 1:1 inversa)