#!/usr/bin/env python
"""
Script para descubrir endpoints reales de Giant-Music-Transformer
"""
import os
import sys
import json

# Configurar Django
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')

import django
django.setup()

def discover_real_endpoints():
    """Descubrir los endpoints reales"""
    print("=== DESCUBRIMIENTO DE ENDPOINTS REALES ===")
    
    try:
        from gradio_client import Client
        
        print("🔗 Conectando a Giant-Music-Transformer...")
        client = Client("asigalov61/Giant-Music-Transformer")
        print("✅ Cliente conectado")
        
        # Endpoints comunes para probar
        endpoints_to_test = [
            "/predict",
            "/generate", 
            "/inference",
            "/generate_callback_wrapper",  # Este es el que usas en tu código
            "/transform",
            "/midi_generation",
            None  # Sin api_name
        ]
        
        print("\n🧪 Probando endpoints...")
        
        import tempfile
        # Crear MIDI mínimo
        midi_bytes = b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x60MTrk\x00\x00\x00\x1a\x00\x90@\x7f\x81`\x80@\x00\x00\x90D\x7f\x81`\x80D\x00\x00\x90G\x7f\x81`\x80G\x00\x00\xff/\x00'
        
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            f.write(midi_bytes)
            temp_path = f.name
        
        working_endpoints = []
        
        for endpoint in endpoints_to_test:
            try:
                print(f"   🔍 Probando: {endpoint or 'default'}")
                
                # Usar los mismos parámetros que tu código original
                kwargs = {
                    'input_midi': temp_path,
                    'num_prime_tokens': 900,
                    'num_gen_tokens': 300,
                    'num_mem_tokens': 1024,
                    'gen_outro': False,
                    'gen_drums': True,
                    'model_temperature': 0.9,
                    'model_sampling_top_p': 0.95
                }
                
                if endpoint:
                    kwargs['api_name'] = endpoint
                
                result = client.predict(**kwargs)
                
                print(f"   ✅ ¡FUNCIONA! {endpoint or 'default'}")
                print(f"   📊 Resultado: {type(result)}")
                if isinstance(result, (list, tuple)):
                    print(f"   📋 Elementos: {len(result)}")
                
                working_endpoints.append(endpoint)
                
            except Exception as e:
                error_msg = str(e)
                if "Cannot find a function" in error_msg:
                    print(f"   ❌ No existe: {endpoint or 'default'}")
                elif "upstream" in error_msg.lower():
                    print(f"   ⚠️ Existe pero error servidor: {endpoint or 'default'}")
                elif "timeout" in error_msg.lower():
                    print(f"   ⏱️ Timeout: {endpoint or 'default'}")
                else:
                    print(f"   ❌ Error: {error_msg[:80]}...")
        
        # Limpiar
        try:
            os.unlink(temp_path)
        except:
            pass
        
        print(f"\n📋 RESUMEN:")
        if working_endpoints:
            print(f"✅ Endpoints que funcionan: {working_endpoints}")
            return working_endpoints[0]  # Devolver el primero que funciona
        else:
            print(f"❌ Ningún endpoint funciona")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    working_endpoint = discover_real_endpoints()
    
    if working_endpoint is not None:
        print(f"\n🔧 SOLUCIÓN ENCONTRADA:")
        if working_endpoint:
            print(f"   Cambiar api_name a: '{working_endpoint}'")
        else:
            print(f"   Eliminar parámetro api_name completamente")
        
        print(f"\n📝 Actualizar en tasks_sync.py:")
        if working_endpoint:
            print(f"   api_name=\"{working_endpoint}\"")
        else:
            print(f"   # Eliminar línea api_name")
    else:
        print(f"\n❌ No se encontró solución. La API puede haber cambiado completamente.")
