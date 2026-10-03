# gestion/admin.py

from django.contrib import admin  # Importa el módulo del panel de administración de Django
from django.db.models import Count  # Count permite contar registros relacionados
from .models import Moneda, Cliente, Contacto, Cuenta, Transaccion  # Importa nuestros cinco modelos
from . import consultas  # Importa el módulo con las consultas (usaremos cuentas_con_saldo)


# ======================================================
# TABLAS ANIDADAS: se muestran dentro de la ficha del cliente
# ============================================================

# Las cuentas del cliente, en una tabla dentro de su ficha
class CuentaInline(admin.TabularInline):
    model = Cuenta   # Modelo que se muestra en la tabla anidada
    fields = ('numero', 'moneda', 'activa')   # Campos que se muestran por cada cuenta
    extra = 0     # Filas vacías extra para agregar cuentas nuevas (0 = ninguna)
    show_change_link = True   # Muestra un enlace para abrir la cuenta completa


# Los contactos que el cliente tiene agendados, en una tabla dentro de su ficha
class ContactoInline(admin.TabularInline):
    model = Contacto    # Modelo que se muestra en la tabla anidada
    fk_name = 'propietario'   # Contacto tiene dos claves hacia Cliente; fk_name dice cuál une con esta ficha
    fields = ('agendado', 'apodo')   # Campos que se muestran por cada contacto
    extra = 0   # Filas vacías extra para agregar contactos nuevos (0 = ninguna)


# ============================================================
# MODELOS REGISTRADOS EN EL PANEL
# ============================================================

# Registra Moneda en el panel con la configuración de esta clase
@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'simbolo')   # Columnas que se muestran en el listado
    search_fields = ('codigo', 'nombre')   # Campos donde busca la caja de búsqueda


# Registra Cliente en el panel
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'cantidad_de_cuentas')  # Columnas del listado; cantidad_de_cuentas es un método definido más abajo
    search_fields = ('nombre', 'email', 'usuario__username')  # La búsqueda también mira el nombre de usuario de login (relación 1:1)
    readonly_fields = ('fecha_registro',)   # La fecha de registro se llena sola, así que solo se muestra y no se edita
    inlines = [CuentaInline, ContactoInline]  # Dentro de la ficha del cliente aparecen sus cuentas y sus contactos

    # Define qué registros trae el listado
    def get_queryset(self, request):
        queryset = super().get_queryset(request)  # Parte de la consulta normal del panel
        return queryset.annotate(num_cuentas=Count('cuentas'))  # Agrega a cada cliente la columna calculada num_cuentas

    # Columna calculada del listado; ordering permite ordenar haciendo clic en su título
    @admin.display(description='Cuentas', ordering='num_cuentas')
    def cantidad_de_cuentas(self, obj):
        return obj.num_cuentas  # Devuelve el valor calculado en get_queryset


# Registra Cuenta en el panel
@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'moneda', 'saldo_actual', 'activa', 'fecha_creacion')   # Columnas del listado; saldo_actual es un método definido más abajo
    list_filter = ('moneda', 'activa')  # Filtros laterales por moneda y por estado
    search_fields = ('numero', 'cliente__nombre', 'cliente__email')  # La búsqueda mira el número de cuenta y los datos del dueño
    readonly_fields = ('fecha_creacion', 'saldo_actual')   # Estos dos campos se muestran pero no se editan

    # Define qué registros trae el listado
    def get_queryset(self, request):
        # Usa la consulta de la etapa 4, que calcula el saldo de todas las cuentas de una vez
        # select_related trae el cliente y la moneda en la misma consulta
        return consultas.cuentas_con_saldo().select_related('cliente', 'moneda')

    # Columna del saldo; ordering permite ordenar haciendo clic en su título
    @admin.display(description='Saldo', ordering='saldo_calculado')
    def saldo_actual(self, obj):
        return getattr(obj, 'saldo_calculado', '-')   # Una cuenta nueva todavía no tiene el saldo calculado, así que se muestra un guion


# Registra Transaccion en el panel
@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'cuenta_origen', 'cuenta_destino', 'monto', 'descripcion', 'fecha')  # Columnas del listado
    list_filter = ('tipo',)  # Filtro lateral por tipo de movimiento
    search_fields = ('descripcion', 'cuenta_origen__numero', 'cuenta_destino__numero')  # La búsqueda mira la descripción y los números de las dos cuentas
    date_hierarchy = 'fecha' # Navegación por año, mes y día arriba del listado
    readonly_fields = ('fecha',) # La fecha se llena sola, así que solo se muestra
    list_select_related = ('cuenta_origen__moneda', 'cuenta_destino__moneda')  # Trae las cuentas y sus monedas en la misma consulta, para que el listado sea rápido

    # Un movimiento ya creado no se edita: forma parte del historial
    def has_change_permission(self, request, obj=None):
        # Sin movimiento concreto (obj es None) Django consulta si puede mostrar el listado: se permite
        # Con un movimiento concreto se rechaza, así que se abre solo en modo lectura
        return obj is None

    # Un movimiento ya creado tampoco se borra
    def has_delete_permission(self, request, obj=None):
        # Siempre se rechaza; así desaparecen los botones y la acción de eliminar
        return False


# Registra Contacto en el panel
@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('propietario', 'agendado', 'apodo', 'fecha_agregado')  # Columnas del listado
    search_fields = ('propietario__nombre', 'agendado__nombre', 'apodo')  # La búsqueda mira los nombres de los dos clientes y el apodo
    readonly_fields = ('fecha_agregado',)  # La fecha se llena sola, así que solo se muestra


# ============================================================
# TEXTOS GENERALES DEL PANEL
# ============================================================

admin.site.site_header = 'Alke Wallet: administración'  # Título grande que aparece en la barra superior
admin.site.site_title = 'Alke Wallet'  # Texto de la pestaña del navegador
admin.site.index_title = 'Panel de administración'  # Título de la página de inicio del panel