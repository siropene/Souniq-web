#!/usr/bin/env python
"""
Script para probar el nuevo enfoque de reintentos en PythonAnywhere
Ejecutar en PythonAnywhere: python test_retry_approach.py
"""
import os
import sys
import json
import time

# Configurar ruta para PythonAnywhere
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

print("=== PRUEBA DE ENFOQUE DE REINTENTOS ===")

def test_client_with_retries():
    """Probar creación de cliente con reintentos"""
    try:
        print("🔧 Importando gradio_client...")
        from gradio_client import Client
        
        print("🔗 Probando SouniQ/Modulo1 con reintentos...")
        
        client = None
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Intento {attempt + 1}/{max_retries}")
                client = Client("SouniQ/Modulo1")
                print("✅ Cliente conectado exitosamente")
                break
                
            except json.JSONDecodeError as json_err:
                print(f"⚠️ JSONDecodeError en intento {attempt + 1}: {json_err}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 5, 10, 15 segundos
                    print(f"😴 Esperando {wait_time} segundos antes del siguiente intento...")
                    time.sleep(wait_time)
                else:
                    print("❌ Todos los intentos fallaron con JSONDecodeError")
                    return False
                    
            except Exception as e:
                print(f"❌ Error crítico en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print("🔄 Reintentando con error crítico...")
                    time.sleep(3)
                else:
                    print(f"❌ Error final: {e}")
                    return False
        
        if client is None:
            print("❌ No se pudo crear el cliente después de todos los intentos")
            return False
            
        # Si llegamos aquí, el cliente se creó exitosamente
        print("🎯 ¡ÉXITO! Cliente creado con enfoque de reintentos")
        
        # Probar que predict está disponible
        if hasattr(client, 'predict'):
            print("✅ Método predict() disponible")
            
            # Probar llamada sin argumentos para ver error esperado
            try:
                client.predict()
            except Exception as e:
                print(f"⚠️ Error esperado en predict(): {e}")
                print("   (Esto es normal - necesita argumentos)")
                
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_client_with_retries()
    if success:
        print("\n🎉 CONCLUSIÓN: El enfoque de reintentos funciona!")
        print("🚀 Ahora se puede probar en la web de producción")
    else:
        print("\n❌ CONCLUSIÓN: Persisten problemas con las APIs")
        print("🔧 Se necesita investigación adicional")
