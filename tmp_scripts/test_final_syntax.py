#!/usr/bin/env python
"""
Script para probar con argumentos posicionales pero tipos correctos
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

def test_final_syntax():
    """Probar con argumentos posicionales pero tipos correctos"""
    print("=== PRUEBA FINAL: POSICIONAL + HANDLE_FILE + STRING ===")
    
    try:
        from gradio_client import Client, handle_file
        from music_processing.models import MidiFile
        import tempfile
        
        # Encontrar MIDI
        midi = MidiFile.objects.filter(status='completed', file__isnull=False).first()
        if not midi:
            print("❌ No hay MIDIs disponibles")
            return
        
        print(f"📁 MIDI: {midi.file.name}")
        print(f"📏 Tamaño: {midi.file.size} bytes")
        
        # Cliente
        original = Client._get_api_info
        Client._get_api_info = lambda self: {'named_endpoints': {}, 'unnamed_endpoints': {}}
        client = Client("asigalov61/Giant-Music-Transformer")
        Client._get_api_info = original
        print("✅ Cliente conectado")
        
        # Archivo temporal
        midi.file.seek(0)
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            f.write(midi.file.read())
            temp_path = f.name
        
        print("🧪 Probando con argumentos posicionales + handle_file + tipos correctos...")
        
        try:
            # Argumentos posicionales con tipos correctos
            result = client.predict(
                handle_file(temp_path),  # input_midi posicional con handle_file
                600,                     # num_prime_tokens
                600,                     # num_gen_tokens
                1024,                    # num_mem_tokens (valor conservador)
                "Auto",                  # gen_outro como STRING (no bool)
                False,                   # gen_drums
                0.9,                     # model_temperature
                0.96,                    # model_sampling_top_p
                api_name="/generate_callback_wrapper"
            )
            
            print("✅ ¡ÉXITO! La sintaxis final funciona")
            print(f"📊 Tipo de resultado: {type(result)}")
            if isinstance(result, (list, tuple)):
                print(f"📋 Elementos devueltos: {len(result)}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:200]}...")
            print("💡 Detalles:")
            print("   - Usamos argumentos posicionales ✓")
            print("   - Usamos handle_file() ✓") 
            print("   - gen_outro es string 'Auto' ✓")
            print("   - ¿Problema en API o valores específicos?")
        
        # Limpiar
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_final_syntax()
