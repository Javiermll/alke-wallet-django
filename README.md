# Alke Wallet

Billetera digital desarrollada con Django para el proyecto final del **Módulo 7: Acceso a datos en aplicaciones Django** (Full Stack Python Trainee, Talento Digital / Alkemy).

La aplicación permitirá a los usuarios crear y gestionar cuentas digitales, realizar transacciones, guardar contactos frecuentes, consultar saldos y generar reportes, usando el ORM de Django, migraciones y las aplicaciones preinstaladas del framework.

## Estado del proyecto

| Etapa | Descripción | Estado |
|---|---|---|
| 0 | Entorno virtual, instalación de Django y repositorio Git | Completada |
| 1 | Conexión a base de datos (SQLite y PostgreSQL) | Completada |
| 2 | App `gestion` y modelos | Completada |
| 3 | Migraciones en SQLite y PostgreSQL | Completada |
| 4 | Consultas personalizadas (`filter`, `exclude`, `annotate`, `raw()`, cursores) | Completada |
| 5 | Panel de administración | Pendiente |
| 6 | Vistas CRUD basadas en clases y templates | Pendiente |
| 7 | Autenticación y archivos estáticos | Pendiente |
| 8 | Pruebas | Pendiente |
| 9 | Documentación final y demostración | Pendiente |

## Tecnologías

| Herramienta | Versión | Uso |
|---|---|---|
| Python | 3.14.6 | Lenguaje base |
| Django | 6.1.1 | Framework web |
| psycopg | 3.3.6 | Adaptador entre Django y PostgreSQL (reemplaza a `psycopg2-binary`; ver incidencia de la etapa 4) |
| python-dotenv | 1.2.3 | Lectura de credenciales desde el archivo `.env` |
| PostgreSQL | 17 | Base de datos de producción |
| SQLite | incluido en Python | Base de datos de desarrollo |
| Visual Studio Code | última versión | Editor |
| Git y GitHub | - | Control de versiones |

## Instalación y ejecución local

Los comandos están escritos para **PowerShell en Windows**.

### 1. Clonar el repositorio

```powershell
# Descarga el proyecto y entra a su carpeta
git clone https://github.com/Javiermll/alke-wallet-django.git
cd alke-wallet-django
```

### 2. Crear y activar el entorno virtual

```powershell
# Crea el entorno virtual en la carpeta "venv"
python -m venv venv

# Lo activa; el prompt debe empezar con (venv)
.\venv\Scripts\activate
```

> Cada terminal nueva necesita la activación antes de trabajar. Sin `(venv)` en el prompt, Python usa la instalación global y Django no se encuentra.

### 3. Instalar las dependencias

```powershell
# Instala las librerías listadas en requirements.txt
python -m pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Copiar la plantilla `.env.example` como `.env` y completar los valores:

```powershell
# Crea el archivo .env a partir de la plantilla
Copy-Item .env.example .env
```

Contenido del `.env`:

```ini
# Motor a usar: "sqlite" (desarrollo) o "postgres" (producción)
DB_ENGINE=sqlite

# Datos de conexión a PostgreSQL (solo se usan si DB_ENGINE=postgres)
DB_NAME=alke_wallet
DB_USER=postgres
DB_PASSWORD=escribe_aqui_tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

Para usar PostgreSQL, crear antes la base de datos vacía (`CREATE DATABASE alke_wallet;`) y cambiar `DB_ENGINE=postgres`.

### 5. Aplicar las migraciones

```powershell
# Crea todas las tablas en la base configurada (las internas de Django y las de gestion)
python manage.py migrate
```

### 6. Cargar datos de demostración (opcional)

```powershell
# Carga clientes, cuentas, contactos y movimientos de ejemplo (se puede repetir sin duplicar)
python manage.py poblar_datos

# Ejecuta todas las consultas del proyecto y muestra el resultado
python manage.py demo_consultas
```

### 7. Ejecutar el servidor

```powershell
# Levanta el servidor de desarrollo en http://127.0.0.1:8000/
python manage.py runserver
```

## Arquitectura

```text
alke_wallet/
├── core/                      # Paquete de configuración del proyecto
│   ├── settings.py            # Configuración general y de base de datos
│   ├── urls.py                # Rutas principales
│   ├── asgi.py
│   └── wsgi.py
├── gestion/                   # App principal con la lógica del negocio
│   ├── management/
│   │   └── commands/
│   │       ├── poblar_datos.py    # Carga datos de demostración sin duplicar
│   │       └── demo_consultas.py  # Ejecuta y muestra todas las consultas
│   ├── migrations/
│   │   └── 0001_initial.py    # Migración inicial: crea las 5 tablas de la app
│   ├── models.py              # Modelos: Moneda, Cliente, Contacto, Cuenta, Transaccion
│   ├── consultas.py           # Consultas reutilizables: ORM, raw() y cursor
│   ├── admin.py               # Panel de administración (etapa 5)
│   ├── views.py               # Vistas (etapa 6)
│   └── tests.py               # Pruebas (etapa 8)
├── docs/
│   └── capturas/              # Capturas de pantalla usadas en este README
├── manage.py                  # Utilidad de línea de comandos de Django
├── requirements.txt           # Dependencias del proyecto
├── .env                       # Credenciales locales (NO se sube a GitHub)
├── .env.example               # Plantilla pública del .env
└── .gitignore                 # Archivos excluidos del repositorio
```

