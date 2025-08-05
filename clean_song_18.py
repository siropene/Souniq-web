#!/usr/bin/env python
"""
Script rápido para limpiar stems de la canción ID 18
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

def clean_song_18():
    """Limpiar stems de la canción ID 18"""
    print("=== LIMPIEZA CANCIÓN ID 18 ===")
    
    try:
        song = Song.objects.get(id=18)
        stems = Stem.objects.filter(song=song)
        
        print(f"🎵 Canción: {song.title}")
        print(f"📊 Stems encontrados: {stems.count()}")
        
        if stems.exists():
            for stem in stems:
                print(f"   - {stem.stem_type} (ID: {stem.id})")
            
            print(f"\n🧹 Eliminando {stems.count()} stems...")
            stems.delete()
            print("✅ Stems eliminados exitosamente")
        else:
            print("ℹ️ No hay stems para eliminar")
            
    except Song.DoesNotExist:
        print("❌ Canción ID 18 no encontrada")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_song_18()
