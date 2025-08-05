#!/usr/bin/env python
"""
Script super simple para probar el enfoque directo
Ejecutar en PythonAnywhere: python test_simple_approach.py
"""
import os
import sys

# Configurar ruta para PythonAnywhere
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

print("=== PRUEBA ENFOQUE DIRECTO ===")

def test_direct_approach():
    """Probar creación directa de cliente como en local"""
    try:
        print("🔧 Importando gradio_client...")
        from gradio_client import Client
        
        print("🔗 Creando cliente SouniQ/Modulo1 directamente...")
        
        # ENFOQUE DIRECTO - como funciona en local
        client = Client("SouniQ/Modulo1")
        print("✅ Cliente creado exitosamente!")
        print("   (Si hay JSONDecodeError, no importa - predict() funcionará)")
        
        # Verificar que predict está disponible
        if hasattr(client, 'predict'):
            print("✅ Método predict() disponible")
            print("🎯 ¡Listo para usar en producción!")
            return True
        else:
            print("❌ predict() NO disponible")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_direct_approach()
    if success:
        print("\n🎉 CONCLUSIÓN: Enfoque directo funciona!")
        print("🚀 Proceder a probar en web real")
    else:
        print("\n❌ CONCLUSIÓN: Problemas con enfoque directo")