## Modelo de datos

```mermaid
erDiagram
    USER ||--|| CLIENTE : "1:1"
    CLIENTE ||--o{ CUENTA : "tiene"
    MONEDA ||--o{ CUENTA : "moneda de"
    CUENTA |o--o{ TRANSACCION : "origen"
    CUENTA |o--o{ TRANSACCION : "destino"
    CLIENTE ||--o{ CONTACTO : "propietario"
    CLIENTE ||--o{ CONTACTO : "agendado"
```

| Modelo | Tabla | Descripción | Relaciones |
|---|---|---|---|
| `Moneda` | `gestion_moneda` | Monedas disponibles (código, nombre, símbolo) | 1 moneda → N cuentas |
| `Cliente` | `gestion_cliente` | Datos de negocio de cada persona | **1:1** con `User` de Django |
| `Contacto` | `gestion_contacto` | Ficha de agenda: quién guarda a quién, con apodo y fecha | Tabla intermedia del **N:M** Cliente ↔ Cliente |
| `Cuenta` | `gestion_cuenta` | Cuenta digital de un cliente en una moneda | **N:1** con Cliente y **N:1** con Moneda |
| `Transaccion` | `gestion_transaccion` | Depósito, retiro o transferencia | **N:1** con Cuenta origen y **N:1** con Cuenta destino |

**Reglas de negocio implementadas:**

| Tipo | Cuenta origen | Cuenta destino |
|---|---|---|
| Depósito | vacía | obligatoria |
| Retiro | obligatoria | vacía |
| Transferencia | obligatoria | obligatoria, distinta de la origen y de la misma moneda |

Otras reglas: el monto debe ser mayor que cero, un cliente no puede agendarse a sí mismo y no se puede agendar dos veces a la misma persona.

## Documentación por etapa

### Etapa 0: entorno y proyecto base

**Objetivo:** dejar un entorno aislado y reproducible con el proyecto Django funcionando y bajo control de versiones.

**Pasos realizados:**

```powershell
# 1. Crear la carpeta raíz y abrirla en VS Code
mkdir alke_wallet
cd alke_wallet
code .

# 2. Crear y activar el entorno virtual
python -m venv venv
.\venv\Scripts\activate

# 3. Instalar las librerías
python -m pip install django psycopg2-binary python-dotenv

# 4. Crear el proyecto con el paquete interno "core" (el punto evita una carpeta anidada)
python -m django startproject core .

# 5. Guardar la lista de librerías (utf8 evita que PowerShell genere UTF-16)
python -m pip freeze | Out-File -Encoding utf8 requirements.txt

# 6. Probar el servidor
python manage.py runserver

# 7. Iniciar el repositorio y guardar el primer commit
git init
git branch -M main
git add .
git commit -m "Configuración inicial del proyecto Django"
```

**Decisiones:**

- **Nombre `core`:** el paquete interno se llama `core` para evitar la estructura `alke_wallet/alke_wallet/`, que resulta confusa.
- **`.gitignore`:** excluye `venv/`, `__pycache__/`, `db.sqlite3`, `.env` y `.vscode/`. El entorno virtual y las credenciales nunca se versionan.
- **`requirements.txt`:** permite reconstruir el entorno en otro equipo con un solo comando.
- **Adaptador de PostgreSQL:** al inicio se instaló `psycopg2-binary`. En la etapa 4 se reemplazó por `psycopg` (ver la incidencia de esa etapa).

**Incidencia resuelta:** en este equipo, una política de control de aplicaciones de Windows bloquea `pip.exe` dentro del entorno virtual.

```text
Error al ejecutar el programa 'pip.exe': Una directiva de Control de aplicaciones bloqueó este archivo
```

Solución: ejecutar pip a través del intérprete de Python, que sí está permitido.

```powershell
# En vez de: pip install ...
python -m pip install django psycopg2-binary python-dotenv

# En vez de: django-admin startproject ...
python -m django startproject core .
```

**Verificación:** al abrir `http://127.0.0.1:8000/` aparece la página de bienvenida de Django (el cohete).

![Servidor de Django funcionando](docs/capturas/01_servidor_cohete.png)

![Estructura del proyecto en VS Code](docs/capturas/02_estructura_proyecto.png)

### Etapa 1: conexión a la base de datos

**Objetivo:** configurar Django para conectarse a **SQLite** (desarrollo) y **PostgreSQL** (producción), alternando entre ambas sin modificar el código.

**Alternativas evaluadas:**

| Opción | Descripción | Resultado |
|---|---|---|
| A. Variable `DB_ENGINE` en `.env` | Un solo `settings.py`; se cambia una línea del `.env` | **Elegida:** cumple la consigna y demuestra ambas conexiones |
| B. Dos archivos de settings | `settings_dev.py` y `settings_prod.py` | Descartada: agrega complejidad innecesaria para este alcance |
| C. Solo SQLite con PostgreSQL comentado | Mínimo exigido | Descartada: la conexión a PostgreSQL quedaría sin demostrar |

**Creación de la base de datos en PostgreSQL:**

```powershell
# Entra a PostgreSQL con el usuario postgres
psql -U postgres
```

```sql
-- Crea la base de datos vacía del proyecto
CREATE DATABASE alke_wallet;

-- Sale de psql
\q
```

