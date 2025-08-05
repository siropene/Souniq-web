#!/usr/bin/env python
"""
Script para investigar los endpoints reales de SouniQ/Modulo1
"""
import os
import sys
import json

# Configurar para que funcione también en PythonAnywhere
path = '/home/aherrasf/Souniq-web'
if path not in sys.path and os.path.exists(path):
    sys.path.insert(0, path)

print("=== INVESTIGACIÓN DE ENDPOINTS SouniQ/Modulo1 ===")

def investigate_api():
    try:
        from gradio_client import Client
        
        print("🔍 Intentando crear cliente SIN patch...")
        try:
            # Intentar sin patch primero
            client = Client("SouniQ/Modulo1")
            print("✅ Cliente creado sin patch!")
            
            # Ver API info
            try:
                api_info = client.view_api()
                print("📋 API Info obtenida:")
                print(api_info)
            except Exception as e:
                print(f"⚠️ Error al obtener view_api(): {e}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSONDecodeError como esperado: {e}")
            print("🔧 Intentando con patch...")
            
            # Guardar método original
            original_get_api_info = Client._get_api_info
            
            # Función de reemplazo
            def patched_get_api_info(self):
                try:
                    return original_get_api_info(self)
                except json.JSONDecodeError:
                    print("⚠️ JSONDecodeError interceptado - retornando estructura mínima")
                    # Estructura mínima para permitir creación del cliente
                    return {
                        'named_endpoints': {},
                        'unnamed_endpoints': {}
                    }
            
            # Aplicar patch
            Client._get_api_info = patched_get_api_info
            
            try:
                client = Client("SouniQ/Modulo1")
                print("✅ Cliente creado CON patch!")
                
                # Intentar ver API después del patch
                try:
                    api_info = client.view_api()
                    print("📋 API Info después del patch:")
                    print(api_info)
                except Exception as e:
                    print(f"⚠️ Error al obtener view_api() después del patch: {e}")
                
                # Intentar acceder a métodos internos
                try:
                    print("\n🔍 Explorando atributos del cliente:")
                    for attr in dir(client):
                        if not attr.startswith('_'):
                            print(f"  - {attr}")
                    
                    # Intentar acceder a endpoints disponibles
                    if hasattr(client, 'endpoints'):
                        print(f"\n📍 Endpoints encontrados: {client.endpoints}")
                    
                    if hasattr(client, 'api_info'):
                        print(f"\n📋 API Info interna: {client.api_info}")
                        
                except Exception as e:
                    print(f"⚠️ Error explorando cliente: {e}")
                
                return True
                
            except Exception as e:
                print(f"❌ Error incluso con patch: {e}")
                return False
            
            finally:
                # Restaurar método original
                Client._get_api_info = original_get_api_info
                
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def test_direct_api_call():
    """Probar llamada directa a la API"""
    try:
        print("\n🌐 Probando llamada HTTP directa...")
        import requests
        
        base_url = "https://souniq-modulo1.hf.space"
        
        # Probar diferentes endpoints
        endpoints = ["/", "/info", "/config", "/api", "/predict", "/upload"]
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"\n🔗 Probando: {url}")
                
                response = requests.get(url, timeout=10)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    print(f"   Content-Type: {content_type}")
                    
                    if 'json' in content_type:
                        try:
                            data = response.json()
                            print(f"   JSON: {data}")
                        except:
                            print(f"   Contenido: {response.text[:200]}...")
                    else:
                        print(f"   Contenido (primeros 200 chars): {response.text[:200]}...")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Error en test_direct_api_call: {e}")

if __name__ == "__main__":
    investigate_api()
    test_direct_api_call()
    print("\n🎯 Investigación completada")
