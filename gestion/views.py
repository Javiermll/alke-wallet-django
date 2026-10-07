# gestion/views.py
# Vistas de la app gestion: clientes, cuentas y transacciones


from django.contrib import messages# messages permite dejar avisos que se muestran en la siguiente página
from django.contrib.messages.views import SuccessMessageMixin# SuccessMessageMixin agrega un aviso de éxito al crear o editar
from django.core.exceptions import ValidationError# ValidationError es el error que lanzan las reglas de validación
from django.db.models import Count, ProtectedError, Q # Count cuenta registros relacionados; ProtectedError aparece al borrar algo protegido; Q permite hacer filtros complejos
from django.shortcuts import get_object_or_404, redirect # get_object_or_404 busca un registro o responde 404; redirect envía a la persona a otra dirección
from django.shortcuts import redirect# redirect envía a la persona a otra dirección
from django.urls import reverse_lazy# reverse_lazy calcula una dirección a partir del nombre de la ruta
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, # Vistas genéricas basadas en clases que trae Django
)
from . import consultas# Consultas reutilizables de la etapa 4
from .forms import (   # Formularios de esta app
    ClienteForm, ClienteEdicionForm, CuentaForm, CuentaEdicionForm,
    TransaccionForm, FiltroTransaccionForm, ContactoForm, RegistroForm,
)
from .models import Cliente, Contacto, Cuenta, Moneda, Transaccion# Modelos de esta app
from .mixins import SoloPersonalMixin, PersonalOClienteMixin# Mixins que limitan cada pantalla según el rol de la persona
from .servicios import registrar_transaccion # Función que registra movimientos de forma segura
from django.utils.functional import cached_property# Para recordar un valor calculado dentro de la vista
from .alcance import limitar_a_cliente, movimientos_visibles# Funciones que limitan los datos al cliente de la sesión
from django.contrib.auth import login# login inicia la sesión de un usuario desde el código
from django.contrib.auth.views import PasswordChangeView# Pantalla ya hecha de Django para cambiar la contraseña (pide la actual y la nueva dos veces)

# ============================================================
# INICIO
# ============================================================

# Página de inicio: totales, últimos movimientos y enlaces rápidos
class InicioView(TemplateView):
    template_name = 'inicio.html' # Template que se muestra (Django lo busca en la carpeta templates/)

    # Agrega datos extra al contexto, que es el diccionario que recibe el template
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)  # Parte del contexto normal de la vista  
        usuario = self.request.user # Persona que hace la petición
        if usuario.is_staff:# El personal ve los totales de todo el sistema
            contexto['total_clientes'] = Cliente.objects.count()
            contexto['total_cuentas'] = Cuenta.objects.count()
            contexto['total_transacciones'] = Transaccion.objects.count()
        # Un cliente con sesión ve solo sus cuentas (con saldo) y la cantidad de sus movimientos
        elif hasattr(usuario, 'cliente'):
            contexto['mis_cuentas'] = consultas.cuentas_con_saldo().filter(cliente=usuario.cliente).select_related('moneda')
            contexto['total_transacciones'] = movimientos_visibles(usuario).count()
        # Los 5 movimientos más recientes que la persona puede ver (mismo filtro que los listados)
        # Un usuario sin cliente no ve datos: el template solo le muestra un aviso
        if usuario.is_staff or hasattr(usuario, 'cliente'):
            contexto['ultimos_movimientos'] = movimientos_visibles(usuario)[:5]
        return contexto # Devuelve el contexto completo


# ============================================================
# CLIENTES
# ============================================================

# Listado de todos los clientes
class ClienteListView(SoloPersonalMixin, ListView):
    model = Cliente# Modelo que se lista
    template_name = 'clientes/lista.html'# Template que se muestra
    context_object_name = 'clientes'# Nombre con el que el template recibe la lista
    # Define qué clientes se muestran y en qué orden
    def get_queryset(self):
        return Cliente.objects.annotate(num_cuentas=Count('cuentas')).order_by('nombre')# Agrega a cada cliente la cantidad de cuentas y los ordena por nombre