**Configuración en `core/settings.py`:**

```python
# "os" permite leer variables de entorno del sistema
import os

# load_dotenv lee el archivo .env y carga sus valores como variables de entorno
from dotenv import load_dotenv

# Carga las variables del archivo .env que está en la raíz del proyecto
load_dotenv(BASE_DIR / '.env')

# Lee del .env qué motor usar; si la variable no existe, usa "sqlite" por defecto
DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite')

# Si en el .env se indicó "postgres", se configura la conexión a PostgreSQL
if DB_ENGINE == 'postgres':
    DATABASES = {
        'default': {
            # Adaptador de PostgreSQL (psycopg)
            'ENGINE': 'django.db.backends.postgresql',
            # Nombre de la base de datos, usuario y contraseña
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            # Dónde corre PostgreSQL y en qué puerto
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
# En cualquier otro caso se usa SQLite (archivo db.sqlite3 en la raíz)
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

**Seguridad:** las credenciales viven únicamente en el `.env`, que está en el `.gitignore`. El repositorio incluye `.env.example`, una plantilla sin la contraseña real.

**Verificación de la conexión con cada motor:**

```powershell
# Lista las migraciones; si la conexión funciona, Django las muestra todas sin aplicar ([ ])
python manage.py showmigrations

# Confirma qué motor y qué base está usando Django en este momento
python manage.py shell -c "from django.db import connection; print(connection.vendor, connection.settings_dict['NAME'])"
```

Resultados obtenidos:

| `DB_ENGINE` | Salida del comando de verificación |
|---|---|
| `sqlite` | `sqlite <ruta>\db.sqlite3` |
| `postgres` | `postgresql alke_wallet` |

En ambos casos `showmigrations` lista las 18 migraciones internas de Django (`admin`, `auth`, `contenttypes` y `sessions`) sin aplicar. Es lo esperado: se aplican en la etapa 3.

![Bloque DATABASES en settings.py](docs/capturas/03_settings_databases.png)

![Verificación con SQLite](docs/capturas/04_verificacion_sqlite.png)

![Verificación con PostgreSQL](docs/capturas/05_verificacion_postgresql.png)

**Solución de errores frecuentes:**

| Error | Causa probable |
|---|---|
| `No module named 'django'` | El entorno virtual no está activo |
| `password authentication failed` | La contraseña del `.env` no coincide con la de PostgreSQL |
| `database "alke_wallet" does not exist` | Falta crear la base de datos |
| `connection refused` | El servicio de PostgreSQL no está corriendo |

### Etapa 2: app `gestion` y modelos

**Objetivo:** crear la app principal y definir el modelo de datos con el ORM de Django, con campos adecuados, validaciones y relaciones Uno a Uno, Muchos a Uno y Muchos a Muchos.

**Pasos realizados:**

```powershell
# Crea la rama de trabajo que pide la consigna y se cambia a ella
git checkout -b feature/modelos

# Crea la app "gestion"
python manage.py startapp gestion
```

Registro de la app en `core/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Nuestra app; sin esta línea Django no reconoce sus modelos
    'gestion',
]
```

**Decisiones de diseño:**

| Tema | Elegida | Alternativa descartada | Motivo |
|---|---|---|---|
| Relación N:M | Contactos frecuentes entre clientes (Cliente ↔ Cliente) | Categorías de transacción | Se acerca más al funcionamiento de una billetera real |
| Contactos | Modelo intermedio `Contacto` con apodo y fecha | `ManyToManyField` simple | Permite guardar datos propios de la relación |
| Saldo | Calculado sumando transacciones | Columna `saldo` guardada y actualizada | Nunca queda desincronizado con los movimientos |
| Monedas | Transferencias solo entre cuentas de la misma moneda | Conversión con tasas de cambio | La conversión queda fuera del alcance |

**Fragmentos clave de `gestion/models.py`** (el archivo completo está en el repositorio):

Relación N:M de Cliente consigo mismo, a través de la tabla intermedia `Contacto`:

```python
# 'self' significa "el mismo modelo"
# through='Contacto': la tabla intermedia la definimos nosotros
# through_fields indica cuál campo de Contacto es "quien agenda" y cuál "a quién agenda"
# symmetrical=False: si Ana agenda a Luis, Luis NO queda agendado por Ana automáticamente
contactos = models.ManyToManyField(
    'self',
    through='Contacto',
    through_fields=('propietario', 'agendado'),
    symmetrical=False,
    related_name='agendado_por',
)
```

Restricciones que la propia base de datos hace cumplir en `Contacto`:

```python
constraints = [
    # No se puede agendar dos veces a la misma persona
    models.UniqueConstraint(fields=['propietario', 'agendado'], name='contacto_unico'),
    # Nadie puede agendarse a sí mismo
    models.CheckConstraint(
        condition=~models.Q(propietario=models.F('agendado')),
        name='no_agendarse_a_si_mismo',
    ),
]
```

Saldo calculado en `Cuenta`, sin columna en la tabla:

```python
# @property permite usarlo como un dato más: cuenta.saldo (sin paréntesis)
@property
def saldo(self):
    # Suma todo el dinero que ha llegado a esta cuenta (None si no hay movimientos)
    entradas = self.transacciones_recibidas.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
    # Suma todo el dinero que ha salido de esta cuenta
    salidas = self.transacciones_enviadas.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
    # El saldo es lo que entró menos lo que salió
    return entradas - salidas
