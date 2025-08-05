#!/usr/bin/env python
"""
Script para comparar funcionamiento local vs producción
"""
import os
import sys

# Configurar Django para local
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings')
import django
django.setup()

print("=== PRUEBA EN LOCAL ===")

def test_local_api():
    """Probar exactamente como funciona en local"""
    try:
        print("📦 Importando gradio_client...")
        from gradio_client import Client, handle_file
        
        print("🔗 Conectando a SouniQ/Modulo1...")
        client = Client("SouniQ/Modulo1")
        print("✅ Cliente creado exitosamente!")
        
        print("📋 Intentando obtener API info...")
        try:
            api_info = client.view_api()
            print(f"✅ API info obtenida: {len(str(api_info))} caracteres")
            
            # Mostrar endpoints disponibles
            if hasattr(api_info, 'named_endpoints') and api_info.named_endpoints:
                print("🎯 Endpoints disponibles:")
                for endpoint in api_info.named_endpoints:
                    print(f"   - {endpoint}")
            else:
                print("⚠️ No se encontraron endpoints nombrados")
                
        except Exception as e:
            print(f"⚠️ Error obteniendo API info: {e}")
            print("   Esto es normal - el error JSON no impide usar predict()")
        
        print("\n🔍 Probando SouniQ/Modulo2...")
        try:
            client2 = Client("SouniQ/Modulo2") 
            print("✅ Cliente Modulo2 creado exitosamente!")
        except Exception as e:
            print(f"❌ Error con Modulo2: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏠 Ejecutando desde entorno LOCAL")
    success = test_local_api()
    
    if success:
        print("\n✅ RESULTADO: Funciona en local")
        print("📋 Ahora compararemos con el código de producción")
    else:
        print("\n❌ RESULTADO: No funciona en local tampoco")
        print("🔧 Verificar configuración de gradio-client")
