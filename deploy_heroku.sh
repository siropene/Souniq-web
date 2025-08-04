#!/bin/bash
# Script de deployment para Heroku

echo "🔵 Preparando proyecto para Heroku..."

# 1. Verificar Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI no está instalado"
    echo "📥 Instalar con: brew tap heroku/brew && brew install heroku"
    exit 1
fi

echo "✅ Heroku CLI encontrado"

# 2. Login a Heroku
echo "🔐 Verificando login a Heroku..."
heroku auth:whoami || {
    echo "❌ No estás logueado en Heroku"
    echo "🔐 Ejecuta: heroku login"
    exit 1
}

echo "✅ Login a Heroku OK"

# 3. Verificar archivos necesarios
echo "✅ Verificando archivos de configuración..."

required_files=("Procfile" "requirements.txt" "runtime.txt" "souniq_web/settings_heroku.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Falta $file"
        exit 1
    fi
done

echo "✅ Archivos de configuración OK"

# 4. Crear aplicación Heroku
echo "🚀 Configurando aplicación Heroku..."

# Generar nombre único
app_name="souniq-web-$(date +%s)"
echo "📝 Nombre de la app: $app_name"

# Crear app
heroku create $app_name
heroku git:remote -a $app_name

echo "✅ Aplicación Heroku creada: $app_name"

# 5. Añadir add-ons
echo "🔧 Añadiendo add-ons..."

# PostgreSQL
heroku addons:create heroku-postgresql:mini -a $app_name
echo "✅ PostgreSQL añadido"

# Redis
heroku addons:create heroku-redis:mini -a $app_name
echo "✅ Redis añadido"

# 6. Configurar variables de entorno
echo "🔐 Configurando variables de entorno..."

# Generar SECRET_KEY
secret_key=$(python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
print(''.join(secrets.choice(alphabet) for i in range(50)))
")

heroku config:set DJANGO_SETTINGS_MODULE=souniq_web.settings_heroku -a $app_name
heroku config:set SECRET_KEY="$secret_key" -a $app_name
heroku config:set DEBUG=False -a $app_name

echo "✅ Variables de entorno configuradas"

# 7. Preparar Git
echo "📝 Preparando repositorio Git..."

if [ ! -d ".git" ]; then
    git init
    echo "✅ Repositorio Git inicializado"
fi

git add .
git commit -m "Deploy to Heroku" 2>/dev/null || echo "⚠️  No hay cambios que commitear"

# 8. Deploy
echo "🚀 Desplegando a Heroku..."

git push heroku main || git push heroku master

# 9. Ejecutar migraciones
echo "🗄️  Ejecutando migraciones..."

heroku run python manage.py migrate -a $app_name
heroku run python manage.py collectstatic --noinput -a $app_name

# 10. Escalar procesos
echo "⚙️  Escalando procesos..."

heroku ps:scale web=1 worker=1 -a $app_name

echo "🎉 ¡Deployment completado!"
echo ""
echo "📋 INFORMACIÓN DE LA APLICACIÓN:"
echo "🌐 URL: https://$app_name.herokuapp.com"
echo "📊 Dashboard: https://dashboard.heroku.com/apps/$app_name"
echo ""
echo "📝 PRÓXIMOS PASOS:"
echo "1. Crear superusuario: heroku run python manage.py createsuperuser -a $app_name"
echo "2. Verificar logs: heroku logs --tail -a $app_name"
echo "3. Abrir app: heroku open -a $app_name"
