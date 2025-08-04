# GUÍA COMPLETA DE DEPLOYMENT

## 🚀 RAILWAY (RECOMENDADO) - $5/mes

### 1. PREPARACIÓN
```bash
# 1. Crear repositorio Git
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tu-usuario/souniq-web.git
git push -u origin main
```

### 2. DEPLOYMENT EN RAILWAY
1. **Ir a https://railway.app**
2. **Conectar con GitHub**
3. **"New Project" → "Deploy from GitHub repo"**
4. **Seleccionar tu repositorio**

### 3. CONFIGURACIÓN AUTOMÁTICA
Railway detectará automáticamente:
- ✅ Procfile
- ✅ requirements.txt
- ✅ runtime.txt

### 4. AÑADIR SERVICIOS
**En el dashboard de Railway:**
- **Add PostgreSQL**: Base de datos
- **Add Redis**: Para Celery
- **Add Worker Service**: Para procesos Celery

### 5. VARIABLES DE ENTORNO
```env
DJANGO_SETTINGS_MODULE=souniq_web.settings_railway
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
DEBUG=False
```

### 6. CONFIGURAR SERVICIOS
**Web Service (Django):**
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn souniq_web.wsgi`

**Worker Service (Celery):**
- Build Command: `pip install -r requirements.txt`
- Start Command: `celery -A souniq_web worker --loglevel=info`

**Beat Service (Celery Scheduler):**
- Build Command: `pip install -r requirements.txt`
- Start Command: `celery -A souniq_web beat --loglevel=info`

### 7. MIGRACIONES
```bash
# Railway ejecutará automáticamente:
python manage.py collectstatic --noinput
python manage.py migrate
```

---

## 🔵 HEROKU - $7/mes (Hobby)

### 1. INSTALACIÓN HEROKU CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Login
heroku login
```

### 2. CREAR APLICACIÓN
```bash
heroku create souniq-web-app
heroku git:remote -a souniq-web-app
```

### 3. AÑADIR ADD-ONS
```bash
# PostgreSQL
heroku addons:create heroku-postgresql:mini

# Redis
heroku addons:create heroku-redis:mini
```

### 4. CONFIGURAR VARIABLES
```bash
heroku config:set DJANGO_SETTINGS_MODULE=souniq_web.settings_railway
heroku config:set SECRET_KEY=tu_clave_secreta
heroku config:set DEBUG=False
```

### 5. CONFIGURAR PROCESOS
```bash
# El Procfile ya está configurado
# Heroku escalará automáticamente los procesos
heroku ps:scale web=1 worker=1
```

### 6. DEPLOY
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py collectstatic --noinput
heroku run python manage.py createsuperuser
```

---

## 📊 COMPARACIÓN

| Característica | Railway | Heroku | PythonAnywhere |
|----------------|---------|--------|----------------|
| **Precio** | $5/mes | $7/mes | $5/mes |
| **Celery** | ✅ Nativo | ✅ Nativo | ❌ Solo pago |
| **Redis** | ✅ Gratis | ✅ $15/mes | ❌ Limitado |
| **Deploy** | 🟢 Automático | 🟡 CLI | 🔴 Manual |
| **PostgreSQL** | ✅ Incluido | ✅ Incluido | ❌ Solo MySQL |
| **Dominio** | ✅ Gratis | ✅ Gratis | ❌ Solo pago |
| **Facilidad** | 🟢 Muy fácil | 🟡 Medio | 🔴 Complejo |

---

## 🏆 RECOMENDACIÓN FINAL

### Para tu proyecto SOUNIQ:
1. **Railway** - Mejor relación precio/facilidad
2. **Heroku** - Si ya tienes experiencia
3. **PythonAnywhere** - Solo para prototipos

### Flujo recomendado:
1. **Subir código a GitHub**
2. **Conectar con Railway**
3. **Configurar servicios automáticamente**
4. **¡Listo en 10 minutos!**

¿Quieres que procedamos con Railway o prefieres Heroku?