# Ficha de un cliente: sus datos, sus cuentas con saldo y sus contactos
class ClienteDetailView(PersonalOClienteMixin, DetailView):
    model = Cliente# Modelo del que se muestra un registro (el pk viene en la dirección)
    template_name = 'clientes/detalle.html'# Template que se muestra
    context_object_name = 'cliente'# Nombre con el que el template recibe el cliente
  
    # Agrega datos extra al contexto
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)# Parte del contexto normal de la vista
        contexto['cuentas'] = consultas.cuentas_con_saldo().filter(cliente=self.object)# Cuentas del cliente con su saldo, usando la consulta de la etapa 4
        contactos = list(self.object.fichas_de_agenda.select_related('agendado'))# Contactos que el cliente tiene agendados, con los datos del cliente agendado
        for ficha in contactos:  # A cada contacto se le suma su primera cuenta activa, para ofrecer el atajo de transferir
            ficha.cuenta_sugerida = ficha.agendado.cuentas.filter(activa=True).order_by('numero').first()
        contexto['contactos'] = contactos  # Entrega la lista de contactos al template
        return contexto  # Devuelve el contexto completo
    
    # Un cliente solo puede abrir su propia ficha; la ajena responde 404
    def get_queryset(self):
        return limitar_a_cliente(Cliente.objects.all(), self.request.user, 'pk')


# Formulario para crear un cliente
class ClienteCreateView(SoloPersonalMixin, SuccessMessageMixin, CreateView):
    form_class = ClienteForm# Formulario que se usa
    template_name = 'clientes/formulario.html'# Template que se muestra
    success_url = reverse_lazy('gestion:cliente_lista')# Dirección a la que se va después de guardar
    success_message = 'Cliente «%(nombre)s» creado correctamente.'# Aviso de éxito; %(nombre)s se reemplaza por el nombre escrito en el formulario


# Formulario para editar un cliente
class ClienteUpdateView(PersonalOClienteMixin, SuccessMessageMixin, UpdateView):
    model = Cliente # Modelo que se edita (el pk viene en la dirección)
    form_class = ClienteEdicionForm # Formulario que se usa
    template_name = 'clientes/formulario.html' # Template que se muestra (el mismo que para crear)
    success_message = 'Cliente «%(nombre)s» actualizado correctamente.' # Aviso de éxito

    # Dirección a la que se va después de guardar: la ficha del cliente
    def get_success_url(self):
        return reverse_lazy('gestion:cliente_detalle', kwargs={'pk': self.object.pk})
    
    # Un cliente solo puede abrir su propia ficha; la ajena responde 404
    def get_queryset(self):
        return limitar_a_cliente(Cliente.objects.all(), self.request.user, 'pk')


# Pantalla de confirmación y borrado de un cliente
class ClienteDeleteView(SoloPersonalMixin, DeleteView):
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
class CuentaListView(PersonalOClienteMixin, ListView):
    model = Cuenta # Modelo que se lista
    template_name = 'cuentas/lista.html' # Template que se muestra
    context_object_name = 'cuentas' # Nombre con el que el template recibe la lista

    # Define qué cuentas se muestran
    def get_queryset(self):
        # Usa la consulta: cada cuenta trae su saldo_calculado
        # select_related trae el cliente y la moneda en la misma consulta
        return limitar_a_cliente(consultas.cuentas_con_saldo().select_related('cliente', 'moneda'), self.request.user, 'cliente')


# Ficha de una cuenta: sus datos, su saldo y sus últimos movimientos
class CuentaDetailView(PersonalOClienteMixin, DetailView):
    model = Cuenta # Modelo del que se muestra un registro (el pk viene en la dirección)
    template_name = 'cuentas/detalle.html' # Template que se muestra
    context_object_name = 'cuenta' # Nombre con el que el template recibe la cuenta

    # Define de dónde sale la cuenta que se muestra
    def get_queryset(self):
        return limitar_a_cliente(consultas.cuentas_con_saldo().select_related('cliente', 'moneda'), self.request.user, 'cliente') # Misma consulta del listado, para que la cuenta traiga su saldo_calculado

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
class CuentaCreateView(SoloPersonalMixin, SuccessMessageMixin, CreateView):
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
class CuentaUpdateView(SoloPersonalMixin, SuccessMessageMixin, UpdateView):
    model = Cuenta # Modelo que se edita (el pk viene en la dirección)
    form_class = CuentaEdicionForm # Formulario que se usa
    template_name = 'cuentas/formulario.html'  # Template que se muestra (el mismo que para crear)
    success_message = 'Cuenta %(numero)s actualizada correctamente.' # Aviso de éxito

    # Dirección a la que se va después de guardar: la ficha de la cuenta
    def get_success_url(self):
        return reverse_lazy('gestion:cuenta_detalle', kwargs={'pk': self.object.pk})


