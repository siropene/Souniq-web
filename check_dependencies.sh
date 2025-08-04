#!/bin/bash

# Script para verificar dependencias en PythonAnywhere

echo "=== VERIFICACIÓN DEL ENTORNO VIRTUAL ==="
echo "Entorno virtual activo: $VIRTUAL_ENV"
echo "Versión de Python: $(python --version)"
echo "Ubicación de Python: $(which python)"
echo ""

echo "=== VERIFICACIÓN DE DEPENDENCIAS ==="
echo "Verificando Django..."
python -c "import django; print(f'Django {django.get_version()}')" 2>/dev/null || echo "❌ Django no encontrado"

echo "Verificando gradio-client..."
python -c "import gradio_client; print(f'✓ gradio-client disponible')" 2>/dev/null || echo "❌ gradio-client no encontrado"

echo "Verificando mysqlclient..."
python -c "import MySQLdb; print('✓ MySQLdb disponible')" 2>/dev/null || echo "❌ MySQLdb no encontrado"

echo "Verificando numpy..."
python -c "import numpy; print(f'✓ numpy {numpy.__version__}')" 2>/dev/null || echo "❌ numpy no encontrado"

echo "Verificando Pillow..."
python -c "from PIL import Image; print('✓ Pillow disponible')" 2>/dev/null || echo "❌ Pillow no encontrado"

echo ""
echo "=== VERIFICACIÓN DE CONFIGURACIÓN DJANGO ==="
cd ~/Souniq-web
echo "Verificando configuración..."
python manage.py check --settings=souniq_web.settings_pythonanywhere --verbosity=0 2>/dev/null && echo "✓ Configuración Django OK" || echo "❌ Error en configuración Django"
