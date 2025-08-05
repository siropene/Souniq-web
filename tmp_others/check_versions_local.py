#!/usr/bin/env python
"""
Script para verificar versiones y crear cliente con manejo de errores robusto
"""
print("=== COMPARACIÓN LOCAL VS PRODUCCIÓN ===")

def check_versions():
    """Verificar versiones de dependencias"""
    try:
        import gradio_client
        print(f"📦 gradio_client versión: {gradio_client.__version__}")
    except:
        print("❌ No se pudo obtener versión de gradio_client")
    
    try:
        import requests
        print(f"📦 requests versión: {requests.__version__}")
    except:
        print("❌ No se pudo obtener versión de requests")

def test_robust_client():
    """Probar cliente con manejo robusto de errores"""
    from gradio_client import Client
    import json
    
    try:
        print("\n🔧 Probando conexión estándar...")
        client = Client("SouniQ/Modulo1")
        print("✅ Conexión estándar exitosa")
        return client
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSONDecodeError detectado: {e}")
        print("   Esto es normal en algunos entornos...")
        
        try:
            print("🔧 Probando con verbose=False...")
            client = Client("SouniQ/Modulo1", verbose=False)
            print("✅ Conexión con verbose=False exitosa")
            return client
        except Exception as e2:
            print(f"❌ También falló: {e2}")
            
        try:
            print("🔧 Probando con timeout personalizado...")
            client = Client("SouniQ/Modulo1", timeout=60)
            print("✅ Conexión con timeout personalizado exitosa")
            return client
        except Exception as e3:
            print(f"❌ También falló: {e3}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
    
    return None

if __name__ == "__main__":
    check_versions()
    client = test_robust_client()
    
    if client:
        print("\n🎉 CLIENTE FUNCIONANDO!")
        print("   Este enfoque debe funcionar en producción")
    else:
        print("\n❌ NO SE PUDO CREAR CLIENTE")
        print("   Problema más profundo en la conexión")