# Pantalla de confirmación y borrado de una cuenta
class CuentaDeleteView(SoloPersonalMixin, DeleteView):
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

# ============================================================
# TRANSACCIONES
# ============================================================

# Listado de movimientos, con filtros y paginación
class TransaccionListView(PersonalOClienteMixin, ListView):
    model = Transaccion# Modelo que se lista
    template_name = 'transacciones/lista.html'# Template que se muestra
    context_object_name = 'transacciones' # Nombre con el que el template recibe la lista
    paginate_by = 10  # Cantidad de movimientos por página

    # Define qué movimientos se muestran
    def get_queryset(self):
        # movimientos_visibles ya deja solo los del cliente de la sesión (el personal ve todos)
        queryset = movimientos_visibles(self.request.user)  # Trae las cuentas y sus monedas en la misma consulta, para que el listado sea rápido
        self.filtro = FiltroTransaccionForm(self.request.GET)  # Formulario de filtros: lee lo que viene en la dirección (?tipo=retiro&cuenta=0004...)
        if self.filtro.is_valid(): # Solo se aplican los filtros si los datos son válidos (por ejemplo, fechas bien escritas)
            datos = self.filtro.cleaned_data # Datos ya limpios y convertidos por el formulario
            if datos['tipo']: # Filtro por tipo
                queryset = queryset.filter(tipo=datos['tipo'])
            if datos['cuenta']: # Filtro por cuenta: el número puede ser el del origen o el del destino
                queryset = queryset.filter(
                    Q(cuenta_origen__numero=datos['cuenta']) | Q(cuenta_destino__numero=datos['cuenta'])
                )
            if datos['desde']: # Filtro desde una fecha (se compara solo el día, en la hora de Santiago)
                queryset = queryset.filter(fecha__date__gte=datos['desde'])
            if datos['hasta']:  # Filtro hasta una fecha
                queryset = queryset.filter(fecha__date__lte=datos['hasta'])
        return queryset # Devuelve los movimientos ya filtrados

    # Agrega datos extra al contexto
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs) # Parte del contexto normal de la vista
        contexto['filtro'] = self.filtro # Entrega el formulario de filtros al template
        parametros = self.request.GET.copy()  # Copia los parámetros de la dirección y quita "page", para que los enlaces de paginación conserven los filtros
        parametros.pop('page', None)
        contexto['parametros'] = parametros.urlencode()

        return contexto  # Devuelve el contexto completo


# Ficha de un movimiento (solo lectura: el historial no se edita ni se borra)
class TransaccionDetailView(PersonalOClienteMixin, DetailView):
    model = Transaccion # Modelo del que se muestra un registro (el pk viene en la dirección)
    template_name = 'transacciones/detalle.html' # Template que se muestra
    context_object_name = 'transaccion'  # Nombre con el que el template recibe el movimiento

    def get_queryset(self): # Define de dónde sale el movimiento que se muestra
        # Solo los movimientos visibles para la persona; uno ajeno responde 404
        return movimientos_visibles(self.request.user).select_related(
            'cuenta_origen__cliente', 'cuenta_destino__cliente',
        )


