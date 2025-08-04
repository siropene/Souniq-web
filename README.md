# SouniQ Web - Plataforma de Procesamiento Musical con IA

![SouniQ Logo](static/images/LOGO_SOUNIQ.png)

SouniQ Web es una aplicación Django avanzada que permite a los usuarios procesar música utilizando inteligencia artificial. La plataforma ofrece tres funcionalidades principales: separación de stems, conversión a MIDI y generación de nuevas pistas musicales.

## 🎵 Características Principales

### 1. Separación de Stems
- **Carga de canciones**: Soporta formatos MP3, WAV, FLAC
- **División automática**: Separa canciones en 7 stems diferentes:
  - Vocals (Voces)
  - Drums (Batería)
  - Bass (Bajo)
  - Piano (Piano)
  - Guitar (Guitarra)
  - Synth (Sintetizador)
  - Other (Otros instrumentos)
- **API Integration**: Utiliza el modelo "SouniQ/Modulo1" de Hugging Face

### 2. Conversión a MIDI
- **Procesamiento de stems**: Convierte stems de audio a archivos MIDI
- **Múltiples formatos**: Entrada de audio → salida MIDI estándar
- **API Integration**: Utiliza el modelo "SouniQ/Modulo2" de Hugging Face

### 3. Generación de Nuevas Pistas
- **Composición con IA**: Genera nuevas canciones basadas en archivos MIDI
- **Parámetros configurables**: Tempo, duración, estilo musical
- **API Integration**: Utiliza "asigalov61/Giant-Music-Transformer" de Hugging Face

## 🛠 Tecnologías Utilizadas

### Backend
- **Django 4.2**: Framework web principal
- **Python 3.11**: Lenguaje de programación
- **Celery**: Procesamiento de tareas en segundo plano
- **Redis**: Broker de mensajes para Celery
- **SQLite**: Base de datos de desarrollo
- **Gradio Client**: Cliente para APIs de Hugging Face

### Frontend
- **Bootstrap 5**: Framework CSS para diseño responsivo
- **FontAwesome**: Iconografía
- **Custom CSS**: Estilos personalizados con paleta corporativa
- **JavaScript**: Interactividad y validaciones del lado cliente

### Autenticación y Usuarios
- **Django Auth**: Sistema de autenticación integrado
- **User Profiles**: Perfiles de usuario extendidos
- **Activity Logging**: Registro de actividad del usuario

## 📋 Requisitos del Sistema

### Software Requerido
```bash
Python 3.11+
Redis Server
Git
```

### Dependencias Python
```bash
Django==4.2.7
celery==5.3.4
redis==5.0.1
gradio-client==0.7.1
django-crispy-forms==2.1
crispy-bootstrap5==0.7
whitenoise==6.6.0
pillow==10.1.0
```

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd WEB2
```

### 2. Configurar Entorno Virtual
```bash
python3.11 -m venv venv
source venv/bin/activate  # En macOS/Linux
# venv\Scripts\activate  # En Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
HUGGINGFACE_TOKEN=tu_token_de_huggingface
REDIS_URL=redis://localhost:6379/0
```

### 5. Configurar Base de Datos
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Recopilar Archivos Estáticos
```bash
python manage.py collectstatic --noinput
```

### 7. Instalar y Configurar Redis
```bash
# macOS con Homebrew
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# Verificar instalación
redis-cli ping
```

## 🏃‍♂️ Ejecución del Proyecto

### Método 1: Script de Inicio (Recomendado)
```bash
chmod +x start_dev.sh
./start_dev.sh
```

### Método 2: Ejecución Manual
```bash
# Terminal 1: Iniciar Celery Worker
celery -A souniq_web worker --loglevel=info

# Terminal 2: Iniciar Celery Beat (opcional)
celery -A souniq_web beat --loglevel=info

