#!/bin/bash
# Script para probar la versión síncrona localmente

echo "🧪 PRUEBA LOCAL - VERSIÓN SÍNCRONA (Sin Celery)"
echo "================================================"

# 1. Activar entorno virtual
if [ -d ".venv" ]; then
    echo "✅ Activando entorno virtual..."
    source .venv/bin/activate
else
    echo "❌ No se encontró entorno virtual .venv"
    echo "💡 Crear con: python -m venv .venv"
    exit 1
fi

# 2. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# 3. Crear directorio de logs
mkdir -p logs

# 4. Configurar variable de entorno
export DJANGO_SETTINGS_MODULE=souniq_web.settings_pythonanywhere
export DEBUG=True

# 5. Verificar configuración
echo "🔍 Verificando configuración..."
python manage.py check --settings=souniq_web.settings_pythonanywhere
if [ $? -ne 0 ]; then
    echo "❌ Error en configuración Django"
    exit 1
fi

# 6. Ejecutar migraciones
echo "🗄️  Ejecutando migraciones..."
python manage.py migrate --settings=souniq_web.settings_pythonanywhere

# 7. Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --settings=souniq_web.settings_pythonanywhere

# 8. Crear superusuario (opcional)
echo "👤 ¿Quieres crear un superusuario? (s/n)"
read -r response
if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
    python manage.py createsuperuser --settings=souniq_web.settings_pythonanywhere
fi

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "🚀 INICIAR SERVIDOR:"
echo "python manage.py runserver --settings=souniq_web.settings_pythonanywhere"
echo ""
echo "🌐 ACCEDER A:"
echo "http://localhost:8000"
echo ""
echo "⚠️  NOTA: Esta versión procesa todo de forma síncrona"
echo "   - Las operaciones pueden tardar más tiempo"
echo "   - El navegador se bloqueará durante el procesamiento"
echo "   - Ideal para pruebas y PythonAnywhere gratuito"
