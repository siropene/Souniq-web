#!/usr/bin/env python
"""
Script de diagnóstico específico para APIs de Hugging Face
Ejecutar en PythonAnywhere para verificar el estado de las APIs
"""
import os
import sys
import time
import requests

# Configurar Django
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')

print("=== DIAGNÓSTICO APIs HUGGING FACE ===")

def test_api_connection(api_name):
    """Probar conexión a una API de Hugging Face"""
    print(f"\n🔍 Probando API: {api_name}")
    
    # URLs de Hugging Face
    base_url = f"https://{api_name.lower().replace('/', '-')}.hf.space"
    config_url = f"{base_url}/config"
    info_url = f"{base_url}/info"
    
    try:
        # 1. Probar conexión básica
        print(f"📡 Probando conexión a {base_url}...")
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        # 2. Probar config endpoint
        print(f"⚙️ Probando config endpoint...")
        config_response = requests.get(config_url, timeout=10)
        print(f"   Config Status: {config_response.status_code}")
        if config_response.status_code == 200:
            print(f"   Config Content-Type: {config_response.headers.get('content-type', 'unknown')}")
            print(f"   Config Length: {len(config_response.content)} bytes")
        
        # 3. Probar info endpoint
        print(f"ℹ️ Probando info endpoint...")
        info_response = requests.get(info_url, timeout=10)
        print(f"   Info Status: {info_response.status_code}")
        if info_response.status_code == 200:
            print(f"   Info Content-Type: {info_response.headers.get('content-type', 'unknown')}")
            print(f"   Info Length: {len(info_response.content)} bytes")
            try:
                info_json = info_response.json()
                print(f"   ✅ JSON válido: {len(info_json)} elementos")
            except:
                print(f"   ❌ JSON inválido o vacío")
        
        # 4. Probar con gradio_client
        print(f"🤖 Probando con gradio_client...")
        try:
            from gradio_client import Client
            client = Client(api_name)
            print(f"   ✅ Cliente creado exitosamente")
            
            # Ver API info
            try:
                api_info = client.view_api()
                print(f"   📋 API info obtenida: {len(str(api_info))} caracteres")
                print(f"   📋 Endpoints disponibles:")
                if hasattr(api_info, 'named_endpoints') and api_info.named_endpoints:
                    for endpoint in api_info.named_endpoints:
                        print(f"      - {endpoint}")
                else:
                    print(f"      No se encontraron endpoints nombrados")
                return True
            except Exception as e:
                print(f"   ❌ Error obteniendo API info: {e}")
                
        except Exception as e:
            print(f"   ❌ Error creando cliente: {e}")
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ Timeout - La API puede estar dormida")
    except requests.exceptions.ConnectionError:
        print(f"   🚫 Error de conexión")
    except Exception as e:
        print(f"   ❌ Error general: {e}")
    
    return False

def wake_up_api(api_name):
    """Intentar despertar una API dormida"""
    print(f"\n😴 Intentando despertar {api_name}...")
    base_url = f"https://{api_name.lower().replace('/', '-')}.hf.space"
    
    for i in range(3):
        try:
            print(f"   Intento {i+1}/3...")
            response = requests.get(base_url, timeout=30)
            if response.status_code == 200:
                print(f"   ✅ API despierta!")
                return True
            time.sleep(10)
        except:
            print(f"   ⏰ Esperando...")
            time.sleep(10)
    
    print(f"   ❌ No se pudo despertar la API")
    return False

# Probar las APIs principales
apis_to_test = [
    "SouniQ/Modulo1",  # Separación de stems
    "SouniQ/Modulo2",  # Conversión MIDI
]

print(f"📅 Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🌐 Probando desde PythonAnywhere...")

for api in apis_to_test:
    success = test_api_connection(api)
    if not success:
        print(f"\n🔄 API {api} no responde, intentando despertar...")
        wake_up_api(api)
        print(f"⏳ Esperando 15 segundos antes de probar de nuevo...")
        time.sleep(15)
        test_api_connection(api)

print("\n=== RECOMENDACIONES ===")
print("1. Si las APIs están dormidas, puede tardar 1-2 minutos en despertar")
print("2. Si hay errores JSON, verifica que las URLs sean correctas")
print("3. Si hay timeouts, prueba más tarde o contacta al propietario de la API")
print("4. Para debugging en tiempo real, usa el script desde la consola de PythonAnywhere")

print("\n=== FIN DIAGNÓSTICO ===")
