#!/usr/bin/env python
"""
Script para diagnosticar paso a paso el problema con Giant-Music-Transformer
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

def test_step_by_step():
    """Probar paso a paso para encontrar el problema"""
    print("=== DIAGNÓSTICO PASO A PASO ===")
    
    try:
        from gradio_client import Client, handle_file
        from music_processing.models import MidiFile
        import tempfile
        
        # Paso 1: Encontrar MIDI válido
        print("\n📁 PASO 1: Encontrar archivo MIDI...")
        midi = MidiFile.objects.filter(status='completed', file__isnull=False).first()
        if not midi:
            print("❌ No hay MIDIs disponibles")
            return
        
        print(f"✅ MIDI encontrado: {midi.file.name}")
        print(f"📏 Tamaño: {midi.file.size} bytes")
        
        # Paso 2: Validar contenido MIDI
        print("\n🔍 PASO 2: Validar contenido MIDI...")
        midi.file.seek(0)
        midi_content = midi.file.read()
        
        if len(midi_content) < 100:
            print(f"❌ MIDI muy pequeño: {len(midi_content)} bytes")
            return
        
        if not midi_content.startswith(b'MThd'):
            print("❌ Header MIDI inválido")
            return
        
        print("✅ MIDI válido")
        
        # Paso 3: Crear cliente con patch
        print("\n🔗 PASO 3: Crear cliente...")
        original = Client._get_api_info
        try:
            Client._get_api_info = lambda self: {'named_endpoints': {}, 'unnamed_endpoints': {}}
            client = Client("asigalov61/Giant-Music-Transformer")
            print("✅ Cliente creado")
        finally:
            Client._get_api_info = original
        
        # Paso 4: Crear archivo temporal
        print("\n📂 PASO 4: Crear archivo temporal...")
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            f.write(midi_content)
            temp_path = f.name
        print(f"✅ Archivo temporal: {temp_path}")
        
        # Paso 5: Probar diferentes métodos de paso de archivo
        print("\n🧪 PASO 5: Probar diferentes métodos...")
        
        # Método 1: Ruta directa (como en nuestro código)
        print("\n🔸 Método 1: Ruta directa")
        try:
            result = client.predict(
                temp_path,    # Ruta directa
                128,          # num_prime_tokens
                100,          # num_gen_tokens  
                512,          # num_mem_tokens
                False,        # gen_outro
                False,        # gen_drums
                0.8,          # model_temperature
                0.9,          # model_sampling_top_p
                api_name="/generate_callback_wrapper"
            )
            print("✅ Método 1 EXITOSO")
            
        except Exception as e:
            print(f"❌ Método 1 falló: {str(e)[:100]}...")
            
            # Método 2: Con handle_file (como documentación Gradio)
            print("\n🔸 Método 2: Con handle_file")
            try:
                result = client.predict(
                    handle_file(temp_path),  # Con handle_file
                    128,          # num_prime_tokens
                    100,          # num_gen_tokens  
                    512,          # num_mem_tokens
                    False,        # gen_outro
                    False,        # gen_drums
                    0.8,          # model_temperature
                    0.9,          # model_sampling_top_p
                    api_name="/generate_callback_wrapper"
                )
                print("✅ Método 2 EXITOSO")
                
            except Exception as e2:
                print(f"❌ Método 2 falló: {str(e2)[:100]}...")
                
                # Método 3: Con valores aún más conservadores
                print("\n🔸 Método 3: Valores mínimos")
                try:
                    result = client.predict(
                        temp_path,    
                        64,           # num_prime_tokens (muy bajo)
                        50,           # num_gen_tokens (muy bajo)
                        256,          # num_mem_tokens (muy bajo)
                        False,        # gen_outro
                        False,        # gen_drums
                        0.7,          # model_temperature (más bajo)
                        0.8,          # model_sampling_top_p (más bajo)
                        api_name="/generate_callback_wrapper"
                    )
                    print("✅ Método 3 EXITOSO")
                    
                except Exception as e3:
                    print(f"❌ Método 3 falló: {str(e3)[:100]}...")
                    
                    # Método 4: Probar otro endpoint
                    print("\n🔸 Método 4: Endpoint diferente")
                    try:
                        result = client.predict(
                            temp_path,    
                            128,          
                            100,          
                            512,          
                            False,        
                            False,        
                            0.8,          
                            0.9,          
                            api_name="/predict"  # Endpoint alternativo
                        )
                        print("✅ Método 4 EXITOSO")
                        
                    except Exception as e4:
                        print(f"❌ Método 4 falló: {str(e4)[:100]}...")
                        print("\n💭 Todos los métodos fallaron. Posibles causas:")
                        print("   1. Archivo MIDI específico problemático")
                        print("   2. API temporalmente caída")
                        print("   3. Problema de conexión")
                        print("   4. Cambios en la API upstream")
        
        # Paso 6: Información del archivo para debugging
        print(f"\n📊 INFORMACIÓN DEL ARCHIVO:")
        print(f"   Nombre: {midi.file.name}")
        print(f"   Stem: {midi.stem.stem_type}")
        print(f"   Canción: {midi.stem.song.title}")
        print(f"   Primeros 20 bytes: {midi_content[:20].hex()}")
        
        # Limpiar
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_step_by_step()
