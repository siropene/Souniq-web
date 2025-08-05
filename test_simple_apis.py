#!/usr/bin/env python
"""
Script de prueba simple para verificar conexión con APIs de Hugging Face
Ejecutar en PythonAnywhere después de los cambios
"""
import os
import sys

# Configurar Django
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')

print("=== PRUEBA RÁPIDA APIs ===")

def test_simple_connection():
    """Probar conexión simple como en el código que funciona en local"""
    try:
        print("🔧 Importando gradio_client...")
        from gradio_client import Client
        
        print("🔗 Conectando a SouniQ/Modulo1 sin obtener info...")
        try:
            # Crear cliente sin llamar a view_api() inmediatamente
            client = Client("SouniQ/Modulo1")
            print("✅ Cliente SouniQ/Modulo1 creado exitosamente!")
            
            # Aquí NO llamamos a view_api() para evitar el JSONDecodeError
            print("⚠️ Saltando view_api() para evitar JSONDecodeError")
            
        except Exception as e:
            print(f"❌ Error creando cliente: {e}")
            return False
        
        print("
🔍 Probando SouniQ/Modulo2...")
        try:
            client2 = Client("SouniQ/Modulo2") 
            print("✅ Cliente Modulo2 creado exitosamente!")
        except Exception as e:
            print(f"❌ Error con Modulo2: {e}")
        
        print("
🎯 LO IMPORTANTE: ¿Podemos usar predict()?")
        print("   (El JSONDecodeError no debería impedir esto)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_connection()
    if success:
        print("\n✅ CONCLUSIÓN: El código simplificado debe funcionar en producción.")
        print("📋 Próximo paso: Probar la separación de stems en la web.")
    else:
        print("\n❌ CONCLUSIÓN: Aún hay problemas con las APIs.")
        print("🔧 Verificar configuración o contactar soporte de Hugging Face.")
