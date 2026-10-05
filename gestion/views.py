# gestion/views.py
# Vistas de la app gestion: clientes, cuentas y transacciones


from django.contrib import messages# messages permite dejar avisos que se muestran en la siguiente página
from django.contrib.messages.views import SuccessMessageMixin# SuccessMessageMixin agrega un aviso de éxito al crear o editar
from django.db.models import Count, ProtectedError, Q # Count cuenta registros relacionados; ProtectedError aparece al borrar algo protegido; Q permite hacer filtros complejos
from django.shortcuts import redirect# redirect envía a la persona a otra dirección
from django.urls import reverse_lazy# reverse_lazy calcula una dirección a partir del nombre de la ruta
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView,# Vistas genéricas basadas en clases que trae Django
)
from . import consultas# Consultas reutilizables de la etapa 4

from .forms import ClienteForm, ClienteEdicionForm, CuentaForm, CuentaEdicionForm # Formularios de esta app
from .models import Cliente, Cuenta, Transaccion# Modelos de esta app


# ============================================================
# INICIO
# ============================================================

# Página de inicio: muestra el total de clientes, cuentas y movimientos
class InicioView(TemplateView):
    template_name = 'inicio.html'# Template que se muestra (Django lo busca en la carpeta templates/)
    def get_context_data(self, **kwargs):  # Agrega datos extra al contexto, que es el diccionario que recibe el template
        contexto = super().get_context_data(**kwargs)# Parte del contexto normal de la vista
        contexto['total_clientes'] = Cliente.objects.count()# Agrega los tres totales
        contexto['total_cuentas'] = Cuenta.objects.count()
        contexto['total_transacciones'] = Transaccion.objects.count()
        return contexto# Devuelve el contexto completo


# ============================================================
# CLIENTES
# ============================================================

# Listado de todos los clientes
class ClienteListView(ListView):
    model = Cliente# Modelo que se lista
    template_name = 'clientes/lista.html'# Template que se muestra
    context_object_name = 'clientes'# Nombre con el que el template recibe la lista
    # Define qué clientes se muestran y en qué orden
    def get_queryset(self):
        return Cliente.objects.annotate(num_cuentas=Count('cuentas')).order_by('nombre')# Agrega a cada cliente la cantidad de cuentas y los ordena por nombre


# Ficha de un cliente: sus datos, sus cuentas con saldo y sus contactos
class ClienteDetailView(DetailView):
    model = Cliente# Modelo del que se muestra un registro (el pk viene en la dirección)
    template_name = 'clientes/detalle.html'# Template que se muestra
    context_object_name = 'cliente'# Nombre con el que el template recibe el cliente
  
    def get_context_data(self, **kwargs):  # Agrega datos extra al contexto
        contexto = super().get_context_data(**kwargs)# Parte del contexto normal de la vista
        contexto['cuentas'] = consultas.cuentas_con_saldo().filter(cliente=self.object)# Cuentas del cliente con su saldo, usando la consulta de la etapa 4
        contexto['contactos'] = self.object.fichas_de_agenda.select_related('agendado')# Contactos que el cliente tiene agendados, con los datos del cliente agendado
        return contexto# Devuelve el contexto completo


# Formulario para crear un cliente
class ClienteCreateView(SuccessMessageMixin, CreateView):
    form_class = ClienteForm# Formulario que se usa
    template_name = 'clientes/formulario.html'# Template que se muestra
    success_url = reverse_lazy('gestion:cliente_lista')# Dirección a la que se va después de guardar
    success_message = 'Cliente «%(nombre)s» creado correctamente.'# Aviso de éxito; %(nombre)s se reemplaza por el nombre escrito en el formulario


# Formulario para editar un cliente
class ClienteUpdateView(SuccessMessageMixin, UpdateView):
    model = Cliente # Modelo que se edita (el pk viene en la dirección)
    form_class = ClienteEdicionForm # Formulario que se usa
    template_name = 'clientes/formulario.html' # Template que se muestra (el mismo que para crear)
    success_message = 'Cliente «%(nombre)s» actualizado correctamente.' # Aviso de éxito

    # Dirección a la que se va después de guardar: la ficha del cliente
    def get_success_url(self):
        return reverse_lazy('gestion:cliente_detalle', kwargs={'pk': self.object.pk})


# Pantalla de confirmación y borrado de un cliente
class ClienteDeleteView(DeleteView):
    model = Cliente # Modelo que se borra (el pk viene en la dirección)
    template_name = 'clientes/confirmar_eliminar.html' # Template de confirmación
    context_object_name = 'cliente'  # Nombre con el que el template recibe el cliente
    success_url = reverse_lazy('gestion:cliente_lista')  # Dirección a la que se va después de borrar

    # Se ejecuta cuando la persona confirma el borrado
    def form_valid(self, form):
        nombre = self.object.nombre # Guarda el nombre antes de borrar, para usarlo en el aviso
        try:
            respuesta = super().form_valid(form) # Intenta el borrado normal de Django
        except ProtectedError:
            messages.error( # Si alguna cuenta del cliente tiene movimientos, Django lo impide
                self.request,
                f'No se puede eliminar a {nombre}: sus cuentas tienen movimientos registrados.',
            )
            return redirect('gestion:cliente_detalle', pk=self.object.pk)  # Vuelve a la ficha del cliente, donde se muestra el aviso
        messages.success(self.request, f'Cliente «{nombre}» eliminado correctamente.')  # Si se borró bien, deja un aviso de éxito
        return respuesta  # Devuelve la redirección al listado

