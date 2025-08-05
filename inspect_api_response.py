#!/usr/bin/env python
"""
Script para inspeccionar la respuesta de la API
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

def inspect_api_response():
    """Inspeccionar qué devuelve exactamente la API"""
    print("=== INSPECCIÓN DE RESPUESTA API ===")
    
    try:
        from gradio_client import Client, handle_file
        from music_processing.models import MidiFile
        import tempfile
        import json
        
        # Encontrar MIDI
        midi = MidiFile.objects.filter(status='completed', file__isnull=False).first()
        if not midi:
            print("❌ No hay MIDIs disponibles")
            return
        
        print(f"📁 MIDI: {midi.file.name}")
        
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
        
        print("🧪 Enviando a API...")
        try:
            result = client.predict(
                handle_file(temp_path),
                600,          # num_prime_tokens
                600,          # num_gen_tokens
                1024,         # num_mem_tokens
                "Auto",       # gen_outro
                False,        # gen_drums
                0.9,          # model_temperature
                0.96,         # model_sampling_top_p
                api_name="/generate_callback_wrapper"
            )
            
            print("✅ API respondió exitosamente")
            print(f"📊 Tipo de resultado: {type(result)}")
            print(f"📏 Longitud: {len(result) if hasattr(result, '__len__') else 'No tiene longitud'}")
            
            if isinstance(result, (list, tuple)):
                print("\n🔍 ANÁLISIS DETALLADO:")
                for i, item in enumerate(result[:5]):  # Analizar primeros 5
                    print(f"\n📂 Elemento {i}:")
                    print(f"   Tipo: {type(item)}")
                    
                    if isinstance(item, str):
                        print(f"   Valor: {item}")
                        print(f"   ¿Existe archivo?: {os.path.exists(item) if item else 'N/A'}")
                    elif isinstance(item, dict):
                        print(f"   Keys: {list(item.keys())}")
                        for key, value in item.items():
                            if isinstance(value, str) and len(value) < 200:
                                print(f"     {key}: {value}")
                            else:
                                print(f"     {key}: {type(value)} (len={len(value) if hasattr(value, '__len__') else 'N/A'})")
                    elif hasattr(item, '__dict__'):
                        print(f"   Atributos: {list(item.__dict__.keys())}")
                    else:
                        print(f"   Valor: {str(item)[:100]}...")
                        
                # Intentar encontrar archivos válidos
                print("\n🗂️ BÚSQUEDA DE ARCHIVOS:")
                valid_files = []
                for i, item in enumerate(result):
                    file_path = None
                    
                    if isinstance(item, str):
                        file_path = item
                    elif isinstance(item, dict):
                        file_path = item.get('name') or item.get('path') or item.get('file')
                    elif hasattr(item, 'name'):
                        file_path = item.name
                    
                    if file_path and os.path.exists(file_path):
                        valid_files.append((i, file_path))
                        print(f"   ✅ Elemento {i}: {file_path}")
                    else:
                        print(f"   ❌ Elemento {i}: {file_path or 'No path found'}")
                
                print(f"\n📈 Archivos válidos encontrados: {len(valid_files)}")
                
        except Exception as e:
            print(f"❌ Error en API: {e}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
        
        # Limpiar
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    inspect_api_response()
