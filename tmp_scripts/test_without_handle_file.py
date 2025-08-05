#!/usr/bin/env python
"""
Script para probar el fix SIN handle_file()
"""
import os
import sys
import tempfile

# Configurar para que funcione también en PythonAnywhere
path = '/home/aherrasf/Souniq-web'
if path not in sys.path and os.path.exists(path):
    sys.path.insert(0, path)

print("=== TEST FIX SIN HANDLE_FILE ===")

def test_api_without_handle_file():
    try:
        from gradio_client import Client
        
        print("🔧 Aplicando patch simplificado...")
        
        # Guardar método original
        original_get_api_info = Client._get_api_info
        
        # Función de reemplazo
        def patched_get_api_info(self):
            try:
                return original_get_api_info(self)
            except Exception:
                print("⚠️ JSONDecodeError interceptado - retornando estructura mínima")
                return {
                    'named_endpoints': {},
                    'unnamed_endpoints': {}
                }
        
        # Aplicar patch
        Client._get_api_info = patched_get_api_info
        
        try:
            print("🔗 Creando cliente SouniQ/Modulo1...")
            client = Client("SouniQ/Modulo1")
            print("✅ Cliente creado exitosamente!")
            
            # Crear archivo de prueba pequeño
            print("📂 Creando archivo de prueba...")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                # Crear un archivo WAV mínimo válido (header WAV básico)
                wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
                temp_file.write(wav_header)
                temp_file_path = temp_file.name
            
            print(f"💾 Archivo temporal: {temp_file_path}")
            
            try:
                # Probar SIN handle_file() - solo la ruta
                print("🚀 Probando SIN handle_file() - solo ruta del archivo...")
                result = client.predict(
                    temp_file_path,  # Solo la ruta, sin handle_file()
                    api_name="/predict"
                )
                print("✅ SUCCESS: SIN handle_file() funcionó!")
                print(f"📥 Resultado: {type(result)}")
                
            except Exception as e:
                if "upload" in str(e) and "404" in str(e):
                    print("❌ FAIL: Aún intenta usar /upload")
                elif "key-word arguments" in str(e):
                    print("❌ FAIL: Aún hay problemas con argumentos")
                else:
                    print(f"⚠️ Otro error (puede ser normal): {e}")
            
            # Limpiar
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
        finally:
            # Restaurar método original
            Client._get_api_info = original_get_api_info
                
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_api_without_handle_file()
    print("\n🎯 Test completado")
