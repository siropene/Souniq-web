#!/usr/bin/env python
"""
Script para probar el patch de gradio_client
"""
import json
from types import SimpleNamespace

print("=== PRUEBA DE PATCH GRADIO_CLIENT ===")

def test_patch_approach():
    """Probar el patch de _get_api_info"""
    try:
        print("🔧 Importando gradio_client...")
        from gradio_client import Client
        
        print("🔧 Aplicando patch a _get_api_info...")
        
        # Guardar método original
        original_get_api_info = Client._get_api_info
        
        # Función de reemplazo que no falla con JSONDecodeError
        def patched_get_api_info(self):
            try:
                return original_get_api_info(self)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSONDecodeError capturado en patch: {e}")
                # Retornar estructura mínima que permita usar predict()
                return SimpleNamespace(
                    named_endpoints=['predict'],
                    unnamed_endpoints=[],
                    dependencies=[]
                )
        
        # Aplicar patch
        Client._get_api_info = patched_get_api_info
        
        print("🔗 Creando cliente SouniQ/Modulo1 con patch...")
        try:
            client = Client("SouniQ/Modulo1")
            print("✅ Cliente creado exitosamente con patch!")
            
            # Verificar que predict está disponible
            if hasattr(client, 'predict'):
                print("✅ Método predict() disponible")
                
                # Intentar llamar predict sin argumentos (solo para probar que funciona)
                try:
                    client.predict()
                except Exception as e:
                    if "required argument" in str(e):
                        print("✅ predict() funciona (error esperado por falta de argumentos)")
                    else:
                        print(f"⚠️ Error inesperado en predict(): {e}")
                        
                return True
            else:
                print("❌ predict() NO disponible")
                return False
                
        except Exception as e:
            print(f"❌ Error creando cliente con patch: {e}")
            return False
        finally:
            # Restaurar método original
            Client._get_api_info = original_get_api_info
            print("🔄 Método original restaurado")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    success = test_patch_approach()
    if success:
        print("\n🎉 CONCLUSIÓN: El patch funciona!")
        print("🚀 Aplicar en tasks_sync.py para PythonAnywhere")
    else:
        print("\n❌ CONCLUSIÓN: El patch no resuelve el problema")