```

**Doble protección de datos:**

| Nivel | Herramienta | Dónde actúa |
|---|---|---|
| Python | `MinValueValidator` y `clean()` | Formularios y panel de administración, con mensajes claros |
| Base de datos | `UniqueConstraint` y `CheckConstraint` | Toda escritura, incluso desde la shell |

**Notas técnicas:**

- `on_delete=PROTECT` en `Cuenta.moneda` y en las cuentas de `Transaccion` impide borrar monedas o cuentas que tengan datos asociados. `CASCADE` se usa donde los datos dependientes no tienen sentido sin su padre (cuentas de un cliente, fichas de contacto).
- Django 6 usa `condition=` en `CheckConstraint`. Los ejemplos antiguos usan `check=`, que ya no existe.
- La regla "no retirar más de lo que hay" no vive en `clean()`. Se aplicará en las vistas, dentro de una operación atómica, para no rechazar la edición de movimientos ya registrados.

**Verificación:**

```powershell
# Revisa que los modelos no tengan errores (no toca la base de datos)
python manage.py check
```

Resultado: `System check identified no issues (0 silenced).`

![INSTALLED_APPS con la app gestion](docs/capturas/06_installed_apps.png)

![Archivo models.py en VS Code](docs/capturas/07_models_py.png)

### Etapa 3: migraciones

**Objetivo:** aplicar las migraciones para reflejar los modelos en el esquema de la base de datos de forma controlada y con historial versionado, en SQLite y en PostgreSQL.

**Idea central:** `makemigrations` escribe el plan (un archivo Python que describe qué crear) y `migrate` lo ejecuta sobre la base de datos. Cada cambio futuro en los modelos generará una migración nueva en vez de modificar la anterior.

**Pasos realizados:**

```powershell
# 1. Genera el plan de migración a partir de los modelos
python manage.py makemigrations gestion

# 2. Muestra el SQL exacto que se ejecutará (no modifica la base)
python manage.py sqlmigrate gestion 0001

# 3. Aplica todas las migraciones pendientes
python manage.py migrate

# 4. Confirma que todas aparecen aplicadas [X]
python manage.py showmigrations

# 5. Lista las tablas creadas en la base que Django está usando
python manage.py shell -c "from django.db import connection; print(sorted(connection.introspection.table_names()))"
```

**Resultado de `makemigrations`:** se creó `gestion/migrations/0001_initial.py` con:

```text
+ Create model Moneda
+ Create model Cliente
+ Create model Contacto
+ Add field contactos to cliente
+ Create model Cuenta
+ Create model Transaccion
+ Create constraint contacto_unico on model contacto
+ Create constraint no_agendarse_a_si_mismo on model contacto
+ Create constraint monto_positivo on model transaccion
```

**Resultado de `migrate`:** se aplicaron 19 migraciones: las 18 internas de Django (`admin`, `auth`, `contenttypes`, `sessions`) más `gestion.0001_initial`.

**Tablas creadas (idénticas en ambos motores):**

| Origen | Tablas |
|---|---|
| App `gestion` | `gestion_moneda`, `gestion_cliente`, `gestion_contacto`, `gestion_cuenta`, `gestion_transaccion` |
| Autenticación (`auth`) | `auth_user`, `auth_group`, `auth_permission`, `auth_group_permissions`, `auth_user_groups`, `auth_user_user_permissions` |
| Administración y sesiones | `django_admin_log`, `django_content_type`, `django_session` |
| Control de migraciones | `django_migrations` |

En PostgreSQL, la verificación se repitió con `psql`:

```powershell
# Lista las tablas de la base alke_wallet en PostgreSQL
psql -U postgres -d alke_wallet -c "\dt"
```

Resultado: 15 tablas, todas en el esquema `public`.

**Prueba funcional en la shell** (`python manage.py shell`), repetida en ambos motores:

```python
# Importa el usuario de login y nuestros modelos
from django.contrib.auth.models import User
from gestion.models import Moneda, Cliente, Contacto, Cuenta, Transaccion

# Crea la moneda
clp = Moneda.objects.create(codigo='CLP', nombre='Peso chileno', simbolo='$')

# Crea dos usuarios de login; create_user guarda la contraseña cifrada
u1 = User.objects.create_user(username='ana', password='<contraseña_de_prueba>')
u2 = User.objects.create_user(username='luis', password='<contraseña_de_prueba>')

# Crea un cliente por cada usuario (relación 1:1)
ana = Cliente.objects.create(usuario=u1, nombre='Ana García', email='ana@example.com', telefono='123456789')
luis = Cliente.objects.create(usuario=u2, nombre='Luis Pérez', email='luis@example.com')

# Crea una cuenta para cada cliente, ambas en pesos
c_ana = Cuenta.objects.create(cliente=ana, moneda=clp, numero='0001')
c_luis = Cuenta.objects.create(cliente=luis, moneda=clp, numero='0002')

# Un depósito de 100000 en la cuenta de Ana (solo tiene destino)
Transaccion.objects.create(tipo='deposito', cuenta_destino=c_ana, monto=100000)

