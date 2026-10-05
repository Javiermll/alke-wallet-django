# gestion/views.py

# TemplateView es la vista más simple: muestra un template
from django.views.generic import TemplateView

# Importa los modelos para contar los registros de la página de inicio
from .models import Cliente, Cuenta, Transaccion


# Página de inicio: muestra el total de clientes, cuentas y movimientos
class InicioView(TemplateView):
    # Template que se muestra (Django lo busca en la carpeta templates/)
    template_name = 'inicio.html'

    # Agrega datos extra al contexto, que es el diccionario que recibe el template
    def get_context_data(self, **kwargs):
        # Parte del contexto normal de la vista
        contexto = super().get_context_data(**kwargs)
        # Agrega los tres totales
        contexto['total_clientes'] = Cliente.objects.count()
        contexto['total_cuentas'] = Cuenta.objects.count()
        contexto['total_transacciones'] = Transaccion.objects.count()
        # Devuelve el contexto completo
        return contexto