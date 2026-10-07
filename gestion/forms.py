# gestion/forms.py
# Formulario para crear o editar un cliente

from django import forms  # forms es el módulo de formularios de Django
from django.contrib.auth.models import User  # Importa el modelo User para elegir el usuario de login del cliente
from django.contrib.auth.forms import UserCreationForm# Formulario ya hecho de Django para crear un usuario con contraseña repetida y validada
from django.db import transaction# atomic agrupa operaciones: o se hacen todas o ninguna
from .models import Cliente, Contacto, Cuenta, Moneda, Transaccion # Importa los modelos sobre los que se construyen los formularios
from .servicios import crear_cliente_con_cuenta
from .alcance import cuentas_de_origen, cuentas_de_destino# Listas de cuentas según quién opera


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

    # Se ejecuta al crear el formulario; recibe a la persona que lo usa para limitar las cuentas
    def __init__(self, *args, usuario, **kwargs):
        super().__init__(*args, **kwargs)# Primero hace lo normal de Django
        self.usuario = usuario# Guarda a la persona para usarla después en clean()
        self.fields['cuenta_origen'].queryset = cuentas_de_origen(usuario)# Cada lista ofrece solo las cuentas que esa persona puede usar (ver alcance.py)
        self.fields['cuenta_destino'].queryset = cuentas_de_destino(usuario)
        
        for campo in ('cuenta_origen', 'cuenta_destino'):# Aplica lo mismo a las dos listas de cuentas
            self.fields[campo].label_from_instance = etiqueta_cuenta# Cómo se escribe cada cuenta en la lista
            self.fields[campo].empty_label = 'Ninguna'# Texto de la opción vacía, en español (una cuenta puede no aplicar según el tipo)
        
        self.fields['tipo'].choices = [('', 'Selecciona un tipo')] + Transaccion.TIPOS # Texto de la opción vacía del tipo, en español

    # Validación que mira varios campos a la vez
    def clean(self):
        datos = super().clean()# Datos ya revisados campo por campo
        # Regla extra solo para clientes: un depósito debe ir a una cuenta propia
        # (la lista de destino incluye cuentas de contactos, pero solo para transferir)
        if not self.usuario.is_staff and datos.get('tipo') == 'deposito':
            destino = datos.get('cuenta_destino')
            if destino is not None and destino.cliente_id != self.usuario.cliente.pk:
                self.add_error('cuenta_destino', 'Un depósito solo puede ir a una de tus cuentas.')
        return datos # Devuelve los datos

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

# ============================================================
# REGISTRO
# ============================================================

# Formulario público para que una persona cree su usuario, su ficha de cliente y su primera cuenta
class RegistroForm(UserCreationForm):
    nombre = forms.CharField(max_length=100, label='Nombre completo')# Datos del cliente que se piden además del usuario y la contraseña
    email = forms.EmailField(label='Correo electrónico')
    telefono = forms.CharField(max_length=20, required=False, label='Teléfono (opcional)')
    # Moneda de la primera cuenta; la opción vacía obliga a elegir una
    moneda = forms.ModelChoiceField(
        queryset=Moneda.objects.order_by('codigo'),
        empty_label='Selecciona una moneda',
        label='Moneda de tu primera cuenta',
    )

    # Configuración del formulario
    class Meta(UserCreationForm.Meta):
        fields = ('username',) # Del usuario solo se pide el nombre de usuario; las contraseñas las agrega UserCreationForm
    field_order = ['username', 'nombre', 'email', 'telefono', 'moneda', 'password1', 'password2']# Orden en que se muestran los campos

    # Revisa que el correo no esté usado por otro cliente
    def clean_email(self):
        email = self.cleaned_data['email'].lower()# Correo escrito, en minúsculas para comparar sin importar mayúsculas
        # Cliente.email es único; se avisa aquí con un mensaje claro en vez de fallar al guardar
        if Cliente.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe un cliente con ese correo.')
        return email# Devuelve el correo limpio

    # Guarda el usuario, el cliente y la cuenta como una sola operación
    def save(self, commit=True):
        # atomic: si algo falla, no queda un usuario suelto sin cliente
        with transaction.atomic():
            # Crea el usuario normal (nunca del personal) con su contraseña ya cifrada
            usuario = super().save()
            # Crea el cliente y su primera cuenta
            crear_cliente_con_cuenta(
                usuario=usuario,
                nombre=self.cleaned_data['nombre'],
                email=self.cleaned_data['email'],
                telefono=self.cleaned_data['telefono'],
                moneda=self.cleaned_data['moneda'],
            )
        return usuario# Devuelve el usuario creado