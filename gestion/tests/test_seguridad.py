# gestion/tests/test_seguridad.py
# Pruebas de seguridad: comprueban que los usuarios solo pueden ver y tocar lo que les corresponde. 


import secrets# secrets crea textos aleatorios; así no hay contraseñas escritas a mano en el código
from decimal import Decimal# Decimal para los montos
from django.contrib.auth.models import User# User para crear usuarios; Client simula un navegador (aquí con la revisión CSRF activada)
from django.test import Client, TestCase
from django.urls import reverse
from gestion.models import Cliente, Contacto, Cuenta, Transaccion
from .utilidades import crear_cliente, crear_cuenta, crear_moneda, crear_personal, depositar


# Base común: personal, dos clientes (Ana y Luis) con una cuenta cada uno, un usuario sin cliente y un movimiento de cada uno
class SeguridadBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moneda = crear_moneda()
        cls.personal = crear_personal()
        cls.ana = crear_cliente(nombre='Ana García', usuario='ana')
        cls.luis = crear_cliente(nombre='Luis Pérez', usuario='luis')
        cls.cuenta_ana = crear_cuenta(cls.ana, numero='0001')
        cls.cuenta_luis = crear_cuenta(cls.luis, numero='0002')
        # Usuario que existe pero no tiene ficha de cliente
        cls.sin_cliente = User.objects.create_user(username='sin_cliente')
        # Un movimiento en cada cuenta
        cls.mov_ana = depositar(cls.cuenta_ana, 100)
        cls.mov_luis = depositar(cls.cuenta_luis, 100)

    # Inicia sesión con un usuario sin pasar por la pantalla de acceso
    def entrar(self, usuario):
        self.client.force_login(usuario)


# ============================================================
# 1. SIN SESIÓN: todo es privado salvo acceso y registro
# ============================================================

