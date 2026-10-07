# gestion/servicios.py
# Servicio para registrar transacciones de forma segura

from django.db import transaction # transaction.atomic agrupa varias operaciones: o se hacen todas, o no se hace ninguna
from .models import Cliente, Cuenta, Transaccion # Modelos que usa el servicio


# Registra un movimiento de dinero de forma segura y devuelve el movimiento creado
# Si algo no es válido lanza ValidationError y no se guarda nada
def registrar_transaccion(tipo, cuenta_origen=None, cuenta_destino=None, monto=None, descripcion=''):
    with transaction.atomic():  # atomic: todo lo que ocurre dentro se guarda junto o se deshace junto
        # Si el dinero sale de una cuenta, se bloquea esa cuenta hasta terminar y se vuelve a leer
        # Así nadie más puede mover dinero de ella mientras se revisa el saldo
        if cuenta_origen is not None:
            cuenta_origen = Cuenta.objects.select_for_update().get(pk=cuenta_origen.pk)
        # La cuenta destino se vuelve a leer sin bloqueo, para conocer su estado actual (activa o no)
        if cuenta_destino is not None:
            cuenta_destino = Cuenta.objects.get(pk=cuenta_destino.pk)

        # Arma el movimiento sin guardarlo todavía
        movimiento = Transaccion(
            tipo=tipo,
            cuenta_origen=cuenta_origen,
            cuenta_destino=cuenta_destino,
            monto=monto,
            descripcion=descripcion,
        )

        movimiento.full_clean()# Repite todas las validaciones con la cuenta ya bloqueada, incluido el saldo
        movimiento.save() # Guarda el movimiento; al salir del bloque atomic se confirma todo

    return movimiento # Devuelve el movimiento creado

# Calcula el siguiente número de cuenta libre: 0001, 0002, 0003...
def siguiente_numero_cuenta():
    # Lista de los números que ya existen
    existentes = Cuenta.objects.values_list('numero', flat=True)
    # Se quedan solo los que son puramente dígitos (los demás no cuentan para la secuencia)
    usados = [int(numero) for numero in existentes if numero.isdigit()]
    # El siguiente es el mayor más uno; si no hay cuentas, parte en 1
    siguiente = max(usados, default=0) + 1
    # zfill rellena con ceros a la izquierda hasta tener 4 dígitos
    return str(siguiente).zfill(4)


# Crea el cliente de un usuario recién registrado y le abre su primera cuenta (con saldo 0)
def crear_cliente_con_cuenta(usuario, nombre, email, telefono, moneda):
    # atomic: o se crean el cliente y la cuenta, o no se crea ninguno
    with transaction.atomic():
        # Cliente asociado al usuario; el teléfono vacío se guarda como NULL
        cliente = Cliente.objects.create(
            usuario=usuario,
            nombre=nombre,
            email=email,
            telefono=telefono or None,
        )
        # Primera cuenta del cliente, en la moneda elegida
        cuenta = Cuenta.objects.create(
            cliente=cliente,
            moneda=moneda,
            numero=siguiente_numero_cuenta(),
        )
    # Devuelve las dos cosas creadas
    return cliente, cuenta