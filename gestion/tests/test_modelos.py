# gestion/tests/test_modelos.py
# Pruebas unitarias de los modelos: comprueban que las reglas de validación

from decimal import Decimal# Decimal guarda dinero sin errores de redondeo
from django.core.exceptions import ValidationError# ValidationError es la excepción que lanzan las reglas de validación (clean y full_clean)
# IntegrityError la lanza la base de datos cuando se rompe una restricción (unicidad, CHECK)
# ProtectedError la lanza Django cuando se intenta borrar algo protegido (on_delete=PROTECT)
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase# TestCase crea una base temporal y deshace los datos al terminar cada prueba
from django.contrib.auth.models import User# Modelos que se prueban
from gestion.models import Cliente, Contacto, Cuenta, Moneda, Transaccion
from .utilidades import crear_cliente, crear_cuenta, crear_moneda, depositar# Funciones de ayuda para crear datos de prueba


# ============================================================
# MONEDA
# ============================================================

class MonedaTests(TestCase):
    def test_se_muestra_con_su_codigo(self):
        # __str__ devuelve el código de la moneda
        self.assertEqual(str(crear_moneda('USD', 'Dólar', 'US$')), 'USD')

    def test_el_codigo_no_se_puede_repetir(self):
        crear_moneda('CLP') # Primera moneda CLP
        # Crear otra con el mismo código rompe la restricción de unicidad
        # transaction.atomic aísla el error para que la prueba pueda seguir usando la base
        with self.assertRaises(IntegrityError), transaction.atomic():
            Moneda.objects.create(codigo='CLP', nombre='Otra', simbolo='$')


# ============================================================
# CLIENTE
# ============================================================

class ClienteTests(TestCase):
    def test_se_muestra_con_su_nombre(self):
        self.assertEqual(str(crear_cliente('Ana García', 'ana')), 'Ana García')

    def test_el_correo_no_se_puede_repetir(self):
        crear_cliente('Ana García', 'ana', email='mismo@prueba.test')# Primer cliente con un correo
        # Un segundo cliente con el mismo correo rompe la unicidad
        with self.assertRaises(IntegrityError), transaction.atomic():
            crear_cliente('Otra Persona', 'otra', email='mismo@prueba.test')

    def test_el_telefono_es_opcional_y_se_guarda_como_null(self):
        # Sin teléfono, la base guarda NULL (no un texto vacío)
        cliente = crear_cliente('Ana García', 'ana', telefono=None)
        cliente.refresh_from_db()
        self.assertIsNone(cliente.telefono)

    def test_dos_clientes_pueden_no_tener_telefono(self):
        # El teléfono no es único: varios clientes pueden dejarlo vacío
        crear_cliente('Ana García', 'ana')
        crear_cliente('Luis Pérez', 'luis')
        self.assertEqual(Cliente.objects.filter(telefono__isnull=True).count(), 2)

    def test_un_usuario_solo_puede_tener_un_cliente(self):
        # Relación 1:1: el mismo usuario no puede tener dos clientes
        cliente = crear_cliente('Ana García', 'ana')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Cliente.objects.create(usuario=cliente.usuario, nombre='Duplicada', email='dup@prueba.test')

    def test_el_usuario_accede_a_su_cliente_con_user_cliente(self):
        # related_name='cliente' permite ir del usuario al cliente
        cliente = crear_cliente('Ana García', 'ana')
        self.assertEqual(cliente.usuario.cliente, cliente)

    def test_al_borrar_el_usuario_se_borra_el_cliente(self):
        # on_delete=CASCADE: sin usuario no queda cliente
        cliente = crear_cliente('Ana García', 'ana')
        cliente.usuario.delete()
        self.assertFalse(Cliente.objects.filter(pk=cliente.pk).exists())


# ============================================================
# CONTACTO
# ============================================================

class ContactoTests(TestCase):
    # setUp se ejecuta antes de cada prueba de esta clase: aquí se crean los datos comunes
    def setUp(self):
        self.ana = crear_cliente('Ana García', 'ana')
        self.luis = crear_cliente('Luis Pérez', 'luis')

    def test_se_muestra_quien_agenda_a_quien(self):
        ficha = Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        self.assertEqual(str(ficha), 'Ana García -> Luis Pérez')

    def test_agendar_es_en_un_solo_sentido(self):
        # Ana agenda a Luis
        Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        # Luis aparece en los contactos de Ana...
        self.assertIn(self.luis, self.ana.contactos.all())
        # ...pero Ana NO aparece en los contactos de Luis (la relación no es simétrica)
        self.assertNotIn(self.ana, self.luis.contactos.all())
        # Y Luis sabe quién lo tiene agendado
        self.assertIn(self.ana, self.luis.agendado_por.all())

    def test_no_se_puede_agendar_dos_veces_al_mismo_cliente(self):
        Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        # El par (propietario, agendado) es único
        with self.assertRaises(IntegrityError), transaction.atomic():
            Contacto.objects.create(propietario=self.ana, agendado=self.luis)

    def test_la_base_impide_agendarse_a_si_mismo(self):
        # Restricción CHECK de la base de datos
        with self.assertRaises(IntegrityError), transaction.atomic():
            Contacto.objects.create(propietario=self.ana, agendado=self.ana)

    def test_clean_impide_agendarse_a_si_mismo_con_un_mensaje_claro(self):
        # clean() es la misma regla, pero con mensaje para formularios y panel
        ficha = Contacto(propietario=self.ana, agendado=self.ana)
        with self.assertRaisesMessage(ValidationError, 'no puede agendarse a sí mismo'):
            ficha.clean()

    def test_al_borrar_un_cliente_se_borran_sus_fichas(self):
        Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        Contacto.objects.create(propietario=self.luis, agendado=self.ana)
        # Borrar a Ana elimina las fichas donde ella es dueña o aparece agendada
        self.ana.delete()
        self.assertEqual(Contacto.objects.count(), 0)


