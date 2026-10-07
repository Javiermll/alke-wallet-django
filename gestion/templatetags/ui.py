# Filtros de plantilla para dibujar los formularios con las clases de Bootstrap
from django import template  # template permite registrar filtros propios
from django.forms import CheckboxInput, Select, SelectMultiple  # Tipos de campo que se dibujan distinto

register = template.Library()  # Registro donde se anotan los filtros de este archivo


@register.filter
def es_casilla(campo):
    return isinstance(campo.field.widget, CheckboxInput)  # True si el campo es una casilla (sí/no)


@register.filter
def es_lista(campo):
    return isinstance(campo.field.widget, (Select, SelectMultiple))  # True si el campo es una lista desplegable


@register.filter
def bootstrap(campo):
    widget = campo.field.widget  # Tipo de campo (texto, lista, casilla...)
    if isinstance(widget, CheckboxInput):
        clase = 'form-check-input'  # Casilla
    elif isinstance(widget, (Select, SelectMultiple)):
        clase = 'form-select'  # Lista desplegable
    else:
        clase = 'form-control'  # Texto, correo, número, fecha, contraseña
    if campo.errors:
        clase += ' is-invalid'  # Borde rojo si el campo tiene errores
    return campo.as_widget(attrs={'class': clase})  # Dibuja el campo conservando sus otros atributos (type="date", etc.)
