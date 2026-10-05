# gestion/servicios.py
# Servicio para registrar transacciones de forma segura

from django.db import transaction # transaction.atomic agrupa varias operaciones: o se hacen todas, o no se hace ninguna
from .models import Cuenta, Transaccion # Modelos que usa el servicio


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