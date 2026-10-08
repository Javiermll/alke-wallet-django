# Alke Wallet

Billetera digital desarrollada con Django para el proyecto final del **Módulo 7: Acceso a datos en aplicaciones Django** (Full Stack Python Trainee, Talento Digital / Alkemy).

Alke Wallet permite crear y gestionar cuentas digitales, registrar depósitos, retiros y transferencias, guardar contactos frecuentes, consultar saldos y generar reportes. Usa el ORM de Django, migraciones y las aplicaciones preinstaladas del framework, y funciona con SQLite en desarrollo y PostgreSQL en producción.

![Portada de Alke Wallet](docs/vista_previa/escritorio_portada.png)

**Contenido:** [Funciones](#funciones) · [Requisitos del proyecto](#requisitos-del-proyecto-y-dónde-están) · [Tecnologías](#tecnologías) · [Instalación](#instalación-y-ejecución-local) · [Pruebas](#pruebas) · [Arquitectura](#arquitectura) · [Modelo de datos](#modelo-de-datos) · [Documentación por etapa](#documentación-por-etapa) · [Autor](#autor)

## Funciones

- **Clientes y cuentas:** alta, ficha, edición y eliminación con vistas basadas en clases. Cada cuenta muestra su saldo, calculado desde los movimientos.
- **Movimientos:** depósitos, retiros y transferencias con validación de saldo, registro atómico y listado con filtros y paginación.
- **Contactos:** agenda de contactos por cliente, con atajo para transferir.
- **Reporte general:** movimientos por tipo, saldos por cliente y movimientos por mes, separados por moneda.
- **Roles y seguridad:** todo es privado salvo el login y el registro. El personal administra todo; cada cliente ve y toca solo lo suyo. Los formularios exigen token CSRF.
- **Registro y perfil:** una persona crea su usuario, su ficha y su primera cuenta, y puede cambiar su contraseña.
- **Panel de administración** de Django con columnas, búsqueda y filtros.
- **Interfaz moderna y adaptable:** Bootstrap 5, portada de presentación con el inicio de sesión y el registro en la misma pantalla, y diseño pensado para escritorio, tablet y celular.
- **Páginas de error propias** (403, 404 y 500) y una **ventana de espera** al iniciar sesión o registrarse, que explica la demora cuando el servidor gratuito estaba dormido.
- **Publicada en Render** con PostgreSQL en Neon: configuración por variables de entorno, archivos estáticos con WhiteNoise, HTTPS y script de construcción. Demostración en línea: <https://alke-wallet.onrender.com>.
- **244 pruebas automatizadas** y un informe de pruebas.

## Demostración en línea

**<https://alke-wallet.onrender.com>** (Render, plan gratuito, con la base de datos en Neon).

- **Primera visita:** el servidor gratuito se duerme tras 15 minutos sin visitas, así que la primera carga puede tardar cerca de un minuto. Después responde con normalidad. Al iniciar sesión o registrarse, una ventana de espera explica la demora.
- **Cómo probarla:** lo más directo es crear una cuenta propia desde "Crear cuenta": el registro es público, toma menos de un minuto y abre una primera cuenta con saldo cero. También existen usuarios de demostración (`ana`, `luis`, `carla`, `diego` y `marta`) con datos de ejemplo; su clave se define con la variable `CLAVE_DEMO` en el panel de Render y no está escrita en el repositorio, por lo que se entrega por separado a quien la necesite.
- **Panel de administración** (`/admin/`): privado, con clave solo del autor.

## Requisitos del proyecto y dónde están

| Requisito | Dónde se cumple |
|---|---|
| CRUD con vistas basadas en clases | [Etapa 6](#etapa-6-pantallas-con-vistas-basadas-en-clases) |
| Protección CSRF en los formularios | Etapas 6 y 7; comprobada en las [pruebas de seguridad](#etapa-8-pruebas-automatizadas) |
| Modelos con relaciones 1:1, N:1 y N:M | [Modelo de datos](#modelo-de-datos) y [Etapa 2](#etapa-2-app-gestion-y-modelos) |
| Migraciones | [Etapa 3](#etapa-3-migraciones) |
| Consultas personalizadas (`filter`, `annotate`, `raw()`, cursores) | [Etapa 4](#etapa-4-consultas-personalizadas) |
| SQLite en desarrollo y PostgreSQL en producción | [Etapa 1](#etapa-1-conexión-a-la-base-de-datos) y [Etapa 3](#etapa-3-migraciones) |
| Ramas de Git por funcionalidad | [Flujo de Git](#flujo-de-git) |
| Pruebas e informe de pruebas | [Pruebas](#pruebas) y [`docs/informe_pruebas.docx`](docs/informe_pruebas.docx) |
| Diseño responsive con Bootstrap | [Etapa 9](#etapa-9-mejora-visual-con-bootstrap) |
| Preparación para publicar en Render y Neon | [Etapa 10](#etapa-10-preparación-para-el-despliegue-en-render) |
| README | Este documento |

## Estado del proyecto

| Etapa | Descripción | Estado |
|---|---|---|
| 0 | Entorno virtual, instalación de Django y repositorio Git | Completada |
| 1 | Conexión a base de datos (SQLite y PostgreSQL) | Completada |
| 2 | App `gestion` y modelos | Completada |
| 3 | Migraciones en SQLite y PostgreSQL | Completada |
| 4 | Consultas personalizadas (`filter`, `exclude`, `annotate`, `raw()`, cursores) | Completada |
| 5 | Panel de administración | Completada |
| 6 | Vistas CRUD basadas en clases y templates | Completada |
| 7 | Autenticación, archivos estáticos, roles, alcance por usuario, registro y perfil | Completada |
| 8 | Pruebas automatizadas (239 pruebas en esa etapa; hoy son 244) e informe de pruebas | Completada |
| 9 | Mejora visual con Bootstrap: portada, diseño responsive, componentes y páginas de error | Completada |
| 10 | Preparación y despliegue en Render y Neon | Completada |
| 11 | Revisión final, README final y publicación | En curso |

## Tecnologías

| Herramienta | Versión | Uso |
|---|---|---|
| Python | 3.14.6 | Lenguaje base |
| Django | 6.1.1 | Framework web |
| psycopg (`psycopg[binary]`) | 3.3.6 | Adaptador entre Django y PostgreSQL (reemplaza a `psycopg2-binary`; ver incidencia de la etapa 4). La variante `[binary]` evita compilarlo al desplegar |
| python-dotenv | 1.2.3 | Lectura de credenciales desde el archivo `.env` |
| PostgreSQL | 17 | Base de datos de producción |
| SQLite | incluido en Python | Base de datos de desarrollo |
| Bootstrap | 5.3.3 (CDN) | Sistema de diseño de la interfaz: rejilla, tarjetas, tablas, formularios y menú |
| Bootstrap Icons | 1.11.3 (CDN) | Íconos de la interfaz |
| Inter (Google Fonts) | - | Tipografía |
| gunicorn | 26.2.0 | Servidor que ejecuta la aplicación en producción (solo en Linux; no corre en Windows) |
| WhiteNoise | 6.12.0 | Sirve los archivos estáticos desde la propia aplicación |
| dj-database-url | 3.1.2 | Convierte la variable `DATABASE_URL` en la configuración de base de datos de Django |
| Render | plan gratuito | Alojamiento de la aplicación en línea |
| Neon | plan gratuito | PostgreSQL en la nube para producción |
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
# Base de datos: sqlite (desarrollo y pruebas) o postgres (producción)
DB_ENGINE=sqlite

# Datos de conexión a PostgreSQL (solo se usan si DB_ENGINE=postgres)
DB_NAME=alke_wallet
DB_USER=postgres
DB_PASSWORD=escribe_aqui_tu_contraseña
DB_HOST=localhost
DB_PORT=5432

# Clave para los usuarios de demostración (opcional; si falta, poblar_datos genera una al azar)
CLAVE_DEMO=
```

Para usar PostgreSQL, crear antes la base de datos vacía (`CREATE DATABASE alke_wallet;`) y cambiar `DB_ENGINE=postgres`.

En producción (Render) no se usa este archivo: las variables `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL` y `DJANGO_SUPERUSER_*` se cargan en el panel del servicio. Están descritas en la [etapa 10](#etapa-10-preparación-para-el-despliegue-en-render). Si no existen, el proyecto usa los valores de desarrollo y funciona igual en local.

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

### 7. Crear un superusuario (para el panel de administración)

```powershell
# Crea la cuenta con la que se entra al panel (pide usuario, correo y contraseña)
python manage.py createsuperuser
```

### 8. Ejecutar el servidor

```powershell
# Levanta el servidor de desarrollo en http://127.0.0.1:8000/
python manage.py runserver
```

Las pantallas de la aplicación están en `http://127.0.0.1:8000/` (inicio), `/clientes/`, `/cuentas/`, `/transacciones/`, `/reporte/` y `/perfil/`. El panel de administración está en `http://127.0.0.1:8000/admin/`.

Todas las pantallas piden iniciar sesión, salvo el login (`/acceso/login/`) y el registro (`/registro/`). Para probar los distintos roles:

| Rol | Con qué usuario | Qué ve |
|---|---|---|
| Personal | El superusuario del paso 7 | Todas las pantallas, el reporte y el panel de administración |
| Cliente | `ana`, `luis`, `carla`, `diego` o `marta` (los crea `poblar_datos`) | Solo sus propias cuentas, movimientos y agenda |
| Sin cliente | Un usuario creado en el panel sin ficha de cliente | Solo el perfil y un aviso en el inicio |

Al crear los usuarios de ejemplo, `poblar_datos` genera una clave aleatoria y la muestra una sola vez en pantalla. Si se prefiere una clave propia para la demostración, se define en el archivo `.env` con la variable `CLAVE_DEMO` (ese archivo no se sube al repositorio). El código no contiene ninguna clave escrita. En la demostración en línea la clave se define con la variable `CLAVE_DEMO` en el panel de Render.

Con `DEBUG=True`, las tres páginas de error se pueden previsualizar en `http://127.0.0.1:8000/vista-403/`, `/vista-404/` y `/vista-500/`. Esas rutas solo existen en desarrollo; con `DEBUG=False` Django usa directamente `403.html`, `404.html` y `500.html`.

Para verificar los accesos y la protección CSRF en cualquier momento:

```powershell
# Prueba roles, alcance por usuario y CSRF con datos temporales (no deja nada en la base de datos)
python manage.py verificar_accesos
```

## Pruebas

El proyecto tiene **244 pruebas automatizadas** en `gestion/tests/`, un archivo por bloque: modelos, servicios, consultas, formularios, vistas, seguridad, la comprobación de salud (`test_salud.py`) y el comando `crear_superusuario` (`test_comandos.py`). Se ejecutan con SQLite (deja `DB_ENGINE=sqlite` en `.env`):

```powershell
# Ejecuta todas las pruebas; Django usa una base temporal y no toca tus datos
python manage.py test gestion

# Ejecuta un bloque con detalle
python manage.py test gestion.tests.test_seguridad -v 2
```

Resultado esperado: `Ran 244 tests` y `OK`. Las primeras 239 son las de la [etapa 8](#etapa-8-pruebas-automatizadas) y están documentadas, junto con la verificación de que detectan fallos, en [`docs/informe_pruebas.docx`](docs/informe_pruebas.docx). Las 5 restantes se agregaron en la [etapa 10](#etapa-10-preparación-para-el-despliegue-en-render): 1 del endpoint `/salud/` y 4 del comando `crear_superusuario`.

**Instalación desde cero comprobada:** se clonó el repositorio en otra carpeta, se creó un entorno virtual nuevo, se instalaron las dependencias, se copió `.env.example` a `.env`, se aplicaron las migraciones, se cargaron los datos de ejemplo y las pruebas (239 en ese momento) terminaron en `OK`.

![Instalación desde cero y pruebas en una copia limpia](docs/capturas/143_instalacion_desde_cero.png)

## Arquitectura

```text
alke_wallet/
├── core/                      # Paquete de configuración del proyecto
│   ├── settings.py            # Configuración general; en producción lee su valor desde variables de entorno
│   ├── urls.py                # Rutas principales (login, registro, salud y vistas previas de errores en desarrollo)
│   ├── formats/es_CL/         # Formato de números chileno: punto como separador de miles y coma decimal
│   ├── asgi.py
│   └── wsgi.py
├── gestion/                   # App principal con la lógica del negocio
│   ├── management/
│   │   └── commands/
│   │       ├── poblar_datos.py        # Carga datos de demostración sin duplicar
│   │       ├── demo_consultas.py      # Ejecuta y muestra todas las consultas
│   │       ├── verificar_accesos.py   # Prueba roles, alcance por usuario y CSRF (no deja datos)
│   │       └── crear_superusuario.py  # Crea el administrador desde variables de entorno (despliegue)
│   ├── migrations/
│   │   ├── 0001_initial.py    # Migración inicial: crea las 5 tablas de la app
│   │   └── 0002_alter_cliente_options_alter_contacto_options_and_more.py  # Nombres legibles (sin cambios en las tablas)
│   ├── templatetags/
│   │   └── ui.py              # Filtros que aplican las clases de Bootstrap a los campos de un formulario
│   ├── models.py              # Modelos: Moneda, Cliente, Contacto, Cuenta, Transaccion
│   ├── consultas.py           # Consultas reutilizables: ORM, raw() y cursor (12 funciones)
│   ├── servicios.py           # registrar_transaccion() atómica con bloqueo; crear_cliente_con_cuenta() para el registro
│   ├── mixins.py              # Roles: SoloPersonalMixin y PersonalOClienteMixin
│   ├── alcance.py             # Filtros por dueño: cada cliente ve solo lo suyo
│   ├── forms.py               # Formularios de clientes, cuentas, transacciones, contactos y registro
│   ├── admin.py               # Panel de administración: columnas, búsqueda, filtros y tablas anidadas
│   ├── views.py               # Vistas basadas en clases: CRUD, inicio, reporte, registro, perfil y salud
│   ├── urls.py                # Rutas de la app, con nombre
│   └── tests/                 # Pruebas automatizadas, un archivo por bloque (244 en total)
├── templates/
│   ├── base.html              # Plantilla común: menú, mensajes y pie de página
│   ├── inicio.html            # Página de inicio (distinta para personal y clientes)
│   ├── reporte.html           # Reporte general con barras de proporción
│   ├── perfil.html            # Datos de acceso y de cliente de la persona con sesión
│   ├── 403.html, 404.html     # Páginas de error que heredan de base.html
│   ├── 500.html               # Error del servidor: documento independiente, sin depender de la sesión ni del menú
│   ├── componentes/           # Piezas reutilizables: campos de formulario, etiquetas, avisos y lista de movimientos para celular
│   ├── registration/          # landing (portada), login, registro y cambiar_clave
│   ├── clientes/              # lista, detalle, formulario y confirmar_eliminar
│   ├── cuentas/               # lista, detalle, formulario y confirmar_eliminar
│   ├── transacciones/         # lista, detalle y formulario
│   └── contactos/             # formulario y confirmar_eliminar
├── static/
│   ├── css/estilos.css        # Capa de marca sobre Bootstrap: colores, tarjetas, portada, pie y animaciones
│   ├── js/app.js              # Ver contraseña, evitar doble envío, avisos que se cierran y ventana de espera
│   └── img/logo.svg           # Logo
├── docs/
│   ├── capturas/              # Capturas de pantalla usadas en este README
│   ├── vista_previa/          # Capturas del nuevo diseño en escritorio, tablet y celular
│   └── informe_pruebas.docx   # Informe de pruebas con casos, resultados y evidencias
├── build.sh                   # Script de construcción para Render (instala, migra, crea el administrador y carga datos)
├── render.yaml                # Plano del servicio en Render
├── .gitattributes             # Fuerza saltos de línea LF en los scripts (Linux falla con los de Windows)
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

El comando `python manage.py demo_consultas` ejecuta las diez consultas de esta etapa (en la etapa 6 se sumaron dos funciones más para el reporte, hasta las 12 que tiene hoy `consultas.py`) y termina con un control que compara el saldo del ORM con el del SQL puro (`coinciden todas las cuentas: True`).

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
- **`NULL` no es lo mismo que texto vacío:** pueden convivir en la misma columna (en los datos de demostración, Marta tiene `''` y Luis tiene `NULL`). Un formulario de Django guarda `NULL` cuando se deja vacío un campo de texto que admite `NULL`, pero los datos que llegan por otra vía pueden traer `''`. La consulta de la consigna (`IS NOT NULL`) cuenta como si tuviera teléfono a quien tiene `''`. Hay que descartar ambos casos.
- **Las agregaciones pueden mentir sin avisar:** dos `Sum` sobre relaciones distintas dan montos inflados sin ningún error. Conviene contrastar siempre con una cuenta conocida.
- **Seguridad:** los parámetros `%s` son lo que separa una consulta segura de una vulnerable a inyección.
- **Las validaciones no se aplican siempre:** `create()`, `update()` masivo y el cursor no ejecutan `clean()`. Solo actúan las restricciones de la base de datos. Las reglas de Python se aplican con `full_clean()`, en formularios y en el panel de administración.
- **Sin dependencia del motor:** las diez consultas dan los mismos resultados con SQLite y con PostgreSQL, cada uno con su adaptador.

### Etapa 5: panel de administración

**Objetivo:** aprovechar `django.contrib.admin` para administrar los datos sin programar pantallas: configurar el idioma, registrar los modelos con columnas, búsqueda y filtros, y crear un superusuario.

**Rama de trabajo:** `feature/admin`. Esta etapa agrega una segunda migración, la `0002`, que no modifica ninguna tabla.

**Decisiones:**

| Tema | Elegida | Alternativa descartada | Motivo |
|---|---|---|---|
| Idioma y zona horaria | `es-cl` y `America/Santiago` | Inglés y UTC | El panel y los mensajes de validación salen en español, y las fechas en hora local |
| Nombres de los modelos | `verbose_name` en cada `Meta`, con la migración `0002` | Dejar los nombres por defecto | Sin esto, el panel mostraría "Transaccions" y "Gestion" |
| Saldo en el panel | `cuentas_con_saldo()` de la etapa 4 | La propiedad `Cuenta.saldo` | Una sola consulta para todo el listado, en vez de dos por cuenta |
| Superusuario | Crearlo en cada base de datos | Crearlo solo en una | Cada base guarda sus propios usuarios |

#### 5.1 Idioma y zona horaria

```python
# Idioma del sitio: español de Chile; afecta al panel de administración y a los mensajes de validación
LANGUAGE_CODE = 'es-cl'

# Zona horaria para mostrar las fechas; la base de datos sigue guardando en UTC porque USE_TZ es True
TIME_ZONE = 'America/Santiago'
```

| Comprobación | Resultado |
|---|---|
| `python manage.py check` | Sin problemas |
| `timezone.localtime()` | La hora actual, terminada en `-03:00` (horario de verano de Chile) |
| `gettext('This field is required.')` | `Este campo es obligatorio.` |

La zona horaria solo cambia cómo se **muestran** las fechas: la base de datos sigue guardándolas en UTC, por lo que las consultas de la etapa 4 no se ven afectadas. Django no trae una traducción propia para Chile y usa la del español general.

![Idioma y zona horaria en settings.py](docs/capturas/41_settings_idioma_zona.png)

![Pantalla de inicio de sesión del panel, en español](docs/capturas/42_admin_login_es.png)

#### 5.2 Nombres legibles y migración `0002`

Cada modelo recibió su nombre en singular y plural dentro de `class Meta`:

```python
# Nombres legibles que se muestran en el panel de administración
class Meta:
    verbose_name = 'transacción'
    verbose_name_plural = 'transacciones'
    ordering = ['-fecha']
```

El nombre de la app se definió en `gestion/apps.py`:

```python
class GestionConfig(AppConfig):
    name = 'gestion'
    # Nombre que se muestra en el menú del panel de administración
    verbose_name = 'Gestión'
```

| Comando | Resultado |
|---|---|
| `makemigrations gestion` | Crea `0002_alter_cliente_options_alter_contacto_options_and_more.py`, con cinco líneas `~ Change Meta options on ...` |
| `sqlmigrate gestion 0002` | Solo comentarios `-- (no-op)`: ningún cambio en las tablas |
| `migrate` | `Applying gestion.0002_... OK` (en SQLite y en PostgreSQL) |
| `showmigrations gestion` | `[X] 0001_initial` y `[X] 0002_...` |
| `makemigrations --check --dry-run` | `No changes detected` |

Django guarda los nombres legibles dentro de las migraciones, por eso cambiarlos genera una migración nueva, aunque no ejecute SQL. Es un ejemplo del historial versionado del esquema.

![Migración 0002 generada y su SQL vacío](docs/capturas/43_migracion_0002.png)

![Migración 0002 aplicada](docs/capturas/44_migrate_0002.png)

#### 5.3 Registro de los modelos: `gestion/admin.py`

| Modelo | Columnas | Búsqueda | Filtros | Extra |
|---|---|---|---|---|
| `Moneda` | código, nombre, símbolo | código, nombre | | |
| `Cliente` | nombre, email, teléfono, cantidad de cuentas | nombre, email, usuario de login | | Sus cuentas y contactos aparecen dentro de su ficha |
| `Cuenta` | número, cliente, moneda, saldo, activa, fecha | número, nombre y email del dueño | moneda, activa | Saldo calculado en una sola consulta |
| `Transaccion` | id, tipo, origen, destino, monto, descripción, fecha | descripción, números de cuenta | tipo | Navegación por año, mes y día |
| `Contacto` | propietario, agendado, apodo, fecha | los dos nombres y el apodo | | |

Tres piezas nuevas:

| Pieza | Para qué sirve |
|---|---|
| Inline (`TabularInline`) | Muestra una tabla relacionada dentro de otra ficha: las cuentas y los contactos de cada cliente |
| `get_queryset` | Cambia qué registros trae el listado, para reutilizar las consultas de la etapa 4 |
| `@admin.display` | Convierte un método en una columna del listado, ordenable con un clic |

```python
# Los contactos del cliente, en una tabla dentro de su ficha
class ContactoInline(admin.TabularInline):
    model = Contacto
    # Contacto tiene dos claves hacia Cliente; fk_name dice cuál une con esta ficha
    fk_name = 'propietario'
    fields = ('agendado', 'apodo')
    extra = 0
```

```python
# En CuentaAdmin: el listado reutiliza la consulta de la etapa 4, que calcula todos los saldos de una vez
def get_queryset(self, request):
    return consultas.cuentas_con_saldo().select_related('cliente', 'moneda')

# Columna del saldo, ordenable con un clic en su título
@admin.display(description='Saldo', ordering='saldo_calculado')
def saldo_actual(self, obj):
    # Una cuenta nueva todavía no tiene el saldo calculado, así que se muestra un guion
    return getattr(obj, 'saldo_calculado', '-')
```

`Contacto` tiene dos claves hacia `Cliente` (propietario y agendado), por eso el inline necesita `fk_name`: sin él, Django no sabría cuál usar.

![Configuración de admin.py](docs/capturas/45_admin_py.png)

![Modelos registrados en el panel](docs/capturas/46_admin_registrados.png)

#### 5.4 Superusuario y recorrido del panel

```powershell
# Crea la cuenta de administración (pide usuario, correo y contraseña)
python manage.py createsuperuser
```

Los clientes de demostración (Ana, Luis, etc.) son usuarios comunes y no pueden entrar al panel: solo lo hace el personal. El superusuario se creó en SQLite y en PostgreSQL, porque cada base guarda sus propios usuarios.

**Recorrido del panel:**

| Pantalla | Resultado |
|---|---|
| Inicio | Dos grupos: Autenticación y autorización, y Gestión (Clientes, Contactos, Cuentas, Monedas, Transacciones) |
| Clientes | 5 clientes, del más nuevo al más antiguo, con su cantidad de cuentas (ordenable) |
| Ficha de Ana García | Tablas con sus cuentas `0001` (CLP) y `0003` (USD) y sus contactos Lucho y Carli |
| Cuentas | Saldos iguales a los de la etapa 4; filtro por moneda; orden por saldo |
| Transacciones | 18 movimientos; filtro por tipo (3 retiros); navegación por fecha; búsqueda por número de cuenta |
| Contactos | 5 fichas |

**Ejercicio de CRUD en el panel**, con un cliente temporal (usuario `tomas`, cuenta `0009`):

| Operación | Resultado |
|---|---|
| Crear | Usuario, cliente con su cuenta (tabla anidada) y un depósito de 25000; el saldo de la `0009` pasa a 25000 |
| Editar | Cambio de teléfono del cliente y desactivación de la cuenta |
| Validar | Los casos inválidos se rechazan con su mensaje (tabla siguiente) |
| Borrar | Borrar una cuenta con movimientos muestra una pantalla de protección; al borrar primero el depósito y luego el usuario, el cliente y su cuenta se borran en cascada. *Desde la etapa 6.1 el panel ya no permite borrar movimientos; para repetir este ejercicio, el depósito de prueba se borra desde la shell* |

Al terminar, la base volvió a tener 5 clientes, 7 cuentas y 18 movimientos.

**Validaciones de `clean()` en los formularios del panel:**

| Caso | Mensaje |
|---|---|
| Depósito con cuenta origen | `Un depósito no debe tener cuenta origen.` |
| Retiro sin cuenta origen | `Un retiro necesita una cuenta origen.` |
| Transferencia entre monedas distintas | `Las cuentas deben tener la misma moneda.` |
| Transferencia a la misma cuenta | `La cuenta origen y la destino deben ser distintas.` |
| Monto cero | `Asegúrese de que este valor es mayor o igual a 0.01.` |
| Contacto a sí mismo | `Un cliente no puede agendarse a sí mismo.` |
| Contacto duplicado | `Contacto con este Propietario y Agendado ya existe.` |

Esto confirma lo que quedó pendiente de la etapa 3: las reglas de `clean()` no actúan al crear desde la shell, pero sí en los formularios.

![Inicio del panel](docs/capturas/47_admin_inicio.png)

![Listado de clientes con su cantidad de cuentas](docs/capturas/48_admin_clientes.png)

![Ficha de un cliente con sus tablas anidadas](docs/capturas/49_admin_cliente_inlines.png)

![Listado de cuentas con saldos y filtros](docs/capturas/50_admin_cuentas_saldo.png)

![Listado de transacciones con filtro y navegación por fecha](docs/capturas/51_admin_transacciones.png)

![Validación en un formulario del panel](docs/capturas/52_admin_validaciones.png)

![Borrado protegido de una cuenta con movimientos](docs/capturas/53_admin_borrado_protegido.png)

![Panel funcionando sobre PostgreSQL](docs/capturas/54_admin_postgresql.png)

**Limitaciones conocidas del panel:**

- **No revisaba el saldo disponible** (resuelto en la etapa 6.1): un retiro o una transferencia mayor que el saldo se guardaba y dejaba la cuenta en negativo. Ahora la regla vive en el modelo y se aplica también en el panel.
- **El superusuario no tiene un `Cliente` asociado.** Las pantallas de usuario que dependan de `request.user.cliente` deberán contemplar ese caso. *(Resuelto en la etapa 7: el personal ve todo y un usuario sin cliente recibe un aviso.)*

**Reflexiones:**

- **Mucho resultado con poco código:** el panel completo, con búsqueda, filtros, tablas anidadas y validaciones, salió de unas 140 líneas en `admin.py`, reutilizando los modelos y las consultas.
- **Las validaciones del modelo se aprovechan solas:** `clean()` y las restricciones definidas en la etapa 2 actúan en el panel sin escribir nada más.
- **`PROTECT` y `CASCADE` se ven en acción:** el panel explica por qué no se puede borrar una cuenta con historial y qué se borraría en cascada, antes de confirmar.
- **Reutilizar consultas:** `cuentas_con_saldo()` sirve en el panel igual que en el comando de demostración, lo que justifica haberla dejado como función.

### Etapa 6: pantallas con vistas basadas en clases

**Objetivo:** construir las pantallas de la aplicación: CRUD con vistas basadas en clases, rutas dinámicas, formularios protegidos con CSRF y templates que heredan de una plantilla común.

**Rama de trabajo:** `feature/crud`. Esta etapa no cambia los modelos, por lo que no genera migraciones.

**Cómo funciona cada pantalla:**

| Pieza | Para qué sirve | Archivo |
|---|---|---|
| Ruta | La dirección que escribe la persona | `gestion/urls.py` |
| Vista | Decide qué datos mostrar o guardar | `gestion/views.py` |
| Formulario | Define los campos y valida lo que se escribe | `gestion/forms.py` |
| Template | El HTML que ve la persona, con `{% csrf_token %}` en cada formulario | `templates/` |

**Rutas** (todas con nombre, usados como `{% url 'gestion:cliente_detalle' pk %}`):

| Sección | Rutas | Vistas |
|---|---|---|
| Inicio | `/` | `TemplateView` |
| Clientes | `/clientes/`, `/clientes/nuevo/`, `/clientes/<pk>/`, `/clientes/<pk>/editar/`, `/clientes/<pk>/eliminar/` | `ListView`, `CreateView`, `DetailView`, `UpdateView`, `DeleteView` |
| Cuentas | `/cuentas/`, `/cuentas/nueva/`, `/cuentas/<pk>/`, `/cuentas/<pk>/editar/`, `/cuentas/<pk>/eliminar/` | `ListView`, `CreateView`, `DetailView`, `UpdateView`, `DeleteView` |
| Transacciones | `/transacciones/`, `/transacciones/nueva/`, `/transacciones/<pk>/` | `ListView`, `FormView`, `DetailView` |
| Contactos | `/clientes/<pk>/contactos/nuevo/`, `/contactos/<pk>/eliminar/` | `CreateView`, `DeleteView` |
| Reporte | `/reporte/` | `TemplateView` |

`<pk>` es una parte variable de la dirección: Django la convierte en un número y se la entrega a la vista para identificar el registro.

**Decisiones:**

| Tema | Elegida | Motivo |
|---|---|---|
| Qué lleva CRUD completo | Clientes y cuentas. Las transacciones solo se listan, se ven y se crean | Los movimientos son el historial y el saldo se calcula con ellos |
| Regla del saldo | En `Transaccion.clean()`, solo al crear | Una sola regla para el panel y para las pantallas |
| Registro de movimientos | A través de `registrar_transaccion()`, con `transaction.atomic()` y bloqueo de la cuenta de origen | Evita que dos retiros simultáneos dejen una cuenta en negativo |
| Cuentas inactivas | No pueden enviar ni recibir movimientos nuevos | El campo `activa` ya existía y no tenía efecto |
| Crear un cliente | Selector con los usuarios que aún no tienen cliente | Más simple que crear usuario y cliente a la vez |
| Borrar con historial | Se captura `ProtectedError` y se muestra un mensaje claro | Evita una página de error 500 |
| Templates | Carpeta `templates/` en la raíz, con `base.html` compartido | Coincide con la consigna y comparte el diseño |
| Coherencia con el panel | Los movimientos son de solo lectura en el panel | Las mismas reglas en todos los accesos |

#### 6.1 Reglas de saldo y cuentas activas

Las reglas viven en el modelo, por lo que valen para el panel y para las pantallas. Solo se revisan al crear un movimiento: `self._state.adding` es `True` mientras el objeto no se ha guardado.

```python
# Reglas que solo se revisan al crear un movimiento nuevo, no al editar uno existente
if self._state.adding:
    # Una cuenta desactivada no puede enviar ni recibir movimientos nuevos
    if self.cuenta_origen is not None and not self.cuenta_origen.activa:
        raise ValidationError('La cuenta origen está inactiva.')
    if self.cuenta_destino is not None and not self.cuenta_destino.activa:
        raise ValidationError('La cuenta destino está inactiva.')

    # El monto puede estar vacío si falló su propia validación; en ese caso no se compara
    # Si sale dinero de una cuenta (retiro o transferencia), debe haber saldo suficiente
    if self.cuenta_origen is not None and self.monto is not None:
        disponible = self.cuenta_origen.saldo
        if disponible < self.monto:
            raise ValidationError(f'Saldo insuficiente: la cuenta origen tiene {disponible:.2f}.')
```

En el panel, `TransaccionAdmin` rechaza editar y borrar movimientos existentes (`has_change_permission` y `has_delete_permission`), por lo que se abren solo en modo lectura. Crear movimientos nuevos sigue funcionando, con las mismas reglas.

Prueba con `full_clean()` desde la shell, sin guardar nada (cuenta `0004` con saldo 140000 y `0005` con 125000):

| Caso | Resultado |
|---|---|
| Retiro de 100000 de la `0004` | Válido |
| Retiro de 150000 de la `0004` | `Saldo insuficiente: la cuenta origen tiene 140000.00.` |
| Transferencia de 200000 de la `0005` a la `0004` | `Saldo insuficiente: la cuenta origen tiene 125000.00.` |
| Transferencia de 1000 de la `0005` a la `0004` | Válido |
| Depósito de 50000 a la `0004` | Válido (un depósito no revisa saldo) |
| Depósito a una cuenta inactiva | `La cuenta destino está inactiva.` |
| Retiro desde una cuenta inactiva | `La cuenta origen está inactiva.` |
| Retiro sin monto | `Este campo no puede ser nulo.` (no un error de Python) |
| Retiro exacto del saldo (140000) | Válido |
| Retiro del saldo más un centavo | `Saldo insuficiente: la cuenta origen tiene 140000.00.` |

![Reglas del saldo probadas desde la shell](docs/capturas/55_regla_saldo_shell.png)

![Movimiento en modo lectura en el panel](docs/capturas/56_admin_movimiento_solo_lectura.png)

![Saldo insuficiente en el panel](docs/capturas/57_admin_saldo_insuficiente.png)

**Incidencia resuelta:** al pegar el método `clean()` nuevo, quedó con 4 espacios de más, dentro de `class Meta`. Django lo rechazó al arrancar con `'class Meta' got invalid attribute(s): clean`. `Meta` solo acepta opciones de configuración; `clean()` es un método del modelo y se alinea con `class Meta`, no dentro de ella.

#### 6.2 Estructura base: `templates/`, rutas y página de inicio

Django busca los templates en la carpeta `templates/` de la raíz, gracias a esta línea de `core/settings.py`:

```python
# Carpeta templates/ de la raíz del proyecto, donde viven las plantillas compartidas
'DIRS': [BASE_DIR / 'templates'],
```

`templates/base.html` es la plantilla común (encabezado, menú, mensajes y pie). Cada página la hereda con `{% extends 'base.html' %}` y rellena solo sus bloques.

Una petición recorre este camino:

| Paso | Qué pasa | Archivo |
|---|---|---|
| 1 | La persona escribe una dirección | |
| 2 | Django busca la ruta en las del proyecto | `core/urls.py` |
| 3 | Esa ruta lo deriva a las de la app (`include`) | `gestion/urls.py` |
| 4 | La ruta apunta a una vista | `gestion/views.py` |
| 5 | La vista prepara los datos y elige un template | `templates/*.html` |
| 6 | El template hereda `base.html` y se convierte en HTML | `templates/base.html` |

En `core/urls.py`, el panel se declara antes de `include('gestion.urls')`, para que `/admin/` no lo capture la app. El menú creció junto con las pantallas: un enlace a una ruta que todavía no existe habría provocado un `NoReverseMatch`.

![Estructura de templates en VS Code](docs/capturas/58_estructura_templates.png)

![Página de inicio](docs/capturas/59_pagina_inicio.png)

#### 6.3 CRUD de clientes

El formulario de creación solo ofrece usuarios que todavía no tienen cliente:

```python
# Solo muestra los usuarios que todavía no tienen un cliente asociado
self.fields['usuario'].queryset = User.objects.filter(cliente__isnull=True).order_by('username')
```

El borrado captura la protección de las cuentas con historial:

```python
try:
    # Intenta el borrado normal de Django
    respuesta = super().form_valid(form)
except ProtectedError:
    # Si alguna cuenta del cliente tiene movimientos, Django lo impide
    messages.error(self.request, f'No se puede eliminar a {nombre}: sus cuentas tienen movimientos registrados.')
    return redirect('gestion:cliente_detalle', pk=self.object.pk)
```

| Prueba | Resultado |
|---|---|
| Listado | 5 clientes por nombre, con su cantidad de cuentas y un guion donde no hay teléfono |
| Ficha de Ana García | Sus datos, cuentas `0001` (`$115000`) y `0003` (`US$400`) con saldo, y sus contactos |
| Dirección inexistente (`/clientes/9999/`) | Error 404 |
| Crear sin teléfono | `Cliente «Tomás Prueba» creado correctamente.` El teléfono se guarda como `NULL`, porque Django guarda `NULL` cuando se deja vacío un campo de texto que lo admite |
| Correo repetido | `Ya existe Cliente con este Email.` |
| Editar | El campo de usuario no aparece; aviso de actualización |
| Eliminar un cliente con cuentas con movimientos (Ana) | Aviso rojo `No se puede eliminar a Ana García: sus cuentas tienen movimientos registrados.` El cliente sigue existiendo |
| Eliminar un cliente sin cuentas | `Cliente «...» eliminado correctamente.` |
| CSRF: formulario, envío sin token y borrado sin token | `200`, `403` y `403` |

![Listado de clientes](docs/capturas/60_clientes_lista.png)

![Ficha de un cliente](docs/capturas/61_cliente_detalle.png)

![Formulario de nuevo cliente](docs/capturas/62_cliente_formulario.png)

![Error de correo duplicado](docs/capturas/63_cliente_error_email.png)

![Cliente creado](docs/capturas/64_cliente_creado.png)

![Confirmación para eliminar un cliente](docs/capturas/65_cliente_eliminar_confirmar.png)

![Eliminación protegida de un cliente con historial](docs/capturas/66_cliente_eliminar_protegido.png)

![Protección CSRF en clientes](docs/capturas/67_csrf_403.png)

#### 6.4 CRUD de cuentas

| Tema | Decisión |
|---|---|
| Qué se puede editar | Solo el número y si está activa. Cambiar el cliente o la moneda dejaría los movimientos históricos sin sentido |
| Eliminar | Se puede si no tiene movimientos. Si los tiene, se ofrece desactivarla |
| Saldo | El listado y la ficha usan `cuentas_con_saldo()` de la etapa 4 |
| Número al crear | El formulario propone el siguiente (`0008`) |
| Crear desde un cliente | `?cliente=3` en la dirección deja ese cliente elegido |

| Prueba | Resultado |
|---|---|
| Listado | 7 cuentas con sus saldos: `$115000`, `$60000`, `US$400`, `$140000`, `$125000`, `US$400`, `$95000` |
| Ficha de la `0001` | Cliente Ana García y movimientos con signo: `+` los que entran y `-` los que salen |
| Crear la cuenta `0008` | `Cuenta 0008 creada correctamente.` y saldo `$0` |
| Número repetido | `Ya existe una cuenta con ese número.` (mensaje propio: el de Django sale sin tilde) |
| Editar | Cliente y moneda aparecen solo como texto; al desmarcar **Cuenta activa**, la ficha muestra **Inactiva** |
| Eliminar una cuenta con movimientos (`0001`) | Aviso rojo con la sugerencia de desactivarla |
| Eliminar una cuenta sin movimientos | `Cuenta 0008 eliminada correctamente.` |
| CSRF | `200`, `403` y `403` |

![Listado de cuentas](docs/capturas/68_cuentas_lista.png)

![Ficha de una cuenta](docs/capturas/69_cuenta_detalle.png)

![Formulario de nueva cuenta](docs/capturas/70_cuenta_formulario.png)

![Cuenta creada](docs/capturas/71_cuenta_creada.png)

![Cuenta desactivada tras editarla](docs/capturas/72_cuenta_editar_inactiva.png)

![Eliminación protegida de una cuenta con movimientos](docs/capturas/73_cuenta_eliminar_protegida.png)

![Protección CSRF en cuentas](docs/capturas/74_csrf_cuentas_403.png)

#### 6.5 Transacciones y registro atómico

Todo movimiento creado desde las pantallas pasa por `gestion/servicios.py`:

```python
def registrar_transaccion(tipo, cuenta_origen=None, cuenta_destino=None, monto=None, descripcion=''):
    # atomic: todo lo que ocurre dentro se guarda junto o se deshace junto
    with transaction.atomic():
        # Si el dinero sale de una cuenta, se bloquea esa cuenta hasta terminar y se vuelve a leer
        if cuenta_origen is not None:
            cuenta_origen = Cuenta.objects.select_for_update().get(pk=cuenta_origen.pk)
        # La cuenta destino se vuelve a leer sin bloqueo, para conocer su estado actual
        if cuenta_destino is not None:
            cuenta_destino = Cuenta.objects.get(pk=cuenta_destino.pk)
        # Arma el movimiento, repite todas las validaciones con la cuenta bloqueada y lo guarda
        movimiento = Transaccion(tipo=tipo, cuenta_origen=cuenta_origen, cuenta_destino=cuenta_destino,
                                 monto=monto, descripcion=descripcion)
        movimiento.full_clean()
        movimiento.save()
    return movimiento
```

El formulario valida al enviarse; el servicio **repite las validaciones con la cuenta ya bloqueada**, porque entre una y otra el saldo pudo cambiar. Solo se bloquea la cuenta de origen: una cuenta destino solo recibe dinero y no corre riesgo de quedar en negativo.

`select_for_update()` bloquea la fila en PostgreSQL, el motor de producción. SQLite no tiene bloqueos por fila y lo ignora, lo cual no afecta el desarrollo.

El listado usa un formulario de filtros enviado por **GET**: los filtros viajan en la dirección (`?tipo=retiro&cuenta=0004`) y por eso no necesitan token CSRF, mientras que el formulario que escribe datos sí lo lleva. La paginación (10 por página) conserva los filtros en sus enlaces.

| Prueba | Resultado |
|---|---|
| Listado | `18 movimiento(s) encontrado(s)`, 10 filas y `Página 1 de 2`; la página 2 tiene 8 |
| Tipo Retiro / Depósito / Transferencia | 3 / 8 / 7 movimientos |
| Cuenta `0004` | 6 movimientos |
| Cuenta `0004` y tipo Transferencia | 4 movimientos |
| Cuenta `9999` | 0 movimientos y el aviso `No hay movimientos con esos filtros` |
| Fecha mal escrita en la dirección | Aviso de error en el filtro y listado completo |
| Ficha de un movimiento | Tipo, fecha, monto, descripción y cuentas con enlace |
| `/transacciones/<pk>/editar/` | Error 404: el historial no se edita ni se elimina |
| Selector de cuentas | Solo cuentas activas, escritas como `0004 · Carla Soto (CLP)` |
| Depósito válido | `Movimiento registrado: Depósito de 25000.` |
| Retiro mayor que el saldo | `Saldo insuficiente: la cuenta origen tiene 165000.00.` No se guarda |
| Transferencia entre monedas distintas | `Las cuentas deben tener la misma moneda.` |
| Depósito con cuenta origen | `Un depósito no debe tener cuenta origen.` |
| Transferencia a la misma cuenta | `La cuenta origen y la destino deben ser distintas.` |
| Monto cero | `Asegúrese de que este valor es mayor o igual a 0.01.` |

**Validación repetida.** Para simular un formulario enviado con datos que ya quedaron viejos, se registran dos retiros de 100000 desde una cuenta con 125000, dentro de una operación que se deshace al final:

| Paso | Resultado |
|---|---|
| Saldo inicial de la `0005` | 125000 |
| Primer retiro de 100000 | Registrado; saldo 25000 |
| Segundo retiro con los mismos datos | `Saldo insuficiente: la cuenta origen tiene 25000.00.` |
| Al final | Saldo 125000 y 18 movimientos: no queda nada |

CSRF: `GET` del formulario `200`, `GET` del listado con filtros `200`, y `POST` sin token `403`.

![Listado de transacciones](docs/capturas/75_transacciones_lista.png)

![Listado filtrado](docs/capturas/76_transacciones_filtros.png)

![Página 2 del listado](docs/capturas/77_transacciones_pagina2.png)

![Ficha de un movimiento](docs/capturas/78_transaccion_detalle.png)

![Formulario de nuevo movimiento](docs/capturas/79_transaccion_formulario.png)

![Movimiento registrado](docs/capturas/80_transaccion_creada.png)

![Saldo insuficiente](docs/capturas/81_transaccion_saldo_insuficiente.png)

![Error de validación en el formulario](docs/capturas/82_transaccion_validaciones.png)

![Validación repetida dentro de la operación atómica](docs/capturas/83_servicio_validacion_repetida.png)

![Protección CSRF en transacciones](docs/capturas/84_csrf_transacciones_403.png)

**Incidencia resuelta:** al compactar un `import` a una sola línea quedó una coma al final antes del comentario: `from .forms import ..., FiltroTransaccionForm, # ...`. Python rechaza con `trailing comma not allowed without surrounding parentheses`, porque esa coma solo es válida si la lista va entre paréntesis.

#### 6.6 Contactos

Los contactos se agregan y se quitan desde la ficha del cliente. El dueño de la agenda sale de la dirección (`/clientes/3/contactos/nuevo/`), y el formulario solo pide a quién agendar y el apodo. El selector excluye al dueño y a quienes ya están en su agenda; la restricción de la base de datos queda como respaldo.

El atajo **Transferir** de cada contacto abre el formulario de movimiento con la transferencia y la primera cuenta activa del contacto ya elegidas, usando una dirección con parámetros (`?tipo=transferencia&cuenta_destino=2`). No registra nada por sí solo.

| Prueba | Resultado |
|---|---|
| Ficha de Ana García | Contactos Lucho (Luis Pérez) y Carli (Carla Soto), cada uno con **Transferir** y **Quitar**; en **Aparece en la agenda de**: Luis Pérez |
| Formulario de agregar contacto en Ana | Solo ofrece a Diego Rojas y Marta Vega |
| Agregar a Diego con apodo | `Contacto «Diego Rojas» agregado correctamente.` y deja de aparecer en el selector |
| Agregar sin apodo | Se guarda; el apodo se ve como un guion |
| Quitar un contacto | `Contacto «Diego Rojas» quitado de la agenda.` El cliente y sus cuentas siguen existiendo |
| Cliente inexistente (`/clientes/9999/contactos/nuevo/`) | Error 404 |
| Atajo **Transferir** | El formulario se abre con Transferencia y la cuenta destino elegidas |
| CSRF | `200`, `403` y `403` |

La agenda no es simétrica: que Ana tenga agendado a Luis no hace que Luis tenga agendada a Ana. La sección **Aparece en la agenda de** usa la relación inversa `agendado_por`, definida en la etapa 2.

![Contactos en la ficha de un cliente](docs/capturas/85_cliente_contactos.png)

![Formulario de agregar contacto](docs/capturas/86_contacto_formulario.png)

![Contacto agregado](docs/capturas/87_contacto_agregado.png)

![Confirmación para quitar un contacto](docs/capturas/88_contacto_quitar_confirmar.png)

![Contacto quitado](docs/capturas/89_contacto_quitado.png)

![Atajo Transferir: formulario con la transferencia y el destino elegidos](docs/capturas/90_atajo_transferir.png)

![Protección CSRF en contactos](docs/capturas/91_csrf_contactos_403.png)

#### 6.7 Inicio y reporte

La página de inicio muestra los totales (con enlace a cada listado), los 5 movimientos más recientes y enlaces rápidos. El reporte reutiliza las consultas de `gestion/consultas.py`, que ahora tiene 12 funciones:

| Dato del reporte | Consulta |
|---|---|
| Movimientos por tipo, por moneda | `resumen_por_tipo()` (etapa 4) |
| Saldo total por cliente, por moneda | `saldo_por_cliente()`: `values` + `annotate(Sum('saldo_calculado'))` sobre la consulta de saldos |
| Movimientos por mes | `movimientos_por_mes()`: `TruncMonth('fecha')` + `Count` |

El reporte tiene una sección por moneda, porque los montos de monedas distintas no se suman entre sí. Agrupa por el `id` del cliente y no por su nombre, para que dos clientes con el mismo nombre no se mezclen.

| Sección | Resultado |
|---|---|
| Inicio | Clientes 5, Cuentas 7, Transacciones 18 y los 5 últimos movimientos |
| CLP, movimientos por tipo | Depósito 6 (`$610000`), Retiro 3 (`$75000`), Transferencia 6 (`$130000`) |
| CLP, saldo por cliente | Carla Soto `$140000`, Diego Rojas `$125000`, Ana García `$115000`, Marta Vega `$95000`, Luis Pérez `$60000`; total `$535000` |
| USD, movimientos por tipo | Depósito 2 (`US$800`), Transferencia 1 (`US$100`) |
| USD, saldo por cliente | Ana García `US$400` y Diego Rojas `US$400`; total `US$800` |
| Movimientos por mes | Una fila por mes; la columna Cantidad suma 18, igual que el total |

Las cifras coinciden con las del comando `demo_consultas` de la etapa 4.

![Inicio con totales y últimos movimientos](docs/capturas/92_inicio_ampliado.png)

![Reporte, sección CLP](docs/capturas/93_reporte_clp.png)

![Reporte, sección USD y movimientos por mes](docs/capturas/94_reporte_usd_meses.png)

**Limitaciones conocidas:**

- **Todavía no hay login.** Cualquier persona que llegue a la dirección ve todas las pantallas, incluido el enlace al panel. *(Resuelto en la etapa 7.)*
- **El superusuario no tiene un `Cliente` asociado.** Las pantallas de usuario que dependan de `request.user.cliente` deberán contemplar ese caso. *(Resuelto en la etapa 7: el personal ve todo y un usuario sin cliente recibe un aviso.)*
- **El diseño es mínimo.** Hay un bloque de estilos temporal dentro de `base.html`, que la etapa 7 reemplaza por archivos estáticos. *(Resuelto en la etapa 7.)*

**Reflexiones:**

- **Las vistas genéricas ahorran mucho código:** `ListView`, `DetailView`, `CreateView`, `UpdateView` y `DeleteView` resuelven lo repetitivo, y cada vista solo declara lo que la distingue.
- **Una sola regla, todos los accesos:** poner el saldo y las cuentas inactivas en `Transaccion.clean()` hace que el panel y las pantallas las apliquen sin duplicar código.
- **Validar dos veces tiene sentido:** el formulario da una respuesta rápida y el servicio, con la cuenta bloqueada, da la definitiva.
- **El historial no se edita:** no hay pantallas ni permisos para modificar movimientos; un error se corrige con un movimiento inverso.
- **Reutilizar consultas paga:** el reporte, el panel y el comando de demostración comparten `cuentas_con_saldo()`, y sus cifras coinciden.

### Etapa 7: autenticación y archivos estáticos

**Objetivo:** que solo entren personas con sesión iniciada, que cada rol vea lo que le corresponde, que cada cliente vea únicamente sus propios datos, y reemplazar los estilos provisorios por archivos estáticos.

**Rama de trabajo:** `feature/auth`. Esta etapa no cambia los modelos, por lo que no genera migraciones.

**Subetapas:**

| Subetapa | Qué se hizo |
|---|---|
| 7.1 | Login y logout con las vistas de `django.contrib.auth` |
| 7.2 | Archivos estáticos: CSS y logo |
| 7.3 | Roles: personal, cliente y usuario sin cliente |
| 7.4 | Alcance por usuario: cada cliente ve solo lo suyo |
| 7.5 | Registro público de clientes con su primera cuenta |
| 7.6 | Mi perfil y cambio de contraseña |
| 7.7 | Verificación de accesos y de la protección CSRF |

#### 7.1 Login y logout

Django 5.1 agregó `LoginRequiredMiddleware`: con él, **todas** las pantallas piden sesión por defecto y solo se publican las que se marcan con `login_not_required`. Es más seguro que proteger cada vista por separado, porque una vista nueva queda protegida aunque se olvide.

| Pieza | Dónde | Qué hace |
|---|---|---|
| `LoginRequiredMiddleware` | `MIDDLEWARE`, después de `AuthenticationMiddleware` | Redirige al login a quien no tiene sesión |
| `LOGIN_URL = 'login'` | `settings.py` | A dónde se envía a quien no ha entrado |
| `LOGIN_REDIRECT_URL = 'gestion:inicio'` | `settings.py` | A dónde se va después de entrar |
| `LOGOUT_REDIRECT_URL = 'login'` | `settings.py` | A dónde se va después de salir |
| `/acceso/login/` | `core/urls.py`, `LoginView` | Pantalla de ingreso; si ya hay sesión, va al inicio |
| `/acceso/logout/` | `core/urls.py`, `LogoutView` | Cierra la sesión; solo acepta POST |

Cuando alguien intenta entrar a una pantalla sin sesión, el login recibe `?next=/ruta/original/` y, tras entrar, lo devuelve a esa pantalla. El botón «Cerrar sesión» es un formulario POST con token CSRF y no un enlace: así un sitio externo no puede cerrar la sesión de otra persona con solo enlazar una dirección.

![Formulario de ingreso](docs/capturas/95_login_formulario.png)

![Error de credenciales](docs/capturas/96_login_error.png)

![Inicio con la sesión iniciada](docs/capturas/97_inicio_con_sesion.png)

![Redirección al login con ?next=](docs/capturas/98_redireccion_login.png)

![Menú de un cliente, sin enlace al panel](docs/capturas/99_menu_cliente_sin_panel.png)

![El login sin token CSRF es rechazado con 403](docs/capturas/100_csrf_login_403.png)

#### 7.2 Archivos estáticos

Los estilos pasaron del bloque provisorio de `base.html` a `static/css/estilos.css`, y se agregó `static/img/logo.svg`.

| Configuración | Para qué sirve |
|---|---|
| `STATIC_URL = 'static/'` | Prefijo de las direcciones de los archivos estáticos |
| `STATICFILES_DIRS = [BASE_DIR / 'static']` | Carpeta del proyecto donde están los archivos propios |
| `STATIC_ROOT = BASE_DIR / 'staticfiles'` | Carpeta donde `collectstatic` junta todo para producción |

En los templates se usa `{% load static %}` y `{% static 'css/estilos.css' %}`, de modo que la dirección real la calcula Django. Dos comandos permiten comprobar la configuración:

```powershell
# Muestra en qué carpeta encuentra Django un archivo estático
python manage.py findstatic css/estilos.css

# Junta los estáticos propios y los del panel de administración en STATIC_ROOT (se usa al desplegar)
python manage.py collectstatic
```

`staticfiles/` se genera con `collectstatic` y no se sube al repositorio.

> **Nota:** los estilos de esta etapa se reemplazaron después, en la [etapa 9](#etapa-9-mejora-visual-con-bootstrap), por una capa de marca sobre Bootstrap. Las capturas siguientes muestran el diseño original.

![Estructura de la carpeta static](docs/capturas/101_static_estructura.png)

![findstatic y collectstatic](docs/capturas/102_findstatic_collectstatic.png)

![Login con estilos](docs/capturas/103_login_con_estilos.png)

![Inicio con estilos](docs/capturas/104_inicio_con_estilos.png)

![Listado con estilos](docs/capturas/105_listado_con_estilos.png)

#### 7.3 Roles

Hay tres tipos de persona con sesión. Se distinguen sin crear tablas nuevas: el personal tiene `is_staff` y un cliente tiene un `Cliente` asociado (relación 1:1).

| Rol | Cómo se detecta | Qué puede hacer |
|---|---|---|
| Personal | `user.is_staff` | Todo: clientes, cuentas, movimientos, reporte y panel |
| Cliente | `hasattr(user, 'cliente')` | Ver su ficha, sus cuentas y sus movimientos; transferir; gestionar su agenda |
| Sin cliente | Ninguno de los anteriores | Solo ver su perfil y un aviso en el inicio |

`gestion/mixins.py` define dos mixins basados en `UserPassesTestMixin`, que se ponen **primero** en las clases base de cada vista. Si el test falla, la persona recibe una página 403 propia (`templates/403.html`).

| Mixin | Quién pasa | Vistas |
|---|---|---|
| `SoloPersonalMixin` | Solo el personal | Listado, alta y baja de clientes; alta, edición y baja de cuentas; reporte |
| `PersonalOClienteMixin` | Personal y clientes | Ficha y edición de cliente; listado y ficha de cuentas; movimientos; contactos |

El menú de `base.html` también cambia según el rol, pero ocultar un enlace no protege nada: la protección real está en las vistas, y el menú solo evita ofrecer lo que daría 403. `hasattr(user, 'cliente')` se usa en lugar de `user.cliente` porque este último lanza una excepción cuando no hay ficha.

![Mixins de roles en mixins.py](docs/capturas/106_roles_mixins_py.png)

![Matriz de permisos](docs/capturas/107_matriz_permisos.png)

![Menú del personal](docs/capturas/108_menu_personal.png)

![Menú de un cliente](docs/capturas/109_menu_cliente.png)

![Página 403 para un cliente](docs/capturas/110_403_cliente.png)

![Inicio de un usuario sin cliente](docs/capturas/111_inicio_sin_cliente.png)

#### 7.4 Alcance por usuario

Los roles dicen **qué pantallas** puede abrir cada persona; el alcance dice **qué registros**. Un cliente solo ve los suyos, y si escribe en la dirección el número de un registro ajeno recibe **404** y no 403, para no confirmar que ese registro existe.

`gestion/alcance.py` concentra las reglas:

| Función | Qué devuelve |
|---|---|
| `limitar_a_cliente(queryset, usuario, campo)` | Deja solo los registros cuyo `campo` apunta al cliente de la sesión; el personal ve todo |
| `movimientos_visibles(usuario)` | Movimientos donde alguna cuenta del cliente es origen o destino |
| `cuentas_de_origen(usuario)` | Cuentas activas desde las que se puede sacar dinero: solo las propias |
| `cuentas_de_destino(usuario)` | Cuentas activas que se pueden recibir: las propias y las de sus contactos |

Las vistas usan estas funciones en `get_queryset()`, de modo que el listado, la ficha, la edición y el borrado aplican el mismo filtro. Además:

- **Movimientos:** el formulario recibe al usuario (`TransaccionForm(usuario=...)`) y ofrece solo las cuentas permitidas. Un retiro solo sale de cuentas propias, una transferencia puede ir a un contacto, y un depósito debe ir a una cuenta propia (regla en `clean()`).
- **Agenda:** `ContactoCreateView` busca al dueño de la agenda con `cached_property` y no en `dispatch`, para que el rol se revise antes. Con `dispatch`, un usuario sin cliente habría provocado un error 500 en lugar de un 403.
- **Inicio:** el personal ve los totales del sistema; un cliente ve sus cuentas con saldo y sus últimos movimientos.

| Caso (cliente `carla`) | Resultado |
|---|---|
| `/cuentas/` | Solo `0004` |
| Ficha, cuenta o movimiento de otro cliente | 404 |
| Destinos de una transferencia | Sus cuentas y las de sus contactos |
| Depósito a la cuenta de un contacto | Error «Un depósito solo puede ir a una de tus cuentas.» |
| Retiro desde una cuenta ajena | Rechazado: la opción no está entre las disponibles |

![Inicio de un cliente](docs/capturas/112_inicio_cliente.png)

![Cuentas: solo las propias](docs/capturas/113_cuentas_solo_propias.png)

![Movimientos: solo los propios](docs/capturas/114_movimientos_solo_propios.png)

![404 al abrir la ficha de otro cliente](docs/capturas/115_404_ficha_ajena.png)

![Destinos permitidos en una transferencia](docs/capturas/116_destinos_permitidos.png)

![Depósito a una cuenta ajena rechazado](docs/capturas/117_deposito_ajeno_rechazado.png)

#### 7.5 Registro de clientes

Cualquier persona puede crear su usuario desde `/registro/`. Es, junto con el login, la única pantalla pública: se marca con `login_not_required` en `core/urls.py`.

| Pieza | Qué hace |
|---|---|
| `RegistroForm` (`forms.py`) | Extiende `UserCreationForm`: pide usuario, nombre, correo, teléfono (opcional), moneda y contraseña dos veces |
| Validaciones | Contraseña no débil ni numérica, claves iguales, correo no repetido (sin distinguir mayúsculas) y moneda elegida |
| `crear_cliente_con_cuenta()` (`servicios.py`) | Crea el cliente y su primera cuenta con saldo cero y el siguiente número libre (`0008`, `0009`...) |
| `RegistroView` (`views.py`) | Guarda todo, inicia la sesión y lleva al inicio; quien ya tiene sesión es enviado al inicio |

El usuario, el cliente y la cuenta se crean dentro de `transaction.atomic()`: o se crean los tres o no se crea ninguno, y nunca queda un usuario sin ficha. El usuario creado nunca pertenece al personal.

![Enlace de registro en el login](docs/capturas/118_login_con_registro.png)

![Formulario de registro](docs/capturas/119_registro_formulario.png)

![Errores de validación en el registro](docs/capturas/120_registro_errores.png)

![Registro exitoso: inicio con la cuenta nueva](docs/capturas/121_registro_exitoso.png)

![Cliente y cuenta creados, vistos en el panel](docs/capturas/122_admin_cliente_registrado.png)

#### 7.6 Perfil y cambio de contraseña

| Ruta | Vista | Qué muestra o hace |
|---|---|---|
| `/perfil/` | `PerfilView` | Usuario, rol y último ingreso; si es cliente, también sus datos de cliente con los enlaces «Editar mis datos» y «Ver mi ficha» |
| `/perfil/clave/` | `CambiarClaveView` (`PasswordChangeView`) | Pide la contraseña actual y la nueva dos veces, con las validaciones de Django |

El perfil sirve para cualquier rol. «Editar mis datos» reutiliza la edición de cliente de la subetapa 7.4, por lo que un cliente solo puede editar su propia ficha. Al cambiar la contraseña la sesión sigue abierta y se muestra un aviso de éxito.

![Perfil de un cliente](docs/capturas/123_perfil_cliente.png)

![Perfil del personal](docs/capturas/124_perfil_personal.png)

![Edición de los datos propios](docs/capturas/125_editar_mis_datos.png)

![Error al escribir mal la contraseña actual](docs/capturas/126_clave_error.png)

![Contraseña cambiada con aviso de éxito](docs/capturas/127_clave_cambiada.png)

#### 7.7 Verificación de accesos y CSRF

El comando `verificar_accesos` prueba todo lo anterior de una vez. Crea datos temporales (personal, dos clientes con cuenta, un movimiento y una ficha de agenda ajenos, y un usuario sin cliente) dentro de `transaction.atomic()` y los deshace al terminar, así que no deja nada en la base de datos. Usa `Client` de Django, que simula un navegador, con `enforce_csrf_checks=True` para exigir el token como en el navegador real.

```powershell
python manage.py verificar_accesos
```

| Grupo | Qué se prueba | Esperado |
|---|---|---|
| Sin sesión | Las pantallas llevan al login con `?next=`; login y registro son públicos | 302 / 200 |
| Personal | Todas las pantallas, incluidas las de otros clientes | 200 |
| Cliente | Sus pantallas propias | 200 |
| Cliente | Pantallas del personal | 403 |
| Cliente | Ficha, cuenta, movimiento y agenda de otro cliente | 404 |
| Sin cliente | Perfil e inicio | 200 |
| Sin cliente | Cuentas, transacciones y clientes | 403 |
| CSRF | Login, registro, logout, cambio de contraseña, nueva transacción y edición, sin token | 403 |
| Logout | Cerrar sesión con GET | 405 |
| CSRF | Login con token y clave incorrecta | 200 (se procesa) |

Resultado: **55 de 55 pruebas correctas**. Las pruebas unitarias formales y el informe de pruebas se abordan en la etapa 8.

![Resultado de verificar_accesos](docs/capturas/128_verificar_accesos.png)

**Decisiones:**

| Decisión | Alternativa descartada | Motivo |
|---|---|---|
| `LoginRequiredMiddleware` | Un mixin de login en cada vista | Todo queda protegido por defecto; las pantallas públicas son la excepción explícita |
| Roles con `is_staff` y la relación 1:1 con `Cliente` | Grupos y permisos de Django o un campo `rol` | No agrega tablas ni migraciones y se entiende de un vistazo |
| Un solo módulo `alcance.py` con las reglas | Filtros repetidos en cada vista | Una regla en un lugar; el listado, la ficha, la edición y el borrado no pueden contradecirse |
| 404 para registros ajenos | 403 | No confirma que el registro exista |
| El rol se revisa antes de buscar el registro | Buscar el registro en `dispatch` | Evita un error 500 para un usuario sin cliente |
| Registro con `atomic()` | Crear usuario, cliente y cuenta por separado | Nunca queda un usuario sin ficha |

**Limitaciones conocidas:**

- **No hay recuperación de contraseña por correo** ni verificación del correo al registrarse; requeriría configurar un servidor de correo.
- **El número de cuenta es «el mayor más uno».** Con muchos registros simultáneos podría repetirse un número y fallar un registro; para este proyecto es suficiente.
- **Solo el personal abre cuentas adicionales** y gestiona clientes; un cliente tiene la cuenta inicial del registro.
- **Las claves de los usuarios de ejemplo** son aleatorias o salen de `CLAVE_DEMO`; los datos de ejemplo no deben usarse en un sistema publicado.
- **No hay bloqueo por intentos fallidos de ingreso.**

**Reflexiones:**

- **Proteger por defecto es más seguro:** con el middleware, olvidar marcar una vista deja un efecto visible (pide login), no un agujero.
- **Un rol no basta:** poder abrir `/cuentas/` no significa poder ver todas las cuentas. Separar roles (qué pantalla) de alcance (qué registro) evitó mezclar ambas reglas.
- **Ocultar un enlace no es seguridad:** el menú por rol es comodidad; las reglas viven en las vistas y se comprueban con `verificar_accesos`.
- **El orden importa:** el mixin de rol debe ejecutarse antes de cualquier código que use `request.user.cliente`.
- **Comprobar con datos temporales** permite repetir las pruebas sin ensuciar la base de datos.

### Etapa 8: pruebas automatizadas

**Objetivo:** comprobar con pruebas automáticas que las reglas de negocio, los formularios, las pantallas y la seguridad funcionan, y que las pruebas fallan cuando una regla se rompe.

**Rama de trabajo:** `feature/tests`. Esta etapa no cambia los modelos, por lo que no genera migraciones. El informe formal está en [`docs/informe_pruebas.docx`](docs/informe_pruebas.docx).

**Cómo se organizan:** la carpeta `gestion/tests/` reemplaza al archivo `tests.py` y tiene un archivo por bloque. `utilidades.py` reúne funciones que crean datos de prueba (moneda, cliente, cuenta, depósito y usuario del personal) para no repetir código.

**Subetapas:**

| Subetapa | Archivo | Pruebas | Qué revisa |
|---|---|---|---|
| 8.0 | `test_humo.py` | 5 | Que el entorno de pruebas funciona: base vacía, aislamiento y login |
| 8.1 | `test_modelos.py` | 42 | Restricciones, validaciones, saldo y protección al borrar |
| 8.2 | `test_servicios.py` | 21 | Movimientos atómicos, bloqueo de la cuenta origen y alta de cliente con cuenta |
| 8.3 | `test_consultas.py` | 31 | Filtros, agregaciones, saldos y consultas SQL propias |
| 8.4 | `test_formularios.py` | 41 | Opciones, validaciones y mensajes de cada formulario |
| 8.4 | `test_vistas.py` | 49 | CRUD, filtros, paginación, avisos y protecciones, como personal |
| 8.5 | `test_seguridad.py` | 50 | Roles, alcance por cliente, reglas de operación, CSRF y sesión |
| 8.6 | `docs/informe_pruebas.docx` | | Informe con tabla de casos, resultados y evidencias |

**Cómo ejecutarlas** (con `DB_ENGINE=sqlite` en `.env`):

```bash
# Todas las pruebas
python manage.py test gestion

# Un bloque con detalle
python manage.py test gestion.tests.test_seguridad -v 2

# Comprobación manual de accesos (no deja datos)
python manage.py verificar_accesos
```

**Resultado:**

```text
Ran 239 tests
OK
```

![Suite completa: 239 pruebas correctas](docs/capturas/141_test_todas_239.png)

![verificar_accesos: 55 de 55 comprobaciones correctas](docs/capturas/142_pruebas_correctas.png)

> **Nota:** el total posterior es de 244 pruebas. Las 5 pruebas adicionales (`test_salud.py` y `test_comandos.py`) se agregaron en la [etapa 10](#etapa-10-preparación-para-el-despliegue-en-render).

**Qué se aprendió y decisiones:**

- **Las pruebas usan una base temporal.** Django crea una base vacía, deshace cada prueba y la elimina al final; los datos reales no se tocan.
- **`force_login` y usuarios sin contraseña** evitan cifrar una clave en cada prueba, que era lo más lento (de 23 s a menos de 1 s en los modelos). Las pocas pruebas que necesitan una clave real usan `secrets`, así no hay contraseñas escritas en el código.
- **CSRF solo se prueba con `Client(enforce_csrf_checks=True)`.** El cliente normal de las pruebas se salta esa revisión.
- **Una prueba vale si falla cuando se rompe la regla.** Se rompió a propósito cada regla de seguridad y se comprobó que al menos una prueba fallaba; los resultados están en el informe.
- **En una prueba que falló al principio** la causa era la prueba y no el código: pedir la página 2 sin tener 11 movimientos devuelve 404.

**Limitaciones conocidas:**

- Las pruebas se ejecutaron en SQLite. En PostgreSQL funcionan igual, pero el usuario de la base necesita permiso `CREATEDB` para crear la base de pruebas.
- En SQLite, `LIKE` ya ignora mayúsculas, así que quitar `LOWER()` de la búsqueda SQL propia no se detecta con esta base.
- `select_for_update` solo tiene efecto real en PostgreSQL; la concurrencia no se prueba de forma automática.
- No se mide la cobertura de código con `coverage.py`.

**Si solo recuerdas esto:**

- Un formulario se prueba con `is_valid()` y `errors`; una vista, con `self.client`, `reverse` y `assertRedirects`.
- Sin sesión redirige al login, con rol incorrecto da 403 y con un registro ajeno da 404.

### Etapa 9: mejora visual con Bootstrap

**Objetivo:** dar a la aplicación una interfaz profesional, moderna y adaptable a escritorio, tablet y celular, sin cambiar la lógica del sistema (modelos, vistas, reglas y rutas).

**Rama de trabajo:** `feature/bootstrap`. Esta etapa no cambia los modelos, por lo que no genera migraciones. Se integró a `main` con 7 commits por tema (fast-forward).

**Subetapas:**

| Subetapa | Qué se hizo |
|---|---|
| 9.1 | Base: Bootstrap 5.3.3, Bootstrap Icons y la tipografía Inter por CDN; `base.html` con menú y pie de página; `estilos.css` como capa de marca |
| 9.2 | Componentes de plantilla reutilizables y filtros propios para dibujar los formularios |
| 9.3 | Rediseño de inicio, perfil, reporte, clientes, cuentas, transacciones y contactos |
| 9.4 | Portada pública con el inicio de sesión y el registro en la misma pantalla |
| 9.5 | Adaptación a tablet y celular |
| 9.6 | Comportamientos en el navegador (`static/js/app.js`) |
| 9.7 | Páginas de error 403, 404 y 500 con el mismo diseño |
| 9.8 | Montos con formato chileno |

#### 9.1 Base: Bootstrap, menú y pie de página

Bootstrap se carga desde un CDN en `base.html`, junto con Bootstrap Icons y la fuente Inter. `static/css/estilos.css` se reescribió: ya no define el diseño completo, sino una **capa de marca** sobre Bootstrap, con variables de color (azul `#1D4E89`, turquesa `#17B8A6`), tarjetas, tablas, formularios y animaciones.

| Pieza de `base.html` | Qué hace |
|---|---|
| Menú superior | Degradado azul con línea turquesa; se convierte en botón de hamburguesa bajo 992 px |
| Enlace activo | Se marca según `request.resolver_match.url_name`, el nombre de la ruta actual |
| Desplegable de usuario | Muestra la inicial, el nombre y el rol; contiene "Mi perfil" y "Cerrar sesión" (que sigue siendo un formulario POST con CSRF) |
| Avisos | `componentes/_mensajes.html`; Django llama `error` al tipo que Bootstrap llama `danger`, y se traduce |
| Pie de página | Marca, enlaces según el rol, tecnologías y año actual con `{% now "Y" %}` |
| Bloque `cuerpo` | Permite que la portada reemplace el contenedor centrado y use todo el ancho |

#### 9.2 Componentes y filtros de plantilla

| Pieza | Dónde | Para qué |
|---|---|---|
| Filtro `bootstrap` | `gestion/templatetags/ui.py` | Agrega `form-control`, `form-select` o `form-check-input` a un campo y `is-invalid` si tiene errores |
| Filtros `es_casilla` y `es_lista` | `gestion/templatetags/ui.py` | Detectan el tipo de campo para dibujarlo distinto |
| `_campos.html` | `templates/componentes/` | Dibuja todos los campos de un formulario (etiqueta, campo, ayuda y errores); con `dos_columnas=True` los acomoda de dos en dos |
| `_tipo.html` | `templates/componentes/` | Etiqueta de color según el tipo de movimiento: verde, rojo o azul |
| `_estado.html` | `templates/componentes/` | Etiqueta Activa o Inactiva de una cuenta |
| `_mensajes.html` | `templates/componentes/` | Avisos de las vistas |
| `_movimiento_item.html` | `templates/componentes/` | Fila de un movimiento pensada para celular |

La alternativa de editar `forms.py` para agregar las clases a cada widget se descartó: habría mezclado la presentación con la lógica de los formularios y obligado a tocar las pruebas.

#### 9.3 Pantallas de gestión

Las listas pasaron a tarjetas con tablas dentro, las fichas a tarjetas con datos y avatares con la inicial, y las confirmaciones de borrado a una tarjeta con franja roja. En el inicio, el personal ve tres tarjetas con los totales y el cliente ve sus cuentas como tarjetas con aspecto de tarjeta bancaria. El reporte muestra las proporciones con barras hechas con CSS puro (`{% widthratio %}` calcula el porcentaje).

Un cambio de comportamiento: los botones que solo puede usar el personal (nueva cuenta, editar, eliminar, volver al listado de clientes) **ya no se muestran a los clientes**. Antes se veían y, al pulsarlos, la persona recibía un 403.

#### 9.4 Portada con inicio de sesión y registro

`templates/registration/landing.html` es la portada pública. De ella heredan `login.html` y `registro.html`, que solo aportan su formulario. Incluye un mensaje de presentación, tres ventajas, una tarjeta decorativa (no muestra datos reales), las características, "Empieza en tres pasos" y un llamado final.

- **Inicio de sesión y registro en la misma pantalla:** las pestañas "Iniciar sesión" y "Crear cuenta" son enlaces a `/acceso/login/#acceso` y `/registro/#acceso`. Cada formulario sigue atendido por su propia vista, por lo que no cambió ninguna ruta ni lógica; para la persona se siente como una sola pantalla.
- **Ancho distinto por página:** la portada define bloques (`columna_texto`, `columna_acceso`, `clase_tarjeta_acceso`) para que el registro, que tiene siete campos, use una tarjeta más ancha.
- **Registro en dos columnas:** los campos se acomodan de dos en dos; la lista de monedas ocupa todo el ancho. Las ayudas largas (más de 120 caracteres), como los requisitos de la contraseña, quedan plegadas detrás de "Ver requisitos". El formulario pasó de unos 900 px de alto a unos 600 px en escritorio.

![Portada en escritorio](docs/vista_previa/escritorio_portada.png)

![Inicio del personal en escritorio](docs/vista_previa/escritorio_inicio_personal.png)

#### 9.5 Adaptación a tablet y celular

| Elemento | Celular | Tablet (desde 768 px) | Escritorio (desde 992 px) |
|---|---|---|---|
| Menú | Botón de hamburguesa | Hamburguesa | Menú horizontal |
| Movimientos (inicio y listado) | Lista compacta con ícono, tipo, cuentas y monto | Tabla completa | Tabla completa con descripción |
| Cuentas y clientes | Columnas secundarias ocultas; el dato va bajo el principal | Más columnas | Todas las columnas |
| Filtros de transacciones | Plegados detrás de un botón | Siempre visibles | Siempre visibles |
| Totales del inicio | Tres tarjetas en una fila | Tres tarjetas | Tres tarjetas |
| Paginación | Botones anterior y siguiente con el número al centro | Igual, con texto | Igual, con texto |
| Portada | Texto centrado, tarjeta de acceso debajo | Tarjeta centrada con ancho máximo | Texto a la izquierda y tarjeta a la derecha |
| Pie de página | Marca centrada y dos columnas ordenadas a la izquierda | Tres columnas | Tres columnas |

Se revisó con capturas de Chrome a 390 px (celular), 768 a 820 px (tablet) y 1100 a 1280 px (escritorio). No se probó en un teléfono real.

![Portada en tablet](docs/vista_previa/tablet_portada.png)

![Inicio en tablet](docs/vista_previa/tablet_inicio.png)

![Portada en celular](docs/vista_previa/movil_portada.png)

![Inicio del personal en celular](docs/vista_previa/movil_inicio_personal.png)

![Inicio del cliente en celular](docs/vista_previa/movil_inicio_cliente.png)

![Movimientos en celular](docs/vista_previa/movil_transacciones.png)

#### 9.6 Comportamientos en el navegador

`static/js/app.js` mejora la experiencia, pero la aplicación funciona igual sin él:

| Comportamiento | Qué hace |
|---|---|
| Ver u ocultar la contraseña | Agrega un botón con un ojo a cada campo de contraseña |
| Evitar el doble envío | Al enviar un formulario POST, el botón se desactiva y muestra un indicador de carga, para que un doble clic no registre dos veces el mismo movimiento |
| Avisos que se cierran | Los avisos de éxito desaparecen a los 6 segundos; los de error y advertencia se quedan hasta que se cierren |

Cuando se vuelve a una página con el botón Atrás, los botones desactivados se reactivan (evento `pageshow`).

#### 9.7 Páginas de error

| Página | Cuándo aparece | Botones |
|---|---|---|
| `403.html` | Una persona entra a una sección que no le corresponde | "Volver a mi panel" (con sesión) o "Iniciar sesión"; "Volver atrás" |
| `404.html` | La dirección o el registro no existen | "Volver a mi panel" (con sesión) o "Ir al inicio"; "Volver atrás" |
| `500.html` | Error interno del servidor | "Reintentar" e "Ir al inicio" |

La 403 y la 404 heredan de `base.html`. La **500 es un documento independiente**: si el error viene de la base de datos o de la sesión, una página que dependa del menú o de `user` fallaría también. Por eso no usa `{% url %}`, `user` ni `request`, solo archivos estáticos y el enlace fijo `/`.

Con `DEBUG=True`, Django muestra su propia página técnica en lugar de `404.html` y `500.html`. Para ver los diseños en desarrollo existen las rutas `/vista-403/`, `/vista-404/` y `/vista-500/`, que solo se registran cuando `DEBUG` es `True`. Los tres errores se comprobaron de forma real con `DEBUG=False`: un 403 (un cliente entrando al listado de clientes), un 404 (dirección inexistente) y un 500 (excepción forzada en la vista de inicio).

#### 9.8 Montos con formato chileno

Los montos pasaron de `$115000,00` a `$115.000,00`. Django solo trae el formato de España para el español, que usa un espacio como separador de miles. En Chile se usa el punto, así que se definió un formato propio:

| Configuración | Para qué sirve |
|---|---|
| `USE_THOUSAND_SEPARATOR = True` | Activa el separador de miles en toda la aplicación |
| `FORMAT_MODULE_PATH = ['core.formats']` | Indica dónde buscar formatos propios |
| `core/formats/es_CL/formats.py` | Define punto como separador de miles y coma como separador decimal |

**Decisiones:**

| Decisión | Alternativa | Por qué |
|---|---|---|
| Bootstrap 5 | Tailwind o CSS propio | Es el estándar para tablas, formularios y menú responsive, y no requiere compilar nada |
| Bootstrap por CDN | Descargarlo al proyecto | Evita subir archivos de terceros; la aplicación necesita internet para verse completa |
| Filtros de plantilla propios | `django-crispy-forms` | Evita una dependencia nueva para algo que se resuelve con un filtro de pocas líneas |
| Ocultar columnas y mostrar una lista en celular | Dejar la tabla con desplazamiento horizontal | Una tabla de siete columnas obligaba a desplazarse y cortaba el monto |
| Pestañas como enlaces entre dos rutas | Un solo formulario con JavaScript | No cambia las vistas ni las rutas; funciona sin JavaScript |
| Barras de proporción con CSS | Chart.js | Cubre lo esencial sin otra librería |
| Modo oscuro descartado | Activarlo con `data-bs-theme` | La paleta de marca está fija; habría que rediseñarla |

**Incidencias resueltas:**

| Problema | Causa | Solución |
|---|---|---|
| Las tarjetas se veían grises en lugar de blancas | Bootstrap toma el color de `var(--bs-body-bg)`, que se había cambiado a gris | Fijar `--bs-card-bg` en blanco y hacer transparentes las tablas |
| La tarjeta decorativa perdió su inclinación | La animación de entrada terminaba en `transform: translateY(0)` y anulaba el giro | Crear una animación propia (`aparecer-inclinada`) que conserva la rotación |
| El desplegable de usuario se salía de la pantalla en celular | Estaba fuera de un `navbar-nav`, así que Bootstrap lo posicionaba con Popper hacia afuera | Colocarlo dentro de un `<ul class="navbar-nav">`: se abre dentro del menú |
| Los títulos de la portada salían oscuros sobre fondo azul | Una regla global les asignaba un color fijo | Usar la variable `--bs-heading-color` y cambiarla dentro de las secciones oscuras |
| Los montos se cortaban en celular | Tabla de siete columnas | Lista compacta en celular y columnas secundarias ocultas |
| Montos con un espacio como separador | El formato de Django para español usa un espacio | Formato propio `es_CL` |

**Verificación:** las 239 pruebas existentes siguieron pasando sin cambios después de cada rediseño, y se renderizaron las pantallas como personal, como cliente y sin sesión, todas con código 200.

**Si solo recuerdas esto:**

- Bootstrap pone la estructura; `estilos.css` solo agrega la marca.
- Un componente reutilizable (`{% include %}`) evita repetir el mismo HTML en cada pantalla.
- La página de error 500 no puede depender de nada que pueda fallar: ni sesión, ni menú, ni base de datos.

### Etapa 10: preparación para el despliegue en Render

**Objetivo:** dejar el proyecto listo para publicarse en Render (aplicación) con PostgreSQL en Neon (base de datos), sin escribir claves en el código y sin romper el funcionamiento local.

**Ramas de trabajo:** `feature/espera` (endpoint de salud y ventana de espera) y `feature/render` (configuración de producción), ambas ya fusionadas con `main`. Esta etapa no cambia los modelos, por lo que no genera migraciones.

**Subetapas:**

| Subetapa | Qué se hizo |
|---|---|
| 10.1 | Variables de entorno para `DEBUG`, `SECRET_KEY`, hosts y orígenes de confianza |
| 10.2 | Dependencias nuevas en `requirements.txt` |
| 10.3 | Base de datos por `DATABASE_URL` y archivos estáticos con WhiteNoise |
| 10.4 | Seguridad en producción y registros |
| 10.5 | Comando `crear_superusuario` |
| 10.6 | `build.sh`, `render.yaml` y `.gitattributes` |
| 10.7 | Endpoint `/salud/` y ventana de espera |
| 10.8 | Verificación simulando la producción en el equipo |
| 10.9 | Base de datos en Neon |
| 10.10 | Despliegue en Render y verificación en línea |

#### 10.1 Variables de entorno

Los valores que cambian entre el equipo y el servidor se leen del entorno. Si la variable no existe se usa el valor de desarrollo, así el proyecto sigue funcionando en local sin configurar nada.

| Variable | Para qué sirve | Valor en local | Valor en Render |
|---|---|---|---|
| `DEBUG` | Activa o no el modo de desarrollo | `True` (por defecto) | `False` |
| `SECRET_KEY` | Clave secreta de Django | Clave de desarrollo (pública) | Aleatoria, la genera Render |
| `ALLOWED_HOSTS` | Direcciones desde las que se puede entrar | Vacía | `.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes desde los que se aceptan formularios | Vacía | `https://*.onrender.com` |
| `DATABASE_URL` | Conexión completa a la base de datos | No existe | Dirección de Neon |
| `DJANGO_SUPERUSER_USERNAME`, `_EMAIL`, `_PASSWORD` | Datos del administrador | No existen | Privados, en el panel de Render |
| `CLAVE_DEMO` | Clave de los clientes de demostración | Opcional | Privada, en el panel de Render |

Si `DEBUG=False` y falta `SECRET_KEY` (o es la de desarrollo), la aplicación se niega a arrancar con un error `ImproperlyConfigured`. Así es imposible publicarla por descuido con la clave pública del repositorio. El punto inicial de `.onrender.com` incluye todos los subdominios.

#### 10.2 Dependencias

| Cambio en `requirements.txt` | Para qué |
|---|---|
| `gunicorn` | Servidor que ejecuta la aplicación en Render |
| `whitenoise` | Sirve CSS, JS e imágenes; en Render no hay otro servidor que lo haga |
| `dj-database-url` | Convierte `DATABASE_URL` en la configuración de Django |
| `psycopg` → `psycopg[binary]` | Instala directo en Render, sin compilar |

Además, el archivo se reescribió en UTF-8 sin BOM y con saltos de línea LF; tenía el formato de Windows.

#### 10.3 Base de datos y archivos estáticos

- **Base de datos:** si existe `DATABASE_URL`, tiene prioridad sobre todo lo demás (`dj_database_url.config(conn_max_age=600, conn_health_checks=True)`). Si no, se mantiene la lógica anterior: `DB_ENGINE=postgres` para PostgreSQL local o SQLite por defecto.
- **Archivos estáticos:** el middleware `whitenoise.middleware.WhiteNoiseMiddleware` va justo después de `SecurityMiddleware`. En producción (`DEBUG=False`) se usa `CompressedManifestStaticFilesStorage`, que comprime los archivos y les pone un código en el nombre (`estilos.9ea9b391c386.css`) para que el navegador descargue la versión nueva cuando cambian. Esa versión necesita haber ejecutado `collectstatic`, por eso en desarrollo se usa el almacenamiento normal.

#### 10.4 Seguridad y registros en producción

Cuando `DEBUG` es `False`:

| Configuración | Qué hace |
|---|---|
| `SECURE_PROXY_SSL_HEADER` | Render atiende el HTTPS por fuera y le pasa a Django la petición como HTTP; este encabezado le indica que el original era HTTPS |
| `SECURE_SSL_REDIRECT = True` | Redirige toda visita HTTP a HTTPS |
| `SECURE_REDIRECT_EXEMPT` | Exime a `/salud/`, que Render consulta por HTTP interno |
| `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` | Las cookies de sesión y de CSRF solo viajan por HTTPS |
| `SECURE_HSTS_SECONDS = 3600` | El navegador recordará usar solo HTTPS durante 1 hora (se puede subir cuando todo esté estable) |

**Registros:** con `DEBUG=False`, Django no muestra los errores en ninguna parte por defecto. Se configuró `LOGGING` para enviarlos a la consola, que es lo que Render muestra en la pestaña de registros.

#### 10.5 Comando `crear_superusuario`

Render gratuito no ofrece una terminal, así que el administrador no se puede crear con `createsuperuser`. El comando `python manage.py crear_superusuario` lo crea desde las variables `DJANGO_SUPERUSER_*`:

- Si faltan las variables, no hace nada (así no falla en local).
- Si el usuario ya existe, no lo toca (repetir el despliegue no cambia una clave que se haya modificado después).
- Nunca imprime la contraseña.

Tiene 4 pruebas en `gestion/tests/test_comandos.py`: crea el superusuario, no hace nada sin variables, repetirlo no cambia la clave y no muestra la clave en pantalla.

#### 10.6 `build.sh`, `render.yaml` y `.gitattributes`

`build.sh` se ejecuta en cada despliegue y se detiene si cualquier paso falla (`set -o errexit`):

| Paso | Comando |
|---|---|
| 1 | `pip install -r requirements.txt` |
| 2 | `python manage.py collectstatic --no-input` |
| 3 | `python manage.py migrate --no-input` |
| 4 | `python manage.py crear_superusuario` |
| 5 | `python manage.py poblar_datos` (no duplica y no cambia las claves de usuarios que ya existen) |

`render.yaml` es el plano del servicio: tipo web, plan gratuito, `buildCommand: bash build.sh`, `startCommand: gunicorn core.wsgi:application --workers 2 --timeout 120` y `healthCheckPath: /salud/`. Los valores privados (`DATABASE_URL`, `DJANGO_SUPERUSER_*` y `CLAVE_DEMO`) están marcados con `sync: false`: se escriben a mano en el panel y no se guardan en el repositorio.

`.gitattributes` fuerza saltos de línea LF en `*.sh`, `render.yaml` y `requirements.txt`. Con los saltos de Windows (CRLF), Linux no puede ejecutar `build.sh`.

#### 10.7 Endpoint `/salud/` y ventana de espera

`/salud/` responde `{"estado": "ok"}` sin sesión ni consulta a la base de datos, y tiene una prueba. La usa Render para saber que la aplicación arrancó.

**Ventana de espera:** el plan gratuito de Render duerme el servicio tras 15 minutos sin visitas y la primera respuesta puede tardar cerca de un minuto; la base de Neon también se suspende por inactividad. Al enviar el formulario de inicio de sesión o el de registro, la aplicación muestra una ventana con un indicador de carga cuyo mensaje cambia con el tiempo:

| Tiempo | Mensaje |
|---|---|
| Al enviar | "Estamos procesando tu solicitud" |
| 4 segundos | "Esto está tardando un poco más de lo normal" |
| 20 segundos | "Despertando el servidor…", con la explicación de que la demostración usa un servidor gratuito |
| 75 segundos | Aparece el botón "Reintentar" |

Desaparece sola: cuando el servidor responde, el navegador carga la página siguiente. Se activa con el atributo `data-espera` en el formulario y se implementa en `static/js/app.js`. Una página puente en GitHub Pages que sondeara `/salud/` desde otro dominio se consideró y se descartó por ser más llamativa: no existe ningún `docs/index.html` en el proyecto, y `/salud/` solo la consulta Render. La primera carga con el servicio dormido la muestra Render con su propia pantalla, que no se puede personalizar en el plan gratuito; la ventana cubre lo que ocurre después.

#### 10.8 Verificación simulando la producción

Con `DEBUG=False`, `SECRET_KEY` y `DATABASE_URL` definidos, una base temporal y el mismo orden de pasos de `build.sh`, se comprobó:

| Comprobación | Resultado |
|---|---|
| `collectstatic` | 399 archivos procesados con nombre con código |
| `migrate` | Todas las migraciones aplicadas |
| `crear_superusuario` (dos veces) | La primera crea el usuario; la segunda informa que ya existe |
| `poblar_datos` | Datos de demostración cargados |
| `/salud/` por HTTP | 200 `{"estado": "ok"}` |
| Otra página por HTTP | 301 hacia HTTPS |
| Login por HTTPS | 200 |
| CSS con código en el nombre | 200, `text/css`, caché de largo plazo |
| Dirección inexistente | 404 con la página propia |
| Inicio de sesión de un cliente | 302 al inicio; cookies de sesión y CSRF con `secure` |
| Arrancar sin `SECRET_KEY` | `ImproperlyConfigured` |

Las 244 pruebas pasan. `check --deploy` informa un error por el backend de correo de consola (la aplicación no envía correos) y avisos de HSTS que se dejaron sin cambiar a propósito. Gunicorn no corre en Windows, así que la verificación usa el cliente de pruebas de Django, que recorre las mismas capas (incluido WhiteNoise); el arranque con gunicorn solo se podrá comprobar en Render.

#### 10.9 Base de datos en Neon

Se creó un proyecto en Neon y se usó la **cadena de conexión directa** (sin la opción "pooled"), para evitar problemas con los cursores del servidor de Django. La conexión se verificó desde el equipo con `DATABASE_URL` definida solo para esa sesión de PowerShell:

```powershell
$env:DATABASE_URL = "postgresql://usuario:clave@host/base?sslmode=require"
.\venv\Scripts\python.exe manage.py showmigrations gestion
```

Las dos migraciones aparecieron sin aplicar (`[ ]`), lo que confirma que se conecta a la base nueva y vacía de Neon, y no al `db.sqlite3` local. La cadena de conexión nunca se escribe en un archivo del repositorio.

**Decisiones:**

| Decisión | Alternativa | Por qué |
|---|---|---|
| Render | Vercel | Vercel es serverless: no sirve archivos estáticos de Django ni mantiene SQLite. Render ejecuta la aplicación como un servicio normal |
| Neon para la base de datos | PostgreSQL de Render | La base gratuita de Render expira; la de Neon no |
| `DATABASE_URL` con prioridad | Variables `DB_*` separadas | Una sola cadena es lo que entregan Neon y Render |
| Archivos estáticos con código en el nombre solo con `DEBUG=False` | Siempre | Requieren `collectstatic`; en desarrollo y en las pruebas fallarían |
| Comando `crear_superusuario` | Crear el administrador desde una terminal | Render gratuito no tiene terminal |
| `poblar_datos` en cada construcción | Cargarlo una vez a mano | Es idempotente y deja la demostración siempre disponible |
| Clave de demostración solo para clientes, definida con `CLAVE_DEMO` en el panel de Render y fuera del repositorio | Publicar también la del administrador, o escribir la clave en el README | El personal puede borrar todos los datos, y una clave escrita en el repositorio la detectan los escáneres de secretos |
| Cadena directa de Neon | Cadena con pooler | El pooler puede dar problemas con los cursores de Django |

**Incidencias resueltas:**

| Problema | Causa | Solución |
|---|---|---|
| `.env.example` tenía `B_ENGINE` | Error de tipeo (faltaba la `D` de `DB_ENGINE`) | Corregido y documentadas las variables de producción |
| Un script con saltos de línea de Windows falla en Linux | Git en Windows convierte LF en CRLF | `.gitattributes` con `eol=lf` |
| Los errores no aparecerían en los registros de Render | Con `DEBUG=False` Django no los muestra por defecto | Configuración `LOGGING` hacia la consola |
| `requirements.txt` con BOM y saltos de Windows | Se generó con PowerShell | Reescrito en UTF-8 sin BOM y con LF |

#### 10.10 Despliegue en Render y verificación en línea

| Paso | Estado |
|---|---|
| Código y configuración de producción | Listo |
| Base de datos en Neon y conexión verificada | Listo |
| `main` publicada en GitHub (15 commits y 3 ramas), tras revisar que no se filtraran claves | Listo |
| Servicio creado en Render como Blueprint desde `render.yaml`, con los valores privados cargados en el panel | Listo |
| Verificación en línea | Listo |

**Servicio:** `alke-wallet`, plan gratuito, rama `main`, dirección <https://alke-wallet.onrender.com>. Se creó desde **New + → Blueprint**, que lee `render.yaml`. Los valores privados (`DATABASE_URL`, `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` y `CLAVE_DEMO`) se escribieron a mano en el panel y no existen en el repositorio. En cada construcción se ejecuta `build.sh` y luego arranca gunicorn. Por defecto, Render vuelve a desplegar cada vez que se publica un cambio en `main`.

**Verificación externa** (peticiones de solo lectura sin sesión):

| Dirección | Resultado |
|---|---|
| `/salud/` | 200, `{"estado": "ok"}` |
| `/acceso/login/` y `/registro/` | 200 |
| `/clientes/` sin sesión | 302 hacia el login |
| Una dirección inexistente | 404 con la página propia |
| `/static/css/estilos.css` | 200, `text/css` (WhiteNoise) |
| Cookies | Con el atributo `Secure` |
| Encabezados | `Strict-Transport-Security` (HSTS), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` y `Referrer-Policy: same-origin` |

**Verificación manual:** se comprobaron en línea el inicio de sesión de un cliente de demostración, el CRUD, el reporte, los estilos y las páginas de error.

**Observaciones:**

- **Versión de Python:** el despliegue se completó con `PYTHON_VERSION=3.13.5`, así que el supuesto quedó confirmado. En local se sigue usando Python 3.14.6.
- **Región:** `render.yaml` no fija una región, por lo que el servicio usa la que Render asigna por defecto. Si se notara latencia entre la aplicación y la base de Neon, es lo primero que habría que revisar.
**Evidencias:**

![Servicio alke-wallet en estado Live en Render, desplegado desde la rama main](docs/capturas/144_render_servicio_live.png)

![Portada en línea, en alke-wallet.onrender.com](docs/capturas/149_app_en_linea_portada.png)

![Inicio del personal en línea, con los totales y los últimos movimientos](docs/capturas/145_app_en_linea_inicio_personal.png)

![Inicio de un cliente en línea, con su cuenta y su saldo](docs/capturas/148_app_en_linea_inicio_cliente.png)

![Página 404 propia en línea, con el botón que vuelve al panel](docs/capturas/146_app_en_linea_404.png)

![Comprobación de salud en línea: {"estado": "ok"}](docs/capturas/147_app_en_linea_salud.png)

![Tablas gestion_* creadas por las migraciones en la base de Neon](docs/capturas/150_neon_tablas.png)

**Limitaciones conocidas:**

- El plan gratuito de Render duerme el servicio tras 15 minutos sin visitas y tarda cerca de un minuto en despertar; Neon también se suspende por inactividad.
- La demostración pública permite que cualquiera se registre y cree datos de prueba.

**Si solo recuerdas esto:**

- Nada privado va al repositorio: lo que cambia entre el equipo y el servidor se lee de variables de entorno.
- `DEBUG=False` cambia varias cosas a la vez: estáticos con código, HTTPS obligatorio, cookies seguras y la exigencia de una `SECRET_KEY` propia.
- Sin terminal, todo lo que se hace una vez (administrador, datos de ejemplo) debe poder ejecutarse sin intervención en la construcción.

### Etapa 11: revisión final y publicación

**Objetivo:** dejar el proyecto listo para entregarlo y mostrarlo.

**Subetapas:**

| Subetapa | Qué se hizo |
|---|---|
| 11.1 | Revisión del repositorio: sin `.env`, base de datos, entornos virtuales ni claves escritas en el código; `.gitignore` y `.env.example` al día; migraciones sin cambios pendientes; dependencias con versiones fijas; instalación desde cero comprobada (239 pruebas en `OK` en ese momento; hoy son 244) |
| 11.2 | README completo con la documentación por etapa, que se usa para generar el documento técnico en Word |

**Pendiente:**

- Versión resumida del README para quien solo quiera inspeccionar el proyecto, con el detalle de cada etapa en el documento Word.
- Actualizar el informe de pruebas con el total actual (244).
- Demostración funcional en video y tarjeta del proyecto en el portafolio.

## Flujo de Git

| Rama | Propósito | Estado |
|---|---|---|
| `main` | Código estable | Activa |
| `feature/modelos` | Definición de modelos y migraciones | Fusionada con `main` (fast-forward) |
| `feature/consultas` | Datos de demostración y consultas personalizadas | Fusionada con `main` |
| `feature/admin` | Idioma, nombres legibles y panel de administración | Fusionada con `main` |
| `feature/crud` | Vistas, formularios, servicio de movimientos, contactos y reporte | Fusionada con `main` |
| `feature/auth` | Login, estáticos, roles, alcance por usuario, registro, perfil y verificación de accesos | Fusionada con `main` |
| `feature/tests` | Pruebas automatizadas (modelos, servicios, consultas, formularios, vistas y seguridad) e informe | Fusionada con `main` |
| `fix/clave-demo` | Clave de los usuarios de demostración al azar o desde `.env` | Fusionada con `main` |
| `feature/bootstrap` | Rediseño con Bootstrap: portada, componentes, diseño responsive, páginas de error y formato de montos | Fusionada con `main` (7 commits por tema, fast-forward) |
| `feature/espera` | Endpoint `/salud/` y ventana de espera al iniciar sesión o registrarse | Fusionada con `main` |
| `feature/render` | Configuración de producción, `crear_superusuario`, `build.sh`, `render.yaml` y actualización del README | Fusionada con `main` |

## Mejoras futuras

- Recuperación de contraseña por correo y verificación del correo al registrarse.
- Bloqueo temporal tras varios intentos fallidos de ingreso.
- Número de cuenta generado de forma segura ante registros simultáneos.
- Medición de cobertura de código con `coverage.py` y pruebas de interfaz con un navegador automatizado.
- Modo oscuro (Bootstrap lo admite, pero la paleta de la marca está fija y habría que rediseñarla).
- Gráficos interactivos en el reporte (hoy las proporciones son barras hechas con CSS).
- Limpieza automática de los usuarios de prueba que se registren en la demostración pública.
- Dominio propio y envío real de correos (hoy el proyecto no envía ninguno).

## Autor

**Javier** · Full Stack Python Trainee (Talento Digital / Alkemy)

- GitHub: [github.com/Javiermll](https://github.com/Javiermll)
- LinkedIn: [linkedin.com/in/jamunozll](https://linkedin.com/in/jamunozll)
- Portafolio: [javiermll.github.io/Portafolio](https://javiermll.github.io/Portafolio)

Proyecto con fines educativos, desarrollado para el Módulo 7 del bootcamp.
