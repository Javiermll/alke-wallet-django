#gestion/tests/test_humo.py
# Pruebas de humo: comprueban que el entorno de pruebas funciona antes de escribir las pruebas reales


# TestCase crea una base de datos vacía y temporal para las pruebas, y la borra al terminar
from django.test import TestCase
from gestion.models import Cliente, Cuenta, Moneda# Modelos que se consultan en las pruebas


# Pruebas de humo: comprueban que el entorno de pruebas funciona antes de escribir las pruebas reales
class PruebaDeHumoTests(TestCase):
    # Cada método cuyo nombre empieza con test_ es una prueba
    def test_la_base_de_pruebas_empieza_vacia(self):
        # La base de pruebas es nueva: no contiene los datos de demostración de la base real
        self.assertEqual(Cliente.objects.count(), 0)
        self.assertEqual(Cuenta.objects.count(), 0)

    def test_lo_que_se_crea_en_una_prueba_no_pasa_a_la_siguiente(self):
        Moneda.objects.create(codigo='CLP', nombre='Peso chileno', simbolo='$')# Crea una moneda dentro de esta prueba
        self.assertEqual(Moneda.objects.count(), 1)# Dentro de esta prueba existe exactamente una

    def test_la_moneda_de_la_prueba_anterior_no_existe(self):
        # TestCase deshace los datos al terminar cada prueba, así que aquí no hay monedas
        self.assertEqual(Moneda.objects.count(), 0)

    def test_el_login_es_publico(self):
        respuesta = self.client.get('/acceso/login/')# self.client simula un navegador; get pide una página
        self.assertEqual(respuesta.status_code, 200)# 200 significa que la página se mostró sin pedir sesión

    def test_una_pantalla_privada_redirige_al_login(self):
        respuesta = self.client.get('/')# Sin sesión, el inicio debe llevar al login
        # assertRedirects comprueba el destino; fetch_redirect_response=False evita pedir la página destino
        self.assertRedirects(respuesta, '/acceso/login/?next=/', fetch_redirect_response=False)