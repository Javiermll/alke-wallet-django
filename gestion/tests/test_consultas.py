# gestion/tests/test_consultas.py
# Pruebas unitarias de las consultas: comprueban que devuelven los datos correctos y en el orden esperado

from datetime import datetime, timedelta# datetime y timedelta arman fechas exactas para los movimientos de prueba
from decimal import Decimal# Decimal guarda dinero sin errores de redondeo
from django.test import TestCase# TestCase crea una base temporal y deshace los datos al terminar cada prueba
from django.utils import timezone# timezone arma fechas con zona horaria, como las guarda Django
from gestion import consultas# Consultas que se prueban y modelos que devuelven
from gestion.models import Cliente, Contacto, Transaccion
from .utilidades import crear_cliente, crear_cuenta, crear_moneda# Funciones de ayuda para crear datos de prueba


# Crea un movimiento y le fija la fecha, porque Transaccion.fecha se llena sola al crear
def crear_movimiento(tipo, origen, destino, monto, fecha):
    movimiento = Transaccion.objects.create(
        tipo=tipo, cuenta_origen=origen, cuenta_destino=destino, monto=Decimal(str(monto)),
    )
    # update no pasa por auto_now_add, así que sirve para fijar la fecha a mano
    Transaccion.objects.filter(pk=movimiento.pk).update(fecha=fecha)
    return movimiento


# Datos conocidos para todas las pruebas de esta clase: así se sabe de antemano cada cifra esperada
#
#   Clientes (teléfono)       Cuentas                      Agenda
#   Ana    '123'              0001 Ana    CLP              Ana   -> Luis, Carla
#   Luis   NULL               0002 Luis   CLP              Diego -> Marta
#   Carla  ''                 0003 Ana    USD
#   Diego  '987'              0004 Carla  CLP
#   Marta  NULL               0005 Diego  CLP
#                             0006 Diego  USD
#                             0007 Marta  CLP (sin movimientos)
#
#   Movimientos (hace cuántos días)
#   1  depósito       0001 +1000   (20)      5  depósito       0003 +100  USD (1)
#   2  depósito       0004 +500    (10)      6  transferencia  0004 -> 0005 100 (0)
#   3  transferencia  0001 -> 0002 300 (5)   7  depósito       0005 +50   (0)
#   4  retiro         0004 -200    (2)       8  depósito       0006 +40   USD (40)
#
#   Saldos: 0001=700  0002=300  0003=100  0004=200  0005=150  0006=40  0007=0


class ConsultasBase(TestCase):
    # setUpTestData se ejecuta una sola vez por clase (más rápido que setUp, que corre antes de cada prueba)
    @classmethod
    def setUpTestData(cls):
        clp = crear_moneda('CLP')
        usd = crear_moneda('USD', 'Dólar', 'US$')
        # Clientes
        cls.ana = crear_cliente('Ana García', 'ana', telefono='123')
        cls.luis = crear_cliente('Luis Pérez', 'luis', telefono=None)
        cls.carla = crear_cliente('Carla Soto', 'carla', telefono='')
        cls.diego = crear_cliente('Diego Rojas', 'diego', telefono='987')
        cls.marta = crear_cliente('Marta Vega', 'marta', telefono=None)
        # Cuentas
        c1 = crear_cuenta(cls.ana, '0001', clp)
        c2 = crear_cuenta(cls.luis, '0002', clp)
        c3 = crear_cuenta(cls.ana, '0003', usd)
        c4 = crear_cuenta(cls.carla, '0004', clp)
        c5 = crear_cuenta(cls.diego, '0005', clp)
        c6 = crear_cuenta(cls.diego, '0006', usd)
        crear_cuenta(cls.marta, '0007', clp)
        # Agenda
        Contacto.objects.create(propietario=cls.ana, agendado=cls.luis)
        Contacto.objects.create(propietario=cls.ana, agendado=cls.carla)
        Contacto.objects.create(propietario=cls.diego, agendado=cls.marta)
        # Movimientos
        ahora = timezone.now()
        hace = lambda dias: ahora - timedelta(days=dias)
        crear_movimiento('deposito', None, c1, 1000, hace(20))
        crear_movimiento('deposito', None, c4, 500, hace(10))
        crear_movimiento('transferencia', c1, c2, 300, hace(5))
        crear_movimiento('retiro', c4, None, 200, hace(2))
        crear_movimiento('deposito', None, c3, 100, hace(1))
        crear_movimiento('transferencia', c4, c5, 100, hace(0))
        crear_movimiento('deposito', None, c5, 50, hace(0))
        crear_movimiento('deposito', None, c6, 40, hace(40))

    # Nombres de una lista de clientes, para comparar sin importar otros datos
    def nombres(self, clientes):
        return [cliente.nombre for cliente in clientes]


