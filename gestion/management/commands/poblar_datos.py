# gestion/management/commands/poblar_datos.py


import os  # os lee variables del entorno; secrets genera claves aleatorias seguras
import secrets
from django.core.management.base import BaseCommand   # Importa la clase base para crear comandos propios de manage.py
from django.contrib.auth.models import User  # Importa el usuario de login de Django
from django.utils import timezone  # Importa timezone para obtener la fecha y hora actual
from datetime import timedelta  # Importa timedelta para restar días a una fecha
from gestion.models import Moneda, Cliente, Contacto, Cuenta, Transaccion  # Importa nuestros modelos

# Clave de los usuarios de demostración nuevos: se lee de .env (variable CLAVE_DEMO) o, si no existe, se genera al azar
# Así no hay ninguna clave escrita en el código
CLAVE_DEMO = os.environ.get('CLAVE_DEMO') or secrets.token_urlsafe(9)

# Lista de monedas: (código, nombre, símbolo)
MONEDAS = [
    ('CLP', 'Peso chileno', '$'),
    ('USD', 'Dólar estadounidense', 'US$'),
]

# Lista de clientes: (usuario de login, nombre, email, teléfono)
# Luis no tiene teléfono (None) y Marta lo tiene como texto vacío (''),
# para probar más adelante la diferencia entre NULL y vacío
CLIENTES = [
    ('ana', 'Ana García', 'ana@example.com', '123456789'),
    ('luis', 'Luis Pérez', 'luis@example.com', None),
    ('carla', 'Carla Soto', 'carla@example.com', '987654321'),
    ('diego', 'Diego Rojas', 'diego@example.com', None),
    ('marta', 'Marta Vega', 'marta@example.com', ''),
]

# Lista de cuentas: (número, usuario dueño, código de moneda)
CUENTAS = [
    ('0001', 'ana', 'CLP'),
    ('0002', 'luis', 'CLP'),
    ('0003', 'ana', 'USD'),
    ('0004', 'carla', 'CLP'),
    ('0005', 'diego', 'CLP'),
    ('0006', 'diego', 'USD'),
    ('0007', 'marta', 'CLP'),
]

# Lista de contactos: (quien agenda, a quién agenda, apodo)
CONTACTOS = [
    ('ana', 'luis', 'Lucho'),
    ('ana', 'carla', 'Carli'),
    ('luis', 'ana', 'Anita'),
    ('carla', 'diego', ''),
    ('diego', 'marta', 'Marti'),
]

# Lista de movimientos: (descripción, tipo, cuenta origen, cuenta destino, monto, días atrás)
# La descripción es única y sirve para reconocer cada movimiento al repetir el comando
# None significa "sin cuenta" (un depósito no tiene origen y un retiro no tiene destino)
TRANSACCIONES = [
    ('Depósito inicial Carla', 'deposito', None, '0004', 200000, 60),
    ('Depósito inicial Diego', 'deposito', None, '0005', 150000, 55),
    ('Depósito inicial Marta', 'deposito', None, '0007', 80000, 50),
    ('Depósito USD Diego', 'deposito', None, '0006', 500, 45),
    ('Depósito USD Ana', 'deposito', None, '0003', 300, 40),
    ('Pago almuerzo', 'transferencia', '0004', '0005', 25000, 35),
    ('Arriendo compartido', 'transferencia', '0005', '0007', 40000, 30),
    ('Retiro cajero Carla', 'retiro', '0004', None, 50000, 25),
    ('Devolución a Carla', 'transferencia', '0001', '0004', 15000, 20),
    ('Pago de cuenta', 'transferencia', '0004', '0001', 10000, 15),
    ('Retiro cajero Marta', 'retiro', '0007', None, 20000, 10),
    ('Envío USD a Ana', 'transferencia', '0006', '0003', 100, 7),
    ('Sueldo Ana', 'deposito', None, '0001', 50000, 5),
    ('Ajuste entre amigos', 'transferencia', '0005', '0004', 10000, 3),
    ('Retiro cajero Marta 2', 'retiro', '0007', None, 5000, 2),
    ('Depósito Luis', 'deposito', None, '0002', 30000, 1),
]