# Formulario para registrar un movimiento nuevo
# Es un FormView porque no usa form.save(): guarda a través de registrar_transaccion
class TransaccionCreateView(PersonalOClienteMixin, FormView):
    form_class = TransaccionForm # Formulario que se usa
    template_name = 'transacciones/formulario.html' # Template que se muestra

    # Datos extra que recibe el formulario al crearse
    def get_form_kwargs(self):
        # Parte de los datos normales de la vista
        kwargs = super().get_form_kwargs()
        # El formulario necesita saber quién opera para limitar las cuentas
        kwargs['usuario'] = self.request.user
        # Devuelve los datos completos
        return kwargs

    # Valores que el formulario muestra ya elegidos al abrirse
    def get_initial(self):
        inicial = super().get_initial()# Parte de los valores normales de la vista
        for campo in ('tipo', 'cuenta_origen', 'cuenta_destino'):# Si la dirección trae ?tipo=...&cuenta_destino=..., el formulario se abre con esos valores elegidos
            valor = self.request.GET.get(campo)
            if valor:
                inicial[campo] = valor
       
        return inicial # Devuelve los valores iniciales

    def form_valid(self, form): # Se ejecuta cuando el formulario pasó las validaciones básicas
        datos = form.cleaned_data # Datos ya limpios del formulario
        try:
            # Registra el movimiento dentro de una operación atómica, con la cuenta origen bloqueada
            movimiento = registrar_transaccion(
                tipo=datos['tipo'],
                cuenta_origen=datos.get('cuenta_origen'),
                cuenta_destino=datos.get('cuenta_destino'),
                monto=datos['monto'],
                descripcion=datos.get('descripcion', ''),
            )
        except ValidationError as error:
            form.add_error(None, error) # Si la segunda revisión falla (por ejemplo, el saldo cambió), se muestra el error en el formulario
            return self.form_invalid(form)
        messages.success( # Si todo salió bien, deja un aviso de éxito
            self.request,
            f'Movimiento registrado: {movimiento.get_tipo_display()} de {movimiento.monto}.',
        )
        return redirect('gestion:transaccion_detalle', pk=movimiento.pk) # Va a la ficha del movimiento recién creado

# ============================================================
# CONTACTOS
# ============================================================

# Formulario para agendar un contacto en la agenda de un cliente
class ContactoCreateView(PersonalOClienteMixin, SuccessMessageMixin, CreateView):
    form_class = ContactoForm  # Formulario que se usa
    template_name = 'contactos/formulario.html' # Template que se muestra
    success_message = 'Contacto «%(agendado)s» agregado correctamente.'  # Aviso de éxito; %(agendado)s se reemplaza por el nombre del cliente agendado

    # Dueño de la agenda; cached_property lo calcula la primera vez que se usa y lo recuerda
    # (así se busca después de que el mixin comprueba el rol, no antes)
    @cached_property
    def propietario(self):
        # Un cliente solo puede tocar su propia agenda; la ajena responde 404
        return get_object_or_404(
            limitar_a_cliente(Cliente.objects.all(), self.request.user, 'pk'),
            pk=self.kwargs['pk'],
        )
    

    # Datos extra que recibe el formulario al crearse
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs() # Parte de los datos normales de la vista
        kwargs['propietario'] = self.propietario  # Le entrega al formulario el dueño de la agenda
        return kwargs  # Devuelve los datos completos

    # Agrega datos extra al contexto
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs) # Parte del contexto normal de la vista
        contexto['propietario'] = self.propietario # El template muestra de quién es la agenda
        return contexto  # Devuelve el contexto completo

    # Dirección a la que se va después de guardar: la ficha del dueño de la agenda
    def get_success_url(self):
        return reverse_lazy('gestion:cliente_detalle', kwargs={'pk': self.propietario.pk})


# Pantalla de confirmación y borrado de un contacto (se quita de la agenda; el cliente no se borra)
class ContactoDeleteView(PersonalOClienteMixin, DeleteView):
    template_name = 'contactos/confirmar_eliminar.html' # Template de confirmación
    context_object_name = 'contacto' # Nombre con el que el template recibe la ficha del contacto

    # Define de dónde sale la ficha que se borra
    def get_queryset(self):
        # Un cliente solo puede quitar fichas de su propia agenda
        return limitar_a_cliente(Contacto.objects.select_related('propietario', 'agendado'), self.request.user, 'propietario')
    # Dirección a la que se va después de borrar: la ficha del dueño de la agenda
    def get_success_url(self):
        return reverse_lazy('gestion:cliente_detalle', kwargs={'pk': self.object.propietario_id})

    # Se ejecuta cuando la persona confirma el borrado
    def form_valid(self, form):
        nombre = self.object.agendado.nombre # Guarda el nombre antes de borrar, para usarlo en el aviso
        respuesta = super().form_valid(form)  # Hace el borrado normal de Django
        messages.success(self.request, f'Contacto «{nombre}» quitado de la agenda.')  # Deja un aviso de éxito
        return respuesta # Devuelve la redirección a la ficha del dueño

