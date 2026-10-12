# Portafolio

Portafolio modular en Django para publicar artículos, investigación académica y proyectos de matemáticas e ingeniería. El contenido se gestiona desde Django Admin; no hay registro público.

## Módulos y rutas

| Sección | Qué contiene | Rutas públicas |
| --- | --- | --- |
| Inicio (`core`) | Perfil editable, enlaces públicos y selecciones de contenido | `/` |
| Blog (`blog`) | Artículos con estado borrador o publicado | `/blog/`, `/blog/<slug>/` |
| Investigación (`research`) | Trabajos relacionados con matemáticas y educación | `/investigacion/`, `/investigacion/<slug>/` |
| Proyectos (`projects`) | Implementaciones, repositorios y demos | `/proyectos/`, `/proyectos/<slug>/` |
| Administración | Gestión del contenido y usuarios | `/admin/` |

La portada muestra hasta tres entradas publicadas, tres trabajos de investigación y tres proyectos marcados como destacados. Los listados y detalles siguen disponibles aunque no haya contenido.

## Requisitos

- Python 3.13 (la versión usada en el desarrollo inicial).
- Git para el flujo de despliegue en Render.
- Las dependencias del proyecto, instaladas desde `requirements.txt`.

## Desarrollo local

En PowerShell, desde la carpeta del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre <http://127.0.0.1:8000/> para el sitio y <http://127.0.0.1:8000/admin/> para el panel. Si PowerShell bloquea la activación del entorno, puedes ejecutar los comandos usando `.venv\Scripts\python.exe` sin activarlo.

La configuración local usa SQLite y `DEBUG=True`. La base local se guarda en `db.sqlite3`, que no se incluye en Git. `DATABASE_URL` permite elegir otra base compatible, como PostgreSQL.

## Primer acceso al Admin

1. Ejecuta `python manage.py createsuperuser` en la terminal del proyecto.
2. Escribe el nombre de usuario, correo (si lo solicita) y contraseña. La contraseña no se muestra mientras la escribes.
3. Inicia el servidor con `python manage.py runserver`.
4. Abre `/admin/`, inicia sesión y entra a la sección correspondiente: **Perfil del portafolio**, **Posts**, **Trabajos de investigación** o **Projects**.
5. Selecciona **Add**, completa el formulario y guarda. Usa **Save and continue editing** si quieres seguir modificando el registro.

El superusuario tiene acceso completo. No existe creación de cuentas desde el sitio público; las cuentas adicionales se crean desde **Authentication and Authorization > Users** y deben tener permisos de staff para entrar al Admin. Comparte credenciales solo con personas que deban administrar el sitio.

#### Crear el primer administrador en Render

Si tu plan no incluye Shell, configura estas variables en **Environment** para el servicio web:

- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

Después, despliega o reinicia el servicio. El comando de inicio ejecuta `bootstrap_superuser` después de las migraciones; crea el usuario solo si todavía no existe. Si las tres variables están vacías, no hace nada; si falta alguna, el inicio falla explícitamente. Una vez creado, puedes borrar estas variables de Render. El comando no cambia la contraseña de un usuario existente. Asegúrate de que `DATABASE_URL` apunte a una base de datos persistente antes de habilitar este método.

### Administrar el perfil

La migración inicial crea un perfil con la información proporcionada para este portafolio. En **Perfil del portafolio**, selecciona el registro para cambiar el nombre, título y biografía que aparecen en la portada. También puedes modificar el correo público, GitHub y LinkedIn. ORCID, Google Scholar y CV son campos opcionales; los enlaces vacíos no se muestran. Por ahora el ORCID no está publicado.

El perfil es único: se edita el registro existente y no se puede crear un segundo desde Admin. Los cambios se reflejan en la siguiente visita a la portada. El correo se presenta como enlace `mailto:` y los demás perfiles se abren en otra pestaña.

### Administrar el currículum

En el módulo **CV** puedes editar el perfil profesional, experiencias, formación académica y productos de investigación. Los campos de texto largo incluyen un editor Markdown con vista previa; usa los botones de lista con viñetas o numerada para organizar responsabilidades y logros. El formato se conserva en la página pública del CV y en su descarga PDF.

### Administrar el blog

En **Posts**, selecciona **Add post**. Los campos son:

| Campo | Uso |
| --- | --- |
| Title | Título del artículo. |
| Slug | Identificador de la URL. El Admin lo propone a partir del título; verifica que sea único y legible. |
| Excerpt | Resumen opcional mostrado en el listado. Si se deja vacío, se usa el inicio del contenido. |
| Content | Texto del artículo. Se respetan saltos de línea; todavía no hay editor Markdown o de texto enriquecido. |
| Status | `Borrador` mantiene el artículo privado; `Publicado` lo hace visible. |
| Published at | Fecha/hora opcional. Se debe introducir manualmente; cambiar el estado a publicado no completa esta fecha automáticamente. |

Para publicar, cambia **Status** a **Publicado** y guarda. Para retirarlo del sitio, vuelve a **Borrador**. Un artículo borrador no aparece en el listado y su URL responde 404. La lista se ordena por fecha de publicación y luego por creación.