class SinSesionTest(SeguridadBase):
    # Direcciones privadas: (nombre de la ruta, argumentos)
    def privadas(self):
        return [
            ('gestion:inicio', []),
            ('gestion:cliente_lista', []), ('gestion:cliente_nuevo', []),
            ('gestion:cliente_detalle', [self.ana.pk]), ('gestion:cliente_editar', [self.ana.pk]),
            ('gestion:cliente_eliminar', [self.ana.pk]),
            ('gestion:cuenta_lista', []), ('gestion:cuenta_nueva', []),
            ('gestion:cuenta_detalle', [self.cuenta_ana.pk]), ('gestion:cuenta_editar', [self.cuenta_ana.pk]),
            ('gestion:cuenta_eliminar', [self.cuenta_ana.pk]),
            ('gestion:transaccion_lista', []), ('gestion:transaccion_nueva', []),
            ('gestion:transaccion_detalle', [self.mov_ana.pk]),
            ('gestion:contacto_nuevo', [self.ana.pk]),
            ('gestion:reporte', []), ('gestion:perfil', []), ('gestion:cambiar_clave', []),
        ]

    def test_pantallas_privadas_redirigen_al_acceso(self):
        for nombre, args in self.privadas():
            # subTest muestra cuál dirección falló sin detener las demás
            with self.subTest(ruta=nombre):
                url = reverse(nombre, args=args)
                r = self.client.get(url)
                # Redirige al login recordando a dónde quería ir
                self.assertRedirects(r, f"{reverse('login')}?next={url}", fetch_redirect_response=False)

    def test_post_sin_sesion_no_hace_nada(self):
        # Un POST anónimo también redirige y no crea ni borra datos
        self.client.post(reverse('gestion:cliente_eliminar', args=[self.ana.pk]))
        self.client.post(reverse('gestion:transaccion_nueva'), {
            'tipo': 'deposito', 'cuenta_destino': self.cuenta_ana.pk, 'monto': '10',
        })
        self.assertTrue(Cliente.objects.filter(pk=self.ana.pk).exists())
        self.assertEqual(Transaccion.objects.count(), 2)

    def test_login_y_registro_son_publicos(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
        self.assertEqual(self.client.get(reverse('registro')).status_code, 200)

    def test_el_panel_admin_exige_sesion(self):
        r = self.client.get('/admin/')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/admin/login/', r.url)


# ============================================================
# 2. ROLES: qué puede abrir cada tipo de usuario
# ============================================================

class RolesTest(SeguridadBase):
    # Pantallas solo del personal (los clientes reciben 403)
    def solo_personal(self):
        return [
            ('gestion:cliente_lista', []), ('gestion:cliente_nuevo', []), ('gestion:cliente_eliminar', [self.ana.pk]),
            ('gestion:cuenta_nueva', []), ('gestion:cuenta_editar', [self.cuenta_ana.pk]),
            ('gestion:cuenta_eliminar', [self.cuenta_ana.pk]), ('gestion:reporte', []),
        ]

    def test_cliente_recibe_403_en_pantallas_del_personal(self):
        self.entrar(self.ana.usuario)
        for nombre, args in self.solo_personal():
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(reverse(nombre, args=args)).status_code, 403)

    def test_cliente_no_puede_ejecutar_acciones_del_personal(self):
        self.entrar(self.ana.usuario)
        # Intenta borrar una cuenta y un cliente con POST: recibe 403 y no se borra nada
        self.client.post(reverse('gestion:cuenta_eliminar', args=[self.cuenta_ana.pk]))
        self.client.post(reverse('gestion:cliente_eliminar', args=[self.ana.pk]))
        self.assertTrue(Cuenta.objects.filter(pk=self.cuenta_ana.pk).exists())
        self.assertTrue(Cliente.objects.filter(pk=self.ana.pk).exists())

    def test_cliente_no_puede_crear_clientes_ni_cuentas(self):
        self.entrar(self.ana.usuario)
        self.client.post(reverse('gestion:cuenta_nueva'), {
            'cliente': self.ana.pk, 'moneda': self.moneda.pk, 'numero': '0099', 'activa': 'on',
        })
        self.assertFalse(Cuenta.objects.filter(numero='0099').exists())

    def test_cliente_abre_sus_pantallas(self):
        self.entrar(self.ana.usuario)
        abiertas = [
            ('gestion:inicio', []), ('gestion:cuenta_lista', []), ('gestion:transaccion_lista', []),
            ('gestion:transaccion_nueva', []), ('gestion:perfil', []), ('gestion:cambiar_clave', []),
            ('gestion:cliente_detalle', [self.ana.pk]), ('gestion:cliente_editar', [self.ana.pk]),
            ('gestion:cuenta_detalle', [self.cuenta_ana.pk]), ('gestion:transaccion_detalle', [self.mov_ana.pk]),
            ('gestion:contacto_nuevo', [self.ana.pk]),
        ]
        for nombre, args in abiertas:
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(reverse(nombre, args=args)).status_code, 200)

    def test_usuario_sin_cliente_recibe_403_en_todo_lo_de_negocio(self):
        self.entrar(self.sin_cliente)
        cerradas = self.solo_personal() + [
            ('gestion:cuenta_lista', []), ('gestion:transaccion_lista', []), ('gestion:transaccion_nueva', []),
            ('gestion:cliente_detalle', [self.ana.pk]), ('gestion:cuenta_detalle', [self.cuenta_ana.pk]),
            ('gestion:transaccion_detalle', [self.mov_ana.pk]), ('gestion:contacto_nuevo', [self.ana.pk]),
        ]
        for nombre, args in cerradas:
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(reverse(nombre, args=args)).status_code, 403)

    def test_usuario_sin_cliente_puede_ver_inicio_y_perfil_sin_datos(self):
        self.entrar(self.sin_cliente)
        r = self.client.get(reverse('gestion:inicio'))
        self.assertEqual(r.status_code, 200)
        # No recibe ningún dato del sistema
        for clave in ('total_clientes', 'mis_cuentas', 'ultimos_movimientos'):
            self.assertNotIn(clave, r.context)
        self.assertEqual(self.client.get(reverse('gestion:perfil')).status_code, 200)

    def test_personal_abre_todo(self):
        self.entrar(self.personal)
        for nombre, args in self.solo_personal() + [
            ('gestion:inicio', []), ('gestion:cuenta_lista', []), ('gestion:transaccion_lista', []),
            ('gestion:cliente_detalle', [self.luis.pk]), ('gestion:transaccion_detalle', [self.mov_luis.pk]),
        ]:
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(reverse(nombre, args=args)).status_code, 200)

    def test_pagina_403_propia(self):
        self.entrar(self.ana.usuario)
        r = self.client.get(reverse('gestion:reporte'))
        # Se usa la plantilla 403.html del proyecto, no la página en blanco de Django
        self.assertTemplateUsed(r, '403.html')