# ============================================================
# FILTROS
# ============================================================

class FiltrosTests(ConsultasBase):
    def test_movimientos_recientes_usa_14_dias_por_defecto(self):
        # Entran los de hace 10, 5, 2, 1 y 0 días (2 de hoy); quedan fuera los de 20 y 40 días
        self.assertEqual(consultas.movimientos_recientes().count(), 6)

    def test_movimientos_recientes_acepta_otra_cantidad_de_dias(self):
        self.assertEqual(consultas.movimientos_recientes(dias=3).count(), 4)
        self.assertEqual(consultas.movimientos_recientes(dias=365).count(), 8)

    def test_movimientos_recientes_salen_del_mas_nuevo_al_mas_antiguo(self):
        fechas = [m.fecha for m in consultas.movimientos_recientes(dias=365)]
        self.assertEqual(fechas, sorted(fechas, reverse=True))

    def test_movimientos_de_cliente_cuenta_origen_y_destino(self):
        self.assertEqual(consultas.movimientos_de_cliente(self.ana).count(), 3) # Ana: depósito a 0001, transferencia desde 0001 y depósito a 0003
        self.assertEqual(consultas.movimientos_de_cliente(self.luis).count(), 1) # Luis solo recibe una transferencia
        self.assertEqual(consultas.movimientos_de_cliente(self.carla).count(), 3) # Carla: depósito, retiro y transferencia que envía
        self.assertEqual(consultas.movimientos_de_cliente(self.diego).count(), 3)# Diego: transferencia que recibe, depósito y depósito en dólares

    def test_movimientos_de_cliente_sin_movimientos_devuelve_vacio(self):
        self.assertEqual(consultas.movimientos_de_cliente(self.marta).count(), 0)

    def test_clientes_con_telefono_descarta_null_y_texto_vacio(self):
        # Luis y Marta tienen NULL; Carla tiene '' (texto vacío)
        self.assertCountEqual(self.nombres(consultas.clientes_con_telefono()), ['Ana García', 'Diego Rojas'])

    def test_clientes_sin_contactos(self):
        # Ana y Diego tienen agenda; los demás no
        self.assertCountEqual(self.nombres(consultas.clientes_sin_contactos()), ['Luis Pérez', 'Carla Soto', 'Marta Vega'])

    def test_clientes_sin_contactos_no_repite_clientes(self):
        # Ana tiene dos contactos, pero aquí solo importa quién no tiene ninguno: sin duplicados
        lista = self.nombres(consultas.clientes_sin_contactos())
        self.assertEqual(len(lista), len(set(lista)))


# ============================================================
# ANOTACIONES Y AGREGACIONES
# ============================================================

