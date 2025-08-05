#!/usr/bin/env python
"""
Script de verificación completa del pipeline de Souniq
Verifica que todos los componentes estén funcionando correctamente
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

def check_pipeline_complete():
    """Verificar el pipeline completo de música"""
    print("=== VERIFICACIÓN COMPLETA DEL PIPELINE SOUNIQ ===")
    
    try:
        from music_processing.models import Song, Stem, MidiFile, GeneratedTrack, GeneratedVersion
        from gradio_client import Client
        import json
        
        print("\n1️⃣ VERIFICANDO BASE DE DATOS...")
        songs = Song.objects.count()
        stems = Stem.objects.count()
        midis = MidiFile.objects.count()
        tracks = GeneratedTrack.objects.count()
        versions = GeneratedVersion.objects.count()
        
        print(f"   📊 Canciones: {songs}")
        print(f"   🎵 Stems: {stems}")
        print(f"   🎼 MIDI files: {midis}")
        print(f"   🎹 Generated tracks: {tracks}")
        print(f"   📀 Generated versions: {versions}")
        
        if songs == 0:
            print("   ⚠️ No hay canciones en la base de datos")
        
        print("\n2️⃣ VERIFICANDO CONEXIONES API...")
        
        # Función patch para evitar JSONDecodeError
        def create_client_with_patch(repo_name):
            original_get_api_info = Client._get_api_info
            try:
                def patched_get_api_info(self):
                    try:
                        return original_get_api_info(self)
                    except json.JSONDecodeError:
                        return {'named_endpoints': {}, 'unnamed_endpoints': {}}
                
                Client._get_api_info = patched_get_api_info
                client = Client(repo_name)
                return client, True
            except Exception as e:
                return None, str(e)
            finally:
                Client._get_api_info = original_get_api_info
        
        # Probar APIs
        apis_to_test = [
            ("SouniQ/Modulo1", "Separación de stems"),
            ("SouniQ/Modulo2", "Conversión a MIDI"),
            ("asigalov61/Giant-Music-Transformer", "Generación musical")
        ]
        
        for repo, description in apis_to_test:
            print(f"   🔗 {description} ({repo}): ", end="")
            client, result = create_client_with_patch(repo)
            if client:
                print("✅ Conectado")
            else:
                print(f"❌ Error: {result}")
        
        print("\n3️⃣ VERIFICANDO ARCHIVOS RECIENTES...")
        
        # Verificar última canción
        latest_song = Song.objects.order_by('-id').first()
        if latest_song:
            print(f"   📁 Última canción: '{latest_song.title}' (ID: {latest_song.id})")
            print(f"   📊 Estado: {latest_song.status}")
            
            # Verificar stems de la última canción
            song_stems = latest_song.stems.all()
            print(f"   🎵 Stems: {song_stems.count()}")
            
            for stem in song_stems:
                has_file = "✅" if stem.file else "❌"
                has_midi = "✅" if hasattr(stem, 'midi_file') and stem.midi_file.file else "❌"
                print(f"      - {stem.stem_type}: Archivo {has_file}, MIDI {has_midi}")
        
        # Verificar último MIDI
        latest_midi = MidiFile.objects.filter(status='completed').order_by('-id').first()
        if latest_midi:
            print(f"   🎼 Último MIDI: {latest_midi.stem.stem_type} (ID: {latest_midi.id})")
            print(f"   📏 Tamaño: {latest_midi.file.size} bytes" if latest_midi.file else "   ❌ Sin archivo")
        
        # Verificar último track generado
        latest_track = GeneratedTrack.objects.order_by('-id').first()
        if latest_track:
            print(f"   🎹 Último track: '{latest_track.title}' (ID: {latest_track.id})")
            print(f"   📊 Estado: {latest_track.status}")
            versions = latest_track.versions.count()
            print(f"   📀 Versiones generadas: {versions}")
        
        print("\n4️⃣ VERIFICANDO INTEGRIDAD DE ARCHIVOS...")
        
        # Verificar archivos MIDI corruptos o pequeños
        problem_midis = MidiFile.objects.filter(status='completed', file__isnull=False)
        problems_found = 0
        
        for midi in problem_midis[:5]:  # Solo los últimos 5
            try:
                size = midi.file.size
                if size < 100:
                    print(f"   ⚠️ MIDI {midi.id} muy pequeño: {size} bytes")
                    problems_found += 1
                elif size > 1000000:
                    print(f"   ⚠️ MIDI {midi.id} muy grande: {size} bytes")
                    problems_found += 1
                
                # Verificar header
                midi.file.seek(0)
                header = midi.file.read(4)
                if header != b'MThd':
                    print(f"   ❌ MIDI {midi.id} header inválido: {header}")
                    problems_found += 1
                    
            except Exception as e:
                print(f"   ❌ Error verificando MIDI {midi.id}: {e}")
                problems_found += 1
        
        if problems_found == 0:
            print("   ✅ Todos los archivos MIDI parecen estar bien")
        else:
            print(f"   ⚠️ Se encontraron {problems_found} problemas")
        
        print("\n5️⃣ RECOMENDACIONES...")
        
        # Recomendaciones basadas en el estado
        if songs > 0 and stems == 0:
            print("   💡 Hay canciones pero no stems - ejecutar separación")
        elif stems > 0 and midis == 0:
            print("   💡 Hay stems pero no MIDIs - ejecutar conversión")
        elif midis > 0 and tracks == 0:
            print("   💡 Hay MIDIs pero no tracks - ejecutar generación")
        elif versions < tracks:
            print("   💡 Algunos tracks no tienen todas las versiones")
        else:
            print("   ✅ Pipeline parece estar completo")
        
        # Sugerir archivos para pruebas
        good_midi = MidiFile.objects.filter(status='completed', file__isnull=False).first()
        if good_midi:
            print(f"   🧪 Para pruebas, usar MIDI ID {good_midi.id} ({good_midi.stem.stem_type})")
        
        print("\n🎉 VERIFICACIÓN COMPLETA")
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_pipeline_complete()
