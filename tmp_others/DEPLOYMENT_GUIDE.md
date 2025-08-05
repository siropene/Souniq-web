# GUÍA DE DEPLOYMENT EN PYTHONANYWHERE

## 1. CREAR CUENTA
- Regístrate en https://www.pythonanywhere.com
- Elige plan (Beginner gratuito es suficiente para empezar)

## 2. SUBIR CÓDIGO
```bash
# Opción A: Usar Git (recomendado)
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo

# Opción B: Subir archivos manualmente
# Usar el File Manager de PythonAnywhere
```

## 3. CONFIGURAR ENTORNO VIRTUAL
```bash
# En la consola de PythonAnywhere
mkvirtualenv --python=/usr/bin/python3.11 souniq-env
workon souniq-env
pip install -r requirements-production.txt
```

## 4. CONFIGURAR BASE DE DATOS
- Ve a "Databases" en el dashboard
- Crea una base de datos MySQL: `tuusername$souniq_db`
- Anota la contraseña generada

## 5. CONFIGURAR APLICACIÓN WEB
- Ve a "Web" en el dashboard
- Clic en "Add a new web app"
- Elige "Manual configuration" + Python 3.11
- Configura:
  * Source code: `/home/tuusername/souniq_web`
  * WSGI file: `/home/tuusername/souniq_web/wsgi_production.py`
  * Virtualenv: `/home/tuusername/.virtualenvs/souniq-env`

## 6. CONFIGURAR ARCHIVOS ESTÁTICOS
En la sección "Static files":
- URL: `/static/`
- Directory: `/home/tuusername/souniq_web/staticfiles/`
- URL: `/media/`
- Directory: `/home/tuusername/souniq_web/media/`

## 7. VARIABLES DE ENTORNO
En el archivo WSGI, añadir:
```python
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'souniq_web.settings_production'
os.environ['DB_PASSWORD'] = 'tu_password_mysql'
```

## 8. EJECUTAR MIGRACIONES
```bash
workon souniq-env
cd /home/tuusername/souniq_web
python manage.py migrate --settings=souniq_web.settings_production
python manage.py collectstatic --settings=souniq_web.settings_production
python manage.py createsuperuser --settings=souniq_web.settings_production
```

## 9. LIMITACIONES CUENTA GRATUITA
- **Celery**: No funciona en cuenta gratuita (necesita procesos en background)
- **Solución temporal**: Procesar archivos de forma síncrona o usar cuenta de pago
- **Redis**: Limitado, considera usar base de datos para cola de tareas

## 10. ALTERNATIVAS PARA CELERY EN CUENTA GRATUITA
- Usar django-rq con Redis limitado
- Procesar archivos de forma síncrona (más lento)
- Usar servicios externos como Hugging Face Spaces para procesamiento

## 11. RECARGAR APLICACIÓN
- Cada vez que hagas cambios, haz clic en "Reload" en la pestaña Web

## 12. LOGS Y DEBUGGING
- Error logs: `/var/log/tuusername.pythonanywhere.com.error.log`
- Server logs: `/var/log/tuusername.pythonanywhere.com.server.log`
