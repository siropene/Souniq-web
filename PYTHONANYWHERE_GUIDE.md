# 🐍 GUÍA PARA PYTHONANYWHERE (VERSIÓN GRATUITA - SIN CELERY)

## ✨ CARACTERÍSTICAS DE ESTA VERSIÓN:
- ✅ **Gratuita** en PythonAnywhere
- ✅ **Sin Celery** - Todo procesamiento síncrono
- ✅ **Todas las funcionalidades** funcionan
- ⚠️  **Más lenta** - El usuario debe esperar
- ⚠️  **Bloquea navegador** durante procesamiento

---

## 🚀 PASOS PARA PYTHONANYWHERE:

### 1. CREAR CUENTA
- Regístrate en https://www.pythonanywhere.com (gratuita)

### 2. SUBIR CÓDIGO
```bash
# Opción A: Git (recomendado)
git clone https://github.com/tu-usuario/souniq-web.git
cd souniq-web

# Opción B: Usar Files manager de PythonAnywhere
```

### 3. CONFIGURAR ENTORNO VIRTUAL
```bash
# En la consola Bash de PythonAnywhere
mkvirtualenv --python=/usr/bin/python3.11 souniq-env
workon souniq-env
pip install -r requirements.txt
```

### 4. CONFIGURAR BASE DE DATOS
- Ve a "Databases" en el dashboard
- Crea base de datos MySQL: `tuusername$souniq_db`
- Anota la contraseña

### 5. CONFIGURAR APLICACIÓN WEB
- Ve a "Web" en el dashboard
- "Add a new web app" → "Manual configuration" → Python 3.11
- **Source code:** `/home/tuusername/souniq-web`
- **WSGI file:** Editar y pegar:

```python
import os
import sys

# Añadir path del proyecto
path = '/home/tuusername/souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere')

# Variables de entorno
os.environ['DB_PASSWORD'] = 'tu_password_mysql_aqui'
os.environ['DEBUG'] = 'False'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 6. CONFIGURAR ARCHIVOS ESTÁTICOS
**En "Static files":**
- URL: `/static/` → Directory: `/home/tuusername/souniq-web/staticfiles/`
- URL: `/media/` → Directory: `/home/tuusername/souniq-web/media/`

### 7. EJECUTAR MIGRACIONES
```bash
workon souniq-env
cd /home/tuusername/souniq-web

# Editar settings_pythonanywhere.py para cambiar 'tuusername' por tu usuario real
python manage.py migrate --settings=souniq_web.settings_pythonanywhere
python manage.py collectstatic --noinput --settings=souniq_web.settings_pythonanywhere
python manage.py createsuperuser --settings=souniq_web.settings_pythonanywhere
```

### 8. RECARGAR APLICACIÓN
- Haz clic en "Reload" en la pestaña Web

---

## 🧪 PRUEBA LOCAL PRIMERO:

```bash
# 1. Ejecutar script de prueba
./test_sync_local.sh

# 2. Iniciar servidor local
python manage.py runserver --settings=souniq_web.settings_pythonanywhere

# 3. Acceder a http://localhost:8000
```

---

## ⚠️  EXPERIENCIA DE USUARIO (VERSIÓN SÍNCRONA):

### **Subida y procesamiento de stems:**
- Usuario sube archivo
- Hace clic en "Generar Stems"
- **Navegador se bloquea 2-5 minutos**
- Página se recarga con stems generados

### **Conversión a MIDI:**
- Usuario selecciona stem
- Hace clic en "Convertir a MIDI"
- **Navegador se bloquea 1-3 minutos**
- Página se recarga con MIDI disponible

### **Generación de tracks:**
- Usuario configura parámetros
- Hace clic en "Generar Track"
- **Navegador se bloquea 3-7 minutos**
- Página se recarga con track generado

---

## 💡 MEJORAS PARA LA EXPERIENCIA:

### 1. **Añadir indicadores de carga:**
```javascript
// En el template, mostrar loading durante submit
$('form').on('submit', function() {
    $('button[type="submit"]').prop('disabled', true).text('Procesando...');
    $('#loading-spinner').show();
});
```

### 2. **Dividir en pasos más pequeños:**
- Procesar stems de uno en uno
- Mostrar progreso parcial

### 3. **Informar mejor al usuario:**
- Mensajes claros sobre tiempo de espera
- Instrucciones de "no cerrar navegador"

---

## 🎯 RESULTADO FINAL:

✅ **Funcionalidad:** 100% operativa
✅ **Costo:** $0 (gratuito)
⚠️  **Velocidad:** Más lenta pero funcional
⚠️  **UX:** Requiere paciencia del usuario

---

## 🚀 SIGUIENTE PASO:

**¿Quieres probar localmente primero?**
```bash
./test_sync_local.sh
```

**¿O prefieres ir directo a PythonAnywhere?**
- Sigue los pasos 1-8 de arriba
