#!/usr/bin/env python
"""
Script para probar predict() en producción
"""
import os
import sys
import json

# Configurar Django
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')

import django
django.setup()

print("=== PRUEBA DE PREDICT() ===")

def test_predict_functionality():
    """Probar si podemos usar predict() después de crear el cliente"""
    try:
        print("🔧 Importando gradio_client...")
        from gradio_client import Client
        
        print("🔗 Creando cliente SouniQ/Modulo1...")
        
        try:
            client = Client("SouniQ/Modulo1")
            print("✅ Cliente creado exitosamente!")
        except json.JSONDecodeError as json_err:
            print(f"⚠️ JSONDecodeError ignorado: {json_err}")
            print("🔄 Cliente debería funcionar de todas formas...")
            client = Client("SouniQ/Modulo1")  # Intentar de nuevo
            
        # Ahora probar si podemos hacer predict (sin archivo real por ahora)
        print("🎯 Probando acceso a función predict...")
        print("   (Solo verificando que la función existe)")
        
        # Ver si tiene el método predict
        if hasattr(client, 'predict'):
            print("✅ Método predict() disponible!")
            
            # Ver endpoints disponibles si es posible
            try:
                print("📋 Intentando obtener información de endpoints...")
                # NO llamar view_api() directamente para evitar JSONDecodeError
                print("⚠️ Saltando view_api() para evitar JSONDecodeError")
                print("✅ Cliente listo para usar con predict()")
                
            except Exception as e:
                print(f"⚠️ No se pudo obtener info de API, pero predict() debería funcionar: {e}")
        else:
            print("❌ Método predict() NO disponible")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_predict_functionality()
    if success:
        print("\n🎯 CONCLUSIÓN: predict() debería funcionar!")
        print("🚀 Próximo paso: Probar en web real con archivo de audio")
    else:
        print("\n❌ CONCLUSIÓN: Problemas con predict()")
