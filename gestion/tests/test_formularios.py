# gestion/tests/test_formularios.py
# Pruebas unitarias de los formularios: comprueban que las reglas de validación funcionan y que los formularios se guardan correctamente

import secrets# secrets crea textos aleatorios; así no hay contraseñas escritas a mano en el código
from django.test import TestCase# TestCase crea una base de datos temporal y deshace los cambios de cada prueba
from django.contrib.auth.models import User# User para comprobar que el registro crea el usuario
from gestion.forms import (# Formularios que se prueban
    ClienteForm, ClienteEdicionForm, CuentaForm, CuentaEdicionForm,
    TransaccionForm, FiltroTransaccionForm, ContactoForm, RegistroForm,
)
from gestion.models import Contacto
from .utilidades import crear_moneda, crear_cliente, crear_cuenta, crear_personal# Funciones de ayuda para armar datos

# Contraseña aleatoria válida para las pruebas de registro (se genera en cada ejecución)
CLAVE = secrets.token_urlsafe(12)
# Contraseña demasiado simple (solo números repetidos), que Django debe rechazar
CLAVE_DEBIL = '0' * 10


# ============================================================
# CLIENTES
# ============================================================

class ClienteFormTest(TestCase):
    # Datos que se preparan una sola vez para todas las pruebas de la clase
    @classmethod
    def setUpTestData(cls):
        # Un usuario libre (sin cliente) y otro que ya tiene cliente
        cls.libre = User.objects.create_user(username='libre')
        cls.ocupado = crear_cliente(nombre='Ana García', usuario='ana').usuario

    # Datos válidos de un cliente nuevo
    def datos(self, **cambios):
        datos = {'usuario': self.libre.pk, 'nombre': 'Luis Pérez', 'email': 'luis@prueba.test', 'telefono': ''}
        datos.update(cambios)
        return datos

    def test_solo_ofrece_usuarios_sin_cliente(self):
        # El usuario que ya tiene cliente no debe aparecer en la lista
        form = ClienteForm()
        self.assertEqual(list(form.fields['usuario'].queryset), [self.libre])

    def test_datos_validos(self):
        self.assertTrue(ClienteForm(self.datos()).is_valid())

    def test_rechaza_usuario_que_ya_tiene_cliente(self):
        # Elegir un usuario ocupado no es una opción válida
        form = ClienteForm(self.datos(usuario=self.ocupado.pk))
        self.assertFalse(form.is_valid())
        self.assertIn('usuario', form.errors)

    def test_rechaza_correo_repetido(self):
        form = ClienteForm(self.datos(email='ana@prueba.test'))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_nombre_es_obligatorio(self):
        form = ClienteForm(self.datos(nombre=''))
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_telefono_es_opcional(self):
        self.assertTrue(ClienteForm(self.datos(telefono='')).is_valid())


class ClienteEdicionFormTest(TestCase):
    def test_solo_permite_editar_nombre_correo_y_telefono(self):
        # El usuario de acceso no se puede cambiar desde este formulario
        self.assertEqual(list(ClienteEdicionForm().fields), ['nombre', 'email', 'telefono'])

    def test_telefono_vacio_se_guarda_como_none(self):
        cliente = crear_cliente(telefono='123')
        form = ClienteEdicionForm({'nombre': 'Ana', 'email': 'ana@prueba.test', 'telefono': ''}, instance=cliente)
        self.assertTrue(form.is_valid())
        form.save()
        cliente.refresh_from_db()
        # Un teléfono vacío queda como NULL, no como texto vacío
        self.assertIsNone(cliente.telefono)


# ============================================================
# CUENTAS
# ============================================================

class CuentaFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cliente = crear_cliente()
        cls.moneda = crear_moneda()
        cls.cuenta = crear_cuenta(cls.cliente, numero='0001', moneda=cls.moneda)

    def test_numero_repetido_muestra_mensaje_propio(self):
        form = CuentaForm({'cliente': self.cliente.pk, 'moneda': self.moneda.pk, 'numero': '0001', 'activa': True})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['numero'], ['Ya existe una cuenta con ese número.'])

    def test_datos_validos(self):
        form = CuentaForm({'cliente': self.cliente.pk, 'moneda': self.moneda.pk, 'numero': '0002', 'activa': True})
        self.assertTrue(form.is_valid())

    def test_edicion_solo_permite_numero_y_activa(self):
        self.assertEqual(list(CuentaEdicionForm().fields), ['numero', 'activa'])

    def test_edicion_con_numero_ajeno_muestra_mensaje_propio(self):
        otra = crear_cuenta(self.cliente, numero='0002', moneda=self.moneda)
        form = CuentaEdicionForm({'numero': '0001', 'activa': True}, instance=otra)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['numero'], ['Ya existe una cuenta con ese número.'])


