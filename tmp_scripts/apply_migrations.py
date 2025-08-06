#!/usr/bin/env python3
"""
Script simple para verificar y aplicar migraciones en PythonAnywhere
"""

import os
import sys

# Configurar el path para PythonAnywhere
sys.path.insert(0, '/home/aherrasf/Souniq-web')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere')

import django
django.setup()

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    print("🔄 Aplicando migraciones en PythonAnywhere...")
    
    # Ejecutar las migraciones
    try:
        execute_from_command_line(['manage.py', 'migrate', 'music_processing'])
        print("✅ Migraciones aplicadas exitosamente")
    except Exception as e:
        print(f"❌ Error: {e}")
