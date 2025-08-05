#!/bin/bash
# Script para verificar y limpiar espacio en disco en PythonAnywhere

echo "=== VERIFICACIÓN DE ESPACIO EN DISCO ==="

echo ""
echo "📊 ESPACIO TOTAL DISPONIBLE:"
df -h /home/aherrasf

echo ""
echo "📁 DIRECTORIOS QUE MÁS ESPACIO OCUPAN:"
du -h --max-depth=1 /home/aherrasf | sort -hr | head -10

echo ""
echo "🗂️ ARCHIVOS GRANDES EN SOUNIQ-WEB:"
echo "--- Archivos de audio originales ---"
find ~/Souniq-web/media/songs -name "*.mp3" -o -name "*.wav" -o -name "*.flac" | head -5 | xargs -I {} ls -lh {}

echo ""
echo "--- Stems generados ---"
find ~/Souniq-web/media/stems -name "*.wav" | head -5 | xargs -I {} ls -lh {}

echo ""
echo "--- Archivos MIDI ---"
find ~/Souniq-web/media/midi -name "*.mid" | head -5 | xargs -I {} ls -lh {}

echo ""
echo "--- Archivos generados ---"
find ~/Souniq-web/media/generated_tracks -name "*" | head -5 | xargs -I {} ls -lh {}

echo ""
echo "🧹 ARCHIVOS TEMPORALES Y CACHE:"
echo "--- Archivos temporales ---"
find /tmp -user aherrasf -name "*" 2>/dev/null | wc -l
echo "--- Cache de Python ---"
find ~/Souniq-web -name "__pycache__" -type d | wc -l

echo ""
echo "💾 TAMAÑOS POR DIRECTORIO DE MEDIA:"
du -h ~/Souniq-web/media/songs/ 2>/dev/null || echo "No existe media/songs"
du -h ~/Souniq-web/media/stems/ 2>/dev/null || echo "No existe media/stems"
du -h ~/Souniq-web/media/midi/ 2>/dev/null || echo "No existe media/midi"
du -h ~/Souniq-web/media/generated_tracks/ 2>/dev/null || echo "No existe media/generated_tracks"

echo ""
echo "🚨 COMANDOS DE LIMPIEZA (EJECUTAR CON CUIDADO):"
echo ""
echo "# Limpiar archivos temporales"
echo "find /tmp -user aherrasf -name '*' -mtime +1 -delete"
echo ""
echo "# Limpiar cache de Python"
echo "find ~/Souniq-web -name '__pycache__' -exec rm -rf {} + 2>/dev/null"
echo ""
echo "# Limpiar logs antiguos (si existen)"
echo "find ~/Souniq-web/logs -name '*.log.*' -mtime +7 -delete 2>/dev/null"
echo ""
echo "# Limpiar archivos de test/desarrollo"
echo "rm -f ~/Souniq-web/*.tmp ~/Souniq-web/test_*.wav ~/Souniq-web/debug_*"
echo ""
echo "# SOLO SI ES NECESARIO: Borrar archivos de audio más antiguos"
echo "# find ~/Souniq-web/media/songs -name '*' -mtime +30 -delete"
echo "# find ~/Souniq-web/media/stems -name '*' -mtime +15 -delete"

echo ""
echo "💡 DESPUÉS DE LIMPIAR, REINICIAR EL SERVIDOR:"
echo "touch /var/www/aherrasf_pythonanywhere_com_wsgi.py"
