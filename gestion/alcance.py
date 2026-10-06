# gestrion/alcance.py
# Funciones que limitan el alcance de las consultas según el usuario que hace la petición

from django.db.models import Q # Q permite combinar condiciones con "o"
from .models import Cuenta, Transaccion # Modelos que se consultan


# Deja en la consulta solo los registros del cliente de la sesión; el personal ve todo
# campo es la ruta desde el modelo hasta el cliente dueño: 'pk' en Cliente, 'cliente' en Cuenta, 'propietario' en Contacto
def limitar_a_cliente(queryset, usuario, campo):
    if usuario.is_staff:# El personal no tiene límites
        return queryset
    # Un cliente solo ve los registros que apuntan a su propio Cliente
    # Se compara con el número (pk) del cliente, que sirve tanto para 'pk' como para una relación como 'cliente'
    return queryset.filter(**{campo: usuario.cliente.pk})


# Movimientos que puede ver la persona: el personal ve todos; un cliente, los de sus cuentas
def movimientos_visibles(usuario):
    # Trae las cuentas y sus monedas en la misma consulta, para que las pantallas sean rápidas
    movimientos = Transaccion.objects.select_related('cuenta_origen__moneda', 'cuenta_destino__moneda')
    if usuario.is_staff:# El personal ve todos los movimientos
        return movimientos
    # Un cliente ve los movimientos donde alguna de sus cuentas es el origen o el destino
    return movimientos.filter(
        Q(cuenta_origen__cliente=usuario.cliente) | Q(cuenta_destino__cliente=usuario.cliente)
    )


# Cuentas desde las que la persona puede sacar dinero (siempre activas)
def cuentas_de_origen(usuario):
    # Solo las cuentas activas, con cliente y moneda traídos en la misma consulta
    cuentas = Cuenta.objects.filter(activa=True).select_related('cliente', 'moneda').order_by('numero')
    # El personal puede operar con cualquier cuenta activa
    if usuario.is_staff:
        return cuentas
    # Un cliente solo puede sacar dinero de sus propias cuentas
    return cuentas.filter(cliente=usuario.cliente)


# Cuentas que la persona puede recibir como destino (siempre activas)
def cuentas_de_destino(usuario):
    # Solo las cuentas activas, con cliente y moneda traídos en la misma consulta
    cuentas = Cuenta.objects.filter(activa=True).select_related('cliente', 'moneda').order_by('numero')
    # El personal puede usar cualquier cuenta activa
    if usuario.is_staff:
        return cuentas
    # Un cliente puede enviar a sus propias cuentas o a las de los clientes que tiene agendados
    agendados = usuario.cliente.fichas_de_agenda.values('agendado')
    return cuentas.filter(Q(cliente=usuario.cliente) | Q(cliente__in=agendados))