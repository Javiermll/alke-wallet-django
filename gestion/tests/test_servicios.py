#gestion/tests/test_servicios.py
# Pruebas unitarias de los servicios: comprueban que las reglas de validación


from decimal import Decimal# Decimal guarda dinero sin errores de redondeo
from django.contrib.auth.models import User# Usuario de Django, para probar el alta de clientes
from django.core.exceptions import ValidationError# ValidationError es la excepción que lanzan las reglas de validación
from django.test import TestCase# TestCase crea una base temporal y deshace los datos al terminar cada prueba
from unittest import mock# mock permite reemplazar temporalmente una función para espiar cómo se usa o forzar un fallo
from gestion.models import Cliente, Cuenta, Transaccion# Modelos y servicios que se prueban
from gestion.servicios import crear_cliente_con_cuenta, registrar_transaccion, siguiente_numero_cuenta
from .utilidades import crear_cliente, crear_cuenta, crear_moneda, depositar# Funciones de ayuda para crear datos de prueba


# ============================================================
# registrar_transaccion
# ============================================================

class RegistrarTransaccionTests(TestCase):
    # Datos comunes: Ana con 1000 en su cuenta y Luis con la cuenta vacía, ambos en CLP
    def setUp(self):
        self.ana = crear_cliente('Ana García', 'ana')
        self.luis = crear_cliente('Luis Pérez', 'luis')
        self.cuenta_ana = crear_cuenta(self.ana, '0001')
        self.cuenta_luis = crear_cuenta(self.luis, '0002')
        depositar(self.cuenta_ana, 1000)

    # Cantidad de movimientos guardados en este momento
    def total_movimientos(self):
        return Transaccion.objects.count()

    # ---------- casos correctos ----------

    def test_un_deposito_suma_al_saldo_y_devuelve_el_movimiento(self):
        antes = self.total_movimientos()
        movimiento = registrar_transaccion('deposito', cuenta_destino=self.cuenta_luis, monto=Decimal('250'), descripcion='Sueldo')
        # Devuelve un movimiento ya guardado, con sus datos
        self.assertIsNotNone(movimiento.pk)
        self.assertEqual(movimiento.descripcion, 'Sueldo')
        # Se guardó exactamente uno más
        self.assertEqual(self.total_movimientos(), antes + 1)
        # El saldo de Luis subió
        self.assertEqual(self.cuenta_luis.saldo, Decimal('250'))

    def test_un_retiro_resta_del_saldo(self):
        registrar_transaccion('retiro', cuenta_origen=self.cuenta_ana, monto=Decimal('300'))
        self.assertEqual(self.cuenta_ana.saldo, Decimal('700'))

    def test_una_transferencia_mueve_el_dinero_sin_crear_ni_perder_nada(self):
        total_antes = self.cuenta_ana.saldo + self.cuenta_luis.saldo
        registrar_transaccion('transferencia', self.cuenta_ana, self.cuenta_luis, Decimal('400'))
        # Ana baja, Luis sube
        self.assertEqual(self.cuenta_ana.saldo, Decimal('600'))
        self.assertEqual(self.cuenta_luis.saldo, Decimal('400'))
        # La suma de los dos saldos no cambia
        self.assertEqual(self.cuenta_ana.saldo + self.cuenta_luis.saldo, total_antes)

    def test_se_puede_retirar_exactamente_todo_el_saldo(self):
        registrar_transaccion('retiro', cuenta_origen=self.cuenta_ana, monto=Decimal('1000'))
        self.assertEqual(self.cuenta_ana.saldo, Decimal('0'))

    def test_la_descripcion_es_opcional(self):
        movimiento = registrar_transaccion('deposito', cuenta_destino=self.cuenta_luis, monto=Decimal('10'))
        self.assertEqual(movimiento.descripcion, '')

    # ---------- casos rechazados: no debe quedar nada guardado ----------

    # Comprueba que el servicio rechaza el movimiento y que nada cambió
    def comprobar_rechazo(self, texto_error, **datos):
        antes = self.total_movimientos()
        saldo_ana = self.cuenta_ana.saldo
        saldo_luis = self.cuenta_luis.saldo
        with self.assertRaisesMessage(ValidationError, texto_error):
            registrar_transaccion(**datos)
        # No se guardó ningún movimiento y los saldos siguen iguales
        self.assertEqual(self.total_movimientos(), antes)
        self.assertEqual(self.cuenta_ana.saldo, saldo_ana)
        self.assertEqual(self.cuenta_luis.saldo, saldo_luis)

    def test_un_retiro_sin_saldo_suficiente_se_rechaza(self):
        self.comprobar_rechazo('Saldo insuficiente', tipo='retiro', cuenta_origen=self.cuenta_ana, monto=Decimal('1000.01'))

    def test_una_transferencia_sin_saldo_suficiente_se_rechaza(self):
        self.comprobar_rechazo('Saldo insuficiente', tipo='transferencia',
                               cuenta_origen=self.cuenta_ana, cuenta_destino=self.cuenta_luis, monto=Decimal('5000'))

    def test_una_cuenta_inactiva_se_rechaza(self):
        self.cuenta_luis.activa = False
        self.cuenta_luis.save()
        self.comprobar_rechazo('destino está inactiva', tipo='deposito', cuenta_destino=self.cuenta_luis, monto=Decimal('10'))

    def test_una_transferencia_entre_monedas_distintas_se_rechaza(self):
        cuenta_usd = crear_cuenta(self.luis, '0003', moneda=crear_moneda('USD', 'Dólar', 'US$'))
        self.comprobar_rechazo('misma moneda', tipo='transferencia',
                               cuenta_origen=self.cuenta_ana, cuenta_destino=cuenta_usd, monto=Decimal('10'))

    def test_un_deposito_con_cuenta_origen_se_rechaza(self):
        self.comprobar_rechazo('no debe tener cuenta origen', tipo='deposito',
                               cuenta_origen=self.cuenta_ana, cuenta_destino=self.cuenta_luis, monto=Decimal('10'))

    def test_un_monto_cero_o_negativo_se_rechaza(self):
        for monto in ('0', '-50'):
            with self.subTest(monto=monto):
                antes = self.total_movimientos()
                with self.assertRaises(ValidationError):
                    registrar_transaccion('deposito', cuenta_destino=self.cuenta_luis, monto=Decimal(monto))
                self.assertEqual(self.total_movimientos(), antes)

    # ---------- el servicio revisa el estado actual, no el que traía la vista ----------

    def test_dos_retiros_seguidos_no_pueden_gastar_mas_que_el_saldo(self):
        # El primer retiro de 600 deja 400
        registrar_transaccion('retiro', cuenta_origen=self.cuenta_ana, monto=Decimal('600'))
        # El segundo de 600 se rechaza aunque el objeto cuenta_ana, en memoria, no se haya actualizado
        with self.assertRaisesMessage(ValidationError, 'Saldo insuficiente: la cuenta origen tiene 400.00.'):
            registrar_transaccion('retiro', cuenta_origen=self.cuenta_ana, monto=Decimal('600'))
        self.assertEqual(self.cuenta_ana.saldo, Decimal('400'))

    def test_usa_el_estado_actual_de_la_cuenta_y_no_el_del_objeto_recibido(self):
        # El objeto en memoria dice activa=True...
        cuenta_en_memoria = crear_cuenta(self.luis, '0004')
        self.assertTrue(cuenta_en_memoria.activa)
        # ...pero en la base alguien la desactivó después de que la vista la leyó
        Cuenta.objects.filter(pk=cuenta_en_memoria.pk).update(activa=False)
        # El servicio la vuelve a leer y rechaza el movimiento
        with self.assertRaisesMessage(ValidationError, 'destino está inactiva'):
            registrar_transaccion('deposito', cuenta_destino=cuenta_en_memoria, monto=Decimal('10'))

    def test_bloquea_solo_la_cuenta_de_origen(self):
        # wraps deja que select_for_update funcione normal, pero permite contar cuántas veces se llamó
        with mock.patch.object(Cuenta.objects, 'select_for_update', wraps=Cuenta.objects.select_for_update) as bloqueo:
            # Un depósito no saca dinero: no se bloquea nada
            registrar_transaccion('deposito', cuenta_destino=self.cuenta_luis, monto=Decimal('10'))
            self.assertEqual(bloqueo.call_count, 0)
            # Un retiro sí: se bloquea la cuenta de origen una vez
            registrar_transaccion('retiro', cuenta_origen=self.cuenta_ana, monto=Decimal('10'))
            self.assertEqual(bloqueo.call_count, 1)


