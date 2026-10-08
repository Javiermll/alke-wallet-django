# gestion/tests/test_salud.py
# Pruebas de la vista de salud: debe responder sin sesión y permitir que la lea la página puente

from django.test import TestCase


class SaludTests(TestCase):
    def test_responde_ok_sin_sesion(self):
        respuesta = self.client.get('/salud/')# Sin iniciar sesión
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {'estado': 'ok'})

    def test_permite_que_la_lea_otra_pagina(self):
        respuesta = self.client.get('/salud/')
        self.assertEqual(respuesta['Access-Control-Allow-Origin'], '*')# Sin este encabezado, GitHub Pages no podría leerla
