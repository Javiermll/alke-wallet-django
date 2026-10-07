# gestion/tests/test_vistas.py
# Pruebas de las vistas: comprueban que las pantallas funcionan y muestran los datos correctos


import secrets# secrets crea textos aleatorios; así no hay contraseñas escritas a mano en el código
from datetime import datetime, timezone as zona# datetime para dar fechas a los movimientos
from decimal import Decimal# Decimal para los montos
from django.contrib.auth.models import User# get_messages lee los avisos que dejó la vista; User para comprobar la sesión
from django.contrib.messages import get_messages
from django.test import TestCase# TestCase crea una base de datos temporal; reverse calcula la dirección a partir del nombre
from django.urls import reverse

from gestion.models import Cliente, Contacto, Cuenta, Transaccion

from .utilidades import crear_moneda, crear_cliente, crear_cuenta, crear_personal, depositar


# Base común: un usuario del personal con sesión iniciada y unos pocos datos
class VistasBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.personal = crear_personal()
        cls.moneda = crear_moneda()
        cls.ana = crear_cliente(nombre='Ana García', usuario='ana')
        cls.luis = crear_cliente(nombre='Luis Pérez', usuario='luis')
        cls.cuenta_ana = crear_cuenta(cls.ana, numero='0001')
        cls.cuenta_luis = crear_cuenta(cls.luis, numero='0002')

    def setUp(self):
        # force_login inicia la sesión sin pasar por la pantalla de acceso
        self.client.force_login(self.personal)

    # Textos de los avisos que dejó la respuesta
    def avisos(self, respuesta):
        return [str(m) for m in get_messages(respuesta.wsgi_request)]


# ============================================================
# INICIO
# ============================================================

