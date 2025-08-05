#!/usr/bin/env python
"""
Script para limpiar stems duplicados en PythonAnywhere
Ejecutar si hay problemas de duplicados en la base de datos
"""
import os
import sys

# Configurar Django
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')

import django
django.setup()

from music_processing.models import Song, Stem

def clean_duplicate_stems():
    """Limpiar stems duplicados"""
    print("=== LIMPIEZA DE STEMS DUPLICADOS ===")
    
    # Buscar canciones con stems
    songs_with_stems = Song.objects.filter(stem__isnull=False).distinct()
    
    for song in songs_with_stems:
        stems = Stem.objects.filter(song=song)
        print(f"\n🎵 Canción ID {song.id}: {stems.count()} stems")
        
        if stems.count() > 7:  # Más de los 7 stems esperados
            print(f"⚠️ Demasiados stems ({stems.count()}), eliminando todos...")
            stems.delete()
            print("✅ Stems eliminados")
        else:
            # Verificar duplicados por tipo
            stem_types = {}
            for stem in stems:
                if stem.stem_type in stem_types:
                    print(f"🔄 Duplicado encontrado: {stem.stem_type}")
                    stem.delete()
                    print(f"   ✅ Stem duplicado eliminado: ID {stem.id}")
                else:
                    stem_types[stem.stem_type] = stem
    
    print("\n✅ Limpieza completada")

if __name__ == "__main__":
    clean_duplicate_stems()
