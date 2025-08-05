#!/usr/bin/env python
"""
Script para comparar el funcionamiento directo vs desde código
"""
import os
import sys
import tempfile

# Configurar Django
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')

import django
django.setup()

def test_with_real_midi():
    """Probar con un archivo MIDI real de la base de datos"""
    print("=== PRUEBA CON ARCHIVO MIDI REAL ===")
    
    try:
        from gradio_client import Client
        from music_processing.models import MidiFile
        import json
        
        # Buscar un archivo MIDI real
        midi_file = MidiFile.objects.filter(status='completed', file__isnull=False).first()
        
        if not midi_file:
            print("❌ No hay archivos MIDI en la base de datos")
            return False
        
        print(f"📁 Usando MIDI: {midi_file.file.name}")
        print(f"� Tamaño: {midi_file.file.size} bytes")
        
        # Crear cliente con patch
        original_get_api_info = Client._get_api_info
        
        def patched_get_api_info(self):
            try:
                return original_get_api_info(self)
            except json.JSONDecodeError:
                return {'named_endpoints': {}, 'unnamed_endpoints': {}}
        
        Client._get_api_info = patched_get_api_info
        client = Client("asigalov61/Giant-Music-Transformer")
        Client._get_api_info = original_get_api_info
        
        print("✅ Cliente conectado")
        
        # Crear archivo temporal con el MIDI real
        midi_file.file.seek(0)
        midi_content = midi_file.file.read()
        
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            f.write(midi_content)
            temp_path = f.name
        
        print(f"📂 Archivo temporal: {temp_path}")
        
        # Probar con diferentes sets de parámetros
        test_configs = [
            {
                'name': 'Parámetros actuales del código',
                'params': {
                    'input_midi': temp_path,
                    'num_prime_tokens': 900,
                    'num_gen_tokens': 300,
                    'num_mem_tokens': 1024,
                    'gen_outro': False,
                    'gen_drums': True,
                    'model_temperature': 0.9,
                    'model_sampling_top_p': 0.95,
                    'api_name': '/generate_callback_wrapper'
                }
            },
            {
                'name': 'Parámetros mínimos',
                'params': {
                    'input_midi': temp_path,
                    'num_prime_tokens': 100,
                    'num_gen_tokens': 50,
                    'num_mem_tokens': 512,
                    'gen_outro': False,
                    'gen_drums': False,
                    'model_temperature': 0.8,
                    'model_sampling_top_p': 0.9,
                    'api_name': '/generate_callback_wrapper'
                }
            },
            {
                'name': 'Sin api_name (default)',
                'params': {
                    'input_midi': temp_path,
                    'num_prime_tokens': 100,
                    'num_gen_tokens': 50,
                    'num_mem_tokens': 512,
                    'gen_outro': False,
                    'gen_drums': False,
                    'model_temperature': 0.8,
                    'model_sampling_top_p': 0.9
                }
            }
        ]
        
        for config in test_configs:
            print(f"
🧪 Probando: {config['name']}")
            
            try:
                result = client.predict(**config['params'])
                
                print(f"   ✅ ¡FUNCIONA!")
                print(f"   📊 Resultado: {type(result)}")
                if isinstance(result, (list, tuple)):
                    print(f"   📋 Elementos: {len(result)}")
                    for i, item in enumerate(result[:3]):  # Solo los primeros 3
                        print(f"      [{i}]: {type(item)} - {str(item)[:50]}...")
                
                # Si funciona, no necesitamos probar más
                break
                
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Error: {error_msg[:100]}...")
                
                # Analizar el error específico
                if "upstream gradio app has raised an exception" in error_msg.lower():
                    print(f"   � Error upstream - puede ser problema de parámetros")
                elif "cannot find a function" in error_msg.lower():
                    print(f"   🔍 Endpoint incorrecto")
                elif "timeout" in error_msg.lower():
                    print(f"   🔍 Timeout - archivo muy grande o servidor lento")
                else:
                    print(f"   🔍 Error desconocido")
        
        # Limpiar
        try:
            os.unlink(temp_path)
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_with_real_midi()