# ============================================================
# 3. ALCANCE: un cliente solo ve y toca lo suyo
# ============================================================

class AlcanceTest(SeguridadBase):
    def setUp(self):
        # Ana es quien navega; Luis es "el otro"
        self.entrar(self.ana.usuario)

    def test_registros_ajenos_dan_404(self):
        # 404 y no 403: así no se revela si el registro existe
        ajenos = [
            ('gestion:cliente_detalle', [self.luis.pk]), ('gestion:cliente_editar', [self.luis.pk]),
            ('gestion:cuenta_detalle', [self.cuenta_luis.pk]), ('gestion:transaccion_detalle', [self.mov_luis.pk]),
            ('gestion:contacto_nuevo', [self.luis.pk]),
        ]
        for nombre, args in ajenos:
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(reverse(nombre, args=args)).status_code, 404)

    def test_no_puede_editar_la_ficha_de_otro(self):
        r = self.client.post(reverse('gestion:cliente_editar', args=[self.luis.pk]), {
            'nombre': 'Hackeado', 'email': 'h@prueba.test', 'telefono': '',
        })
        self.assertEqual(r.status_code, 404)
        self.luis.refresh_from_db()
        self.assertEqual(self.luis.nombre, 'Luis Pérez')

    def test_no_puede_agendar_contactos_en_la_agenda_de_otro(self):
        self.client.post(reverse('gestion:contacto_nuevo', args=[self.luis.pk]), {'agendado': self.ana.pk})
        self.assertFalse(Contacto.objects.filter(propietario=self.luis).exists())

    def test_no_puede_quitar_contactos_de_otro(self):
        carla = crear_cliente(nombre='Carla', usuario='carla')
        ficha = Contacto.objects.create(propietario=self.luis, agendado=carla)
        r = self.client.post(reverse('gestion:contacto_eliminar', args=[ficha.pk]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Contacto.objects.filter(pk=ficha.pk).exists())

    def test_puede_quitar_contactos_propios(self):
        ficha = Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        r = self.client.post(reverse('gestion:contacto_eliminar', args=[ficha.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Contacto.objects.filter(pk=ficha.pk).exists())

    def test_listado_de_cuentas_solo_trae_las_propias(self):
        r = self.client.get(reverse('gestion:cuenta_lista'))
        self.assertEqual([c.numero for c in r.context['cuentas']], ['0001'])

    def test_listado_de_movimientos_solo_trae_los_propios(self):
        r = self.client.get(reverse('gestion:transaccion_lista'))
        self.assertEqual([t.pk for t in r.context['transacciones']], [self.mov_ana.pk])

    def test_un_filtro_no_permite_ver_movimientos_ajenos(self):
        # Filtrar por la cuenta de Luis no devuelve nada de Luis
        r = self.client.get(reverse('gestion:transaccion_lista') + '?cuenta=0002')
        self.assertEqual(list(r.context['transacciones']), [])

    def test_transferencia_recibida_si_es_visible(self):
        # Si Luis le transfiere a Ana, ese movimiento es de Ana también
        Transaccion.objects.create(
            tipo='transferencia', cuenta_origen=self.cuenta_luis, cuenta_destino=self.cuenta_ana, monto=Decimal('5'),
        )
        r = self.client.get(reverse('gestion:transaccion_lista'))
        self.assertEqual(len(r.context['transacciones']), 2)

    def test_inicio_solo_muestra_datos_propios(self):
        r = self.client.get(reverse('gestion:inicio'))
        self.assertEqual([c.numero for c in r.context['mis_cuentas']], ['0001'])
        self.assertEqual(r.context['total_transacciones'], 1)
        self.assertNotIn('total_clientes', r.context)

    def test_personal_si_ve_los_registros_de_todos(self):
        self.entrar(self.personal)
        self.assertEqual(len(self.client.get(reverse('gestion:cuenta_lista')).context['cuentas']), 2)
        self.assertEqual(len(self.client.get(reverse('gestion:transaccion_lista')).context['transacciones']), 2)


# ============================================================
# 4. REGLAS DE OPERACIÓN PARA CLIENTES
# ============================================================

class OperacionesDeClienteTest(SeguridadBase):
    def setUp(self):
        self.entrar(self.ana.usuario)

    def post(self, datos):
        return self.client.post(reverse('gestion:transaccion_nueva'), datos)

    def test_formulario_solo_ofrece_cuentas_permitidas(self):
        # Sin contactos: origen y destino son solo las cuentas de Ana
        form = self.client.get(reverse('gestion:transaccion_nueva')).context['form']
        self.assertEqual([c.numero for c in form.fields['cuenta_origen'].queryset], ['0001'])
        self.assertEqual([c.numero for c in form.fields['cuenta_destino'].queryset], ['0001'])

    def test_contacto_agendado_aparece_como_destino_pero_no_como_origen(self):
        Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        form = self.client.get(reverse('gestion:transaccion_nueva')).context['form']
        self.assertEqual([c.numero for c in form.fields['cuenta_destino'].queryset], ['0001', '0002'])
        self.assertEqual([c.numero for c in form.fields['cuenta_origen'].queryset], ['0001'])

    def test_no_puede_retirar_de_una_cuenta_ajena(self):
        r = self.post({'tipo': 'retiro', 'cuenta_origen': self.cuenta_luis.pk, 'monto': '10'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('cuenta_origen', r.context['form'].errors)
        self.assertEqual(Transaccion.objects.count(), 2)

    def test_no_puede_transferir_desde_una_cuenta_ajena(self):
        Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        r = self.post({
            'tipo': 'transferencia', 'cuenta_origen': self.cuenta_luis.pk,
            'cuenta_destino': self.cuenta_ana.pk, 'monto': '10',
        })
        self.assertIn('cuenta_origen', r.context['form'].errors)
        self.assertEqual(Transaccion.objects.count(), 2)

    def test_no_puede_transferir_a_quien_no_tiene_agendado(self):
        r = self.post({
            'tipo': 'transferencia', 'cuenta_origen': self.cuenta_ana.pk,
            'cuenta_destino': self.cuenta_luis.pk, 'monto': '10',
        })
        self.assertIn('cuenta_destino', r.context['form'].errors)
        self.assertEqual(Transaccion.objects.count(), 2)

    def test_puede_transferir_a_un_contacto_agendado(self):
        Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        r = self.post({
            'tipo': 'transferencia', 'cuenta_origen': self.cuenta_ana.pk,
            'cuenta_destino': self.cuenta_luis.pk, 'monto': '10',
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.cuenta_ana.saldo, Decimal('90'))
        self.assertEqual(self.cuenta_luis.saldo, Decimal('110'))

    def test_no_puede_depositar_en_la_cuenta_de_un_contacto(self):
        # Aunque la cuenta del contacto aparece en la lista, un depósito solo puede ir a una cuenta propia
        Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        r = self.post({'tipo': 'deposito', 'cuenta_destino': self.cuenta_luis.pk, 'monto': '10'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form'].errors['cuenta_destino'], ['Un depósito solo puede ir a una de tus cuentas.'])
        self.assertEqual(Transaccion.objects.count(), 2)

    def test_puede_depositar_en_su_propia_cuenta(self):
        r = self.post({'tipo': 'deposito', 'cuenta_destino': self.cuenta_ana.pk, 'monto': '10'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.cuenta_ana.saldo, Decimal('110'))

    def test_el_personal_si_puede_depositar_en_cualquier_cuenta(self):
        self.entrar(self.personal)
        r = self.post({'tipo': 'deposito', 'cuenta_destino': self.cuenta_luis.pk, 'monto': '10'})
        self.assertEqual(r.status_code, 302)

    def test_usuario_sin_cliente_no_puede_operar(self):
        self.entrar(self.sin_cliente)
        r = self.post({'tipo': 'deposito', 'cuenta_destino': self.cuenta_ana.pk, 'monto': '10'})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(Transaccion.objects.count(), 2)


# ============================================================
# 5. CSRF: los formularios exigen el token
# ============================================================

class CsrfTest(SeguridadBase):
    def setUp(self):
        # Este navegador de prueba SÍ revisa el token CSRF (el Client normal lo salta)
        self.navegador = Client(enforce_csrf_checks=True)

    # Envía un token válido: se pide una pantalla con formulario (deja la cookie) y se reutiliza el valor
    def token(self, url):
        self.navegador.get(url)
        return self.navegador.cookies['csrftoken'].value

    def test_post_sin_token_da_403_en_los_formularios_del_personal(self):
        self.navegador.force_login(self.personal)
        envios = [
            (reverse('gestion:cliente_nuevo'), {'nombre': 'X'}),
            (reverse('gestion:cliente_editar', args=[self.ana.pk]), {'nombre': 'X'}),
            (reverse('gestion:cliente_eliminar', args=[self.ana.pk]), {}),
            (reverse('gestion:cuenta_nueva'), {'numero': '0099'}),
            (reverse('gestion:cuenta_eliminar', args=[self.cuenta_ana.pk]), {}),
            (reverse('gestion:transaccion_nueva'), {'tipo': 'deposito'}),
            (reverse('gestion:contacto_nuevo', args=[self.ana.pk]), {'agendado': self.luis.pk}),
            (reverse('gestion:cambiar_clave'), {}),
        ]
        for url, datos in envios:
            with self.subTest(url=url):
                self.assertEqual(self.navegador.post(url, datos).status_code, 403)

    def test_post_sin_token_no_cambia_datos(self):
        self.navegador.force_login(self.personal)
        self.navegador.post(reverse('gestion:cliente_eliminar', args=[self.ana.pk]))
        self.assertTrue(Cliente.objects.filter(pk=self.ana.pk).exists())

    def test_registro_y_login_tambien_exigen_token(self):
        self.assertEqual(self.navegador.post(reverse('registro'), {'username': 'x'}).status_code, 403)
        self.assertEqual(self.navegador.post(reverse('login'), {'username': 'x', 'password': 'y'}).status_code, 403)

    def test_logout_sin_token_da_403(self):
        self.navegador.force_login(self.ana.usuario)
        self.assertEqual(self.navegador.post(reverse('logout')).status_code, 403)

    def test_post_con_token_valido_funciona(self):
        self.navegador.force_login(self.personal)
        url = reverse('gestion:transaccion_nueva')
        r = self.navegador.post(url, {
            'tipo': 'deposito', 'cuenta_destino': self.cuenta_ana.pk, 'monto': '10',
            'csrfmiddlewaretoken': self.token(url),
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Transaccion.objects.count(), 3)

    def test_token_falso_da_403(self):
        self.navegador.force_login(self.personal)
        url = reverse('gestion:transaccion_nueva')
        self.token(url)
        r = self.navegador.post(url, {
            'tipo': 'deposito', 'cuenta_destino': self.cuenta_ana.pk, 'monto': '10',
            'csrfmiddlewaretoken': 'a' * 64,
        })
        self.assertEqual(r.status_code, 403)

    def test_los_formularios_html_incluyen_el_token(self):
        self.client.force_login(self.personal)
        for nombre, args in [('gestion:cliente_nuevo', []), ('gestion:transaccion_nueva', []),
                             ('gestion:cuenta_eliminar', [self.cuenta_ana.pk])]:
            with self.subTest(ruta=nombre):
                self.assertContains(self.client.get(reverse(nombre, args=args)), 'csrfmiddlewaretoken')


# ============================================================
# 6. ACCESO Y SESIÓN
# ============================================================

class AccesoTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Aquí sí se necesita una contraseña real, porque se prueba el login de verdad
        cls.clave = secrets.token_urlsafe(12)
        cls.usuario = User.objects.create_user(username='ana', password=cls.clave)
        crear_cliente(usuario='ana_cli')

    def test_login_correcto_va_al_inicio(self):
        r = self.client.post(reverse('login'), {'username': 'ana', 'password': self.clave})
        self.assertRedirects(r, reverse('gestion:inicio'))

    def test_clave_incorrecta_no_inicia_sesion(self):
        r = self.client.post(reverse('login'), {'username': 'ana', 'password': secrets.token_urlsafe(12)})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_usuario_desactivado_no_puede_entrar(self):
        self.usuario.is_active = False
        self.usuario.save()
        r = self.client.post(reverse('login'), {'username': 'ana', 'password': self.clave})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_vuelve_a_la_pagina_pedida(self):
        url = reverse('gestion:perfil')
        r = self.client.post(f"{reverse('login')}?next={url}", {'username': 'ana', 'password': self.clave})
        self.assertRedirects(r, url)

    def test_login_no_redirige_a_sitios_externos(self):
        # Protección contra "open redirect": un next hacia otro sitio se ignora
        r = self.client.post(
            f"{reverse('login')}?next=https://sitio-malo.test/", {'username': 'ana', 'password': self.clave},
        )
        self.assertRedirects(r, reverse('gestion:inicio'))

    def test_logout_solo_acepta_post(self):
        self.client.force_login(self.usuario)
        # Un GET (por ejemplo un enlace puesto por un tercero) no cierra la sesión
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)

    def test_logout_con_post_cierra_la_sesion(self):
        self.client.force_login(self.usuario)
        r = self.client.post(reverse('logout'))
        self.assertEqual(r.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)
        # Y ya no puede abrir pantallas privadas
        self.assertEqual(self.client.get(reverse('gestion:perfil')).status_code, 302)

    def test_registro_no_permite_crear_personal(self):
        moneda = crear_moneda()
        clave = secrets.token_urlsafe(12)
        # Se intenta colarse como personal enviando campos extra
        self.client.post(reverse('registro'), {
            'username': 'intruso', 'nombre': 'Intruso', 'email': 'i@prueba.test', 'telefono': '',
            'moneda': moneda.pk, 'password1': clave, 'password2': clave,
            'is_staff': 'on', 'is_superuser': 'on',
        })
        intruso = User.objects.get(username='intruso')
        self.assertFalse(intruso.is_staff)
        self.assertFalse(intruso.is_superuser)

    def test_las_claves_se_guardan_cifradas(self):
        self.assertNotEqual(self.usuario.password, self.clave)
        self.assertTrue(self.usuario.password.startswith(('pbkdf2_', 'argon2', 'bcrypt', 'scrypt')))

    def test_pantallas_no_se_pueden_incrustar_en_otro_sitio(self):
        # Protección contra clickjacking: la respuesta pide no mostrarse dentro de un iframe ajeno
        r = self.client.get(reverse('login'))
        self.assertEqual(r.headers['X-Frame-Options'], 'DENY')