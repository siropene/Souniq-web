#!/usr/bin/env python
"""
Script para probar predict() con archivo real de la base de datos
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

def test_predict_real_file():
    """Probar predict() con un archivo real de la base de datos"""
    print("=== PRUEBA CON ARCHIVO REAL ===")
    
    try:
        from music_processing.models import Song
        from gradio_client import Client, handle_file
        import json
        
        # Buscar una canción en la base de datos
        try:
            song = Song.objects.filter(status='uploaded').first()
            if not song:
                song = Song.objects.first()
            
            if not song:
                print("❌ No hay canciones en la base de datos")
                return
                
            print(f"🎵 Usando canción: {song.title}")
            print(f"📁 Archivo: {song.original_file.name}")
            
            # Verificar que el archivo existe
            if not song.original_file:
                print("❌ La canción no tiene archivo")
                return
                
        except Exception as e:
            print(f"❌ Error accediendo a la base de datos: {e}")
            return
        
        # Crear archivo temporal con el contenido real
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            song.original_file.seek(0)
            temp_file.write(song.original_file.read())
            temp_file_path = temp_file.name
            print(f"📂 Archivo temporal creado: {temp_file_path}")
            print(f"📏 Tamaño: {os.path.getsize(temp_file_path)} bytes")
        
        # Crear cliente con patch
        print("🔗 Creando cliente...")
        
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
            
            # Probar predict con timeout mayor
            print("🚀 Probando predict() con archivo real...")
            print("⏱️ Esto puede tardar hasta 2-3 minutos...")
            
            result = client.predict(
                handle_file(temp_file_path),
                api_name="/predict"
            )
            
            print(f"📥 Resultado: {type(result)}")
            if result:
                print(f"   Longitud: {len(result) if hasattr(result, '__len__') else 'No tiene longitud'}")
                if hasattr(result, '__len__'):
                    print(f"   ✅ ¡ÉXITO! Recibidos {len(result)} elementos")
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
    test_predict_real_file()
