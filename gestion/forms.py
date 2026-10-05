# gestion/forms.py
# Formulario para crear o editar un cliente

from django import forms  # forms es el módulo de formularios de Django
from django.contrib.auth.models import User  # Importa el modelo User para elegir el usuario de login del cliente
from .models import Cliente, Contacto, Cuenta, Moneda, Transaccion # Importa los modelos sobre los que se construyen los formularios
# Textos de las etiquetas, para que aparezcan bien escritos (con tildes)
ETIQUETAS_CLIENTE = {
    'usuario': 'Usuario de acceso',
    'nombre': 'Nombre',
    'email': 'Correo electrónico',
    'telefono': 'Teléfono',
}

# Textos de las etiquetas de cuenta
ETIQUETAS_CUENTA = {
    'cliente': 'Cliente',
    'moneda': 'Moneda',
    'numero': 'Número de cuenta',
    'activa': 'Cuenta activa',
}


# Mensajes de error propios para los campos de cuenta
MENSAJES_CUENTA = {
    'numero': {
        'unique': 'Ya existe una cuenta con ese número.',
    },
}

# ============================================================
# CLIENTES
# ============================================================

# Formulario para crear un cliente nuevo
class ClienteForm(forms.ModelForm):
    # Configuración del formulario
    class Meta:
        model = Cliente    # Modelo sobre el que se construye
        fields = ['usuario', 'nombre', 'email', 'telefono'] # Campos que se piden, en este orden
        labels = ETIQUETAS_CLIENTE # Etiquetas que se muestran junto a cada campo

    # Se ejecuta al crear el formulario; sirve para ajustar sus campos
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # Primero hace lo normal de Django
        self.fields['usuario'].queryset = User.objects.filter(cliente__isnull=True).order_by('username') # Solo muestra los usuarios que todavía no tienen un cliente asociado
        # Texto de ayuda bajo el campo
        self.fields['usuario'].help_text = (
            'Solo aparecen usuarios sin cliente. Se crean en el panel de administración.'
        )


# Formulario para editar un cliente existente (el usuario de acceso no se cambia)
class ClienteEdicionForm(forms.ModelForm):
    # Configuración del formulario
    class Meta:
        model = Cliente# Modelo sobre el que se construye
        fields = ['nombre', 'email', 'telefono'] # Campos que se pueden editar
        labels = ETIQUETAS_CLIENTE # Etiquetas que se muestran junto a cada campo

# ============================================================
# CUENTAS
# ============================================================

# Formulario para crear una cuenta nueva
class CuentaForm(forms.ModelForm):
    # Configuración del formulario
    class Meta:
        model = Cuenta  # Modelo sobre el que se construye
        fields = ['cliente', 'moneda', 'numero', 'activa']  # Campos que se piden, en este orden
        labels = ETIQUETAS_CUENTA  # Etiquetas que se muestran junto a cada campo
        error_messages = MENSAJES_CUENTA   # Mensaje propio cuando el número de cuenta ya existe (el de Django sale sin tilde)

    # Se ejecuta al crear el formulario; sirve para ajustar sus campos
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Primero hace lo normal de Django
        self.fields['cliente'].queryset = Cliente.objects.order_by('nombre')  # Ordena las listas desplegables para que sean fáciles de recorrer
        self.fields['moneda'].queryset = Moneda.objects.order_by('codigo')


# Formulario para editar una cuenta existente (cliente y moneda no se cambian)
class CuentaEdicionForm(forms.ModelForm):
    # Configuración del formulario
    class Meta:
        model = Cuenta  # Modelo sobre el que se construye
        fields = ['numero', 'activa']  # Campos que se pueden editar
        labels = ETIQUETAS_CUENTA  # Etiquetas que se muestran junto a cada campo
        error_messages = MENSAJES_CUENTA   # Mensaje propio cuando el número de cuenta ya existe


# ============================================================
# TRANSACCIONES
# ============================================================

