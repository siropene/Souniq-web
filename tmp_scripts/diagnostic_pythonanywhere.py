#!/usr/bin/env python
"""
Script de diagnóstico para PythonAnywhere
Ejecutar en la consola de PythonAnywhere para verificar configuración
"""
import os
import sys

# Configurar path y settings como en WSGI
path = '/home/aherrasf/souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere')

print("=== DIAGNÓSTICO SOUNIQ PYTHONANYWHERE ===")
print(f"Python path: {sys.path[:3]}...")
print(f"Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

try:
    # Importar Django settings
    from django.conf import settings
    print(f"✅ Django settings importado correctamente")
    print(f"✅ DEBUG: {settings.DEBUG}")
    print(f"✅ INSTALLED_APPS contiene {len(settings.INSTALLED_APPS)} apps:")
    
    for app in settings.INSTALLED_APPS:
        mark = "✅" if "crispy" in app else "  "
        print(f"   {mark} {app}")
    
    # Verificar crispy forms específicamente
    if 'crispy_forms' in settings.INSTALLED_APPS:
        print("\n✅ crispy_forms está en INSTALLED_APPS")
    else:
        print("\n❌ crispy_forms NO está en INSTALLED_APPS")
        
    if 'crispy_bootstrap5' in settings.INSTALLED_APPS:
        print("✅ crispy_bootstrap5 está en INSTALLED_APPS")
    else:
        print("❌ crispy_bootstrap5 NO está en INSTALLED_APPS")
        
    # Probar importación directa
    try:
        import crispy_forms
        print(f"✅ crispy_forms importado correctamente - versión: {crispy_forms.__version__}")
    except ImportError as e:
        print(f"❌ Error importando crispy_forms: {e}")
        
    try:
        import crispy_bootstrap5
        print(f"✅ crispy_bootstrap5 importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando crispy_bootstrap5: {e}")
        
    # Verificar configuración crispy
    if hasattr(settings, 'CRISPY_TEMPLATE_PACK'):
        print(f"✅ CRISPY_TEMPLATE_PACK: {settings.CRISPY_TEMPLATE_PACK}")
    else:
        print("❌ CRISPY_TEMPLATE_PACK no configurado")

except Exception as e:
    print(f"❌ Error general: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIN DIAGNÓSTICO ===")
