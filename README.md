# AdoptaPatitas

Aplicación web para la gestión integral de una protectora de animales y la
facilitación del proceso de adopción.

Trabajo de Fin de Grado — 2.º curso de Desarrollo de Aplicaciones
Multiplataforma (DAM).

## Stack tecnológico

- Python + Django
- PostgreSQL
- Django Templates + HTML5 + CSS3 + JavaScript + Bootstrap

## Requisitos previos

- Python 3.12 o superior.
- PostgreSQL instalado y en ejecución localmente.
- pip.

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd AdoptaPatitas
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows (Git Bash)
source venv/Scripts/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo y edítalo con tus propios valores locales:

```bash
cp .env.example .env
```

Variables que debes rellenar en `.env`:

- `SECRET_KEY`: clave secreta de Django. Puedes generar una con:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- `DEBUG`: `True` en desarrollo local.
- `ALLOWED_HOSTS`: hosts permitidos, separados por comas (ej. `localhost,127.0.0.1`).
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: credenciales de conexión a PostgreSQL.

**El archivo `.env` nunca debe subirse al repositorio.**

### 5. Configurar la base de datos en PostgreSQL

Crea un usuario y una base de datos propios para el proyecto (evita usar el
superusuario `postgres` para la aplicación). Desde `psql` o una terminal con
acceso a PostgreSQL:

```sql
CREATE USER adoptapatitas_user WITH PASSWORD 'tu_password_local';
CREATE DATABASE adoptapatitas_dev OWNER adoptapatitas_user;
GRANT ALL PRIVILEGES ON DATABASE adoptapatitas_dev TO adoptapatitas_user;
ALTER USER adoptapatitas_user CREATEDB;
```

La última línea (`CREATEDB`) es necesaria para poder ejecutar
`python manage.py test`, ya que Django crea automáticamente una base de
datos temporal de pruebas y la destruye al finalizar.

Asegúrate de que los valores de `DB_NAME`, `DB_USER` y `DB_PASSWORD` en tu
`.env` coinciden con los que hayas usado aquí.

> **Nota sobre el modelo de usuario:** el proyecto utiliza un modelo de
> usuario personalizado (`usuarios.Usuario`, configurado mediante
> `AUTH_USER_MODEL`). Si ya habías ejecutado `migrate` antes de que existiera
> la app `usuarios`, tendrás que recrear tu base de datos de desarrollo desde
> cero (borrarla y volver a crearla vacía con los comandos anteriores) antes
> de continuar, ya que Django no permite cambiar `AUTH_USER_MODEL` sobre una
> base de datos que ya tiene migraciones aplicadas con el usuario por
> defecto.

### 6. Aplicar las migraciones

```bash
python manage.py migrate
```

### 7. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/`.

### 8. Ejecutar los tests

```bash
python manage.py test
```