# ============================================================
# CUENTAS
# ============================================================

# Listado de todas las cuentas, con su saldo
class CuentaListView(ListView):
    model = Cuenta # Modelo que se lista
    template_name = 'cuentas/lista.html' # Template que se muestra
    context_object_name = 'cuentas' # Nombre con el que el template recibe la lista

    # Define qué cuentas se muestran
    def get_queryset(self):
        # Usa la consulta: cada cuenta trae su saldo_calculado
        # select_related trae el cliente y la moneda en la misma consulta
        return consultas.cuentas_con_saldo().select_related('cliente', 'moneda')


# Ficha de una cuenta: sus datos, su saldo y sus últimos movimientos
class CuentaDetailView(DetailView):
    model = Cuenta # Modelo del que se muestra un registro (el pk viene en la dirección)
    template_name = 'cuentas/detalle.html' # Template que se muestra
    context_object_name = 'cuenta' # Nombre con el que el template recibe la cuenta

    # Define de dónde sale la cuenta que se muestra
    def get_queryset(self):
        return consultas.cuentas_con_saldo().select_related('cliente', 'moneda') # Misma consulta del listado, para que la cuenta traiga su saldo_calculado

    # Agrega datos extra al contexto
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs) # Parte del contexto normal de la vista
        # Movimientos en los que la cuenta es origen o destino (el modelo ya los ordena del más nuevo)
        movimientos = Transaccion.objects.filter(
            Q(cuenta_origen=self.object) | Q(cuenta_destino=self.object)
        )
        contexto['movimientos'] = movimientos[:15] # Solo se muestran los 15 más recientes
        # Total de movimientos de la cuenta, para avisar si hay más de los que se muestran
        contexto['total_movimientos'] = movimientos.count()
        return contexto # Devuelve el contexto completo


# Formulario para crear una cuenta
class CuentaCreateView(SuccessMessageMixin, CreateView):
    form_class = CuentaForm # Formulario que se usa
    template_name = 'cuentas/formulario.html' # Template que se muestra
    success_message = 'Cuenta %(numero)s creada correctamente.' # Aviso de éxito; %(numero)s se reemplaza por el número escrito en el formulario

    # Valores que el formulario muestra ya escritos al abrirse
    def get_initial(self):
        inicial = super().get_initial() # Parte de los valores normales de la vista
        numeros = [int(n) for n in Cuenta.objects.values_list('numero', flat=True) if n.isdigit()] # Propone el siguiente número de cuenta: el mayor número que exista, más uno, con 4 dígitos
        inicial['numero'] = f'{max(numeros, default=0) + 1:04d}'
        cliente = self.request.GET.get('cliente') # Si la dirección trae ?cliente=3, deja ese cliente elegido
        if cliente:
            inicial['cliente'] = cliente
        return inicial # Devuelve los valores iniciales

    # Dirección a la que se va después de guardar: la ficha de la cuenta nueva
    def get_success_url(self):
        return reverse_lazy('gestion:cuenta_detalle', kwargs={'pk': self.object.pk})


# Formulario para editar una cuenta
class CuentaUpdateView(SuccessMessageMixin, UpdateView):
    model = Cuenta # Modelo que se edita (el pk viene en la dirección)
    form_class = CuentaEdicionForm # Formulario que se usa
    template_name = 'cuentas/formulario.html'  # Template que se muestra (el mismo que para crear)
    success_message = 'Cuenta %(numero)s actualizada correctamente.' # Aviso de éxito

    # Dirección a la que se va después de guardar: la ficha de la cuenta
    def get_success_url(self):
        return reverse_lazy('gestion:cuenta_detalle', kwargs={'pk': self.object.pk})


# Pantalla de confirmación y borrado de una cuenta
class CuentaDeleteView(DeleteView):
    model = Cuenta # Modelo que se borra (el pk viene en la dirección)
    template_name = 'cuentas/confirmar_eliminar.html' # Template de confirmación
    context_object_name = 'cuenta' # Nombre con el que el template recibe la cuenta
    success_url = reverse_lazy('gestion:cuenta_lista') # Dirección a la que se va después de borrar

    # Se ejecuta cuando la persona confirma el borrado
    def form_valid(self, form):
        numero = self.object.numero # Guarda el número antes de borrar, para usarlo en el aviso
        try:
            respuesta = super().form_valid(form) # Intenta el borrado normal de Django
        except ProtectedError:
            messages.error( # Si la cuenta tiene movimientos, Django lo impide
                self.request,
                f'No se puede eliminar la cuenta {numero}: tiene movimientos registrados. '
                'Puedes desactivarla desde Editar.',
            )
            return redirect('gestion:cuenta_detalle', pk=self.object.pk) # Vuelve a la ficha de la cuenta, donde se muestra el aviso
        messages.success(self.request, f'Cuenta {numero} eliminada correctamente.') # Si se borró bien, deja un aviso de éxito
        return respuesta # Devuelve la redirección al listado