class AgregacionesTests(ConsultasBase):
    def test_clientes_con_numero_de_cuentas_ordenados(self):
        resultado = [(c.nombre, c.num_cuentas) for c in consultas.clientes_con_numero_de_cuentas()]
        # Primero quien más cuentas tiene; a igual cantidad, por nombre
        self.assertEqual(resultado, [
            ('Ana García', 2), ('Diego Rojas', 2), ('Carla Soto', 1), ('Luis Pérez', 1), ('Marta Vega', 1),
        ])

    def test_resumen_por_tipo_en_clp(self):
        resultado = consultas.resumen_por_tipo('CLP')
        self.assertEqual(resultado, [
            {'tipo': 'deposito', 'cantidad': 3, 'total': Decimal('1550')},
            {'tipo': 'retiro', 'cantidad': 1, 'total': Decimal('200')},
            {'tipo': 'transferencia', 'cantidad': 2, 'total': Decimal('400')},
        ])

    def test_resumen_por_tipo_en_usd(self):
        # Solo hay dos depósitos en dólares: no se mezclan con los pesos
        self.assertEqual(consultas.resumen_por_tipo('USD'), [
            {'tipo': 'deposito', 'cantidad': 2, 'total': Decimal('140')},
        ])

    def test_resumen_por_tipo_usa_clp_por_defecto(self):
        self.assertEqual(consultas.resumen_por_tipo(), consultas.resumen_por_tipo('CLP'))

    def test_resumen_por_tipo_de_una_moneda_sin_movimientos(self):
        self.assertEqual(consultas.resumen_por_tipo('EUR'), [])

    def test_cuentas_con_saldo(self):
        saldos = {c.numero: c.saldo_calculado for c in consultas.cuentas_con_saldo()}
        self.assertEqual(saldos, {
            '0001': Decimal('700'), '0002': Decimal('300'), '0003': Decimal('100'), '0004': Decimal('200'),
            '0005': Decimal('150'), '0006': Decimal('40'), '0007': Decimal('0'),
        })

    def test_cuentas_con_saldo_muestra_entradas_y_salidas(self):
        cuenta = consultas.cuentas_con_saldo().get(numero='0001')
        self.assertEqual(cuenta.entradas, Decimal('1000'))
        self.assertEqual(cuenta.salidas, Decimal('300'))

    def test_una_cuenta_sin_movimientos_tiene_saldo_cero_y_no_nulo(self):
        # Coalesce cambia NULL por 0; sin él, la resta daría NULL
        cuenta = consultas.cuentas_con_saldo().get(numero='0007')
        self.assertEqual(cuenta.saldo_calculado, Decimal('0'))

    def test_cuentas_con_saldo_vienen_ordenadas_por_numero(self):
        numeros = [c.numero for c in consultas.cuentas_con_saldo()]
        self.assertEqual(numeros, sorted(numeros))

    def test_el_saldo_calculado_coincide_con_la_propiedad_saldo(self):
        # Dos formas de calcular lo mismo deben dar lo mismo, para todas las cuentas
        for cuenta in consultas.cuentas_con_saldo():
            with self.subTest(cuenta=cuenta.numero):
                self.assertEqual(cuenta.saldo_calculado, cuenta.saldo)

    def test_saldo_por_cliente_en_clp(self):
        resultado = [(f['cliente__nombre'], f['total']) for f in consultas.saldo_por_cliente('CLP')]
        # De mayor a menor; Marta aparece con 0 porque su cuenta existe
        self.assertEqual(resultado, [
            ('Ana García', Decimal('700')), ('Luis Pérez', Decimal('300')), ('Carla Soto', Decimal('200')),
            ('Diego Rojas', Decimal('150')), ('Marta Vega', Decimal('0')),
        ])

    def test_saldo_por_cliente_en_usd_no_suma_pesos(self):
        resultado = [(f['cliente__nombre'], f['total']) for f in consultas.saldo_por_cliente('USD')]
        self.assertEqual(resultado, [('Ana García', Decimal('100')), ('Diego Rojas', Decimal('40'))])

    def test_dos_clientes_con_el_mismo_nombre_no_se_mezclan(self):
        # Se agrupa por el id del cliente y no por el nombre
        otra_ana = crear_cliente('Ana García', 'ana2')
        crear_cuenta(otra_ana, '0008')
        filas = [f for f in consultas.saldo_por_cliente('CLP') if f['cliente__nombre'] == 'Ana García']
        self.assertEqual(len(filas), 2)