# ============================================================
# CUENTA
# ============================================================

class CuentaTests(TestCase):
    def setUp(self):
        self.ana = crear_cliente('Ana García', 'ana')
        self.cuenta = crear_cuenta(self.ana, '0001')

    def test_se_muestra_con_numero_y_moneda(self):
        self.assertEqual(str(self.cuenta), '0001 (CLP)')

    def test_el_numero_no_se_puede_repetir(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            crear_cuenta(self.ana, '0001')

    def test_una_cuenta_nueva_tiene_saldo_cero(self):
        self.assertEqual(self.cuenta.saldo, Decimal('0.00'))

    def test_el_saldo_es_entradas_menos_salidas(self):
        # Segunda cuenta para poder transferir
        luis = crear_cliente('Luis Pérez', 'luis')
        otra = crear_cuenta(luis, '0002')
        # Deposita 1000 en la cuenta de Ana
        depositar(self.cuenta, 1000)
        # Ana transfiere 300 a Luis y retira 200
        Transaccion.objects.create(tipo='transferencia', cuenta_origen=self.cuenta, cuenta_destino=otra, monto=Decimal('300'))
        Transaccion.objects.create(tipo='retiro', cuenta_origen=self.cuenta, monto=Decimal('200'))
        # 1000 - 300 - 200 = 500 para Ana; 300 para Luis
        self.assertEqual(self.cuenta.saldo, Decimal('500'))
        self.assertEqual(otra.saldo, Decimal('300'))

    def test_una_moneda_con_cuentas_no_se_puede_borrar(self):
        # on_delete=PROTECT en Cuenta.moneda
        with self.assertRaises(ProtectedError):
            self.cuenta.moneda.delete()

    def test_un_cliente_con_movimientos_no_se_puede_borrar(self):
        # Hay un movimiento en su cuenta: Transaccion protege a la cuenta
        depositar(self.cuenta, 100)
        with self.assertRaises(ProtectedError):
            self.ana.delete()

    def test_un_cliente_sin_movimientos_se_borra_con_sus_cuentas(self):
        # Sin movimientos, el borrado en cascada elimina también sus cuentas
        self.ana.delete()
        self.assertEqual(Cuenta.objects.count(), 0)


# ============================================================
# TRANSACCION
# ============================================================

class TransaccionTests(TestCase):
    def setUp(self):
        self.ana = crear_cliente('Ana García', 'ana')
        self.luis = crear_cliente('Luis Pérez', 'luis')
        # Cuenta de Ana con 1000 de saldo y cuenta de Luis vacía, ambas en CLP
        self.cuenta_ana = crear_cuenta(self.ana, '0001')
        self.cuenta_luis = crear_cuenta(self.luis, '0002')
        depositar(self.cuenta_ana, 1000)

    # Arma una transacción sin guardarla, para probar sus reglas con full_clean
    def armar(self, tipo, origen=None, destino=None, monto='100'):
        return Transaccion(tipo=tipo, cuenta_origen=origen, cuenta_destino=destino, monto=Decimal(monto))

    def test_se_muestra_con_tipo_y_monto(self):
        movimiento = self.armar('deposito', destino=self.cuenta_luis, monto='50.00')
        self.assertEqual(str(movimiento), 'Depósito de 50.00')

    # ---------- reglas por tipo ----------

    def test_un_deposito_valido_pasa(self):
        # full_clean no lanza error si todo está bien
        self.armar('deposito', destino=self.cuenta_luis).full_clean()

    def test_un_deposito_necesita_destino(self):
        with self.assertRaisesMessage(ValidationError, 'necesita una cuenta destino'):
            self.armar('deposito').full_clean()

    def test_un_deposito_no_lleva_origen(self):
        with self.assertRaisesMessage(ValidationError, 'no debe tener cuenta origen'):
            self.armar('deposito', origen=self.cuenta_ana, destino=self.cuenta_luis).full_clean()

    def test_un_retiro_valido_pasa(self):
        self.armar('retiro', origen=self.cuenta_ana, monto='500').full_clean()

    def test_un_retiro_necesita_origen(self):
        with self.assertRaisesMessage(ValidationError, 'necesita una cuenta origen'):
            self.armar('retiro').full_clean()

    def test_un_retiro_no_lleva_destino(self):
        with self.assertRaisesMessage(ValidationError, 'no debe tener cuenta destino'):
            self.armar('retiro', origen=self.cuenta_ana, destino=self.cuenta_luis).full_clean()

    def test_una_transferencia_valida_pasa(self):
        self.armar('transferencia', self.cuenta_ana, self.cuenta_luis, '400').full_clean()

    def test_una_transferencia_necesita_las_dos_cuentas(self):
        with self.assertRaisesMessage(ValidationError, 'necesita cuenta origen y destino'):
            self.armar('transferencia', origen=self.cuenta_ana).full_clean()

    def test_una_transferencia_no_puede_ser_a_la_misma_cuenta(self):
        with self.assertRaisesMessage(ValidationError, 'deben ser distintas'):
            self.armar('transferencia', self.cuenta_ana, self.cuenta_ana).full_clean()

    def test_una_transferencia_exige_la_misma_moneda(self):
        # Cuenta de Luis en dólares
        cuenta_usd = crear_cuenta(self.luis, '0003', moneda=crear_moneda('USD', 'Dólar', 'US$'))
        with self.assertRaisesMessage(ValidationError, 'misma moneda'):
            self.armar('transferencia', self.cuenta_ana, cuenta_usd).full_clean()

    # ---------- cuentas inactivas y saldo ----------

    def test_una_cuenta_origen_inactiva_no_envia_dinero(self):
        self.cuenta_ana.activa = False
        self.cuenta_ana.save()
        with self.assertRaisesMessage(ValidationError, 'origen está inactiva'):
            self.armar('retiro', origen=self.cuenta_ana).full_clean()

    def test_una_cuenta_destino_inactiva_no_recibe_dinero(self):
        self.cuenta_luis.activa = False
        self.cuenta_luis.save()
        with self.assertRaisesMessage(ValidationError, 'destino está inactiva'):
            self.armar('deposito', destino=self.cuenta_luis).full_clean()

    def test_no_se_puede_sacar_mas_que_el_saldo(self):
        # Ana tiene 1000; intenta retirar 1000.01
        with self.assertRaisesMessage(ValidationError, 'Saldo insuficiente: la cuenta origen tiene 1000.00.'):
            self.armar('retiro', origen=self.cuenta_ana, monto='1000.01').full_clean()

    def test_se_puede_sacar_exactamente_el_saldo(self):
        # Retirar todo el saldo es válido
        self.armar('retiro', origen=self.cuenta_ana, monto='1000').full_clean()

    def test_la_regla_de_saldo_tambien_aplica_a_transferencias(self):
        with self.assertRaisesMessage(ValidationError, 'Saldo insuficiente'):
            self.armar('transferencia', self.cuenta_ana, self.cuenta_luis, '5000').full_clean()

    def test_editar_un_movimiento_guardado_no_revisa_saldo_ni_cuentas_inactivas(self):
        # Se guarda una transferencia válida de 400
        movimiento = Transaccion.objects.create(
            tipo='transferencia', cuenta_origen=self.cuenta_ana, cuenta_destino=self.cuenta_luis, monto=Decimal('400'),
        )
        # Después la cuenta de origen se desactiva
        self.cuenta_ana.activa = False
        self.cuenta_ana.save()
        # Revalidar el movimiento ya guardado no falla: esas reglas solo valen al crear (_state.adding)
        movimiento.full_clean()

    # ---------- monto ----------

    def test_el_monto_cero_o_negativo_no_pasa_la_validacion(self):
        for monto in ('0', '-5'):
            with self.subTest(monto=monto):
                with self.assertRaises(ValidationError):
                    self.armar('deposito', destino=self.cuenta_luis, monto=monto).full_clean()

    def test_la_base_impide_montos_no_positivos_aunque_se_salte_la_validacion(self):
        # create no llama a clean; la restricción CHECK de la base es la última defensa
        for monto in ('0', '-5'):
            with self.subTest(monto=monto):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Transaccion.objects.create(tipo='deposito', cuenta_destino=self.cuenta_luis, monto=Decimal(monto))

    # ---------- orden ----------

    def test_los_movimientos_salen_del_mas_nuevo_al_mas_antiguo(self):
        from datetime import timedelta
        from django.utils import timezone
        # Tres depósitos; luego se fijan fechas distintas a mano (fecha se llena sola al crear)
        primero = depositar(self.cuenta_luis, 1)
        segundo = depositar(self.cuenta_luis, 2)
        tercero = depositar(self.cuenta_luis, 3)
        ahora = timezone.now()
        Transaccion.objects.filter(pk=primero.pk).update(fecha=ahora - timedelta(days=3))
        Transaccion.objects.filter(pk=segundo.pk).update(fecha=ahora - timedelta(days=2))
        Transaccion.objects.filter(pk=tercero.pk).update(fecha=ahora - timedelta(days=1))
        # Solo los tres depósitos a la cuenta de Luis, en el orden por defecto del modelo
        orden = list(Transaccion.objects.filter(cuenta_destino=self.cuenta_luis).values_list('pk', flat=True))
        self.assertEqual(orden, [tercero.pk, segundo.pk, primero.pk])