# Una transferencia de 30000 de Ana a Luis
Transaccion.objects.create(tipo='transferencia', cuenta_origen=c_ana, cuenta_destino=c_luis, monto=30000)

# Ana agenda a Luis como contacto (se crea la ficha intermedia)
Contacto.objects.create(propietario=ana, agendado=luis, apodo='Lucho')

# Saldos calculados, contactos de Ana y agendas donde aparece Luis
print(c_ana.saldo, c_luis.saldo)
print(ana.contactos.all())
print(luis.agendado_por.all())

# La base de datos debe rechazar un monto 0 (restricción monto_positivo)
from django.db import IntegrityError
try:
    Transaccion.objects.create(tipo='deposito', cuenta_destino=c_ana, monto=0)
except IntegrityError:
    print('La base rechazó el monto 0')
```

Resultados obtenidos:

| Comprobación | SQLite | PostgreSQL |
|---|---|---|
| Saldo de Ana (100000 − 30000) | `70000` | `70000.00` |
| Saldo de Luis | `30000.00` | `30000.00` |
| Contactos de Ana | `Luis Pérez` | `Luis Pérez` |
| Agendas donde aparece Luis | `Ana García` | `Ana García` |
| Monto 0 | Rechazado por la base | Rechazado por la base |

Estos datos de prueba se conservan en ambas bases para las consultas de la etapa 4.

**Reflexiones:**

- **Historial versionado:** la migración `0001_initial.py` se versiona en Git. Cualquier persona que clone el repositorio reconstruye el mismo esquema con `migrate`. El archivo `db.sqlite3` no se versiona porque contiene datos, no código.
- **Un plan, dos dialectos:** los mismos archivos de migración sirven para SQLite y PostgreSQL. El ORM traduce cada modelo al SQL de cada motor.
- **Reconstrucción de tablas en SQLite:** `sqlmigrate` muestra que SQLite no puede añadir restricciones a una tabla existente. Django crea una tabla temporal `new__...`, copia los datos, borra la original y renombra la nueva. Es una limitación del motor, que el ORM resuelve automáticamente.
- **Decimales:** SQLite no tiene un tipo decimal nativo, por eso el saldo de Ana se muestra como `70000` y no como `70000.00`. El valor es el mismo. PostgreSQL sí conserva los dos decimales.
- **Validaciones:** las creaciones desde la shell no ejecutan `clean()`; solo actúan las restricciones de la base de datos. Por eso el monto 0 se probó con `IntegrityError`. Las reglas de `clean()` se comprobarán en formularios y en el panel de administración.

![Migración 0001_initial.py en VS Code](docs/capturas/08_migracion_inicial.png)

![Salida de sqlmigrate](docs/capturas/09_sqlmigrate.png)

![Migrate y showmigrations en SQLite](docs/capturas/10_migrate_sqlite.png)

![Tablas en SQLite](docs/capturas/11_tablas_sqlite.png)

![Migrate y showmigrations en PostgreSQL](docs/capturas/12_migrate_postgresql.png)

![Tablas en PostgreSQL con psql](docs/capturas/13_tablas_postgresql.png)

![Prueba en la shell con SQLite](docs/capturas/14_prueba_shell_sqlite.png)

![Prueba en la shell con PostgreSQL](docs/capturas/15_prueba_shell_postgresql.png)

### Etapa 4: consultas personalizadas

**Objetivo:** acceder y manipular datos con el ORM de Django y con SQL propio: CRUD desde la shell, filtros avanzados, anotaciones y agregaciones, `raw()` y cursores.

**Rama de trabajo:** `feature/consultas`. No se modificó ningún modelo, por lo que esta etapa no genera migraciones nuevas.

**Decisiones:**

| Tema | Elegida | Alternativa descartada | Motivo |
|---|---|---|---|
| Datos de prueba | Comando propio `poblar_datos`, repetible sin duplicar | Cargarlos a mano en la shell o con un fixture JSON | Con pocos datos, los filtros y las anotaciones no muestran nada. El comando funciona igual en SQLite y PostgreSQL |
| Dónde viven las consultas | Funciones en `gestion/consultas.py` | `Manager` o `QuerySet` propio en `models.py` | Más simple, y se reutilizan después en las vistas |
| Valores en el SQL propio | Siempre parámetros `%s` | Pegar el texto dentro del SQL | Evita la inyección SQL |
| Prueba en ambos motores | Comando `demo_consultas` | Solo pruebas unitarias | Sirve como demostración funcional y compara SQLite con PostgreSQL con un solo comando |

#### 4.1 Datos de demostración: `poblar_datos`

El comando `python manage.py poblar_datos` carga clientes, cuentas, contactos y movimientos de ejemplo. Usa `get_or_create` con un campo único (código, número de cuenta, descripción o usuario), por lo que **se puede ejecutar varias veces sin duplicar datos**. Las fechas de los movimientos se reparten en los últimos 60 días, para poder probar filtros por fecha.

| Tabla | Total en la base |
|---|---|
| Monedas | 2 (CLP y USD) |
| Clientes | 5 |
| Cuentas | 7 |
| Contactos | 5 |
| Transacciones | 18 |

Saldos resultantes:

| Cuenta | Dueño | Moneda | Saldo |
|---|---|---|---|
| 0001 | Ana García | CLP | 115000 |
| 0002 | Luis Pérez | CLP | 60000 |
| 0003 | Ana García | USD | 400 |
| 0004 | Carla Soto | CLP | 140000 |
| 0005 | Diego Rojas | CLP | 125000 |
| 0006 | Diego Rojas | USD | 400 |
| 0007 | Marta Vega | CLP | 95000 |

Dos datos se dejaron a propósito para probar más adelante: Luis y Diego tienen teléfono `NULL`, y Marta lo tiene como texto vacío (`''`).

La segunda ejecución informa `0` registros nuevos, lo que demuestra que no duplica.

![Primera ejecución de poblar_datos](docs/capturas/16_poblar_datos_sqlite.png)

![Segunda ejecución: sin registros nuevos](docs/capturas/17_poblar_datos_repetido.png)

![poblar_datos en PostgreSQL](docs/capturas/18_poblar_datos_postgresql.png)

#### 4.2 CRUD desde la shell

Se hizo sobre un cliente temporal, **Pedro Prueba**, que se crea y se borra, para dejar intactos los datos de demostración.

```python
# CREATE: create() guarda de inmediato; Modelo(...) más save() lo hace en dos pasos
usuario = User.objects.create_user(username='pedro', password='<contraseña_de_prueba>')
pedro = Cliente(usuario=usuario, nombre='Pedro Prueba', email='pedro@example.com')
pedro.save()

