#!/usr/bin/env python
"""
Script completo para verificar problemas de cuota y estado de Hugging Face
"""
import os
import sys
import time
import json

# Configurar Django
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')

import django
django.setup()

def test_quota_and_limits():
    """Probar específicamente problemas de cuota"""
    print("=== VERIFICACIÓN DE CUOTAS Y LÍMITES HUGGING FACE ===")
    
    try:
        from gradio_client import Client
        
        # Probar Giant-Music-Transformer específicamente
        print("🎯 Probando Giant-Music-Transformer (API que falla)...")
        
        try:
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
            
            print("✅ Conexión establecida")
            
            # Crear archivo MIDI muy pequeño para probar
            import tempfile
            
            # MIDI mínimo válido (solo una nota)
            midi_bytes = b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x60MTrk\x00\x00\x00\x1a\x00\x90@\x7f\x81`\x80@\x00\x00\x90D\x7f\x81`\x80D\x00\x00\x90G\x7f\x81`\x80G\x00\x00\xff/\x00'
            
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
                f.write(midi_bytes)
                temp_path = f.name
            
            print(f"🎵 Archivo MIDI de prueba creado ({len(midi_bytes)} bytes)")
            
            # Intentar la llamada con parámetros mínimos
            print("🚀 Enviando solicitud a la API...")
            start_time = time.time()
            
            try:
                # Usar los mismos parámetros que tu código real
                result = client.predict(
                    input_midi=temp_path,
                    num_prime_tokens=900,
                    num_gen_tokens=50,  # Reducido para ser más rápido
                    num_mem_tokens=1024,
                    gen_outro=False,
                    gen_drums=True,
                    model_temperature=0.8,
                    model_sampling_top_p=0.95,
                    api_name="/generate_callback_wrapper"  # Endpoint correcto
                )
                
                elapsed = time.time() - start_time
                print(f"✅ ¡API FUNCIONA! Respuesta en {elapsed:.2f}s")
                print(f"📊 Resultado: {type(result)}")
                
                if isinstance(result, (list, tuple)):
                    print(f"📋 Elementos devueltos: {len(result)}")
                
                return True
                
            except Exception as e:
                elapsed = time.time() - start_time
                error_str = str(e).lower()
                
                print(f"❌ Error después de {elapsed:.2f}s: {str(e)[:100]}...")
                
                # Análisis específico del error
                if "quota" in error_str or "exceeded" in error_str:
                    print("\n🚨 PROBLEMA DETECTADO: CUOTA EXCEDIDA")
                    print("   📊 Has superado tu límite de uso gratuito")
                    print("   ⏳ Solución: Esperar hasta mañana para que se renueve")
                    print("   💳 Alternativa: Considerar plan de pago de Hugging Face")
                    return False
                    
                elif "rate limit" in error_str or "too many requests" in error_str:
                    print("\n⏱️ PROBLEMA DETECTADO: RATE LIMIT")
                    print("   🔄 Demasiadas solicitudes en poco tiempo")
                    print("   ⏳ Solución: Esperar 10-15 minutos")
                    return False
                    
                elif "upstream gradio app has raised an exception" in error_str:
                    print("\n🔧 PROBLEMA DETECTADO: ERROR DEL SERVIDOR UPSTREAM")
                    print("   🖥️ El problema está en el servidor de Hugging Face")
                    print("   💡 Posibles causas:")
                    print("      - Sobrecarga del servidor")
                    print("      - Mantenimiento en curso") 
                    print("      - Cuota del propietario de la API excedida")
                    print("   ⏳ Solución: Esperar e intentar más tarde")
                    return False
                    
                elif "timeout" in error_str:
                    print("\n⏱️ PROBLEMA DETECTADO: TIMEOUT")
                    print("   🐌 La API tardó demasiado en responder")
                    print("   💡 El servidor puede estar sobrecargado")
                    return False
                    
                elif "forbidden" in error_str or "401" in error_str or "403" in error_str:
                    print("\n🚫 PROBLEMA DETECTADO: ACCESO DENEGADO")
                    print("   🔐 Problema de permisos o autenticación")
                    return False
                    
                else:
                    print(f"\n❓ ERROR DESCONOCIDO:")
                    print(f"   {str(e)}")
                    return False
                    
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Error creando cliente: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def check_space_status():
    """Verificar el estado del espacio web"""
    print(f"\n=== VERIFICACIÓN DEL ESPACIO WEB ===")
    
    try:
        import requests
        
        space_url = "https://huggingface.co/spaces/asigalov61/Giant-Music-Transformer"
        print(f"🌐 Consultando: {space_url}")
        
        response = requests.get(space_url, timeout=15)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            if "runtime error" in content:
                print("🔥 PROBLEMA: Runtime error detectado en el espacio")
            elif "building" in content or "loading" in content:
                print("🔨 INFO: El espacio se está reconstruyendo/cargando")
            elif "sleeping" in content:
                print("😴 INFO: El espacio está en modo reposo")
            elif "queue" in content:
                print("⏳ INFO: Hay cola de usuarios")
            else:
                print("✅ El espacio web parece funcionar normalmente")
                
        else:
            print(f"⚠️ Código HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error consultando espacio: {e}")

def recommend_solutions():
    """Recomendar soluciones basadas en los resultados"""
    print(f"\n=== RECOMENDACIONES ===")
    
    print("🔍 PARA DIAGNOSTICAR EL PROBLEMA:")
    print("   1. Ejecuta este script cada hora para ver si cambia")
    print("   2. Prueba la API manualmente en: https://huggingface.co/spaces/asigalov61/Giant-Music-Transformer")
    print("   3. Verifica si otros espacios de Hugging Face funcionan")
    
    print("\n💡 SOLUCIONES POSIBLES:")
    print("   📅 Si es cuota: Esperar 24h para renovación automática")
    print("   ⏰ Si es rate limit: Esperar 15-30 minutos")
    print("   🔄 Si es servidor: Probar en 1-2 horas")
    print("   🎯 Alternativa: Buscar otro espacio similar")
    
    print("\n🚨 ALTERNATIVAS:")
    print("   1. Buscar otros espacios de generación musical")
    print("   2. Considerar plan de pago de Hugging Face")
    print("   3. Implementar cola de reintentos automáticos")

if __name__ == "__main__":
    working = test_quota_and_limits()
    check_space_status()
    recommend_solutions()
    
    if working:
        print("\n🎉 ¡LA API FUNCIONA! El problema debe estar en otra parte.")
    else:
        print("\n⚠️ CONFIRMADO: Hay problemas con la API de Hugging Face.")
