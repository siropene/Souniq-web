#!/bin/bash
"""
Script de limpieza automática rápida para PythonAnywhere (sin confirmaciones)
Usar con cuidado - elimina archivos automáticamente

Ejecutar:
cd ~/Souniq-web && source ~/.virtualenvs/souniq-env-new/bin/activate && bash tmp_scripts/cleanup_auto.sh
"""

echo "🚀 LIMPIEZA AUTOMÁTICA RÁPIDA - SOUNIQ"
echo "====================================="

# Verificar directorio
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Ejecutar desde ~/Souniq-web"
    exit 1
fi

echo "⏰ $(date)"
echo "📍 $(pwd)"

# Mostrar espacio inicial
echo "💾 Espacio inicial:"
du -h ~ | tail -1

echo ""
echo "🧹 Limpiando automáticamente..."

# Contadores
TOTAL_FILES=0
TOTAL_SIZE_BEFORE=$(du -s ~ | cut -f1)

# 1. Stems > 3 días
if [ -d "media/stems/" ]; then
    STEMS_COUNT=$(find media/stems/ -name "*.wav" -o -name "*.mp3" -mtime +3 2>/dev/null | wc -l)
    if [ $STEMS_COUNT -gt 0 ]; then
        echo "🗑️ Eliminando $STEMS_COUNT stems (>3 días)..."
        find media/stems/ -name "*.wav" -o -name "*.mp3" -mtime +3 -delete 2>/dev/null
        TOTAL_FILES=$((TOTAL_FILES + STEMS_COUNT))
    fi
fi

# 2. Generated tracks > 3 días
if [ -d "media/generated_tracks/" ]; then
    TRACKS_COUNT=$(find media/generated_tracks/ -type f -mtime +3 2>/dev/null | wc -l)
    if [ $TRACKS_COUNT -gt 0 ]; then
        echo "🗑️ Eliminando $TRACKS_COUNT tracks generados (>3 días)..."
        find media/generated_tracks/ -type f -mtime +3 -delete 2>/dev/null
        TOTAL_FILES=$((TOTAL_FILES + TRACKS_COUNT))
    fi
fi

# 3. MIDI > 5 días
if [ -d "media/midi/" ]; then
    MIDI_COUNT=$(find media/midi/ -name "*.mid" -mtime +5 2>/dev/null | wc -l)
    if [ $MIDI_COUNT -gt 0 ]; then
        echo "🗑️ Eliminando $MIDI_COUNT archivos MIDI (>5 días)..."
        find media/midi/ -name "*.mid" -mtime +5 -delete 2>/dev/null
        TOTAL_FILES=$((TOTAL_FILES + MIDI_COUNT))
    fi
fi

# 4. Canciones > 10 días
if [ -d "media/songs/" ]; then
    SONGS_COUNT=$(find media/songs/ -type f -mtime +10 2>/dev/null | wc -l)
    if [ $SONGS_COUNT -gt 0 ]; then
        echo "🗑️ Eliminando $SONGS_COUNT canciones (>10 días)..."
        find media/songs/ -type f -mtime +10 -delete 2>/dev/null
        TOTAL_FILES=$((TOTAL_FILES + SONGS_COUNT))
    fi
fi

# 5. Cache y archivos temporales
echo "🧹 Limpiando cache..."
pip cache purge >/dev/null 2>&1

PYC_COUNT=$(find . -name "*.pyc" 2>/dev/null | wc -l)
if [ $PYC_COUNT -gt 0 ]; then
    echo "🗑️ Eliminando $PYC_COUNT archivos .pyc..."
    find . -name "*.pyc" -delete 2>/dev/null
    TOTAL_FILES=$((TOTAL_FILES + PYC_COUNT))
fi

# 6. Logs grandes
if [ -d "logs/" ]; then
    for log_file in logs/*.log; do
        if [ -f "$log_file" ]; then
            # Verificar si el log es > 5MB (usando stat)
            LOG_SIZE=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo "0")
            if [ $LOG_SIZE -gt 5242880 ]; then  # 5MB
                echo "✂️ Truncando log: $(basename "$log_file")"
                echo "# Log truncado automáticamente el $(date)" > "$log_file"
            fi
        fi
    done
fi

# 7. Archivos temporales del usuario
TEMP_COUNT=$(find /tmp -user $(whoami) -type f -mtime +0 2>/dev/null | wc -l)
if [ $TEMP_COUNT -gt 0 ]; then
    echo "🗑️ Eliminando $TEMP_COUNT archivos temporales..."
    find /tmp -user $(whoami) -type f -mtime +0 -delete 2>/dev/null
    TOTAL_FILES=$((TOTAL_FILES + TEMP_COUNT))
fi

# 8. Directorios vacíos
find media/ -type d -empty -delete 2>/dev/null

# Calcular espacio liberado
TOTAL_SIZE_AFTER=$(du -s ~ | cut -f1)
SPACE_FREED=$((TOTAL_SIZE_BEFORE - TOTAL_SIZE_AFTER))

echo ""
echo "✅ LIMPIEZA COMPLETADA"
echo "====================="
echo "📊 Archivos eliminados: $TOTAL_FILES"
echo "💾 Espacio liberado: $((SPACE_FREED / 1024)) MB"

echo ""
echo "💾 Espacio final:"
du -h ~ | tail -1

echo ""
echo "⏰ Completado a las $(date '+%H:%M:%S')"

# Log de la operación
echo "$(date): Limpieza automática - $TOTAL_FILES archivos, $((SPACE_FREED / 1024))MB liberados" >> logs/cleanup.log 2>/dev/null || true

echo "✨ ¡Listo!"
