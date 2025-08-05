#!/usr/bin/env python
"""
Script para probar con valores que funcionan en el espacio web
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

def test_working_values():
    """Probar con valores que seguramente funcionan"""
    print("=== PRUEBA CON VALORES QUE FUNCIONAN EN EL ESPACIO ===")
    
    try:
        from gradio_client import Client
        from music_processing.models import MidiFile
        import json
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
        
        print("🧪 Probando con valores conservadores...")
        
        try:
            # Valores muy conservadores (argumentos posicionales)
            result = client.predict(
                temp_path,    # input_midi
                128,          # num_prime_tokens
                100,          # num_gen_tokens  
                512,          # num_mem_tokens
                False,        # gen_outro
                False,        # gen_drums
                0.8,          # model_temperature
                0.9,          # model_sampling_top_p
                api_name="/generate_callback_wrapper"
            )
            
            print("✅ ¡ÉXITO! Los valores conservadores funcionan")
            print(f"📊 Tipo de resultado: {type(result)}")
            if isinstance(result, (list, tuple)):
                print(f"📋 Elementos devueltos: {len(result)}")
            
            # Ahora probar incrementalmente
            print("\n🔄 Probando con valores más altos...")
            result2 = client.predict(
                temp_path,    # input_midi
                500,          # num_prime_tokens (incrementar)
                200,          # num_gen_tokens (incrementar)
                1024,         # num_mem_tokens (tu valor original)
                False,        # gen_outro
                True,         # gen_drums (como tu código)
                0.9,          # model_temperature (tu valor)
                0.95,         # model_sampling_top_p (tu valor)
                api_name="/generate_callback_wrapper"
            )
            
            print("✅ ¡TAMBIÉN FUNCIONA! Valores más altos OK")
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg[:150]}...")
            
            if "upstream" in error_msg.lower():
                print("💡 Error upstream - posiblemente valores de parámetros problemáticos")
                print("🔧 Recomendación: Usar valores más conservadores en producción")
        
        # Limpiar
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_working_values()
