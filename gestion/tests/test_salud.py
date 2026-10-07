# gestion/tests/test_salud.py
# Prueba de la vista de salud: debe responder sin sesión, porque la consulta Render y no una persona

from django.test import TestCase


class SaludTests(TestCase):
    def test_responde_ok_sin_sesion(self):
        respuesta = self.client.get('/salud/')# Sin iniciar sesión
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {'estado': 'ok'})
