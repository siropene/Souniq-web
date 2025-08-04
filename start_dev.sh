#!/bin/bash

# Script de inicio para desarrollo de SouniQ
# Este script inicia todos los servicios necesarios

echo "🎵 Iniciando SouniQ - Plataforma de Procesamiento Musical con IA"
echo "=================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py. Asegúrate de estar en el directorio del proyecto."
    exit 1
fi

# Verificar que el entorno virtual está activado
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Activando entorno virtual..."
    source .venv/bin/activate
fi

# Verificar que Redis está corriendo
echo "🔍 Verificando Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis no está corriendo. Por favor, inicia Redis:"
    echo "   redis-server"
    exit 1
fi

echo "✅ Redis está corriendo"

# Aplicar migraciones pendientes
echo "🔄 Aplicando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $CELERY_PID 2>/dev/null
    kill $DJANGO_PID 2>/dev/null
    echo "👋 ¡Hasta luego!"
    exit 0
}

# Configurar trap para limpieza
trap cleanup SIGINT SIGTERM

# Iniciar Celery Worker en background
echo "🔧 Iniciando Celery Worker..."
celery -A souniq_web worker --loglevel=info &
CELERY_PID=$!

# Esperar un momento para que Celery se inicie
sleep 3

# Iniciar servidor Django
echo "🚀 Iniciando servidor Django..."
echo ""
echo "📱 Aplicación disponible en: http://127.0.0.1:8000"
echo "⚙️  Panel de administración: http://127.0.0.1:8000/admin"
echo ""
echo "💡 Presiona Ctrl+C para detener todos los servicios"
echo ""

python manage.py runserver &
DJANGO_PID=$!

# Esperar a que ambos procesos terminen
wait $CELERY_PID $DJANGO_PID
