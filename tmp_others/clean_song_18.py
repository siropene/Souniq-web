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
    """Limpiar stems de la canción ID 18 y 21"""
    print("=== LIMPIEZA CANCIONES ID 18 y 21 ===")
    
    for song_id in [18, 21]:
        try:
            song = Song.objects.get(id=song_id)
            stems = Stem.objects.filter(song=song)
            
            print(f"\n🎵 Canción ID {song_id}: {song.title}")
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
            print(f"❌ Canción ID {song_id} no encontrada")
        except Exception as e:
            print(f"❌ Error con canción {song_id}: {e}")

if __name__ == "__main__":
    clean_song_18()
