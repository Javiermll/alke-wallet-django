# gestion/consultas.py
#Se guardan las consultas para luego probarlas en los dos motores de base de datos (SQLite y PostgreSQL)

from django.db.models import Count, Sum, Q, F  # Importa las funciones de cálculo y las herramientas para combinar condiciones
from django.db.models import OuterRef, Subquery, DecimalField  # Importa las herramientas para las subconsultas del saldo
from django.db.models.functions import Coalesce  # Coalesce reemplaza un valor vacío (NULL) por otro, por ejemplo 0
from django.db import connection  # connection permite abrir un cursor para escribir SQL directo
from django.utils import timezone  # timezone da la fecha y hora actual
from datetime import timedelta   # timedelta permite restar días a una fecha
from decimal import Decimal  # Decimal sirve para escribir montos exactos
from .models import Cliente, Cuenta, Transaccion  # Importa los modelos que vamos a consultar (el punto significa "de esta misma app")


# ============================================================
# CONSULTAS CON EL ORM: filtros
# ============================================================

# Movimientos de los últimos N días (por defecto 14)
def movimientos_recientes(dias=14):
    fecha_limite = timezone.now() - timedelta(days=dias) # Calcula la fecha límite: hoy menos la cantidad de días indicada
    return Transaccion.objects.filter(fecha__gte=fecha_limite) # Devuelve los movimientos desde esa fecha; el modelo ya los ordena del más nuevo al más antiguo


# Movimientos en los que participa algún cliente, como origen o como destino
def movimientos_de_cliente(cliente):
    return Transaccion.objects.filter(   # Q permite el "O": la cuenta origen es del cliente O la cuenta destino es del cliente
        Q(cuenta_origen__cliente=cliente) | Q(cuenta_destino__cliente=cliente)
    )


# Clientes que realmente tienen un teléfono escrito
def clientes_con_telefono():
    return Cliente.objects.exclude(telefono__isnull=True).exclude(telefono='')  # Primero descarta los teléfonos NULL y luego los guardados como texto vacío


# Clientes que no han agendado a nadie
def clientes_sin_contactos():
    return Cliente.objects.filter(fichas_de_agenda__isnull=True)  # Un cliente sin fichas de agenda como propietario no tiene contactos


# ============================================================
# CONSULTAS CON EL ORM: anotaciones y agregaciones
# ============================================================

# Cada cliente con la cantidad de cuentas que tiene
def clientes_con_numero_de_cuentas():
    # annotate agrega la columna calculada num_cuentas a cada cliente
    # Se ordena de mayor a menor cantidad y, si empatan, por nombre
    return Cliente.objects.annotate(num_cuentas=Count('cuentas')).order_by('-num_cuentas', 'nombre')


# Cantidad de movimientos y monto total por tipo, solo en una moneda
def resumen_por_tipo(codigo_moneda='CLP'):
    # Se queda con los movimientos cuyo origen o destino está en una cuenta de esa moneda
    solo_moneda = Transaccion.objects.filter(
        Q(cuenta_origen__moneda__codigo=codigo_moneda) | Q(cuenta_destino__moneda__codigo=codigo_moneda)
    )
    # order_by() vacío quita el orden por defecto; values agrupa por tipo; annotate calcula por grupo
    resumen = (
        solo_moneda.order_by()
        .values('tipo')
        .annotate(cantidad=Count('id'), total=Sum('monto'))
        .order_by('tipo')
    )
    # Devuelve una lista de diccionarios, fácil de recorrer o mostrar
    return list(resumen)


# Cada cuenta con su saldo calculado en una sola consulta
def cuentas_con_saldo():
    # Tipo de campo decimal para los montos, igual que en el modelo
    campo_dinero = DecimalField(max_digits=14, decimal_places=2)

    # Pregunta 1: cuánto entró a la cuenta de la fila actual (OuterRef('pk'))
    entradas_sq = (
        Transaccion.objects
        .filter(cuenta_destino=OuterRef('pk'))
        .order_by()
        .values('cuenta_destino')
        .annotate(total=Sum('monto'))
        .values('total')
    )

    # Pregunta 2: cuánto salió de la cuenta de la fila actual
    salidas_sq = (
        Transaccion.objects
        .filter(cuenta_origen=OuterRef('pk'))
        .order_by()
        .values('cuenta_origen')
        .annotate(total=Sum('monto'))
        .values('total')
    )

    # Agrega las dos respuestas como columnas (0 si no hubo movimientos) y luego las resta
    return Cuenta.objects.annotate(
        entradas=Coalesce(Subquery(entradas_sq, output_field=campo_dinero), Decimal('0.00'), output_field=campo_dinero),
        salidas=Coalesce(Subquery(salidas_sq, output_field=campo_dinero), Decimal('0.00'), output_field=campo_dinero),
    ).annotate(saldo_calculado=F('entradas') - F('salidas')).order_by('numero')


# ============================================================
# CONSULTAS CON SQL PROPIO
# ============================================================

# Clientes con teléfono escrito, usando raw(); devuelve objetos Cliente
def clientes_con_telefono_sql():
    # Descarta NULL y texto vacío; raw() exige incluir la clave primaria (aquí viene con el *)
    consulta = "SELECT * FROM gestion_cliente WHERE telefono IS NOT NULL AND telefono <> ''"
    return list(Cliente.objects.raw(consulta))


# Busca clientes cuyo nombre contenga un texto, con raw() y parámetros seguros
def buscar_clientes_sql(texto):
    # LOWER en ambos lados hace la búsqueda igual en SQLite y PostgreSQL, sin distinguir mayúsculas
    consulta = "SELECT * FROM gestion_cliente WHERE LOWER(nombre) LIKE LOWER(%s) ORDER BY nombre"
    # El texto va como parámetro (%s), nunca pegado dentro del SQL; los % rodean al texto buscado
    return list(Cliente.objects.raw(consulta, ['%' + texto + '%']))


# Saldo de cada cuenta con un cursor; devuelve una lista de diccionarios
def saldos_sql():
    # Dos subconsultas por cuenta (entradas y salidas) y una resta; COALESCE cambia NULL por 0
    consulta = """
    SELECT c.numero, m.codigo AS moneda, cl.nombre AS cliente,
      COALESCE((SELECT SUM(t.monto) FROM gestion_transaccion t WHERE t.cuenta_destino_id = c.id), 0)
      - COALESCE((SELECT SUM(t.monto) FROM gestion_transaccion t WHERE t.cuenta_origen_id = c.id), 0)
      AS saldo
    FROM gestion_cuenta c
    JOIN gestion_moneda m ON m.id = c.moneda_id
    JOIN gestion_cliente cl ON cl.id = c.cliente_id
    ORDER BY c.numero
    """
    # El cursor se abre con "with" para que se cierre solo al terminar
    with connection.cursor() as cursor:
        # Ejecuta la consulta
        cursor.execute(consulta)
        # description guarda los nombres de las columnas
        nombres = [columna[0] for columna in cursor.description]
        # zip une cada nombre con su valor, y así cada fila queda como diccionario
        return [dict(zip(nombres, fila)) for fila in cursor.fetchall()]