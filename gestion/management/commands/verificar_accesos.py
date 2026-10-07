import logging# logging permite silenciar los avisos que Django escribe en consola cuando responde 403 o 404
from django.core.management.base import BaseCommand, CommandError# BaseCommand es la base de los comandos de manage.py; CommandError corta el comando con un mensaje de error
from django.contrib.auth.models import User# User es el modelo de usuarios de Django
from django.db import transaction# transaction.atomic permite crear datos de prueba y deshacerlos al final
from django.test import Client# Client simula un navegador que hace peticiones sin abrir el servidor
from gestion.models import Cliente, Contacto, Cuenta, Moneda, Transaccion# Modelos de la app



# Excepción propia: se lanza al final para que atomic deshaga todos los datos de prueba
class DeshacerPruebas(Exception):
    pass

class Command(BaseCommand):
    # Texto que aparece en: python manage.py help verificar_accesos
    help = 'Prueba quién puede entrar a cada pantalla y que los formularios exijan el token CSRF. No deja datos.'

    # Se ejecuta con: python manage.py verificar_accesos
    def handle(self, *args, **options):
        
        self.resultados = []# Lista donde se guardan los resultados: (nombre, esperado, obtenido)
        logging.disable(logging.CRITICAL)# Silencia los avisos de Django mientras se hacen las pruebas
        try:
            # atomic: todo lo que se cree dentro se deshace al salir con la excepción
            with transaction.atomic():
                self.ejecutar_pruebas()
                raise DeshacerPruebas()
        except DeshacerPruebas:
            
            pass# Es la salida normal: la base de datos queda como estaba
        finally:
            logging.disable(logging.NOTSET) # Vuelve a activar los avisos

        # Muestra el resultado de cada prueba
        fallos = 0
        for nombre, esperado, obtenido in self.resultados:
            # Una prueba pasa si el código obtenido es el esperado
            if obtenido == esperado:
                self.stdout.write(f'  OK     {nombre:<52} {obtenido}')
            else:
                fallos += 1
                self.stdout.write(self.style.ERROR(f'  FALLA  {nombre:<52} esperado {esperado}, obtenido {obtenido}'))
        # Resumen final
        total = len(self.resultados)
        if fallos:
            raise CommandError(f'{fallos} de {total} pruebas fallaron.')
        self.stdout.write(self.style.SUCCESS(f'\n{total} de {total} pruebas correctas. Los datos de prueba se deshicieron.'))

    # Anota el resultado de una prueba
    def anotar(self, nombre, esperado, respuesta):
        self.resultados.append((nombre, esperado, respuesta.status_code))

    # Crea los datos de prueba y recorre todas las comprobaciones
    def ejecutar_pruebas(self):
        # ---------- datos de prueba (se deshacen al final) ----------
        # Moneda: usa una existente o crea una de prueba
        moneda = Moneda.objects.first() or Moneda.objects.create(codigo='TST', nombre='Prueba', simbolo='T')
        # Usuario del personal, usuario cliente A, usuario cliente B y usuario sin cliente
        personal = User.objects.create_user('_prueba_personal', password='x', is_staff=True)
        usuario_a = User.objects.create_user('_prueba_a', password='x')
        usuario_b = User.objects.create_user('_prueba_b', password='x')
        sin_cliente = User.objects.create_user('_prueba_sin', password='x')
        # Dos clientes con una cuenta cada uno
        cliente_a = Cliente.objects.create(usuario=usuario_a, nombre='Prueba A', email='_a@prueba.test')
        cliente_b = Cliente.objects.create(usuario=usuario_b, nombre='Prueba B', email='_b@prueba.test')
        cuenta_a = Cuenta.objects.create(cliente=cliente_a, moneda=moneda, numero='_PA')
        cuenta_b = Cuenta.objects.create(cliente=cliente_b, moneda=moneda, numero='_PB')
        # Un movimiento que solo pertenece a B, y una ficha de agenda de B
        mov_b = Transaccion.objects.create(tipo='deposito', cuenta_destino=cuenta_b, monto=10)
        ficha_b = Contacto.objects.create(propietario=cliente_b, agendado=cliente_a)

        # Crea un navegador simulado; force_login inicia la sesión sin pasar por el formulario
        def navegador(usuario=None, csrf=False):
            # enforce_csrf_checks=True hace que el token CSRF se exija como en el navegador real
            nav = Client(enforce_csrf_checks=csrf, raise_request_exception=False, SERVER_NAME='localhost')
            if usuario:
                nav.force_login(usuario)
            return nav

        # ---------- 1. sin sesión ----------
        anonimo = navegador()
        for ruta in ('/', '/clientes/', '/cuentas/', '/transacciones/', '/reporte/', '/perfil/'):
            self.anotar(f'sin sesión: {ruta} lleva al login', 302, anonimo.get(ruta))
        # Además de ser 302, el destino debe ser el login con ?next=
        destino = anonimo.get('/clientes/')['Location']
        self.resultados.append(('sin sesión: el destino incluye ?next=', 302, 302 if destino == '/acceso/login/?next=/clientes/' else 0))
        self.anotar('sin sesión: /acceso/login/ es pública', 200, anonimo.get('/acceso/login/'))
        self.anotar('sin sesión: /registro/ es pública', 200, anonimo.get('/registro/'))

        # ---------- 2. personal ----------
        nav = navegador(personal)
        for ruta in ('/', '/clientes/', '/cuentas/', '/transacciones/', '/reporte/', '/perfil/', '/clientes/nuevo/', '/cuentas/nueva/',
                     f'/clientes/{cliente_b.pk}/', f'/cuentas/{cuenta_b.pk}/', f'/transacciones/{mov_b.pk}/'):
            self.anotar(f'personal: {ruta}', 200, nav.get(ruta))

        # ---------- 3. cliente A ----------
        nav = navegador(usuario_a)
        # Pantallas permitidas
        for ruta in ('/', '/cuentas/', '/transacciones/', '/perfil/', '/transacciones/nueva/',
                     f'/clientes/{cliente_a.pk}/', f'/clientes/{cliente_a.pk}/editar/', f'/cuentas/{cuenta_a.pk}/'):
            self.anotar(f'cliente: {ruta} (propio)', 200, nav.get(ruta))
        # Pantallas reservadas al personal: 403
        for ruta in ('/clientes/', '/clientes/nuevo/', '/cuentas/nueva/', '/reporte/',
                     f'/cuentas/{cuenta_a.pk}/editar/', f'/cuentas/{cuenta_a.pk}/eliminar/', f'/clientes/{cliente_a.pk}/eliminar/'):
            self.anotar(f'cliente: {ruta} (solo personal)', 403, nav.get(ruta))
        # Registros ajenos: 404
        for ruta in (f'/clientes/{cliente_b.pk}/', f'/clientes/{cliente_b.pk}/editar/', f'/cuentas/{cuenta_b.pk}/',
                     f'/transacciones/{mov_b.pk}/', f'/clientes/{cliente_b.pk}/contactos/nuevo/', f'/contactos/{ficha_b.pk}/eliminar/'):
            self.anotar(f'cliente: {ruta} (ajeno)', 404, nav.get(ruta))

        # ---------- 4. usuario sin cliente ----------
        nav = navegador(sin_cliente)
        self.anotar('sin cliente: /perfil/', 200, nav.get('/perfil/'))
        self.anotar('sin cliente: / (inicio con aviso)', 200, nav.get('/'))
        for ruta in ('/cuentas/', '/transacciones/', '/clientes/', '/transacciones/nueva/'):
            self.anotar(f'sin cliente: {ruta}', 403, nav.get(ruta))

        # ---------- 5. CSRF ----------
        # Con enforce_csrf_checks=True, un POST sin token debe responder 403
        self.anotar('CSRF: login sin token', 403, navegador(csrf=True).post('/acceso/login/', {'username': 'x', 'password': 'x'}))
        self.anotar('CSRF: registro sin token', 403, navegador(csrf=True).post('/registro/', {}))
        nav = navegador(usuario_a, csrf=True)
        self.anotar('CSRF: cerrar sesión sin token', 403, nav.post('/acceso/logout/'))
        self.anotar('CSRF: cambiar contraseña sin token', 403, nav.post('/perfil/clave/', {}))
        self.anotar('CSRF: nueva transacción sin token', 403, nav.post('/transacciones/nueva/', {'tipo': 'deposito'}))
        self.anotar('CSRF: editar mis datos sin token', 403, nav.post(f'/clientes/{cliente_a.pk}/editar/', {}))
        # Cerrar sesión con GET no está permitido (solo POST)
        self.anotar('logout con GET no permitido', 405, navegador(usuario_a).get('/acceso/logout/'))
        # Con token, el mismo envío sí se procesa: se pide la página para recibir la cookie y se reenvía el token
        anon_csrf = navegador(csrf=True)
        anon_csrf.get('/acceso/login/')
        token = anon_csrf.cookies['csrftoken'].value
        # Clave incorrecta: el formulario vuelve con el error (200), no con 403
        self.anotar('CSRF: login con token (clave mala) se procesa', 200,
                    anon_csrf.post('/acceso/login/', {'username': '_prueba_a', 'password': 'mala', 'csrfmiddlewaretoken': token}))