# Texto con el que se muestra cada cuenta en las listas desplegables
def etiqueta_cuenta(cuenta):
    return f'{cuenta.numero} · {cuenta.cliente.nombre} ({cuenta.moneda.codigo})' # Ejemplo: 0004 · Carla Soto (CLP)


# Formulario para registrar un movimiento nuevo
class TransaccionForm(forms.ModelForm):
    # Configuración del formulario
    class Meta:
        model = Transaccion   # Modelo sobre el que se construye
        fields = ['tipo', 'cuenta_origen', 'cuenta_destino', 'monto', 'descripcion'] # Campos que se piden, en este orden
        labels = {  # Etiquetas que se muestran junto a cada campo
            'tipo': 'Tipo de movimiento',
            'cuenta_origen': 'Cuenta origen',
            'cuenta_destino': 'Cuenta destino',
            'monto': 'Monto',
            'descripcion': 'Descripción',
        }

        help_texts = {   # Texto de ayuda bajo el campo tipo
            'tipo': 'Depósito: solo cuenta destino. Retiro: solo cuenta origen. Transferencia: las dos.',
        }

    # Se ejecuta al crear el formulario; sirve para ajustar sus campos
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # Primero hace lo normal de Django
        # Solo se ofrecen cuentas activas, ordenadas por número
        # select_related trae el cliente y la moneda para mostrarlos sin consultas extra
        activas = Cuenta.objects.filter(activa=True).select_related('cliente', 'moneda').order_by('numero')
        for campo in ('cuenta_origen', 'cuenta_destino'): # Aplica lo mismo a las dos listas de cuentas
            self.fields[campo].queryset = activas  # Cuentas que se pueden elegir
            self.fields[campo].label_from_instance = etiqueta_cuenta  # Cómo se escribe cada cuenta en la lista


# Formulario de filtros del listado (se envía por GET, así que no lleva token CSRF)
class FiltroTransaccionForm(forms.Form):
    tipo = forms.ChoiceField( # Filtro por tipo; la primera opción vacía significa "todos"
        required=False,
        choices=[('', 'Todos')] + Transaccion.TIPOS,
        label='Tipo',
    )

    cuenta = forms.CharField(required=False, max_length=20, label='Número de cuenta') # Filtro por número de cuenta (origen o destino)
    desde = forms.DateField(required=False, label='Desde', widget=forms.DateInput(attrs={'type': 'date'})) # Filtro desde una fecha; type="date" muestra un selector de calendario
    hasta = forms.DateField(required=False, label='Hasta', widget=forms.DateInput(attrs={'type': 'date'})) # Filtro hasta una fecha


# ============================================================
# CONTACTOS
# ============================================================

# Formulario para agendar un contacto en la agenda de un cliente
class ContactoForm(forms.ModelForm):
    
    class Meta:# Configuración del formulario
        model = Contacto # Modelo sobre el que se construye
        fields = ['agendado', 'apodo'] # Campos que se piden; el dueño de la agenda no se pide porque ya se conoce
        labels = {   # Etiquetas que se muestran junto a cada campo
            'agendado': 'Cliente a agendar',
            'apodo': 'Apodo (opcional)',
        }

    # Se ejecuta al crear el formulario; recibe al cliente dueño de la agenda
    def __init__(self, *args, propietario, **kwargs):
        super().__init__(*args, **kwargs) # Primero hace lo normal de Django
        self.instance.propietario = propietario  # Deja al dueño de la agenda puesto en la ficha que se está creando
        ya_agendados = propietario.fichas_de_agenda.values('agendado') # Clientes que ya están en la agenda de este dueño
        self.fields['agendado'].queryset = ( # Solo se pueden agendar clientes distintos del dueño y que todavía no estén en su agenda
            Cliente.objects.exclude(pk=propietario.pk).exclude(pk__in=ya_agendados).order_by('nombre')
        )