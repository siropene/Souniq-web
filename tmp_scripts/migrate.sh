#!/bin/bash
"""
Script de shell para ejecutar migraciones
Ejecutar en PythonAnywhere bash console:
cd ~/Souniq-web && source ~/.virtualenvs/souniq-env-new/bin/activate && bash tmp_scripts/migrate.sh
"""

echo "🔄 MIGRACIONES DE ORPHEUS"
echo "=========================="

echo "📍 Directorio actual: $(pwd)"
echo "🐍 Python: $(which python)"
echo "📦 Django: $(python -c 'import django; print(django.get_version())')"

echo ""
echo "📋 Estado actual de migraciones:"
python manage.py showmigrations music_processing

echo ""
echo "🚀 Aplicando migraciones..."
python manage.py migrate music_processing --verbosity=2

echo ""
echo "📋 Estado final:"
python manage.py showmigrations music_processing

echo ""
echo "🔍 Verificando estructura de tabla..."
python -c "
import os, sys, django
sys.path.insert(0, '/home/aherrasf/Souniq-web')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('DESCRIBE music_processing_generatedtrack;')
columns = cursor.fetchall()
print('Columnas en la tabla:')
for col in columns:
    print(f'  - {col[0]} ({col[1]})')

required = ['apply_sustains', 'remove_duplicate_pitches', 'remove_overlapping_durations', 'model_top_p', 'prime_instruments_json', 'add_drums', 'add_outro', 'num_prime_tokens']
existing = [col[0] for col in columns]
missing = [col for col in required if col not in existing]
if missing:
    print(f'❌ Faltan columnas: {missing}')
else:
    print('✅ Todas las columnas requeridas están presentes')
"

echo ""
echo "✅ Script de migración completado"