# READ: get() devuelve un registro; filter() devuelve una lista; exists() devuelve True o False
Cliente.objects.get(email='pedro@example.com')
Cliente.objects.filter(email='pedro@example.com').exists()

# UPDATE: save() guarda un objeto; update() modifica directo en la base y devuelve las filas cambiadas
pedro.telefono = '555123456'
pedro.save()
Cuenta.objects.filter(numero='0008').update(activa=False)

# DELETE: primero se borra lo que protege (movimiento, cuenta) y luego el usuario
deposito.delete()
cuenta.delete()
usuario.delete()
```

| Operación | Qué se comprobó |
|---|---|
| Create | El objeto no tiene id hasta que se guarda; el saldo de un depósito de 10000 es `10000` |
| Read | `get()` falla con `DoesNotExist` si no hay registro; las relaciones se recorren en ambos sentidos, incluida la 1:1 |
| Update | `update()` no actualiza el objeto que ya está en memoria hasta usar `refresh_from_db()` |
| Validación | `full_clean()` detecta `Un depósito no debe tener cuenta origen.` y el monto mínimo |
| Delete | `PROTECT` impide borrar una moneda con cuentas y una cuenta con movimientos; `CASCADE` borra el cliente al borrar su usuario |

Al terminar, la base quedó como antes: 5 clientes, 7 cuentas y 18 movimientos.

![CRUD: crear](docs/capturas/19_crud_create.png)

![CRUD: leer](docs/capturas/20_crud_read.png)

![CRUD: actualizar](docs/capturas/21_crud_update.png)

![Validación con full_clean()](docs/capturas/22_crud_validar.png)

![CRUD: borrar, con PROTECT y CASCADE](docs/capturas/23_crud_delete.png)

#### 4.3 Filtros avanzados

`filter()` y `exclude()` encadenan condiciones; la coma equivale a **Y**, y para **O** y **NO** se usa `Q` con `|` y `~`. El doble guion bajo cumple dos funciones: `campo__operador` compara, y `relacion__campo` cruza tablas.

| Consulta | Resultado |
|---|---|
| `monto__gt=50000` | 4 movimientos |
| `monto__gte=50000` | 6 |
| `monto__range=(10000, 30000)` | 7 |
| `descripcion__icontains='retiro'` | 3 |
| `nombre__istartswith='a'` (clientes) | Ana García |
| `fecha__gte` hace 14 días | 8 (depende de la fecha en que se ejecute) |
| `tipo='transferencia', monto__gte=20000` | 3 |
| `exclude(tipo='deposito')` | 10 |
| `Q(tipo='retiro') \| Q(monto__gte=100000)` | 6 |
| `~Q(tipo='deposito') & Q(monto__lt=20000)` | 5 |
| `cuenta_destino__cliente__nombre='Ana García'` | 5 |
| Cuentas con `moneda__codigo='USD'` | 0003 y 0006 |
| Clientes con `cuentas__moneda__codigo='USD'` | Ana García y Diego Rojas |
| Clientes con `fichas_de_agenda__isnull=True` | Marta Vega |

**`NULL` frente a texto vacío:**

| Filtro | Clientes |
|---|---|
| `telefono__isnull=True` | Luis Pérez y Diego Rojas |
| `telefono=''` | Marta Vega |
| `telefono__isnull=False` | Ana García, Carla Soto y **Marta Vega** |
| `telefono__isnull=False` con `exclude(telefono='')` | Ana García y Carla Soto |

`isnull=False` cuenta como "con teléfono" a Marta, que en realidad no tiene. Para detectar un teléfono escrito hay que descartar también el texto vacío.

Los querysets son perezosos: no consultan la base hasta que se usan, y `.query` muestra el SQL que se ejecutaría.

![Operadores de campo](docs/capturas/24_filtros_operadores.png)

![exclude y Q](docs/capturas/25_filtros_exclude_q.png)

![Filtros a través de relaciones](docs/capturas/26_filtros_relaciones.png)

![NULL frente a texto vacío](docs/capturas/27_filtros_null_vacio.png)

![Orden, límite y SQL generado](docs/capturas/28_filtros_orden_sql.png)

#### 4.4 Anotaciones y agregaciones

`aggregate()` devuelve **un** resultado para toda la consulta. `annotate()` agrega un cálculo **por fila**, y combinado con `values()` lo hace **por grupo** (equivale a `GROUP BY`). Los montos en pesos y en dólares no se suman entre sí, por lo que los totales se filtran por moneda.

Resumen global de los movimientos en pesos:

| Cálculo | Resultado |
|---|---|
| Cantidad | 15 |
| Total | 815000 |
| Promedio | ≈ 54333,33 |
| Mayor y menor | 200000 y 5000 |
| Depósitos, transferencias y retiros | 610000, 130000 y 75000 (con `Sum(..., filter=Q(...))`) |

Por grupo y por fila:

| Consulta | Resultado |
|---|---|
| Movimientos por tipo (todas las monedas) | Depósito 8, retiro 3, transferencia 7 |
| Cuentas por cliente | Ana 2, Diego 2, Carla 1, Luis 1, Marta 1 |
| Contactos agendados por cliente | Ana 2, Carla 1, Diego 1, Luis 1, Marta 0 |
| Clientes con más de una cuenta (`num_cuentas__gt=1`) | Ana García y Diego Rojas |

**La trampa del saldo.** Calcular las entradas y las salidas con dos `Sum` en un mismo `annotate` da resultados inflados. Django une las dos relaciones y cada movimiento se repite tantas veces como filas tiene el otro lado. La cuenta `0001` tiene 3 entradas y 2 salidas: cada entrada se cuenta 2 veces y cada salida 3 veces.

| Cuenta | Entradas calculadas | Salidas calculadas | Entradas reales | Salidas reales |
|---|---|---|---|---|
| 0001 | 320000 | 135000 | 160000 | 45000 |
| 0004 | 675000 | 255000 | 225000 | 85000 |
| 0005 | 350000 | 100000 | 175000 | 50000 |
| 0007 | 240000 | 50000 | 120000 | 25000 |

Las cuentas con pocos movimientos salen bien, por lo que el error pasa desapercibido hasta revisar una cuenta con entradas y salidas múltiples.

`Sum(distinct=True)` tampoco sirve: la cuenta `0002` recibió dos veces 30000 y contaría uno solo.

**Solución:** dos subconsultas (`Subquery`), una para lo que entró y otra para lo que salió, y una resta. Se calcula en una sola consulta, y el resultado coincide con la propiedad `Cuenta.saldo` en las siete cuentas.

![aggregate](docs/capturas/29_aggregate.png)

![Agrupación por tipo](docs/capturas/30_group_by_tipo.png)

![annotate sobre clientes](docs/capturas/31_annotate_clientes.png)

![La trampa del saldo](docs/capturas/32_saldo_trampa.png)

![Saldo correcto con subconsultas](docs/capturas/33_saldo_subqueries.png)

#### 4.5 SQL propio: `raw()` y cursores

| Herramienta | Devuelve | Cuándo conviene |
|---|---|---|
| `raw()` | Objetos del modelo (con `.nombre`, `.email`, etc.) | Cuando se quiere seguir usando el modelo |
| Cursor | Filas planas (tuplas) | Reportes, conteos y modificaciones directas |

```python
# raw(): devuelve objetos Cliente; los valores van siempre como parámetros (%s)
consulta = "SELECT * FROM gestion_cliente WHERE nombre LIKE %s ORDER BY nombre"
Cliente.objects.raw(consulta, ['%a%'])

