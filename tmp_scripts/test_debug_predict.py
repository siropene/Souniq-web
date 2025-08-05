#!/usr/bin/env python
"""
Script para probar predict() específicamente con archivo de prueba
"""
import os
import sys
import tempfile

# Configurar Django
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')

def test_predict():
    """Probar predict() con un archivo simple"""
    print("=== PRUEBA DE PREDICT() ===")
    
    try:
        from gradio_client import Client, handle_file
        
        # Crear un archivo temporal de prueba simple
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            # Crear un archivo WAV mínimo (silencio)
            import wave
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(1)  # mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(44100)  # 44.1kHz
                # 1 segundo de silencio
                frames = b'\x00\x00' * 44100
                wav_file.writeframes(frames)
            
            temp_file_path = temp_file.name
            print(f"📂 Archivo temporal creado: {temp_file_path}")
        
        # Crear cliente con patch
        print("🔗 Creando cliente...")
        from gradio_client import Client
        import json
        
        # Patch para JSONDecodeError
        original_get_api_info = Client._get_api_info
        
        def patched_get_api_info(self):
            try:
                return original_get_api_info(self)
            except json.JSONDecodeError:
                print("⚠️ JSONDecodeError - usando estructura mínima")
                return {
                    'named_endpoints': {},
                    'unnamed_endpoints': {}
                }
        
        Client._get_api_info = patched_get_api_info
        
        try:
            client = Client("SouniQ/Modulo1")
            print("✅ Cliente creado")
            
            # Probar predict
            print("🚀 Probando predict()...")
            result = client.predict(
                handle_file(temp_file_path),
                api_name="/predict"
            )
            
            print(f"📥 Resultado: {type(result)}")
            if result:
                print(f"   Longitud: {len(result) if hasattr(result, '__len__') else 'No tiene longitud'}")
                if hasattr(result, '__len__'):
                    for i, item in enumerate(result[:3]):
                        print(f"   Item {i}: {type(item)} - {str(item)[:50] if item else 'None'}")
            else:
                print("   ❌ Resultado es None")
                
        except Exception as e:
            print(f"❌ Error en predict(): {e}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            
        finally:
            # Restaurar método original
            Client._get_api_info = original_get_api_info
            
            # Limpiar archivo temporal
            os.unlink(temp_file_path)
            print("🧹 Archivo temporal eliminado")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        print(f"📋 Traceback general: {traceback.format_exc()}")

if __name__ == "__main__":
    test_predict()
