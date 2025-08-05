#!/bin/bash
# Script de comandos útiles para PythonAnywhere
# Ejecutar en la consola de PythonAnywhere

echo "=== COMANDOS ÚTILES PARA SOUNIQ EN PYTHONANYWHERE ==="

echo ""
echo "📂 VERIFICAR ARCHIVOS:"
echo "ls -la ~/Souniq-web/media/songs/"
echo "ls -la ~/Souniq-web/media/stems/"
echo "ls -la ~/Souniq-web/media/midi/"
echo "ls -la ~/Souniq-web/media/generated_tracks/"

echo ""
echo "🔍 VERIFICAR LOGS:"
echo "tail -f ~/Souniq-web/logs/django.log"
echo "tail -20 ~/Souniq-web/logs/django.log | grep ERROR"
echo "tail -20 ~/Souniq-web/logs/django.log | grep '🚀'"

echo ""
echo "📊 COMANDOS DJANGO:"
echo "cd ~/Souniq-web && python manage.py shell"
echo "cd ~/Souniq-web && python manage.py showmigrations"
echo "cd ~/Souniq-web && python manage.py collectstatic --noinput"

echo ""
echo "🧪 SCRIPTS DE DIAGNÓSTICO:"
echo "cd ~/Souniq-web && python diagnose_midi_quality.py"
echo "cd ~/Souniq-web && python test_giant_music_api.py"

echo ""
echo "🔄 REINICIAR APLICACIÓN:"
echo "touch /var/www/aherrasf_pythonanywhere_com_wsgi.py"

echo ""
echo "💾 VERIFICAR BASE DE DATOS:"
echo "# En shell de Django:"
echo "from music_processing.models import Song, Stem, MidiFile, GeneratedTrack"
echo "Song.objects.count()"
echo "Stem.objects.count()"
echo "MidiFile.objects.filter(status='completed').count()"

echo ""
echo "📦 VERIFICAR PAQUETES:"
echo "pip list | grep gradio"
echo "pip list | grep django"

echo ""
echo "🌐 VERIFICAR APIS:"
echo "# En shell de Django:"
echo "from gradio_client import Client"
echo "client = Client('SouniQ/Modulo1')"
echo "client = Client('SouniQ/Modulo2')"
echo "client = Client('asigalov61/Giant-Music-Transformer')"

echo ""
echo "🧹 LIMPIAR ARCHIVOS TEMPORALES:"
echo "find ~/Souniq-web/media -name '*.tmp' -delete"
echo "find /tmp -name '*mid*' -user aherrasf -delete"

echo ""
echo "📈 VERIFICAR ESTADO:"
echo "# Última canción procesada:"
echo "# Song.objects.latest('id')"
echo "# Últimos MIDIs generados:"
echo "# MidiFile.objects.filter(status='completed').order_by('-id')[:5]"

echo ""
echo "🚨 DEBUG ESPECÍFICO:"
echo "# Para probar función específica en shell:"
echo "from music_processing.tasks_sync import process_song_to_stems_sync, convert_stem_to_midi_sync, generate_new_track_sync"
echo "# result = process_song_to_stems_sync(SONG_ID)"
echo "# result = convert_stem_to_midi_sync(STEM_ID)"
echo "# result = generate_new_track_sync(TRACK_ID)"

echo ""
echo "Ejecuta los comandos según tu necesidad específica 🎵"
