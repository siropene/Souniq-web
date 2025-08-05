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
            # Valores muy conservadores (como los defaults del espacio)
            result = client.predict(
                input_midi=temp_path,
                num_prime_tokens=128,   # Valor típico default
                num_gen_tokens=100,    # Valor bajo
                num_mem_tokens=512,    # Valor estándar
                gen_outro=False,
                gen_drums=False,
                model_temperature=0.8,
                model_sampling_top_p=0.9,
                api_name="/generate_callback_wrapper"
            )
            
            print("✅ ¡ÉXITO! Los valores conservadores funcionan")
            print(f"📊 Tipo de resultado: {type(result)}")
            if isinstance(result, (list, tuple)):
                print(f"📋 Elementos devueltos: {len(result)}")
            
            # Ahora probar incrementalmente
            print("\n🔄 Probando con valores más altos...")
            result2 = client.predict(
                input_midi=temp_path,
                num_prime_tokens=500,   # Incrementar
                num_gen_tokens=200,    # Incrementar
                num_mem_tokens=1024,   # Tu valor original
                gen_outro=False,
                gen_drums=True,        # Como tu código
                model_temperature=0.9, # Tu valor
                model_sampling_top_p=0.95, # Tu valor
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