# ============================================================
# TRANSACCIONES
# ============================================================

class TransaccionFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.personal = crear_personal()
        cls.carla = crear_cliente(nombre='Carla Soto', usuario='carla')
        cls.activa = crear_cuenta(cls.carla, numero='0004')
        cls.inactiva = crear_cuenta(cls.carla, numero='0005', activa=False)

    def test_personal_solo_ve_cuentas_activas(self):
        form = TransaccionForm(usuario=self.personal)
        self.assertEqual(list(form.fields['cuenta_origen'].queryset), [self.activa])
        self.assertEqual(list(form.fields['cuenta_destino'].queryset), [self.activa])

    def test_etiqueta_de_cuenta(self):
        form = TransaccionForm(usuario=self.personal)
        self.assertEqual(form.fields['cuenta_destino'].label_from_instance(self.activa), '0004 · Carla Soto (CLP)')

    def test_textos_de_las_opciones_vacias(self):
        form = TransaccionForm(usuario=self.personal)
        self.assertEqual(form.fields['cuenta_origen'].empty_label, 'Ninguna')
        self.assertEqual(form.fields['cuenta_destino'].empty_label, 'Ninguna')
        self.assertEqual(form.fields['tipo'].choices[0], ('', 'Selecciona un tipo'))

    def test_tipos_disponibles(self):
        form = TransaccionForm(usuario=self.personal)
        valores = [valor for valor, _ in form.fields['tipo'].choices]
        self.assertEqual(valores, ['', 'deposito', 'retiro', 'transferencia'])

    def test_exige_el_argumento_usuario(self):
        # Sin saber quién opera no se pueden limitar las cuentas
        with self.assertRaises(TypeError):
            TransaccionForm()

    def test_deposito_valido_del_personal(self):
        form = TransaccionForm(
            {'tipo': 'deposito', 'cuenta_destino': self.activa.pk, 'monto': '50.00', 'descripcion': ''},
            usuario=self.personal,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_cuenta_inactiva_no_es_opcion_valida(self):
        form = TransaccionForm(
            {'tipo': 'deposito', 'cuenta_destino': self.inactiva.pk, 'monto': '50.00'},
            usuario=self.personal,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('cuenta_destino', form.errors)

    def test_monto_cero_es_invalido(self):
        form = TransaccionForm(
            {'tipo': 'deposito', 'cuenta_destino': self.activa.pk, 'monto': '0'},
            usuario=self.personal,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('monto', form.errors)

    def test_tipo_es_obligatorio(self):
        form = TransaccionForm({'tipo': '', 'monto': '10'}, usuario=self.personal)
        self.assertFalse(form.is_valid())
        self.assertIn('tipo', form.errors)


# ============================================================
# FILTROS
# ============================================================

class FiltroTransaccionFormTest(TestCase):
    def test_vacio_es_valido(self):
        # Sin filtros se muestran todos los movimientos
        self.assertTrue(FiltroTransaccionForm({}).is_valid())

    def test_filtros_validos(self):
        form = FiltroTransaccionForm({'tipo': 'retiro', 'cuenta': '0004', 'desde': '2026-01-01', 'hasta': '2026-12-31'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['tipo'], 'retiro')

    def test_fecha_mal_escrita_es_invalida(self):
        form = FiltroTransaccionForm({'desde': '31/13/2026'})
        self.assertFalse(form.is_valid())
        self.assertIn('desde', form.errors)

    def test_tipo_desconocido_es_invalido(self):
        form = FiltroTransaccionForm({'tipo': 'regalo'})
        self.assertFalse(form.is_valid())
        self.assertIn('tipo', form.errors)


# ============================================================
# CONTACTOS
# ============================================================

class ContactoFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ana = crear_cliente(nombre='Ana', usuario='ana')
        cls.luis = crear_cliente(nombre='Luis', usuario='luis')
        cls.carla = crear_cliente(nombre='Carla', usuario='carla')
        # Ana ya tiene a Luis agendado
        Contacto.objects.create(propietario=cls.ana, agendado=cls.luis)

    def test_no_ofrece_al_propietario_ni_a_los_ya_agendados(self):
        form = ContactoForm(propietario=self.ana)
        # Solo queda Carla: Ana es la dueña y Luis ya está agendado
        self.assertEqual(list(form.fields['agendado'].queryset), [self.carla])

    def test_deja_al_propietario_en_la_ficha(self):
        form = ContactoForm(propietario=self.ana)
        self.assertEqual(form.instance.propietario, self.ana)

    def test_guarda_el_contacto(self):
        form = ContactoForm({'agendado': self.carla.pk, 'apodo': 'Cari'}, propietario=self.ana)
        self.assertTrue(form.is_valid(), form.errors)
        ficha = form.save()
        self.assertEqual((ficha.propietario, ficha.agendado, ficha.apodo), (self.ana, self.carla, 'Cari'))

    def test_rechaza_agendarse_a_si_mismo(self):
        form = ContactoForm({'agendado': self.ana.pk}, propietario=self.ana)
        self.assertFalse(form.is_valid())

    def test_rechaza_un_contacto_ya_agendado(self):
        form = ContactoForm({'agendado': self.luis.pk}, propietario=self.ana)
        self.assertFalse(form.is_valid())

    def test_apodo_es_opcional(self):
        form = ContactoForm({'agendado': self.carla.pk}, propietario=self.ana)
        self.assertTrue(form.is_valid())


# ============================================================
# REGISTRO
# ============================================================

class RegistroFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moneda = crear_moneda()

    # Datos válidos de un registro
    def datos(self, **cambios):
        datos = {
            'username': 'nuevo', 'nombre': 'Nuevo Cliente', 'email': 'Nuevo@Prueba.test', 'telefono': '',
            'moneda': self.moneda.pk, 'password1': CLAVE, 'password2': CLAVE,
        }
        datos.update(cambios)
        return datos

    def test_orden_de_los_campos(self):
        self.assertEqual(
            list(RegistroForm().fields),
            ['username', 'nombre', 'email', 'telefono', 'moneda', 'password1', 'password2'],
        )

    def test_crea_usuario_cliente_y_cuenta(self):
        form = RegistroForm(self.datos())
        self.assertTrue(form.is_valid(), form.errors)
        usuario = form.save()
        # El usuario es normal, no del personal
        self.assertFalse(usuario.is_staff)
        # Tiene cliente con una cuenta en la moneda elegida
        cliente = usuario.cliente
        self.assertEqual(cliente.nombre, 'Nuevo Cliente')
        self.assertEqual(cliente.cuentas.count(), 1)
        self.assertEqual(cliente.cuentas.get().moneda, self.moneda)

    def test_correo_se_guarda_en_minusculas(self):
        form = RegistroForm(self.datos())
        form.is_valid()
        self.assertEqual(form.cleaned_data['email'], 'nuevo@prueba.test')

    def test_correo_repetido_sin_importar_mayusculas(self):
        crear_cliente(usuario='ana', email='ana@prueba.test')
        form = RegistroForm(self.datos(email='ANA@prueba.test'))
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Ya existe un cliente con ese correo.'])

    def test_contrasenas_distintas(self):
        form = RegistroForm(self.datos(password2=secrets.token_urlsafe(12)))
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_contrasena_debil(self):
        form = RegistroForm(self.datos(password1=CLAVE_DEBIL, password2=CLAVE_DEBIL))
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_moneda_es_obligatoria(self):
        form = RegistroForm(self.datos(moneda=''))
        self.assertFalse(form.is_valid())
        self.assertIn('moneda', form.errors)

    def test_telefono_es_opcional(self):
        self.assertTrue(RegistroForm(self.datos(telefono='')).is_valid())

    def test_usuario_repetido(self):
        User.objects.create_user(username='nuevo')
        form = RegistroForm(self.datos())
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_si_falla_no_queda_nada_a_medias(self):
        # Se crea un cliente con ese correo justo antes de guardar, para forzar el error en save()
        form = RegistroForm(self.datos())
        self.assertTrue(form.is_valid())
        crear_cliente(usuario='otro', email='nuevo@prueba.test')
        with self.assertRaises(Exception):
            form.save()
        # atomic deshizo el usuario: no queda un usuario suelto sin cliente
        self.assertFalse(User.objects.filter(username='nuevo').exists())