#!/bin/bash
"""
Script de limpieza de archivos temporales y medios para PythonAnywhere
Ejecutar en PythonAnywhere bash console:
cd ~/Souniq-web && source ~/.virtualenvs/souniq-env-new/bin/activate && bash tmp_scripts/cleanup_server.sh
"""

echo "🧹 SCRIPT DE LIMPIEZA SERVIDOR - SOUNIQ"
echo "======================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Debes ejecutar este script desde el directorio del proyecto (~/Souniq-web)"
    exit 1
fi

echo "📍 Directorio actual: $(pwd)"
echo "🗓️ Fecha: $(date)"

# Función para mostrar espacio antes y después
show_disk_usage() {
    echo "💾 Uso de disco actual:"
    du -h --max-depth=1 ~ | sort -hr | head -5
}

echo ""
echo "📊 Estado inicial del disco:"
show_disk_usage

echo ""
echo "🚀 Iniciando limpieza..."

# 1. Limpiar archivos de medios generados
echo ""
echo "1️⃣ Limpiando archivos de medios generados..."

# Stems generados
if [ -d "media/stems/" ]; then
    OLD_STEMS=$(find media/stems/ -name "*.wav" -o -name "*.mp3" 2>/dev/null | wc -l)
    if [ $OLD_STEMS -gt 0 ]; then
        echo "   🗑️ Eliminando $OLD_STEMS stems..."
        find media/stems/ -name "*.wav" -o -name "*.mp3" -delete 2>/dev/null
    else
        echo "   ✅ No hay stems para eliminar"
    fi
fi

# Tracks generados
if [ -d "media/generated_tracks/" ]; then
    OLD_TRACKS=$(find media/generated_tracks/ -name "*.mid" -o -name "*.wav" -o -name "*.mp3" 2>/dev/null | wc -l)
    if [ $OLD_TRACKS -gt 0 ]; then
        echo "   🗑️ Eliminando $OLD_TRACKS tracks..."
        find media/generated_tracks/ -name "*.mid" -o -name "*.wav" -o -name "*.mp3" -delete 2>/dev/null
    else
        echo "   ✅ No hay tracks para eliminar"
    fi
fi

# Archivos MIDI
if [ -d "media/midi/" ]; then
    OLD_MIDI=$(find media/midi/ -name "*.mid" 2>/dev/null | wc -l)
    if [ $OLD_MIDI -gt 0 ]; then
        echo "   🗑️ Eliminando $OLD_MIDI archivos MIDI..."
        find media/midi/ -name "*.mid" -delete 2>/dev/null
    else
        echo "   ✅ No hay archivos MIDI para eliminar"
    fi
fi

# 2. Limpiar archivos subidos por usuarios
echo ""
echo "2️⃣ Limpiando archivos subidos por usuarios..."

if [ -d "media/songs/" ]; then
    OLD_SONGS=$(find media/songs/ -type f 2>/dev/null | wc -l)
    if [ $OLD_SONGS -gt 0 ]; then
        echo "   🗑️ Eliminando $OLD_SONGS canciones..."
        find media/songs/ -type f -delete 2>/dev/null
    else
        echo "   ✅ No hay canciones para eliminar"
    fi
fi

# 3. Limpiar archivos de cache
echo ""
echo "3️⃣ Limpiando archivos de cache..."

# Cache de pip
echo "   🧹 Limpiando cache de pip..."
pip cache purge >/dev/null 2>&1

# Archivos .pyc
PYC_COUNT=$(find . -name "*.pyc" 2>/dev/null | wc -l)
if [ $PYC_COUNT -gt 0 ]; then
    echo "   🗑️ Eliminando $PYC_COUNT archivos .pyc..."
    find . -name "*.pyc" -delete 2>/dev/null
else
    echo "   ✅ No hay archivos .pyc para eliminar"
fi

# Cache de virtualenv wheel
if [ -d ~/.local/share/virtualenv/wheel/ ]; then
    WHEEL_SIZE=$(du -sh ~/.local/share/virtualenv/wheel/ 2>/dev/null | cut -f1)
    echo "   🗑️ Limpiando cache de virtualenv wheel ($WHEEL_SIZE)..."
    rm -rf ~/.local/share/virtualenv/wheel/* 2>/dev/null
fi

# 4. Limpiar logs antiguos
echo ""
echo "4️⃣ Limpiando logs antiguos..."

if [ -d "logs/" ]; then
    # Truncar logs grandes (>10MB)
    for log_file in logs/*.log; do
        if [ -f "$log_file" ]; then
            LOG_SIZE=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo "0")
            if [ $LOG_SIZE -gt 10485760 ]; then  # 10MB
                echo "   ✂️ Truncando log grande: $(basename "$log_file") ($(du -sh "$log_file" | cut -f1))"
                echo "# Log truncado el $(date)" > "$log_file"
            fi
        fi
    done
fi

# 5. Limpiar archivos temporales del sistema
echo ""
echo "5️⃣ Limpiando archivos temporales del sistema..."

# Archivos temporales propios en /tmp
TEMP_COUNT=$(find /tmp -user $(whoami) -type f -mtime +1 2>/dev/null | wc -l)
if [ $TEMP_COUNT -gt 0 ]; then
    echo "   🗑️ Eliminando $TEMP_COUNT archivos temporales..."
    find /tmp -user $(whoami) -type f -mtime +1 -delete 2>/dev/null
else
    echo "   ✅ No hay archivos temporales para eliminar"
fi

# 6. Limpiar directorios vacíos
echo ""
echo "6️⃣ Limpiando directorios vacíos en media/..."
find media/ -type d -empty -delete 2>/dev/null && echo "   🗑️ Directorios vacíos eliminados" || echo "   ✅ No hay directorios vacíos"

echo ""
echo "✅ LIMPIEZA COMPLETADA"
echo "====================="

echo ""
echo "📊 Estado final del disco:"
show_disk_usage

echo ""
echo "💡 RECOMENDACIONES:"
echo "   - Ejecutar este script semanalmente: bash tmp_scripts/cleanup_server.sh"
echo "   - Monitorear el uso de disco regularmente"
echo "   - Considerar eliminar archivos manualmente si el espacio sigue siendo crítico"
echo ""
echo "🎯 Script completado exitosamente!"