# ============================================================
# siguiente_numero_cuenta y crear_cliente_con_cuenta
# ============================================================

class NumeroDeCuentaTests(TestCase):
    def test_sin_cuentas_el_primer_numero_es_0001(self):
        self.assertEqual(siguiente_numero_cuenta(), '0001')

    def test_el_siguiente_es_el_mayor_mas_uno(self):
        ana = crear_cliente('Ana García', 'ana')
        crear_cuenta(ana, '0003')
        crear_cuenta(ana, '0007')
        self.assertEqual(siguiente_numero_cuenta(), '0008')

    def test_ignora_los_numeros_que_no_son_solo_digitos(self):
        ana = crear_cliente('Ana García', 'ana')
        crear_cuenta(ana, 'ABC-1')
        crear_cuenta(ana, '0002')
        self.assertEqual(siguiente_numero_cuenta(), '0003')

    def test_pasado_el_9999_sigue_sin_error(self):
        ana = crear_cliente('Ana García', 'ana')
        crear_cuenta(ana, '9999')
        self.assertEqual(siguiente_numero_cuenta(), '10000')


class CrearClienteConCuentaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='nora')
        self.clp = crear_moneda('CLP')

    def test_crea_el_cliente_y_su_primera_cuenta_con_saldo_cero(self):
        cliente, cuenta = crear_cliente_con_cuenta(self.usuario, 'Nora Nueva', 'nora@prueba.test', '555', self.clp)
        # El cliente quedó asociado al usuario
        self.assertEqual(cliente.usuario, self.usuario)
        self.assertEqual(cliente.nombre, 'Nora Nueva')
        # La cuenta es del cliente, en la moneda elegida, con el primer número libre y sin dinero
        self.assertEqual(cuenta.cliente, cliente)
        self.assertEqual(cuenta.moneda, self.clp)
        self.assertEqual(cuenta.numero, '0001')
        self.assertEqual(cuenta.saldo, Decimal('0'))

    def test_un_telefono_vacio_se_guarda_como_null(self):
        cliente, _ = crear_cliente_con_cuenta(self.usuario, 'Nora Nueva', 'nora@prueba.test', '', self.clp)
        cliente.refresh_from_db()
        self.assertIsNone(cliente.telefono)

    def test_si_falla_la_cuenta_no_queda_el_cliente(self):
        # Se fuerza un fallo al calcular el número de cuenta
        with mock.patch('gestion.servicios.siguiente_numero_cuenta', side_effect=RuntimeError('falla simulada')):
            with self.assertRaises(RuntimeError):
                crear_cliente_con_cuenta(self.usuario, 'Nora Nueva', 'nora@prueba.test', '', self.clp)
        # atomic deshizo la creación del cliente
        self.assertEqual(Cliente.objects.count(), 0)
        self.assertEqual(Cuenta.objects.count(), 0)