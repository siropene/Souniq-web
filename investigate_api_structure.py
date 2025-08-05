#!/usr/bin/env python
"""
Script para investigar la estructura real de la API info
"""
import json
from types import SimpleNamespace

print("=== INVESTIGAR ESTRUCTURA API INFO ===")

def investigate_api_structure():
    """Investigar qué estructura necesita gradio_client"""
    try:
        from gradio_client import Client
        
        print("🔍 Intentando obtener estructura real de una API que funciona...")
        
        # Guardar método original
        original_get_api_info = Client._get_api_info
        
        # Variable para capturar la estructura real
        real_structure = None
        
        def capturing_get_api_info(self):
            nonlocal real_structure
            try:
                result = original_get_api_info(self)
                real_structure = result
                print(f"✅ Estructura real capturada: {type(result)}")
                print(f"📋 Atributos: {dir(result)}")
                
                # Si es un objeto con atributos, mostrar algunos
                if hasattr(result, '__dict__'):
                    print(f"📝 __dict__: {result.__dict__}")
                
                return result
            except json.JSONDecodeError as e:
                print(f"⚠️ JSONDecodeError: {e}")
                
                # Si tenemos estructura real previa, usar esa
                if real_structure:
                    print("🔄 Usando estructura real capturada anteriormente")
                    return real_structure
                
                # Si no, intentar estructura mínima compatible
                print("🔄 Usando estructura mínima compatible")
                
                # Crear estructura que imite la real
                class APIInfo:
                    def __init__(self):
                        self.named_endpoints = {'predict': {'parameters': [], 'returns': []}}
                        self.unnamed_endpoints = []
                        self.dependencies = []
                    
                    def __getitem__(self, key):
                        return getattr(self, key, None)
                
                return APIInfo()
        
        # Aplicar patch investigativo
        Client._get_api_info = capturing_get_api_info
        
        try:
            # Intentar con una API que sabemos que funciona en local
            print("🔗 Probando con SouniQ/Modulo1...")
            client = Client("SouniQ/Modulo1")
            print("✅ Cliente creado!")
            
            # Mostrar información del cliente
            if hasattr(client, '_info'):
                print(f"📊 Tipo _info: {type(client._info)}")
                if hasattr(client._info, '__dict__'):
                    print(f"📝 _info.__dict__: {client._info.__dict__}")
                    
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            # Restaurar método original
            Client._get_api_info = original_get_api_info
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    success = investigate_api_structure()
    if success:
        print("\n🎉 Investigación completada")
    else:
        print("\n❌ Falló la investigación")
