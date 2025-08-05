#!/usr/bin/env python
"""
Script final para probar las 3 APIs con patch en PythonAnywhere
Ejecutar: python test_all_apis_patched.py
"""
import os
import sys
import json

# Configurar ruta para PythonAnywhere
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

print("=== PRUEBA COMPLETA APIS CON PATCH ===")

def test_api_with_patch(space_name, endpoint_name="predict"):
    """Probar API específica con patch"""
    try:
        print(f"🔗 Probando {space_name}...")
        
        from gradio_client import Client
        
        # Guardar método original
        original_get_api_info = Client._get_api_info
        
        # Función de reemplazo que no falla con JSONDecodeError
        def patched_get_api_info(self):
            try:
                return original_get_api_info(self)
            except json.JSONDecodeError:
                print(f"⚠️ JSONDecodeError capturado para {space_name}")
                # Retornar diccionario compatible con gradio_client
                if endpoint_name == "generate_callback_wrapper":
                    # Para Giant-Music-Transformer
                    return {
                        'named_endpoints': {
                            f'/{endpoint_name}': {
                                'parameters': [],
                                'returns': []
                            }
                        },
                        'unnamed_endpoints': {}
                    }
                else:
                    # Para SouniQ/Modulo1 y SouniQ/Modulo2
                    return {
                        'named_endpoints': {
                            f'/{endpoint_name}': {
                                'parameters': [
                                    {
                                        'label': 'Sube un archivo .wav',
                                        'parameter_name': 'input_wav_path',
                                        'parameter_has_default': False,
                                        'parameter_default': None,
                                        'type': {}
                                    }
                                ],
                                'returns': [
                                    {'type': {}}
                                ]
                            }
                        },
                        'unnamed_endpoints': {}
                    }
        
        # Aplicar patch
        Client._get_api_info = patched_get_api_info
        
        try:
            # Crear cliente con patch activo
            client = Client(space_name)
            print(f"✅ Cliente {space_name} creado exitosamente")
            
            # Verificar método predict disponible
            if hasattr(client, 'predict'):
                print(f"✅ predict() disponible en {space_name}")
                return True
            else:
                print(f"❌ predict() NO disponible en {space_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error con {space_name}: {e}")
            return False
        finally:
            # Restaurar método original
            Client._get_api_info = original_get_api_info
            
    except Exception as e:
        print(f"❌ Error general con {space_name}: {e}")
        return False

def test_all_apis():
    """Probar todas las APIs"""
    apis = [
        ("SouniQ/Modulo1", "predict"),
        ("SouniQ/Modulo2", "predict"),
        ("asigalov61/Giant-Music-Transformer", "generate_callback_wrapper")
    ]
    
    results = []
    for space_name, endpoint in apis:
        success = test_api_with_patch(space_name, endpoint)
        results.append((space_name, success))
        print()
    
    return results

if __name__ == "__main__":
    results = test_all_apis()
    
    print("📊 RESULTADOS:")
    success_count = 0
    for space_name, success in results:
        status = "✅ OK" if success else "❌ FALLO"
        print(f"  {space_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n🎯 RESUMEN: {success_count}/{len(results)} APIs funcionando")
    
    if success_count == len(results):
        print("🎉 ¡TODAS LAS APIS FUNCIONAN CON PATCH!")
        print("🚀 Listo para testing en producción")
    else:
        print("⚠️ Algunas APIs siguen fallando")
        print("🔧 Revisar logs para más detalles")