# ============================================================
# REPORTE
# ============================================================

# Reporte general: movimientos por tipo, saldos por cliente y movimientos por mes
class ReporteView(SoloPersonalMixin, TemplateView):
    template_name = 'reporte.html' # Template que se muestra

    # Arma todos los datos del reporte reutilizando las consultas de gestion/consultas.py
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs) # Parte del contexto normal de la vista
        nombres_tipo = dict(Transaccion.TIPOS)  # Diccionario con los nombres legibles de los tipos: {'deposito': 'Depósito', ...}
        secciones = []  # Lista de secciones, una por moneda (no se pueden sumar monedas distintas)
        for moneda in Moneda.objects.order_by('codigo'):  # Recorre las monedas en orden de código
            resumen = consultas.resumen_por_tipo(moneda.codigo)   # Cantidad de movimientos y monto total por tipo, solo en esta moneda
            for fila in resumen: # Agrega a cada fila el nombre legible del tipo
                fila['tipo_nombre'] = nombres_tipo[fila['tipo']]
            saldos = consultas.saldo_por_cliente(moneda.codigo)   # Saldo total de cada cliente en esta moneda
            total_saldos = sum(fila['total'] for fila in saldos)  # Suma de los saldos de todos los clientes
            secciones.append({   # Guarda todo junto como una sección del reporte
                'moneda': moneda,
                'resumen': resumen,
                'saldos': saldos,
                'total_saldos': total_saldos,
            })
      
        contexto['secciones'] = secciones  # Entrega las secciones al template
        contexto['por_mes'] = consultas.movimientos_por_mes()  # Cantidad de movimientos de cada mes
        contexto['total_movimientos'] = Transaccion.objects.count() # Total de movimientos, para comprobar que la tabla por mes suma lo mismo
        return contexto # Devuelve el contexto completo

# ============================================================
# REGISTRO
# ============================================================

# Pantalla pública de registro: crea usuario, cliente y primera cuenta, e inicia la sesión
class RegistroView(FormView):
    form_class = RegistroForm# Formulario que se usa
    template_name = 'registration/registro.html'# Template que se muestra

    # Se ejecuta primero; quien ya tiene sesión no necesita registrarse
    def dispatch(self, request, *args, **kwargs):
        # Si ya hay sesión iniciada, se va al inicio
        if request.user.is_authenticated:
            return redirect('gestion:inicio')
        return super().dispatch(request, *args, **kwargs)# Si no, sigue el funcionamiento normal de la vista

    # Se ejecuta cuando los datos pasaron todas las validaciones
    def form_valid(self, form):
        usuario = form.save()# Guarda usuario, cliente y cuenta
        login(self.request, usuario)# Inicia la sesión de inmediato, para que no tenga que escribir de nuevo sus datos
        messages.success(self.request, '¡Bienvenido a Alke Wallet! Tu cuenta quedó creada.')# Aviso de bienvenida
        return redirect('gestion:inicio')# Va al inicio, donde ve su cuenta

# ============================================================
# PERFIL
# ============================================================

# Perfil de la persona con sesión: sus datos de acceso y, si es cliente, sus datos de cliente
class PerfilView(TemplateView):
    template_name = 'perfil.html'# Template que se muestra


# Cambio de contraseña de la persona con sesión
class CambiarClaveView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'registration/cambiar_clave.html'# Template que se muestra
    success_url = reverse_lazy('gestion:perfil')# Dirección a la que se va después de cambiarla: el perfil
    success_message = 'Tu contraseña se cambió correctamente.'# Aviso de éxito