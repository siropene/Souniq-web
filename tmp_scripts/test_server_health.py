#!/usr/bin/env python
"""
Script de prueba rápida para verificar que el servidor Django funciona
"""
import os
import sys
import requests

# Configuración
BASE_URL = "https://aherrasf.pythonanywhere.com"
ENDPOINTS_TO_TEST = [
    "/music/",
    "/music/songs/",
    "/music/stems/",
    "/music/midi/",
    "/music/generate/",
]

def test_server_health():
    """Probar que el servidor responde correctamente"""
    print("=== PRUEBA DE SALUD DEL SERVIDOR ===")
    
    try:
        for endpoint in ENDPOINTS_TO_TEST:
            url = BASE_URL + endpoint
            print(f"🔍 Probando {endpoint}...", end=" ")
            
            try:
                response = requests.get(url, timeout=10)
                
                # Verificar si no hay error 500
                if response.status_code == 500:
                    print(f"❌ Error 500")
                elif response.status_code == 302:
                    print(f"✅ Redirect (probablemente a login)")
                elif response.status_code == 200:
                    print(f"✅ OK")
                else:
                    print(f"⚠️ Status {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print("⏱️ Timeout")
            except requests.exceptions.ConnectionError:
                print("🌐 Error de conexión")
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
        
        # Probar específicamente la subida de canciones con GET
        print(f"\n🎯 Probando endpoint problemático...")
        url = BASE_URL + "/music/songs/upload/"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 500:
                print(f"❌ /music/songs/upload/ sigue dando error 500")
            elif response.status_code == 302:
                print(f"✅ /music/songs/upload/ redirige correctamente (no más error 500)")
            else:
                print(f"✅ /music/songs/upload/ responde con status {response.status_code}")
        except Exception as e:
            print(f"❌ Error probando upload: {e}")
        
        print(f"\n💡 NOTA: Los redirects (302) son normales para usuarios no autenticados")
        print(f"💡 Lo importante es que NO haya errores 500")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_server_health()