# Terminal 3: Iniciar Django
python manage.py runserver
```

### Acceso a la Aplicación
- **Aplicación web**: http://127.0.0.1:8000
- **Panel de administración**: http://127.0.0.1:8000/admin

## 📁 Estructura del Proyecto

```
WEB2/
├── souniq_web/              # Configuración principal de Django
│   ├── __init__.py
│   ├── settings.py          # Configuración de la aplicación
│   ├── urls.py             # URLs principales
│   ├── wsgi.py             # Configuración WSGI
│   └── celery.py           # Configuración de Celery
├── accounts/               # Aplicación de usuarios
│   ├── models.py           # Modelos de perfil de usuario
│   ├── views.py            # Vistas de autenticación
│   ├── forms.py            # Formularios de usuario
│   ├── urls.py             # URLs de cuentas
│   └── admin.py            # Configuración del admin
├── music_processing/       # Aplicación principal de procesamiento
│   ├── models.py           # Modelos de datos musicales
│   ├── views.py            # Vistas del procesamiento
│   ├── forms.py            # Formularios de carga
│   ├── tasks.py            # Tareas de Celery
│   ├── urls.py             # URLs de procesamiento
│   └── admin.py            # Configuración del admin
├── core/                   # Aplicación núcleo
│   ├── views.py            # Vistas generales
│   ├── urls.py             # URLs principales
│   └── utils.py            # Utilidades comunes
├── templates/              # Plantillas HTML
│   ├── base.html           # Plantilla base
│   ├── accounts/           # Plantillas de usuarios
│   ├── music_processing/   # Plantillas de procesamiento
│   └── core/               # Plantillas generales
├── static/                 # Archivos estáticos
│   ├── css/                # Hojas de estilo
│   ├── js/                 # Scripts JavaScript
│   └── images/             # Imágenes y logo
├── media/                  # Archivos subidos por usuarios
│   ├── songs/              # Canciones originales
│   ├── stems/              # Stems generados
│   ├── midi_files/         # Archivos MIDI
│   └── generated_tracks/   # Pistas generadas
├── requirements.txt        # Dependencias Python
├── start_dev.sh           # Script de inicio
└── README.md              # Este archivo
```

## 🔧 Configuración de APIs

### Hugging Face Token
1. Crear cuenta en [Hugging Face](https://huggingface.co)
2. Obtener token de acceso en Settings > Access Tokens
3. Configurar en archivo `.env`:
   ```env
   HUGGINGFACE_TOKEN=hf_tu_token_aqui
   ```

### APIs Utilizadas
- **SouniQ/Modulo1**: Separación de stems
- **SouniQ/Modulo2**: Conversión a MIDI
- **asigalov61/Giant-Music-Transformer**: Generación de pistas

## 👥 Gestión de Usuarios

### Características de Usuario
- **Registro y autenticación**: Sistema completo de cuentas
- **Perfiles personalizados**: Avatar, biografía, información personal
- **Historial de actividad**: Seguimiento de acciones del usuario
- **Notificaciones**: Email y notificaciones de procesamiento
- **Estadísticas**: Contador de canciones, stems, MIDIs generados

### Roles y Permisos
- **Usuario regular**: Puede usar todas las funcionalidades
- **Administrador**: Acceso al panel de admin de Django
- **Staff**: Gestión de usuarios y contenido

## 🎨 Diseño y UX

### Paleta de Colores
- **Primario**: #007bff (Azul SouniQ)
- **Secundario**: #6c757d (Gris)
- **Éxito**: #28a745 (Verde)
- **Advertencia**: #ffc107 (Amarillo)
- **Peligro**: #dc3545 (Rojo)

### Características de Diseño
- **Responsive**: Adaptado a móviles, tablets y desktop
- **Accesibilidad**: Cumple estándares WCAG
- **Logo integration**: Logo SouniQ prominente en navegación
- **Modern UI**: Interfaz limpia y profesional

## 🔍 Monitoreo y Logs

### Logs de Django
```bash
# Ver logs en tiempo real
tail -f logs/django.log
```

### Logs de Celery
```bash
# Ver estado de workers
celery -A souniq_web inspect active

# Ver estadísticas
celery -A souniq_web inspect stats
```

### Monitoreo de Redis
```bash
# Conectar a Redis
redis-cli

# Ver información
INFO
MONITOR
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
python manage.py test

# Tests específicos de app
python manage.py test music_processing
python manage.py test accounts
```

### Coverage
```bash
# Instalar coverage
pip install coverage

