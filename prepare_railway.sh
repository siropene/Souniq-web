#!/bin/bash
# Script de deployment para Railway

echo "🚀 Preparando proyecto para Railway..."

# 1. Verificar archivos necesarios
echo "✅ Verificando archivos de configuración..."

if [ ! -f "Procfile" ]; then
    echo "❌ Falta Procfile"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ Falta requirements.txt"
    exit 1
fi

if [ ! -f "runtime.txt" ]; then
    echo "❌ Falta runtime.txt"
    exit 1
fi

echo "✅ Archivos de configuración OK"

# 2. Verificar configuraciones Django
echo "✅ Verificando configuración Django..."

if [ ! -f "souniq_web/settings_railway.py" ]; then
    echo "❌ Falta settings_railway.py"
    exit 1
fi

# 3. Generar SECRET_KEY si no existe
if [ ! -f ".env.railway" ]; then
    echo "🔐 Generando SECRET_KEY..."
    python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
secret_key = ''.join(secrets.choice(alphabet) for i in range(50))
with open('.env.railway', 'w') as f:
    f.write(f'SECRET_KEY={secret_key}\n')
    f.write('DEBUG=False\n')
    f.write('DJANGO_SETTINGS_MODULE=souniq_web.settings_railway\n')
print('✅ SECRET_KEY generada en .env.railway')
"
fi

# 4. Test local
echo "🧪 Probando configuración local..."
source .venv/bin/activate 2>/dev/null || echo "⚠️  No se encontró entorno virtual"

export DJANGO_SETTINGS_MODULE=souniq_web.settings_railway
export DEBUG=True
export DATABASE_URL=sqlite:///db.sqlite3

python manage.py check --settings=souniq_web.settings_railway
if [ $? -ne 0 ]; then
    echo "❌ Error en configuración Django"
    exit 1
fi

echo "✅ Configuración Django OK"

# 5. Preparar Git
echo "📝 Preparando repositorio Git..."

if [ ! -d ".git" ]; then
    git init
    echo "✅ Repositorio Git inicializado"
fi

# Añadir archivos
git add .
git status

echo "🎉 ¡Proyecto listo para Railway!"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. Hacer commit: git commit -m 'Deploy to Railway'"
echo "2. Subir a GitHub: git remote add origin <tu-repo-url> && git push -u origin main"
echo "3. Ir a https://railway.app y conectar tu repositorio"
echo "4. Añadir servicios: PostgreSQL + Redis"
echo "5. Configurar variables de entorno desde .env.railway"
echo ""
echo "📖 Consulta DEPLOYMENT_GUIDE_COMPLETE.md para más detalles"
