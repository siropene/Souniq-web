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
        
        print("🔗 Conectando a SouniQ/Modulo1...")
        client = Client("SouniQ/Modulo1")
        print("✅ Cliente SouniQ/Modulo1 creado exitosamente!")
        
        print("🔗 Conectando a SouniQ/Modulo2...")  
        client2 = Client("SouniQ/Modulo2")
        print("✅ Cliente SouniQ/Modulo2 creado exitosamente!")
        
        print("\n🎉 AMBAS APIs FUNCIONAN! El código simple es correcto.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_connection()
    if success:
        print("\n✅ CONCLUSIÓN: El código simplificado debe funcionar en producción.")
        print("📋 Próximo paso: Probar la separación de stems en la web.")
    else:
        print("\n❌ CONCLUSIÓN: Aún hay problemas con las APIs.")
        print("🔧 Verificar configuración o contactar soporte de Hugging Face.")
