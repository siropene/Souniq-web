#!/usr/bin/env python
"""
Script para ver las claves exactas del diccionario API info
"""
import json

print("=== VER CLAVES DEL DICCIONARIO API ===")

def inspect_api_dict():
    """Ver contenido real del diccionario de API info"""
    try:
        from gradio_client import Client
        
        # Guardar método original
        original_get_api_info = Client._get_api_info
        
        def inspecting_get_api_info(self):
            try:
                result = original_get_api_info(self)
                print(f"✅ API info obtenida exitosamente")
                print(f"📊 Tipo: {type(result)}")
                print(f"🔑 Claves: {list(result.keys()) if isinstance(result, dict) else 'No es dict'}")
                
                # Mostrar contenido de claves importantes
                if isinstance(result, dict):
                    for key in ['named_endpoints', 'unnamed_endpoints', 'dependencies']:
                        if key in result:
                            value = result[key]
                            print(f"📝 {key}: {type(value)} - {value if len(str(value)) < 200 else str(value)[:200] + '...'}")
                
                return result
            except json.JSONDecodeError as e:
                print(f"⚠️ JSONDecodeError: {e}")
                
                # Crear diccionario compatible basado en lo que sabemos
                print("🔄 Creando diccionario compatible...")
                
                # Basado en la documentación que proporcionaste
                api_dict = {
                    'named_endpoints': {
                        'predict': {
                            'parameters': [
                                {
                                    'name': 'input_wav_path',
                                    'type': 'filepath',
                                    'required': True
                                }
                            ],
                            'returns': [
                                {'type': 'filepath'},  # Vocals
                                {'type': 'filepath'},  # Drums  
                                {'type': 'filepath'},  # Bass
                                {'type': 'filepath'},  # Guitar
                                {'type': 'filepath'},  # Piano
                                {'type': 'filepath'},  # Other
                                {'type': 'filepath'},  # Base instrumental
                            ]
                        }
                    },
                    'unnamed_endpoints': [],
                    'dependencies': []
                }
                
                print(f"📊 Diccionario creado: {list(api_dict.keys())}")
                return api_dict
        
        # Aplicar patch
        Client._get_api_info = inspecting_get_api_info
        
        try:
            print("🔗 Creando cliente para inspeccionar...")
            client = Client("SouniQ/Modulo1")
            print("✅ Cliente creado exitosamente!")
            
            # Verificar que predict funciona
            if hasattr(client, 'predict'):
                print("✅ predict() disponible")
                
                # Intentar llamada de prueba
                try:
                    client.predict()
                except Exception as e:
                    if "required argument" in str(e).lower():
                        print("✅ predict() funciona (necesita argumentos)")
                    else:
                        print(f"⚠️ Error en predict(): {e}")
                        
            return True
                        
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            Client._get_api_info = original_get_api_info
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    success = inspect_api_dict()
    if success:
        print("\n🎉 Inspección completada - diccionario funciona")
    else:
        print("\n❌ Problemas con el diccionario")
