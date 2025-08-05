#!/usr/bin/env python
"""
Test específico para Giant-Music-Transformer API
Prueba diferentes archivos MIDI para identificar problemas
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

def test_giant_music_transformer():
    """Probar Giant-Music-Transformer con diferentes MIDIs"""
    print("=== TEST GIANT-MUSIC-TRANSFORMER ===")
    
    try:
        from gradio_client import Client
        from music_processing.models import MidiFile
        
        # Crear cliente
        print("🔗 Conectando con Giant-Music-Transformer...")
        client = Client("asigalov61/Giant-Music-Transformer")
        print("✅ Cliente conectado")
        
        # Buscar MIDIs para probar
        midi_files = MidiFile.objects.filter(status='completed', file__isnull=False)[:3]
        
        if not midi_files.exists():
            print("❌ No hay archivos MIDI para probar")
            return
            
        print(f"\n📁 Probando con {midi_files.count()} archivos MIDI:")
        
        for midi_file in midi_files:
            print(f"\n🎵 Probando MIDI ID {midi_file.id}:")
            print(f"   - Stem: {midi_file.stem.stem_type}")
            print(f"   - Archivo: {midi_file.file.name}")
            print(f"   - Tamaño: {midi_file.file.size} bytes")
            
            try:
                # Intentar usar el archivo MIDI
                result = client.predict(
                    midi_file.file.path,  # Ruta del archivo MIDI
                    "Continue",           # Modo
                    900,                  # Tokens
                    0.9,                  # Temperature
                    api_name="/predict"
                )
                
                print("   ✅ API respondió correctamente")
                print(f"   📝 Resultado: {type(result)}")
                
                if isinstance(result, (list, tuple)) and len(result) > 0:
                    print(f"   📊 Primer elemento: {type(result[0])}")
                    
            except Exception as e:
                print(f"   ❌ Error con este MIDI: {e}")
                
                # Detectar tipos específicos de error
                error_str = str(e).lower()
                if "upstream gradio app has raised an exception" in error_str:
                    print("   🔍 Error del servidor upstream - posible problema con el archivo MIDI")
                elif "connection" in error_str:
                    print("   🌐 Error de conexión")
                elif "timeout" in error_str:
                    print("   ⏱️ Timeout - archivo demasiado grande o complejo")
                else:
                    print(f"   🤔 Error desconocido: {type(e).__name__}")
                    
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

def test_simple_midi():
    """Crear y probar un MIDI simple"""
    print("\n=== CREANDO MIDI SIMPLE PARA PRUEBA ===")
    
    try:
        import tempfile
        from gradio_client import Client
        
        # Crear un MIDI muy simple
        midi_content = b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x60MTrk\x00\x00\x00\x1a\x00\x90@\x7f\x81`\x80@\x00\x00\x90D\x7f\x81`\x80D\x00\x00\x90G\x7f\x81`\x80G\x00\x00\xff/\x00'
        
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            f.write(midi_content)
            temp_midi = f.name
            
        print(f"📄 MIDI temporal creado: {temp_midi}")
        print(f"📊 Tamaño: {len(midi_content)} bytes")
        
        # Probar con Giant-Music-Transformer
        client = Client("asigalov61/Giant-Music-Transformer")
        
        result = client.predict(
            temp_midi,
            "Continue",
            100,  # Pocos tokens para prueba rápida
            0.8,
            api_name="/predict"
        )
        
        print("✅ MIDI simple funciona correctamente")
        print(f"📝 Resultado: {type(result)}")
        
        # Limpiar archivo temporal
        os.unlink(temp_midi)
        
    except Exception as e:
        print(f"❌ Error con MIDI simple: {e}")
        if temp_midi and os.path.exists(temp_midi):
            os.unlink(temp_midi)

if __name__ == "__main__":
    test_giant_music_transformer()
    test_simple_midi()
