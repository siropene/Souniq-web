#!/usr/bin/env python3
"""
Test script para verificar Orpheus-Music-Transformer
"""

import os
import sys
import django
import tempfile
from django.conf import settings

# Configurar Django
sys.path.append('/Users/albertoherrastifigueroa/Library/Mobile Documents/com~apple~CloudDocs/Documents/Master/TFM/WEB2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings')
django.setup()

from gradio_client import Client, handle_file
import json

def test_orpheus_api():
    """Test básico de la API Orpheus-Music-Transformer"""
    print("🔥 Testing Orpheus-Music-Transformer API...")
    
    try:
        # Patch para JSONDecodeError
        original_get_api_info = Client._get_api_info
        
        def patched_get_api_info(self):
            try:
                return original_get_api_info(self)
            except json.JSONDecodeError:
                print("⚠️ JSONDecodeError interceptado - usando patch")
                return {
                    'named_endpoints': {},
                    'unnamed_endpoints': {}
                }
        
        Client._get_api_info = patched_get_api_info
        
        print("🔗 Conectando con asigalov61/Orpheus-Music-Transformer...")
        client = Client("asigalov61/Orpheus-Music-Transformer")
        print("✅ Cliente creado exitosamente")
        
        # Ver API info
        print("📋 Información de la API:")
        try:
            api_info = client.view_api()
            print(f"   Endpoints disponibles: {len(api_info) if api_info else 0}")
        except Exception as e:
            print(f"   Error obteniendo API info: {e}")
        
        # Crear archivo MIDI temporal simple para testing
        print("📂 Creando archivo MIDI temporal...")
        midi_content = b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x60MTrk\x00\x00\x00\x0b\x00\x90\x40\x40\x81\x40\x80\x40\x40\x00\xff\x2f\x00'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as temp_file:
            temp_file.write(midi_content)
            temp_file_path = temp_file.name
        
        print(f"💾 Archivo MIDI temporal: {temp_file_path}")
        print(f"📏 Tamaño: {len(midi_content)} bytes")
        
        # Test de predicción con parámetros de ejemplo
        print("🚀 Enviando request a la API...")
        print("⚙️ Parámetros:")
        print("   - apply_sustains: True")
        print("   - remove_duplicate_pitches: True") 
        print("   - remove_overlapping_durations: True")
        print("   - prime_instruments: []")
        print("   - num_prime_tokens: 6656")
        print("   - num_gen_tokens: 512")
        print("   - model_temperature: 0.9")
        print("   - model_top_p: 0.96")
        print("   - add_drums: False")
        print("   - add_outro: False")
        
        result = client.predict(
            input_midi=handle_file(temp_file_path),
            apply_sustains=True,
            remove_duplicate_pitches=True,
            remove_overlapping_durations=True,
            prime_instruments=[],
            num_prime_tokens=6656,
            num_gen_tokens=512,
            model_temperature=0.9,
            model_top_p=0.96,
            add_drums=False,
            add_outro=False,
            api_name="/generate_music_and_state"
        )
        
        print("📥 Resultado recibido:")
        print(f"   Tipo: {type(result)}")
        print(f"   Longitud: {len(result) if hasattr(result, '__len__') else 'No tiene longitud'}")
        
        if hasattr(result, '__len__') and len(result) > 0:
            print("   Primeros elementos:")
            for i, item in enumerate(result[:3]):
                print(f"      [{i}] {type(item)} - {str(item)[:100] if item else 'None'}")
        
        print("✅ Test completado exitosamente")
        
        # Limpiar archivo temporal
        os.unlink(temp_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False
    
    finally:
        # Restaurar método original
        if 'original_get_api_info' in locals():
            Client._get_api_info = original_get_api_info

if __name__ == "__main__":
    print("🎵 Test de Orpheus-Music-Transformer")
    print("=" * 50)
    
    success = test_orpheus_api()
    
    print("=" * 50)
    if success:
        print("🎉 Test exitoso! Orpheus-Music-Transformer está funcionando")
    else:
        print("❌ Test falló. Revisa los logs para más detalles")
