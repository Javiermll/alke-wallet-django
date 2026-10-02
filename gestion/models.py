#gestion/models.py

from django.db import models # Importa las herramientas para definir modelos (tablas)
from django.contrib.auth.models import User # Importa el modelo User que trae Django para el login
from django.core.exceptions import ValidationError  # Importa el error que usamos para rechazar datos inválidos
from django.core.validators import MinValueValidator   # Importa un validador que exige un valor mínimo en un campo
from django.db.models import Sum   # Importa Sum, que suma los valores de una columna
from decimal import Decimal  # Importa Decimal, que guarda montos de dinero sin errores de redondeo


# ---------------------------------------------------------
# MONEDA: tabla de referencia (CLP, USD, etc.)
# ---------------------------------------------------------
class Moneda(models.Model):
    codigo = models.CharField(max_length=3, unique=True)  # Código de 3 letras; unique=True impide repetir el mismo código
    nombre = models.CharField(max_length=50)  # Nombre completo de la moneda
    simbolo = models.CharField(max_length=5)  # Símbolo para mostrar, por ejemplo $ o US$

    # Nombres legibles que se muestran en el panel de administración
    class Meta:
        verbose_name = 'moneda'
        verbose_name_plural = 'monedas'

    
    # Al imprimir una moneda se muestra su código
    def __str__(self):
        return self.codigo


# ---------------------------------------------------------
# CLIENTE: los datos de negocio de cada persona
# ---------------------------------------------------------
class Cliente(models.Model):
    # Relación 1:1 con User: un usuario de login tiene un solo cliente, y al revés
    # on_delete=CASCADE: si se borra el usuario, se borra también su cliente
    # related_name='cliente' permite escribir usuario.cliente para llegar a él
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    nombre = models.CharField(max_length=100)  # Nombre de hasta 100 caracteres
    email = models.EmailField(unique=True)  # Correo con formato validado; unique=True impide dos clientes con el mismo email
    telefono = models.CharField(max_length=20, blank=True, null=True) # Teléfono opcional: blank=True permite dejarlo vacío en formularios | # null=True permite guardar NULL en la base de datos
    fecha_registro = models.DateTimeField(auto_now_add=True)  # Fecha y hora que se llenan solas cuando se crea el cliente

    # Relación N:M de Cliente con Cliente, pasando por la ficha "Contacto"
    # 'self' significa "el mismo modelo"
    # through='Contacto' le dice a Django que la tabla intermedia la definimos nosotros
    # through_fields indica cuál campo de Contacto es "quien agenda" y cuál "a quién agenda"
    # symmetrical=False: si Ana agenda a Luis, Luis NO queda agendado por Ana automáticamente
    # related_name='agendado_por' permite preguntar quién tiene agendado a un cliente
    contactos = models.ManyToManyField(
        'self',
        through='Contacto',
        through_fields=('propietario', 'agendado'),
        symmetrical=False,
        related_name='agendado_por',
    )

    # Nombres legibles que se muestran en el panel de administración
    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'

    # Texto que se muestra cuando Django imprime un cliente (admin, shell, listas)
    def __str__(self):
        return self.nombre


# ---------------------------------------------------------
# CONTACTO: la ficha de agenda entre dos clientes
# ---------------------------------------------------------
class Contacto(models.Model):
    # Cliente que guarda el contacto (el dueño de la agenda)
    # related_name='fichas_de_agenda' permite escribir cliente.fichas_de_agenda.all()
    propietario = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='fichas_de_agenda',
    )

    # Cliente que fue guardado como contacto
    # related_name='fichas_donde_aparece' permite ver en qué agendas está un cliente
    agendado = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='fichas_donde_aparece',
    )

    apodo = models.CharField(max_length=50, blank=True)  # Apodo opcional para reconocer rápido al contacto
    fecha_agregado = models.DateTimeField(auto_now_add=True)  # Fecha y hora que se llenan solas cuando se agrega el contacto

    # Configuración extra del modelo
    class Meta:
        # Nombres legibles que se muestran en el panel de administración
        verbose_name = 'contacto'
        verbose_name_plural = 'contactos'
        # Reglas que la propia base de datos hace cumplir
        constraints = [
            # No se puede agendar dos veces a la misma persona
            models.UniqueConstraint(
                fields=['propietario', 'agendado'],
                name='contacto_unico',
            ),
            # Nadie puede agendarse a sí mismo
            models.CheckConstraint(
                condition=~models.Q(propietario=models.F('agendado')),
                name='no_agendarse_a_si_mismo',
            ),
        ]

    # Misma regla de no agendarse a sí mismo, pero con mensaje claro en formularios
    def clean(self):
        # Usamos los id porque los campos pueden estar vacíos mientras se valida
        if self.propietario_id is not None and self.propietario_id == self.agendado_id:
            raise ValidationError('Un cliente no puede agendarse a sí mismo.')

    # Al imprimir la ficha se muestra quién agenda a quién
    def __str__(self):
        return f'{self.propietario} -> {self.agendado}'


