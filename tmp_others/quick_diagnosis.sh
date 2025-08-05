#!/bin/bash
# Script de diagnóstico rápido para retomar sesión
# Ejecutar: chmod +x quick_diagnosis.sh && ./quick_diagnosis.sh

echo "🔍 DIAGNÓSTICO RÁPIDO - SouniQ Web"
echo "=================================="

# Activar entorno
cd "/Users/albertoherrastifigueroa/Library/Mobile Documents/com~apple~CloudDocs/Documents/Master/TFM/WEB2"
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=souniq_web.settings_pythonanywhere
export DEBUG=True

echo ""
echo "1️⃣ Verificando estado de la canción de prueba..."
python manage.py shell -c "
from music_processing.models import Song
song = Song.objects.get(id=13)
print(f'✅ Canción: {song.title}')
print(f'📊 Estado: {song.status}')
print(f'🎼 Stems: {song.stems.count()}')
for stem in song.stems.all()[:3]:
    print(f'   - {stem.stem_type}: {stem.file.name}')
if song.stems.count() > 3:
    print(f'   ... y {song.stems.count() - 3} más')
"

echo ""
echo "2️⃣ Verificando APIs de Hugging Face..."
python manage.py shell -c "
from gradio_client import Client

print('🔗 Verificando SouniQ/Modulo2 (MIDI)...')
try:
    client = Client('SouniQ/Modulo2')
    print('✅ Conexión exitosa')
    api_info = str(client.view_api())
    if 'input_wav_path' in api_info:
        print('✅ Parámetro input_wav_path encontrado')
    elif 'input_audio' in api_info:
        print('⚠️  Parámetro input_audio encontrado (necesita corrección)')
    else:
        print('❌ Parámetros no identificados')
except Exception as e:
    print(f'❌ Error conectando: {e}')

print('')
print('🔗 Verificando Giant-Music-Transformer (Generación)...')
try:
    client = Client('Giant-Music-Transformer')
    print('✅ Conexión exitosa')
except Exception as e:
    print(f'❌ Error conectando: {e}')
"

echo ""
echo "3️⃣ Estado del servidor..."
if pgrep -f "manage.py runserver" > /dev/null; then
    echo "✅ Servidor Django corriendo"
    echo "🌐 URL: http://localhost:8001"
else
    echo "❌ Servidor Django no está corriendo"
    echo "▶️  Para iniciar: python manage.py runserver 0.0.0.0:8001"
fi

echo ""
echo "4️⃣ Archivos críticos..."
if [ -f "music_processing/tasks_sync.py" ]; then
    echo "✅ tasks_sync.py existe"
    line_count=$(wc -l < music_processing/tasks_sync.py)
    echo "📄 Líneas: $line_count"
else
    echo "❌ tasks_sync.py no encontrado"
fi

echo ""
echo "🎯 PRÓXIMOS PASOS:"
echo "1. Corregir convert_stem_to_midi_sync() con parámetros correctos"
echo "2. Corregir generate_new_track_sync() con parámetros correctos"
echo "3. Probar flujo completo: Canción → Stems → MIDI → Nueva canción"
echo ""
echo "📖 Leer SESSION_STATE.md para detalles completos"
