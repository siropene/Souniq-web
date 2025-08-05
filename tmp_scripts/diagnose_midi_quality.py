#!/usr/bin/env python
"""
Script de diagnóstico para verificar archivos MIDI
Ejecutar para verificar la calidad de los MIDIs generados
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

def diagnose_midi_files():
    """Diagnosticar archivos MIDI en la base de datos"""
    print("=== DIAGNÓSTICO DE ARCHIVOS MIDI ===")
    
    try:
        from music_processing.models import MidiFile
        
        # Buscar archivos MIDI
        midi_files = MidiFile.objects.filter(status='completed').order_by('-id')[:5]
        
        if not midi_files.exists():
            print("❌ No hay archivos MIDI completados en la base de datos")
            return
        
        print(f"📁 Encontrados {midi_files.count()} archivos MIDI recientes:")
        
        for midi_file in midi_files:
            print(f"\n🎵 MIDI ID {midi_file.id}:")
            print(f"   - Stem: {midi_file.stem.stem_type}")
            print(f"   - Canción: {midi_file.stem.song.title}")
            print(f"   - Archivo: {midi_file.file.name}")
            
            if midi_file.file:
                try:
                    # Verificar tamaño del archivo
                    size = midi_file.file.size
                    print(f"   - Tamaño: {size} bytes")
                    
                    if size < 100:
                        print("   ⚠️ ADVERTENCIA: Archivo muy pequeño (< 100 bytes)")
                    elif size > 1000000:
                        print("   ⚠️ ADVERTENCIA: Archivo muy grande (> 1MB)")
                    else:
                        print("   ✅ Tamaño normal")
                    
                    # Intentar leer los primeros bytes para verificar formato MIDI
                    midi_file.file.seek(0)
                    header = midi_file.file.read(4)
                    if header == b'MThd':
                        print("   ✅ Header MIDI válido")
                    else:
                        print(f"   ❌ Header inválido: {header}")
                        
                except Exception as e:
                    print(f"   ❌ Error al verificar archivo: {e}")
            else:
                print("   ❌ Archivo no existe")
                
        # Recomendar qué MIDI probar
        print(f"\n💡 RECOMENDACIÓN:")
        best_midi = midi_files.filter(file__isnull=False).first()
        if best_midi:
            print(f"   Probar generación con MIDI ID {best_midi.id}")
            print(f"   Comando: Usar stem '{best_midi.stem.stem_type}' de la canción '{best_midi.stem.song.title}'")
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_midi_files()