# Cursor: devuelve filas planas; "with" lo cierra al terminar
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM gestion_cliente")
    total = cursor.fetchone()[0]
```

**Resultados:**

| Prueba | Resultado |
|---|---|
| `telefono IS NOT NULL` (ejemplo de la consigna) | Ana, Carla y **Marta** (teléfono vacío) |
| Con `AND telefono <> ''` | Ana y Carla |
| Inyección SQL con texto pegado en el SQL | 5 clientes (devuelve todos) |
| El mismo texto como parámetro `%s` | 0 clientes |
| Columna extra `COUNT(...) AS num_cuentas` | Disponible como `cliente.num_cuentas` |
| `SELECT` sin la clave primaria | `FieldDoesNotExist: Raw query must include the primary key` |
| Saldo por cuenta con cursor | Igual al del ORM en las siete cuentas |
| `UPDATE ... WHERE numero = %s` con cursor | `rowcount` = 1; se revirtió después |

Los parámetros `%s` tratan el valor como dato y nunca como código SQL. Pegar el texto dentro de la consulta permite que un valor malicioso cambie su condición, como ocurrió con el ejemplo de inyección.

El cursor y `raw()` no pasan por `clean()` ni por la lógica del modelo, por lo que las modificaciones de datos de la aplicación irán por el ORM.

![raw() básico](docs/capturas/34_raw_basico.png)

![Parámetros e inyección SQL](docs/capturas/35_raw_parametros.png)

![Columnas extra y clave primaria](docs/capturas/36_raw_columnas_extra.png)

![Saldos con cursor](docs/capturas/37_cursor_saldos.png)

![UPDATE con cursor](docs/capturas/38_cursor_update.png)

#### 4.6 Consultas reutilizables y comando `demo_consultas`

Las consultas quedaron como funciones en `gestion/consultas.py`, que se reutilizarán en las vistas de la etapa 6.

| Función | Técnica |
|---|---|
| `movimientos_recientes(dias)` | `filter` con fecha |
| `movimientos_de_cliente(cliente)` | `Q` con O sobre origen y destino |
| `clientes_con_telefono()` | `exclude` de `NULL` y de texto vacío |
| `clientes_sin_contactos()` | `isnull` sobre una relación inversa |
| `clientes_con_numero_de_cuentas()` | `annotate` con `Count` |
| `resumen_por_tipo(moneda)` | `values` más `annotate`, filtrado por moneda |
| `cuentas_con_saldo()` | `annotate` con `Subquery` |
| `clientes_con_telefono_sql()` | `raw()` |
| `buscar_clientes_sql(texto)` | `raw()` con parámetros |
| `saldos_sql()` | Cursor con SQL puro |

El comando `python manage.py demo_consultas` ejecuta las diez y termina con un control que compara el saldo del ORM con el del SQL puro (`coinciden todas las cuentas: True`).

**Resultados, idénticos en SQLite y PostgreSQL:**

| Consulta | Resultado |
|---|---|
| Movimientos de los últimos 14 días | 8 (depende de la fecha) |
| Movimientos de Ana García | 7 (tres depósitos y cuatro transferencias) |
| Clientes con teléfono escrito | Ana García y Carla Soto |
| Clientes sin contactos | Marta Vega |
| Resumen en CLP | Depósito 6 (610000), retiro 3 (75000), transferencia 6 (130000) |
| Resumen en USD | Depósito 2 (800), transferencia 1 (100) |
| Nombres que contienen "ar" (`raw`) | Ana García, Carla Soto y Marta Vega |
| Saldos por cuenta | Los de la tabla de la sección 4.1 |

La única diferencia entre motores es el formato de los decimales: PostgreSQL muestra los montos con dos decimales (`115000.00`) y SQLite los muestra sin ellos (`115000`). El valor es el mismo.

![demo_consultas en SQLite](docs/capturas/39_demo_consultas_sqlite.png)

![demo_consultas en PostgreSQL](docs/capturas/40_demo_consultas_postgresql.png)

**Incidencia resuelta: adaptador de PostgreSQL bloqueado.** Al probar `demo_consultas` en PostgreSQL apareció este error:

```text
ImportError: DLL load failed while importing _psycopg: Una directiva de Control de aplicaciones bloqueó este archivo.
django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 or psycopg module
```

Es la misma política de Windows que bloqueaba `pip.exe` en la etapa 0: impide cargar el archivo compilado de `psycopg2`. Django admite también `psycopg` (versión 3), que se instala sin archivos compilados propios y usa el `libpq.dll` que ya trae PostgreSQL.

```powershell
# Instala el adaptador de PostgreSQL en Python puro (versión 3)
python -m pip install psycopg

