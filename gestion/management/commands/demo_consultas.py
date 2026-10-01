# gestion/management/commands/demo_consultas.py
# Comando de manage.py para ejecutar todas las consultas y mostrar sus resultados


from django.core.management.base import BaseCommand   # Importa la clase base para crear comandos propios de manage.py
from gestion import consultas   # Importa el módulo con todas las consultas que escribimos
from gestion.models import Cliente  # Importa el modelo Cliente para elegir un cliente de ejemplo


# Todo comando debe llamarse Command y heredar de BaseCommand
class Command(BaseCommand):
    help = 'Ejecuta y muestra todas las consultas de gestion/consultas.py'  # Texto que aparece al escribir: python manage.py help demo_consultas

    def titulo(self, texto):  # Método auxiliar para escribir un título destacado
        self.stdout.write('')  # Deja una línea en blanco y escribe el título en verde
        self.stdout.write(self.style.SUCCESS(texto))

    
    def handle(self, *args, **options):  # handle es el método que se ejecuta al correr el comando
        ana = Cliente.objects.get(email='ana@example.com')  # Cliente de ejemplo para las consultas que reciben un cliente

        # --- Filtros ---
        self.titulo('1. Movimientos de los últimos 14 días')
        self.stdout.write(f'   cantidad: {consultas.movimientos_recientes(14).count()}')

        self.titulo('2. Movimientos de Ana García (como origen o destino)')
        for mov in consultas.movimientos_de_cliente(ana):
            self.stdout.write(f'   {mov.tipo}: {mov.monto} {mov.descripcion}')

        self.titulo('3. Clientes con teléfono escrito')
        self.stdout.write(f'   {list(consultas.clientes_con_telefono())}')

        self.titulo('4. Clientes sin contactos')
        self.stdout.write(f'   {list(consultas.clientes_sin_contactos())}')

        # --- Anotaciones y agregaciones ---
        self.titulo('5. Cantidad de cuentas por cliente')
        for cliente in consultas.clientes_con_numero_de_cuentas():
            self.stdout.write(f'   {cliente.nombre}: {cliente.num_cuentas}')

        self.titulo('6. Resumen por tipo de movimiento')
        for moneda in ['CLP', 'USD']:
            self.stdout.write(f'   {moneda}:')
            for fila in consultas.resumen_por_tipo(moneda):
                self.stdout.write(f"      {fila['tipo']}: {fila['cantidad']} movimientos, total {fila['total']}")

        self.titulo('7. Saldo por cuenta (ORM con subconsultas)')
        for cuenta in consultas.cuentas_con_saldo():
            self.stdout.write(f'   {cuenta.numero} ({cuenta.moneda.codigo}): {cuenta.saldo_calculado}')

        # --- SQL propio ---
        self.titulo('8. Clientes con teléfono escrito (raw)')
        self.stdout.write(f'   {consultas.clientes_con_telefono_sql()}')

        self.titulo("9. Clientes cuyo nombre contiene 'ar' (raw con parámetros)")
        self.stdout.write(f"   {consultas.buscar_clientes_sql('ar')}")

        self.titulo('10. Saldo por cuenta (cursor con SQL puro)')
        for fila in consultas.saldos_sql():
            self.stdout.write(f"   {fila['numero']} ({fila['moneda']}) {fila['cliente']}: {fila['saldo']}")

        # --- Control: el saldo del ORM y el del SQL deben ser iguales ---
        self.titulo('Control: saldo ORM frente a saldo SQL')
        saldos_sql = {fila['numero']: fila['saldo'] for fila in consultas.saldos_sql()}  # Diccionario número de cuenta -> saldo según el SQL
        todo_igual = all(              # Compara cada cuenta con el saldo calculado por el ORM
            float(cuenta.saldo_calculado) == float(saldos_sql[cuenta.numero])
            for cuenta in consultas.cuentas_con_saldo()
        )
        self.stdout.write(f'   coinciden todas las cuentas: {todo_igual}')