# Ejecutar con coverage
coverage run manage.py test
coverage report
coverage html
```

## 📦 Deployment

### Preparación para Producción
1. **Configurar variables de entorno**:
   ```env
   DEBUG=False
   SECRET_KEY=clave_secreta_muy_segura
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...
   ALLOWED_HOSTS=tu-dominio.com
   ```

2. **Configurar base de datos PostgreSQL**
3. **Configurar servidor web (Nginx + Gunicorn)**
4. **Configurar SSL/TLS**
5. **Configurar backup automático**

### Docker (Opcional)
```dockerfile
# Ejemplo de Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "souniq_web.wsgi:application"]
```

## 🐛 Troubleshooting

### Problemas Comunes

**Error: Redis Connection**
```bash
# Verificar que Redis esté ejecutándose
redis-cli ping
# Respuesta esperada: PONG
```

**Error: Celery Worker**
```bash
# Reiniciar worker
pkill -f "celery worker"
celery -A souniq_web worker --loglevel=info
```

**Error: Migraciones**
```bash
# Reset migraciones
python manage.py migrate --fake-initial
python manage.py makemigrations
python manage.py migrate
```

**Error: Archivos Estáticos**
```bash
# Recopilar archivos estáticos
python manage.py collectstatic --clear --noinput
```

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📞 Soporte

Para soporte técnico o preguntas:
- **Email**: soporte@souniq.com
- **GitHub Issues**: [Crear nuevo issue](https://github.com/tu-usuario/souniq-web/issues)
- **Documentación**: [Wiki del proyecto](https://github.com/tu-usuario/souniq-web/wiki)

## 🔄 Changelog

### v1.0.0 (2024-01-XX)
- ✨ Funcionalidad inicial de separación de stems
- ✨ Conversión de audio a MIDI
- ✨ Generación de pistas con IA
- ✨ Sistema completo de usuarios
- ✨ Panel de administración
- ✨ Diseño responsive con logo SouniQ

---

**SouniQ Web** - Transformando la música con inteligencia artificial 🎵🤖
   SECRET_KEY=tu_clave_secreta_aqui
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   HUGGINGFACE_TOKEN=tu_token_de_huggingface
   ```

5. **Ejecutar migraciones**:
   ```bash
   python manage.py migrate
   ```

6. **Crear superusuario**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Recopilar archivos estáticos**:
   ```bash
   python manage.py collectstatic
   ```

## Ejecución

### Desarrollo

1. **Iniciar Redis** (en otra terminal):
   ```bash
   redis-server
   ```

2. **Iniciar Celery Worker** (en otra terminal):
   ```bash
   celery -A souniq_web worker --loglevel=info
   ```

3. **Iniciar servidor Django**:
   ```bash
   python manage.py runserver
   ```

4. **Acceder a la aplicación**:
   - Web: http://127.0.0.1:8000
   - Admin: http://127.0.0.1:8000/admin

## Estructura del Proyecto

```
WEB2/
├── accounts/              # Aplicación de gestión de usuarios
├── core/                  # Aplicación principal
├── music_processing/      # Aplicación de procesamiento musical
├── souniq_web/           # Configuración principal de Django
├── static/               # Archivos estáticos (CSS, JS, imágenes)
├── templates/            # Plantillas HTML
├── media/                # Archivos subidos por usuarios
├── .env                  # Variables de entorno
├── requirements.txt      # Dependencias Python
└── manage.py            # Script de gestión de Django
```

## Funcionalidades Principales

### 1. Gestión de Usuarios
- Registro y login
- Perfiles de usuario
- Reseteo de contraseña con doble factor
- Registro de actividad

### 2. Procesamiento Musical
- Subida de archivos de audio (MP3, WAV, FLAC, AAC, M4A)
- Generación automática de stems usando IA
- Visualización y descarga de stems
- Reproductor de audio integrado

### 3. Conversión MIDI
- Conversión de stems a archivos MIDI
- Descarga de archivos MIDI
- Visualización del estado de conversión

### 4. Generación de Música
- Generación de nuevas composiciones basadas en MIDI
- Parámetros configurables del modelo de IA
- Múltiples variaciones por generación

### 5. Panel de Administración
- Gestión completa de usuarios y contenido
- Estadísticas de uso
- Monitoreo de tareas de procesamiento

## Configuración de Producción

### Variables de Entorno Adicionales

```
DEBUG=False
SECRET_KEY=clave_secreta_muy_segura
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DATABASE_URL=postgres://usuario:password@host:puerto/database
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Servidor Web

Se recomienda usar Gunicorn con Nginx:

```bash
gunicorn souniq_web.wsgi:application --bind 0.0.0.0:8000
```

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/NuevaFuncionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/NuevaFuncionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte técnico o preguntas:
- Email: soporte@souniq.com
- Issues: Crear un issue en GitHub

## Roadmap

- [ ] Soporte para más formatos de audio
- [ ] API REST para integraciones
- [ ] Aplicación móvil
- [ ] Colaboración en tiempo real
- [ ] Integración con DAWs populares
- [ ] Sistema de suscripciones premium

---

Desarrollado con ❤️ para la comunidad musical