# Verifica que carga; debe imprimir la versión y la palabra "python"
python -c "import psycopg; print(psycopg.__version__, psycopg.pq.__impl__)"

# Retira el adaptador bloqueado y actualiza la lista de dependencias
python -m pip uninstall psycopg2-binary -y
python -m pip freeze | Out-File -Encoding utf8 requirements.txt
```

No fue necesario cambiar `settings.py`: el motor `django.db.backends.postgresql` prueba primero `psycopg` y recurre a `psycopg2` solo si no lo encuentra. La consigna menciona `psycopg2` como ejemplo de adaptador; `psycopg` cumple el mismo papel.

**Reflexiones:**

- **ORM frente a SQL propio:** el ORM resuelve casi todo y evita errores de sintaxis. El SQL propio ayuda a entender qué hay debajo y a escribir consultas complejas, como el saldo, que pueden hacerse igual con subconsultas del ORM.
- **`NULL` no es lo mismo que texto vacío:** un formulario guarda un teléfono sin completar como `''`. La consulta de la consigna (`IS NOT NULL`) lo cuenta como si existiera. Hay que descartar ambos casos.
- **Las agregaciones pueden mentir sin avisar:** dos `Sum` sobre relaciones distintas dan montos inflados sin ningún error. Conviene contrastar siempre con una cuenta conocida.
- **Seguridad:** los parámetros `%s` son lo que separa una consulta segura de una vulnerable a inyección.
- **Las validaciones no se aplican siempre:** `create()`, `update()` masivo y el cursor no ejecutan `clean()`. Solo actúan las restricciones de la base de datos. Las reglas de Python se aplican con `full_clean()`, en formularios y en el panel de administración.
- **Sin dependencia del motor:** las diez consultas dan los mismos resultados con SQLite y con PostgreSQL, cada uno con su adaptador.

## Flujo de Git

| Rama | Propósito | Estado |
|---|---|---|
| `main` | Código estable | Activa |
| `feature/modelos` | Definición de modelos y migraciones | Fusionada con `main` (fast-forward) |
| `feature/consultas` | Datos de demostración y consultas personalizadas | Fusionada con `main` |
| `feature/crud` | Vistas y formularios | Pendiente |

## Próximas etapas

Las secciones sobre panel de administración, CRUD, autenticación, pruebas y demostración se agregarán a medida que se completen las etapas correspondientes.