class MovimientosPorMesTests(TestCase):
    # fecha_santiago arma una fecha con la zona horaria del proyecto (America/Santiago)
    def fecha_santiago(self, año, mes, dia, hora=12, minuto=0):
        return timezone.make_aware(datetime(año, mes, dia, hora, minuto))

    def test_agrupa_por_mes_del_mas_antiguo_al_mas_reciente(self):
        cuenta = crear_cuenta(crear_cliente('Ana García', 'ana'), '0001')
        # Dos movimientos en enero y uno en marzo, creados en desorden
        crear_movimiento('deposito', None, cuenta, 10, self.fecha_santiago(2026, 3, 5))
        crear_movimiento('deposito', None, cuenta, 10, self.fecha_santiago(2026, 1, 15))
        crear_movimiento('deposito', None, cuenta, 10, self.fecha_santiago(2026, 1, 20))
        resultado = [(f['mes'].year, f['mes'].month, f['cantidad']) for f in consultas.movimientos_por_mes()]
        self.assertEqual(resultado, [(2026, 1, 2), (2026, 3, 1)])

    def test_usa_la_hora_de_santiago_para_decidir_el_mes(self):
        cuenta = crear_cuenta(crear_cliente('Ana García', 'ana'), '0001')
        # 31 de enero a las 23:30 en Santiago es ya febrero en UTC; debe contar como enero
        crear_movimiento('deposito', None, cuenta, 10, self.fecha_santiago(2026, 1, 31, 23, 30))
        resultado = [(f['mes'].year, f['mes'].month) for f in consultas.movimientos_por_mes()]
        self.assertEqual(resultado, [(2026, 1)])

    def test_sin_movimientos_devuelve_lista_vacia(self):
        self.assertEqual(consultas.movimientos_por_mes(), [])


# ============================================================
# SQL PROPIO: raw() y cursor
# ============================================================

class SqlPropioTests(ConsultasBase):
    def test_clientes_con_telefono_sql_da_lo_mismo_que_la_version_orm(self):
        con_sql = self.nombres(consultas.clientes_con_telefono_sql())
        con_orm = self.nombres(consultas.clientes_con_telefono())
        self.assertCountEqual(con_sql, con_orm)
        self.assertCountEqual(con_sql, ['Ana García', 'Diego Rojas'])

    def test_raw_devuelve_objetos_cliente_completos(self):
        for cliente in consultas.clientes_con_telefono_sql():
            self.assertIsInstance(cliente, Cliente)

    def test_buscar_clientes_sql_no_distingue_mayusculas_y_ordena(self):
        # 'AR' aparece en García, Carla y Marta
        self.assertEqual(self.nombres(consultas.buscar_clientes_sql('AR')), ['Ana García', 'Carla Soto', 'Marta Vega'])
        self.assertEqual(self.nombres(consultas.buscar_clientes_sql('ana')), ['Ana García'])

    def test_buscar_clientes_sql_sin_coincidencias_devuelve_lista_vacia(self):
        self.assertEqual(consultas.buscar_clientes_sql('zzz'), [])

    def test_buscar_clientes_sql_resiste_inyeccion_de_sql(self):
        # El texto malicioso va como parámetro: se busca como texto, no se ejecuta
        self.assertEqual(consultas.buscar_clientes_sql("'; DROP TABLE gestion_cliente; --"), [])
        # La tabla sigue intacta
        self.assertEqual(Cliente.objects.count(), 5)

    def test_saldos_sql_trae_una_fila_por_cuenta_con_sus_columnas(self):
        filas = consultas.saldos_sql()
        self.assertEqual(len(filas), 7)
        self.assertEqual(set(filas[0].keys()), {'numero', 'moneda', 'cliente', 'saldo'})
        # Vienen ordenadas por número de cuenta
        self.assertEqual([f['numero'] for f in filas], ['0001', '0002', '0003', '0004', '0005', '0006', '0007'])

    def test_saldos_sql_coincide_con_el_saldo_calculado_por_el_orm(self):
        # Tres formas distintas de calcular el saldo deben coincidir: ORM, propiedad y SQL con cursor
        con_orm = {c.numero: c.saldo_calculado for c in consultas.cuentas_con_saldo()}
        for fila in consultas.saldos_sql():
            with self.subTest(cuenta=fila['numero']):
                # Decimal(str(...)) permite comparar aunque la base devuelva int, float o Decimal
                self.assertEqual(Decimal(str(fila['saldo'])), con_orm[fila['numero']])