#gesrtion/tests/utilidades.py
# Funciones de ayuda para crear datos de prueba con pocas líneas, para no repetir código en cada archivo de pruebas

from decimal import Decimal# Decimal guarda dinero sin errores de redondeo (a diferencia de float)
from django.contrib.auth.models import User# User es el modelo de usuarios de Django
from gestion.models import Cliente, Cuenta, Moneda, Transaccion# Modelos que se crean en las pruebas


# Funciones de ayuda: crean datos de prueba con pocas líneas, para no repetir código en cada archivo de pruebas

# Crea (o recupera) una moneda
def crear_moneda(codigo='CLP', nombre='Peso chileno', simbolo='$'):
    # get_or_create evita el error de código repetido si se pide dos veces la misma moneda
    moneda, _ = Moneda.objects.get_or_create(codigo=codigo, defaults={'nombre': nombre, 'simbolo': simbolo})
    return moneda


# Crea un usuario con su cliente asociado
def crear_cliente(nombre='Ana García', usuario='ana', email=None, telefono=None):
    email = email or f'{usuario}@prueba.test'  # Si no se da correo, se arma uno a partir del nombre de usuario
    # Sin contraseña: el usuario queda con clave inutilizable, lo que basta porque las pruebas inician sesión con force_login
    # (además evita cifrar una clave en cada prueba, que es lo más lento)
    user = User.objects.create_user(username=usuario)
    return Cliente.objects.create(usuario=user, nombre=nombre, email=email, telefono=telefono)


# Crea una cuenta para un cliente
def crear_cuenta(cliente, numero='0001', moneda=None, activa=True):
    moneda = moneda or crear_moneda() # Si no se da moneda, se usa CLP
    return Cuenta.objects.create(cliente=cliente, moneda=moneda, numero=numero, activa=activa)


# Deja dinero en una cuenta con un depósito directo (no pasa por clean, así que sirve para armar saldos)
def depositar(cuenta, monto):
    return Transaccion.objects.create(tipo='deposito', cuenta_destino=cuenta, monto=Decimal(str(monto)))

# Crea un usuario del personal (is_staff), que es quien administra todo el sistema
def crear_personal(usuario='jefe'):
    # Sin contraseña, igual que los clientes: las pruebas inician sesión con force_login
    return User.objects.create_user(username=usuario, is_staff=True)