# Todo comando debe llamarse Command y heredar de BaseCommand
class Command(BaseCommand):
    # Texto que aparece al escribir: python manage.py help poblar_datos
    help = 'Carga datos de demostración sin duplicar los que ya existen'

    # handle es el método que se ejecuta al correr el comando
    def handle(self, *args, **options):
        # Contadores para informar al final cuántos registros nuevos se crearon
        nuevos = {
            'monedas': 0,
            'clientes': 0,
            'cuentas': 0,
            'contactos': 0,
            'transacciones': 0,
        }

        # Diccionarios para encontrar rápido cada objeto por su código, usuario o número
        monedas = {}
        clientes = {}
        cuentas = {}

        # ---------- MONEDAS ----------
        for codigo, nombre, simbolo in MONEDAS:
            # get_or_create busca por código; si no existe, la crea con los valores de defaults
            # Devuelve dos cosas: el objeto y un True/False que dice si se creó ahora
            moneda, creada = Moneda.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'simbolo': simbolo},
            )
            # Guarda la moneda en el diccionario para usarla después
            monedas[codigo] = moneda
            # Si se creó ahora, suma uno al contador
            if creada:
                nuevos['monedas'] += 1

        # ---------- CLIENTES (y sus usuarios de login) ----------
        for usuario_login, nombre, email, telefono in CLIENTES:
            # Busca el usuario de login; si no existe, lo crea
            usuario, usuario_creado = User.objects.get_or_create(username=usuario_login)
            # Solo a los usuarios nuevos se les asigna contraseña (se guarda cifrada)
            if usuario_creado:
                usuario.set_password(CLAVE_DEMO)
                # Muestra la clave una sola vez, porque no queda guardada en ningún archivo
                print(f'  Usuario {usuario.username}: clave {CLAVE_DEMO}')
                usuario.save()

            # Busca el cliente de ese usuario; si no existe, lo crea con los datos de defaults
            cliente, creado = Cliente.objects.get_or_create(
                usuario=usuario,
                defaults={'nombre': nombre, 'email': email, 'telefono': telefono},
            )
            # Guarda el cliente en el diccionario, usando el nombre de usuario como llave
            clientes[usuario_login] = cliente
            # Si se creó ahora, suma uno al contador
            if creado:
                nuevos['clientes'] += 1

        # ---------- CUENTAS ----------
        for numero, usuario_login, codigo in CUENTAS:
            # Busca la cuenta por su número; si no existe, la crea con su cliente y su moneda
            cuenta, creada = Cuenta.objects.get_or_create(
                numero=numero,
                defaults={
                    'cliente': clientes[usuario_login],
                    'moneda': monedas[codigo],
                },
            )
            # Guarda la cuenta en el diccionario, usando el número como llave
            cuentas[numero] = cuenta
            # Si se creó ahora, suma uno al contador
            if creada:
                nuevos['cuentas'] += 1

        # ---------- CONTACTOS ----------
        for propietario, agendado, apodo in CONTACTOS:
            # Busca la ficha con esa pareja; si no existe, la crea con el apodo
            contacto, creado = Contacto.objects.get_or_create(
                propietario=clientes[propietario],
                agendado=clientes[agendado],
                defaults={'apodo': apodo},
            )
            # Si se creó ahora, suma uno al contador
            if creado:
                nuevos['contactos'] += 1

        # ---------- TRANSACCIONES ----------
        for descripcion, tipo, num_origen, num_destino, monto, dias in TRANSACCIONES:
            # Si hay número de cuenta origen, busca la cuenta; si no, queda vacía (None)
            origen = cuentas[num_origen] if num_origen else None
            # Lo mismo para la cuenta destino
            destino = cuentas[num_destino] if num_destino else None

            # Busca el movimiento por su descripción; si no existe, lo crea
            transaccion, creada = Transaccion.objects.get_or_create(
                descripcion=descripcion,
                defaults={
                    'tipo': tipo,
                    'cuenta_origen': origen,
                    'cuenta_destino': destino,
                    'monto': monto,
                },
            )

            # Solo si se creó ahora, le ponemos una fecha en el pasado
            if creada:
                # El campo fecha se llena solo con la fecha de hoy (auto_now_add)
                # update() modifica la fecha directo en la base, sin pasar por esa regla
                Transaccion.objects.filter(pk=transaccion.pk).update(
                    fecha=timezone.now() - timedelta(days=dias)
                )
                # Suma uno al contador
                nuevos['transacciones'] += 1

        # ---------- RESUMEN ----------
        # Informa cuántos registros nuevos se crearon en esta ejecución
        self.stdout.write(self.style.SUCCESS('Registros nuevos en esta ejecución:'))
        for nombre_tabla, cantidad in nuevos.items():
            self.stdout.write(f'  {nombre_tabla}: {cantidad}')

        # Informa cuántos registros hay en total en la base
        self.stdout.write(self.style.SUCCESS('Totales en la base de datos:'))
        self.stdout.write(f'  monedas: {Moneda.objects.count()}')
        self.stdout.write(f'  clientes: {Cliente.objects.count()}')
        self.stdout.write(f'  cuentas: {Cuenta.objects.count()}')
        self.stdout.write(f'  contactos: {Contacto.objects.count()}')
        self.stdout.write(f'  transacciones: {Transaccion.objects.count()}')

        # Muestra el saldo calculado de cada cuenta, para verificar los datos
        self.stdout.write(self.style.SUCCESS('Saldos por cuenta:'))
        for cuenta in Cuenta.objects.order_by('numero'):
            self.stdout.write(
                f'  {cuenta.numero} ({cuenta.moneda.codigo}) {cuenta.cliente.nombre}: {cuenta.saldo}'
            )