class InicioTest(VistasBase):
    def test_muestra_los_totales_del_sistema(self):
        depositar(self.cuenta_ana, 100)
        r = self.client.get(reverse('gestion:inicio'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['total_clientes'], 2)
        self.assertEqual(r.context['total_cuentas'], 2)
        self.assertEqual(r.context['total_transacciones'], 1)

    def test_ultimos_movimientos_son_como_maximo_cinco(self):
        for _ in range(7):
            depositar(self.cuenta_ana, 10)
        r = self.client.get(reverse('gestion:inicio'))
        self.assertEqual(len(r.context['ultimos_movimientos']), 5)


# ============================================================
# CLIENTES
# ============================================================

class ClienteVistasTest(VistasBase):
    def test_lista_ordenada_por_nombre_con_cantidad_de_cuentas(self):
        r = self.client.get(reverse('gestion:cliente_lista'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual([c.nombre for c in r.context['clientes']], ['Ana García', 'Luis Pérez'])
        self.assertEqual(r.context['clientes'][0].num_cuentas, 1)

    def test_crear_cliente(self):
        libre = User.objects.create_user(username='libre')
        r = self.client.post(reverse('gestion:cliente_nuevo'), {
            'usuario': libre.pk, 'nombre': 'Marta Díaz', 'email': 'marta@prueba.test', 'telefono': '',
        })
        self.assertRedirects(r, reverse('gestion:cliente_lista'))
        self.assertTrue(Cliente.objects.filter(nombre='Marta Díaz').exists())
        self.assertEqual(self.avisos(r), ['Cliente «Marta Díaz» creado correctamente.'])

    def test_crear_cliente_con_datos_invalidos_vuelve_al_formulario(self):
        r = self.client.post(reverse('gestion:cliente_nuevo'), {'nombre': ''})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].errors)
        self.assertEqual(Cliente.objects.count(), 2)

    def test_detalle_trae_cuentas_con_saldo_y_contactos(self):
        depositar(self.cuenta_ana, 80)
        Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        r = self.client.get(reverse('gestion:cliente_detalle', args=[self.ana.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['cuentas'][0].saldo_calculado, Decimal('80.00'))
        contacto = r.context['contactos'][0]
        self.assertEqual(contacto.agendado, self.luis)
        # El atajo de transferir apunta a la primera cuenta activa del contacto
        self.assertEqual(contacto.cuenta_sugerida, self.cuenta_luis)

    def test_cuenta_sugerida_ignora_las_cuentas_inactivas(self):
        # Luis tiene una cuenta inactiva con número menor: no debe ser la sugerida
        crear_cuenta(self.luis, numero='0000', activa=False)
        Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        r = self.client.get(reverse('gestion:cliente_detalle', args=[self.ana.pk]))
        self.assertEqual(r.context['contactos'][0].cuenta_sugerida, self.cuenta_luis)

    def test_detalle_de_cliente_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse('gestion:cliente_detalle', args=[9999])).status_code, 404)

    def test_editar_cliente(self):
        r = self.client.post(reverse('gestion:cliente_editar', args=[self.ana.pk]), {
            'nombre': 'Ana María', 'email': 'ana@prueba.test', 'telefono': '555',
        })
        self.assertRedirects(r, reverse('gestion:cliente_detalle', args=[self.ana.pk]))
        self.ana.refresh_from_db()
        self.assertEqual((self.ana.nombre, self.ana.telefono), ('Ana María', '555'))
        self.assertEqual(self.avisos(r), ['Cliente «Ana María» actualizado correctamente.'])

    def test_eliminar_cliente_sin_movimientos(self):
        r = self.client.post(reverse('gestion:cliente_eliminar', args=[self.luis.pk]))
        self.assertRedirects(r, reverse('gestion:cliente_lista'))
        self.assertFalse(Cliente.objects.filter(pk=self.luis.pk).exists())
        self.assertEqual(self.avisos(r), ['Cliente «Luis Pérez» eliminado correctamente.'])

    def test_eliminar_cliente_con_movimientos_esta_protegido(self):
        depositar(self.cuenta_luis, 10)
        r = self.client.post(reverse('gestion:cliente_eliminar', args=[self.luis.pk]))
        self.assertRedirects(r, reverse('gestion:cliente_detalle', args=[self.luis.pk]))
        # El cliente sigue existiendo y se explica por qué
        self.assertTrue(Cliente.objects.filter(pk=self.luis.pk).exists())
        self.assertEqual(
            self.avisos(r),
            ['No se puede eliminar a Luis Pérez: sus cuentas tienen movimientos registrados.'],
        )

    def test_pantalla_de_confirmacion_no_borra(self):
        # Un GET solo muestra la pregunta; borrar exige POST
        r = self.client.get(reverse('gestion:cliente_eliminar', args=[self.luis.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Cliente.objects.filter(pk=self.luis.pk).exists())


# ============================================================
# CUENTAS
# ============================================================

class CuentaVistasTest(VistasBase):
    def test_lista_trae_saldo_calculado(self):
        depositar(self.cuenta_ana, 40)
        r = self.client.get(reverse('gestion:cuenta_lista'))
        self.assertEqual(r.status_code, 200)
        saldos = {c.numero: c.saldo_calculado for c in r.context['cuentas']}
        self.assertEqual(saldos, {'0001': Decimal('40.00'), '0002': Decimal('0')})

    def test_formulario_propone_el_siguiente_numero(self):
        r = self.client.get(reverse('gestion:cuenta_nueva'))
        self.assertEqual(r.context['form'].initial['numero'], '0003')

    def test_formulario_deja_elegido_el_cliente_de_la_direccion(self):
        r = self.client.get(reverse('gestion:cuenta_nueva') + f'?cliente={self.luis.pk}')
        self.assertEqual(str(r.context['form'].initial['cliente']), str(self.luis.pk))

    def test_crear_cuenta(self):
        r = self.client.post(reverse('gestion:cuenta_nueva'), {
            'cliente': self.ana.pk, 'moneda': self.moneda.pk, 'numero': '0003', 'activa': 'on',
        })
        cuenta = Cuenta.objects.get(numero='0003')
        self.assertRedirects(r, reverse('gestion:cuenta_detalle', args=[cuenta.pk]))
        self.assertEqual(self.avisos(r), ['Cuenta 0003 creada correctamente.'])

    def test_crear_cuenta_con_numero_repetido_muestra_error(self):
        r = self.client.post(reverse('gestion:cuenta_nueva'), {
            'cliente': self.ana.pk, 'moneda': self.moneda.pk, 'numero': '0001', 'activa': 'on',
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['form'].errors['numero'], ['Ya existe una cuenta con ese número.'])
        self.assertEqual(Cuenta.objects.count(), 2)

    def test_detalle_trae_movimientos_y_total(self):
        depositar(self.cuenta_ana, 10)
        depositar(self.cuenta_ana, 20)
        r = self.client.get(reverse('gestion:cuenta_detalle', args=[self.cuenta_ana.pk]))
        self.assertEqual(r.context['total_movimientos'], 2)
        self.assertEqual(len(r.context['movimientos']), 2)

    def test_detalle_muestra_como_maximo_quince_movimientos(self):
        for _ in range(17):
            depositar(self.cuenta_ana, 1)
        r = self.client.get(reverse('gestion:cuenta_detalle', args=[self.cuenta_ana.pk]))
        self.assertEqual(len(r.context['movimientos']), 15)
        self.assertEqual(r.context['total_movimientos'], 17)

    def test_editar_cuenta(self):
        r = self.client.post(reverse('gestion:cuenta_editar', args=[self.cuenta_ana.pk]), {'numero': '0010'})
        self.assertRedirects(r, reverse('gestion:cuenta_detalle', args=[self.cuenta_ana.pk]))
        self.cuenta_ana.refresh_from_db()
        # Sin la casilla "activa" marcada, la cuenta queda desactivada
        self.assertEqual((self.cuenta_ana.numero, self.cuenta_ana.activa), ('0010', False))
        self.assertEqual(self.avisos(r), ['Cuenta 0010 actualizada correctamente.'])

    def test_eliminar_cuenta_sin_movimientos(self):
        r = self.client.post(reverse('gestion:cuenta_eliminar', args=[self.cuenta_luis.pk]))
        self.assertRedirects(r, reverse('gestion:cuenta_lista'))
        self.assertFalse(Cuenta.objects.filter(pk=self.cuenta_luis.pk).exists())
        self.assertEqual(self.avisos(r), ['Cuenta 0002 eliminada correctamente.'])

    def test_eliminar_cuenta_con_movimientos_esta_protegida(self):
        depositar(self.cuenta_luis, 10)
        r = self.client.post(reverse('gestion:cuenta_eliminar', args=[self.cuenta_luis.pk]))
        self.assertRedirects(r, reverse('gestion:cuenta_detalle', args=[self.cuenta_luis.pk]))
        self.assertTrue(Cuenta.objects.filter(pk=self.cuenta_luis.pk).exists())
        self.assertEqual(
            self.avisos(r),
            ['No se puede eliminar la cuenta 0002: tiene movimientos registrados. Puedes desactivarla desde Editar.'],
        )


# ============================================================
# TRANSACCIONES
# ============================================================

class TransaccionVistasTest(VistasBase):
    def test_lista_pagina_de_a_diez(self):
        for _ in range(12):
            depositar(self.cuenta_ana, 1)
        url = reverse('gestion:transaccion_lista')
        self.assertEqual(len(self.client.get(url).context['transacciones']), 10)
        self.assertEqual(len(self.client.get(url + '?page=2').context['transacciones']), 2)

    def test_filtro_por_tipo(self):
        depositar(self.cuenta_ana, 100)
        Transaccion.objects.create(tipo='retiro', cuenta_origen=self.cuenta_ana, monto=Decimal('10'))
        r = self.client.get(reverse('gestion:transaccion_lista') + '?tipo=retiro')
        self.assertEqual([t.tipo for t in r.context['transacciones']], ['retiro'])

    def test_filtro_por_numero_de_cuenta_origen_o_destino(self):
        depositar(self.cuenta_ana, 100)
        depositar(self.cuenta_luis, 50)
        Transaccion.objects.create(
            tipo='transferencia', cuenta_origen=self.cuenta_ana, cuenta_destino=self.cuenta_luis, monto=Decimal('5'),
        )
        r = self.client.get(reverse('gestion:transaccion_lista') + '?cuenta=0002')
        # Salen el depósito a Luis y la transferencia (donde Luis es destino)
        self.assertEqual(sorted(t.tipo for t in r.context['transacciones']), ['deposito', 'transferencia'])

    def test_filtro_por_fechas(self):
        viejo = depositar(self.cuenta_ana, 1)
        nuevo = depositar(self.cuenta_ana, 2)
        # fecha usa auto_now_add; update() permite fijar fechas de prueba
        Transaccion.objects.filter(pk=viejo.pk).update(fecha=datetime(2026, 1, 10, 15, 0, tzinfo=zona.utc))
        Transaccion.objects.filter(pk=nuevo.pk).update(fecha=datetime(2026, 3, 10, 15, 0, tzinfo=zona.utc))
        url = reverse('gestion:transaccion_lista')
        desde = self.client.get(url + '?desde=2026-02-01').context['transacciones']
        self.assertEqual([t.pk for t in desde], [nuevo.pk])
        hasta = self.client.get(url + '?hasta=2026-02-01').context['transacciones']
        self.assertEqual([t.pk for t in hasta], [viejo.pk])

    def test_filtro_invalido_se_ignora_y_muestra_todo(self):
        depositar(self.cuenta_ana, 1)
        depositar(self.cuenta_ana, 2)
        r = self.client.get(reverse('gestion:transaccion_lista') + '?desde=basura')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['transacciones']), 2)
        self.assertFalse(r.context['filtro'].is_valid())

    def test_parametros_conservan_filtros_pero_no_la_pagina(self):
        # Hacen falta más de 10 depósitos para que exista la página 2
        for _ in range(12):
            depositar(self.cuenta_ana, 1)
        r = self.client.get(reverse('gestion:transaccion_lista') + '?tipo=deposito&page=2')
        self.assertEqual(r.context['parametros'], 'tipo=deposito')

    def test_formulario_nuevo_se_abre_con_valores_de_la_direccion(self):
        r = self.client.get(
            reverse('gestion:transaccion_nueva') + f'?tipo=deposito&cuenta_destino={self.cuenta_ana.pk}'
        )
        self.assertEqual(r.context['form'].initial['tipo'], 'deposito')
        self.assertEqual(r.context['form'].initial['cuenta_destino'], str(self.cuenta_ana.pk))

    def test_registrar_deposito(self):
        r = self.client.post(reverse('gestion:transaccion_nueva'), {
            'tipo': 'deposito', 'cuenta_destino': self.cuenta_ana.pk, 'monto': '25.50', 'descripcion': 'sueldo',
        })
        mov = Transaccion.objects.get()
        self.assertRedirects(r, reverse('gestion:transaccion_detalle', args=[mov.pk]))
        self.assertEqual(mov.monto, Decimal('25.50'))
        self.assertEqual(self.avisos(r), ['Movimiento registrado: Depósito de 25.50.'])

    def test_retiro_sin_saldo_no_se_guarda_y_muestra_error(self):
        depositar(self.cuenta_ana, 10)
        r = self.client.post(reverse('gestion:transaccion_nueva'), {
            'tipo': 'retiro', 'cuenta_origen': self.cuenta_ana.pk, 'monto': '50',
        })
        # Vuelve al formulario con el error y no se crea nada nuevo
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].non_field_errors())
        self.assertEqual(Transaccion.objects.count(), 1)

    def test_transferencia_entre_cuentas(self):
        depositar(self.cuenta_ana, 100)
        r = self.client.post(reverse('gestion:transaccion_nueva'), {
            'tipo': 'transferencia', 'cuenta_origen': self.cuenta_ana.pk,
            'cuenta_destino': self.cuenta_luis.pk, 'monto': '30',
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.cuenta_ana.saldo, Decimal('70'))
        self.assertEqual(self.cuenta_luis.saldo, Decimal('30'))

    def test_detalle_del_movimiento(self):
        mov = depositar(self.cuenta_ana, 5)
        r = self.client.get(reverse('gestion:transaccion_detalle', args=[mov.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['transaccion'], mov)

    def test_los_movimientos_no_se_editan_ni_se_borran(self):
        # No existen rutas para ello: el historial es de solo lectura
        mov = depositar(self.cuenta_ana, 5)
        for sufijo in ('editar/', 'eliminar/'):
            self.assertEqual(self.client.get(f'/transacciones/{mov.pk}/{sufijo}').status_code, 404)


# ============================================================
# CONTACTOS
# ============================================================

class ContactoVistasTest(VistasBase):
    def test_agregar_contacto(self):
        r = self.client.post(
            reverse('gestion:contacto_nuevo', args=[self.ana.pk]), {'agendado': self.luis.pk, 'apodo': 'Lucho'},
        )
        self.assertRedirects(r, reverse('gestion:cliente_detalle', args=[self.ana.pk]))
        self.assertTrue(Contacto.objects.filter(propietario=self.ana, agendado=self.luis, apodo='Lucho').exists())
        self.assertEqual(self.avisos(r), ['Contacto «Luis Pérez» agregado correctamente.'])

    def test_formulario_muestra_de_quien_es_la_agenda(self):
        r = self.client.get(reverse('gestion:contacto_nuevo', args=[self.ana.pk]))
        self.assertEqual(r.context['propietario'], self.ana)

    def test_agenda_de_cliente_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse('gestion:contacto_nuevo', args=[9999])).status_code, 404)

    def test_quitar_contacto_no_borra_al_cliente(self):
        ficha = Contacto.objects.create(propietario=self.ana, agendado=self.luis)
        r = self.client.post(reverse('gestion:contacto_eliminar', args=[ficha.pk]))
        self.assertRedirects(r, reverse('gestion:cliente_detalle', args=[self.ana.pk]))
        self.assertFalse(Contacto.objects.filter(pk=ficha.pk).exists())
        # Luis sigue existiendo: solo se quitó la ficha de la agenda
        self.assertTrue(Cliente.objects.filter(pk=self.luis.pk).exists())
        self.assertEqual(self.avisos(r), ['Contacto «Luis Pérez» quitado de la agenda.'])


# ============================================================
# REPORTE
# ============================================================

class ReporteVistaTest(VistasBase):
    def test_una_seccion_por_moneda_con_sus_totales(self):
        usd = crear_moneda('USD', 'Dólar', '$')
        cuenta_usd = crear_cuenta(self.ana, numero='0003', moneda=usd)
        depositar(self.cuenta_ana, 100)
        depositar(cuenta_usd, 7)
        r = self.client.get(reverse('gestion:reporte'))
        self.assertEqual(r.status_code, 200)
        secciones = r.context['secciones']
        # Monedas en orden de código y sin mezclar sus saldos
        self.assertEqual([s['moneda'].codigo for s in secciones], ['CLP', 'USD'])
        self.assertEqual(secciones[0]['total_saldos'], Decimal('100.00'))
        self.assertEqual(secciones[1]['total_saldos'], Decimal('7.00'))
        self.assertEqual(secciones[0]['resumen'][0]['tipo_nombre'], 'Depósito')

    def test_movimientos_por_mes_suman_el_total(self):
        depositar(self.cuenta_ana, 1)
        depositar(self.cuenta_ana, 2)
        r = self.client.get(reverse('gestion:reporte'))
        self.assertEqual(r.context['total_movimientos'], 2)
        self.assertEqual(sum(fila['cantidad'] for fila in r.context['por_mes']), 2)

    def test_sin_datos_no_falla(self):
        # Solo existe la moneda CLP y ningún movimiento: el reporte igual se muestra
        r = self.client.get(reverse('gestion:reporte'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['total_movimientos'], 0)


# ============================================================
# REGISTRO Y PERFIL
# ============================================================

class RegistroVistaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moneda = crear_moneda()
        # Contraseña aleatoria de la ejecución
        cls.clave = secrets.token_urlsafe(12)

    def datos(self, **cambios):
        datos = {
            'username': 'nuevo', 'nombre': 'Nuevo Cliente', 'email': 'nuevo@prueba.test', 'telefono': '',
            'moneda': self.moneda.pk, 'password1': self.clave, 'password2': self.clave,
        }
        datos.update(cambios)
        return datos

    def test_pantalla_publica(self):
        # Sin sesión se puede abrir (no pide acceso)
        self.assertEqual(self.client.get(reverse('registro')).status_code, 200)

    def test_registro_inicia_sesion_y_va_al_inicio(self):
        r = self.client.post(reverse('registro'), self.datos())
        self.assertRedirects(r, reverse('gestion:inicio'))
        # La sesión quedó iniciada con el usuario nuevo
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='nuevo').pk)
        self.assertEqual(self.avisos(r), ['¡Bienvenido a Alke Wallet! Tu cuenta quedó creada.'])

    def test_registro_con_error_no_crea_nada(self):
        r = self.client.post(reverse('registro'), self.datos(password2='otra'))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username='nuevo').exists())

    def test_quien_ya_tiene_sesion_es_enviado_al_inicio(self):
        self.client.force_login(crear_cliente().usuario)
        self.assertRedirects(self.client.get(reverse('registro')), reverse('gestion:inicio'))

    def avisos(self, respuesta):
        return [str(m) for m in get_messages(respuesta.wsgi_request)]


class PerfilVistaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.clave = secrets.token_urlsafe(12)
        cls.nueva = secrets.token_urlsafe(12)
        cls.cliente = crear_cliente()
        # Aquí sí se necesita una clave real, porque se prueba el cambio de contraseña
        cls.cliente.usuario.set_password(cls.clave)
        cls.cliente.usuario.save()

    def setUp(self):
        self.client.force_login(self.cliente.usuario)

    def test_perfil_se_muestra(self):
        self.assertEqual(self.client.get(reverse('gestion:perfil')).status_code, 200)

    def test_cambiar_clave(self):
        r = self.client.post(reverse('gestion:cambiar_clave'), {
            'old_password': self.clave, 'new_password1': self.nueva, 'new_password2': self.nueva,
        })
        self.assertRedirects(r, reverse('gestion:perfil'))
        self.assertEqual([str(m) for m in get_messages(r.wsgi_request)], ['Tu contraseña se cambió correctamente.'])
        self.cliente.usuario.refresh_from_db()
        self.assertTrue(self.cliente.usuario.check_password(self.nueva))

    def test_la_sesion_sigue_abierta_tras_cambiar_la_clave(self):
        self.client.post(reverse('gestion:cambiar_clave'), {
            'old_password': self.clave, 'new_password1': self.nueva, 'new_password2': self.nueva,
        })
        # Si la sesión se hubiera cerrado, esto redirigiría al acceso
        self.assertEqual(self.client.get(reverse('gestion:perfil')).status_code, 200)

    def test_clave_actual_incorrecta(self):
        r = self.client.post(reverse('gestion:cambiar_clave'), {
            'old_password': 'incorrecta', 'new_password1': self.nueva, 'new_password2': self.nueva,
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn('old_password', r.context['form'].errors)
        self.cliente.usuario.refresh_from_db()
        self.assertTrue(self.cliente.usuario.check_password(self.clave))