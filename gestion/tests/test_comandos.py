# gestion/tests/test_comandos.py
# Pruebas del comando crear_superusuario, que se ejecuta en cada despliegue en Render

from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

VARIABLES = {
    'DJANGO_SUPERUSER_USERNAME': 'jefa',
    'DJANGO_SUPERUSER_EMAIL': 'jefa@example.com',
    'DJANGO_SUPERUSER_PASSWORD': 'una-clave-larga-123',
}


class CrearSuperusuarioTests(TestCase):
    def ejecutar(self, variables):
        salida = StringIO()
        # patch.dict reemplaza el entorno solo durante la prueba; clear=True quita las variables reales
        with mock.patch.dict('os.environ', variables, clear=True):
            call_command('crear_superusuario', stdout=salida)
        return salida.getvalue()

    def test_crea_el_superusuario(self):
        self.ejecutar(VARIABLES)
        usuario = get_user_model().objects.get(username='jefa')
        self.assertTrue(usuario.is_superuser and usuario.is_staff)
        self.assertTrue(usuario.check_password('una-clave-larga-123'))

    def test_no_hace_nada_sin_variables(self):
        self.ejecutar({})
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_repetirlo_no_cambia_la_clave(self):
        self.ejecutar(VARIABLES)
        self.ejecutar({**VARIABLES, 'DJANGO_SUPERUSER_PASSWORD': 'otra-clave-distinta-9'})
        self.assertTrue(get_user_model().objects.get(username='jefa').check_password('una-clave-larga-123'))

    def test_no_muestra_la_clave_en_pantalla(self):
        self.assertNotIn('una-clave-larga-123', self.ejecutar(VARIABLES))