### Administrar investigación

En **Trabajos de investigación**, añade un registro por publicación o trabajo:

| Campo | Uso |
| --- | --- |
| Title y Slug | Título y URL única; el slug se propone desde el título. |
| Topic | Matemáticas, Educación o Matemáticas y educación. |
| Abstract | Resumen mostrado en la ficha y en el listado. |
| Authors | Autores, como texto libre; admite varios nombres en un solo campo. |
| Publication | Revista, congreso, institución u otra referencia bibliográfica. |
| Year | Año de publicación; opcional. |
| Publication URL | Enlace externo a la publicación; opcional, debe ser una URL válida. |

El listado se ordena por año descendente y título. No hay estados de borrador para esta sección: cada elemento guardado queda visible.

### Administrar proyectos

En **Projects**, añade una ficha para cada implementación:

| Campo | Uso |
| --- | --- |
| Title y Slug | Nombre y URL única; el slug se propone desde el título. |
| Summary | Resumen corto, hasta 300 caracteres. |
| Description | Descripción completa; se respetan saltos de línea. |
| Technologies | Tecnologías usadas, en texto libre; puedes separarlas con comas. |
| Repository URL | Enlace al código fuente; opcional. |
| Demo URL | Enlace a la implementación; opcional. |
| Featured | Si está marcado, el proyecto puede aparecer entre los destacados de la portada. |

Todos los proyectos guardados aparecen en `/proyectos/`. Los destacados se ordenan primero; la portada muestra hasta tres.

## Estructura del proyecto

- `config/`: configuración Django, rutas raíz y punto de entrada WSGI.
- `core/`: portada, perfil único y su administración.
- `blog/`: modelo, vistas, rutas, Admin y pruebas del blog.
- `research/`: fichas académicas y su administración.
- `projects/`: fichas de implementación y su administración.
- `templates/`: plantillas HTML compartidas y por sección.
- `requirements.txt`: dependencias Python.
- `build.sh`: instala dependencias y recopila archivos estáticos.
- `render.yaml`: definición del servicio web y PostgreSQL en Render.

### Añadir otro módulo

Como punto de partida, crea una app Django con `python manage.py startapp nombre_app`. Añádela a `INSTALLED_APPS` en `config/settings.py`; define sus modelos, vistas, rutas, plantillas y registro en `admin.py`; después incluye sus rutas en `config/urls.py`. Para los modelos nuevos, genera y versiona migraciones:

```powershell
python manage.py makemigrations nombre_app
python manage.py migrate
python manage.py test nombre_app
```

En producción, el comando de inicio de Render aplica las migraciones pendientes automáticamente.

## Pruebas y comprobaciones

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
```

Las pruebas actuales verifican que el blog mantiene los borradores privados y que la portada carga sin contenido.

## Despliegue en Render

El archivo `render.yaml` define un servicio web Python, una base PostgreSQL y estas acciones:

- **Build:** `bash build.sh`, que instala `requirements.txt` y recopila estáticos.
- **Inicio:** aplica migraciones y ejecuta Gunicorn con `config.wsgi:application`.
- **Variables:** Render conecta `DATABASE_URL`, genera `SECRET_KEY` y establece `DEBUG=False`.

Pasos para desplegar:

1. Sube este proyecto a un repositorio Git remoto.
2. En Render, crea un **Blueprint** y conecta el repositorio.
3. Revisa los recursos que describe `render.yaml` y confirma su creación.
4. Espera a que terminen el build y el primer deploy. Render proporciona el dominio del sitio.
5. En el dashboard del servicio web, abre **Shell** y ejecuta `python manage.py createsuperuser` para crear el administrador de producción.
6. Entra a `https://<dominio-de-render>/admin/` y comienza a cargar contenido.

No se ha realizado un despliegue remoto desde este workspace. En Render, conserva `DEBUG=False` y no publiques `SECRET_KEY` ni credenciales de base de datos. Render ya permite el hostname asignado mediante `RENDER_EXTERNAL_HOSTNAME`. Si conectas un dominio propio, configura `ALLOWED_HOSTS` con ese hostname y `CSRF_TRUSTED_ORIGINS` con su origen HTTPS, por ejemplo `https://www.ejemplo.com`.

El servicio usa HTTPS, redirección a HTTPS y HSTS básico cuando `DEBUG=False`. La configuración no activa HSTS para todos los subdominios ni preload. Los estáticos se sirven mediante WhiteNoise.

## Límites actuales y siguientes decisiones

- No se han implementado carga de imágenes o documentos, categorías, etiquetas, búsqueda, paginación, comentarios ni editor enriquecido.
- El texto de artículos, resúmenes y descripciones es texto plano; las plantillas muestran los saltos de línea.
- Los archivos guardados en el disco local de un servicio Render no son almacenamiento persistente. Antes de añadir imágenes o documentos, integra almacenamiento de objetos u otro servicio persistente.
- La base PostgreSQL de Render tiene su propio ciclo de vida y plan. Configura una estrategia de respaldo adecuada antes de depender de ella para datos importantes.