# ---------------------------------------------------------
# CUENTA: donde "vive" el dinero de un cliente
# ---------------------------------------------------------
class Cuenta(models.Model):
    # Relación N:1: un cliente puede tener muchas cuentas
    # on_delete=CASCADE: si se borra el cliente, se borran sus cuentas
    # related_name='cuentas' permite escribir cliente.cuentas.all()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='cuentas')

    # Relación N:1: cada cuenta tiene una moneda
    # on_delete=PROTECT: Django no deja borrar una moneda que tenga cuentas
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT, related_name='cuentas')
    numero = models.CharField(max_length=20, unique=True)  # Número de cuenta, único en todo el sistema
    activa = models.BooleanField(default=True)  # Indica si la cuenta está en uso (True) o desactivada (False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha y hora que se llenan solas al crear la cuenta

    # Nombres legibles que se muestran en el panel de administración
    class Meta:
        verbose_name = 'cuenta'
        verbose_name_plural = 'cuentas'

    # El saldo NO es una columna: se calcula cada vez que se pide
    # @property permite usarlo como un dato más: cuenta.saldo (sin paréntesis)
    @property
    def saldo(self):
        # Suma todo el dinero que ha llegado a esta cuenta
        # Sum devuelve None si no hay transacciones, por eso el "or Decimal('0.00')"
        entradas = self.transacciones_recibidas.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        salidas = self.transacciones_enviadas.aggregate(total=Sum('monto'))['total'] or Decimal('0.00') # Suma todo el dinero que ha salido de esta cuenta
        return entradas - salidas   # El saldo es lo que entró menos lo que salió

    # Al imprimir una cuenta se muestra su número y la moneda
    def __str__(self):
        return f'{self.numero} ({self.moneda.codigo})'


# ---------------------------------------------------------
# TRANSACCION: un movimiento de dinero
# ---------------------------------------------------------
class Transaccion(models.Model):
    # Lista de opciones válidas para el tipo: (valor guardado, texto visible)
    TIPOS = [
        ('deposito', 'Depósito'),
        ('retiro', 'Retiro'),
        ('transferencia', 'Transferencia'),
    ]

    tipo = models.CharField(max_length=15, choices=TIPOS)  # Tipo de movimiento; choices limita el campo a las opciones de arriba

    # Cuenta de la que sale el dinero (vacía en un depósito)
    # on_delete=PROTECT: no se puede borrar una cuenta que tenga movimientos
    # related_name='transacciones_enviadas' permite cuenta.transacciones_enviadas.all()
    cuenta_origen = models.ForeignKey(
        Cuenta,
        on_delete=models.PROTECT,
        related_name='transacciones_enviadas',
        null=True,
        blank=True,
    )

    # Cuenta a la que llega el dinero (vacía en un retiro)
    cuenta_destino = models.ForeignKey(
        Cuenta,
        on_delete=models.PROTECT,
        related_name='transacciones_recibidas',
        null=True,
        blank=True,
    )

    monto = models.DecimalField(
        max_digits=14,     # Monto con hasta 14 dígitos en total y 2 decimales
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],  # MinValueValidator: en formularios y admin no acepta cero ni negativos
    )

    descripcion = models.CharField(max_length=200, blank=True) # Texto libre opcional para anotar el motivo
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha y hora que se llenan solas al crear la transacción

    # Configuración extra del modelo
    class Meta:
        # Nombres legibles que se muestran en el panel de administración
        verbose_name = 'transacción'
        verbose_name_plural = 'transacciones'
        # El signo menos ordena de la más nueva a la más antigua
        ordering = ['-fecha']
        # Regla que la base de datos hace cumplir aunque se guarde desde la shell.
        # En simples palabras, no permite montos negativos.
        constraints = [
            models.CheckConstraint(
                condition=models.Q(monto__gt=0),
                name='monto_positivo',
            ),
        ]

    # Reglas que combinan varios campos; Django las ejecuta al validar formularios y el admin
    def clean(self):
        # Depósito: solo entra dinero, así que necesita destino y no origen
        if self.tipo == 'deposito':
            if self.cuenta_destino is None:
                raise ValidationError('Un depósito necesita una cuenta destino.')
            if self.cuenta_origen is not None:
                raise ValidationError('Un depósito no debe tener cuenta origen.')

        # Retiro: solo sale dinero, así que necesita origen y no destino
        if self.tipo == 'retiro':
            if self.cuenta_origen is None:
                raise ValidationError('Un retiro necesita una cuenta origen.')
            if self.cuenta_destino is not None:
                raise ValidationError('Un retiro no debe tener cuenta destino.')

        # Transferencia: necesita las dos cuentas
        if self.tipo == 'transferencia':
            if self.cuenta_origen is None or self.cuenta_destino is None:
                raise ValidationError('Una transferencia necesita cuenta origen y destino.')
            # No se puede transferir de una cuenta a sí misma
            if self.cuenta_origen == self.cuenta_destino:
                raise ValidationError('La cuenta origen y la destino deben ser distintas.')
            # Solo se transfiere entre cuentas de la misma moneda (sin conversión)
            if self.cuenta_origen.moneda != self.cuenta_destino.moneda:
                raise ValidationError('Las cuentas deben tener la misma moneda.')

    # Al imprimir una transacción se muestra el tipo y el monto
    def __str__(self):
        return f'{self.get_tipo_display()} de {self.monto}'
