# gestion/forms.py
# Formulario para crear o editar un cliente

from django import forms  # forms es el módulo de formularios de Django
from django.contrib.auth.models import User  # Importa el modelo User para elegir el usuario de login del cliente
from .models import Cliente, Cuenta, Moneda # Importa los modelos sobre los que se construyen los formularios
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