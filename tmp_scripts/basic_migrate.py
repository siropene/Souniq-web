#!/usr/bin/env python3
"""
Script básico para ejecutar migraciones
Ejecutar en PythonAnywhere bash console:
cd ~/Souniq-web && source ~/.virtualenvs/souniq-env-new/bin/activate && python tmp_scripts/basic_migrate.py
"""

import os
import sys

# Configurar el path para PythonAnywhere
sys.path.insert(0, '/home/aherrasf/Souniq-web')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere')

import django
django.setup()

if __name__ == "__main__":
    print("🔄 Ejecutando migraciones básicas...")
    
    try:
        # Importar después de configurar Django
        from django.core.management import call_command
        
        print("📋 Mostrando estado de migraciones...")
        call_command('showmigrations', 'music_processing')
        
        print("\n🚀 Aplicando migraciones...")
        call_command('migrate', 'music_processing', verbosity=2)
        
        print("\n✅ Migraciones completadas")
        
        print("\n📋 Estado final:")
        call_command('showmigrations', 'music_processing')
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
