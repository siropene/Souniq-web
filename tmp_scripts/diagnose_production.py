#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el estado de la base de datos en producción
Ejecutar en PythonAnywhere bash console:
cd ~/Souniq-web && source ~/.virtualenvs/souniq-env-new/bin/activate && python tmp_scripts/diagnose_production.py
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/aherrasf/Souniq-web')  # Ajustar para PythonAnywhere
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def diagnose_database():
    """Diagnostica el estado de la base de datos"""
    print("🔍 DIAGNÓSTICO DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Verificar configuración de base de datos
        from django.conf import settings
        db_config = settings.DATABASES['default']
        print(f"📊 Base de datos: {db_config['ENGINE']}")
        print(f"📦 Nombre: {db_config['NAME']}")
        print(f"🌐 Host: {db_config.get('HOST', 'localhost')}")
        
        # Verificar conexión
        cursor = connection.cursor()
        print("✅ Conexión a base de datos exitosa")
        
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'music_processing_generatedtrack';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Tabla 'music_processing_generatedtrack' existe")
            
            # Verificar estructura de la tabla
            cursor.execute("DESCRIBE music_processing_generatedtrack;")
            columns = cursor.fetchall()
            print(f"\n📋 Columnas en la tabla ({len(columns)} total):")
            
            required_columns = [
                'apply_sustains',
                'remove_duplicate_pitches', 
                'remove_overlapping_durations',
                'model_top_p',
                'prime_instruments_json',
                'add_drums',
                'add_outro',
                'num_prime_tokens'
            ]
            
            existing_columns = [col[0] for col in columns]
            
            for col in existing_columns:
                is_new = col in required_columns
                status = "🆕" if is_new else "📄"
                print(f"  {status} {col}")
            
            print(f"\n🔍 Verificando columnas requeridas:")
            missing_columns = []
            for req_col in required_columns:
                if req_col in existing_columns:
                    print(f"  ✅ {req_col}")
                else:
                    print(f"  ❌ {req_col} - FALTA")
                    missing_columns.append(req_col)
            
            if missing_columns:
                print(f"\n⚠️ PROBLEMA: Faltan {len(missing_columns)} columnas:")
                for col in missing_columns:
                    print(f"     - {col}")
                print("\n💡 SOLUCIÓN: Ejecutar migraciones")
            else:
                print("\n✅ Todas las columnas requeridas están presentes")
                
        else:
            print("❌ Tabla 'music_processing_generatedtrack' NO existe")
            
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

def check_migrations():
    """Verifica el estado de las migraciones"""
    print("\n🔄 VERIFICANDO MIGRACIONES")
    print("=" * 50)
    
    try:
        from django.core.management.commands.showmigrations import Command
        from io import StringIO
        import sys
        
        # Capturar output del comando showmigrations
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            command = Command()
            command.handle(app_label=['music_processing'], verbosity=1, settings=None)
            output = mystdout.getvalue()
        finally:
            sys.stdout = old_stdout
            
        print("📋 Estado de migraciones music_processing:")
        print(output)
        
        # Verificar si falta la migración 0005
        if "[ ] 0005_" in output:
            print("⚠️ PROBLEMA: Migración 0005 NO aplicada")
            print("💡 SOLUCIÓN: python manage.py migrate music_processing")
        elif "[X] 0005_" in output:
            print("✅ Migración 0005 aplicada correctamente")
        else:
            print("❓ Estado de migración 0005 unclear")
            
    except Exception as e:
        print(f"❌ Error verificando migraciones: {e}")

def check_model_fields():
    """Verifica que el modelo tenga los campos correctos"""
    print("\n🏗️ VERIFICANDO MODELO")
    print("=" * 50)
    
    try:
        from music_processing.models import GeneratedTrack
        
        # Verificar campos del modelo
        model_fields = [field.name for field in GeneratedTrack._meta.fields]
        print(f"📋 Campos en el modelo ({len(model_fields)} total):")
        
        required_fields = [
            'apply_sustains',
            'remove_duplicate_pitches',
            'remove_overlapping_durations', 
            'model_top_p',
            'prime_instruments_json',
            'add_drums',
            'add_outro',
            'num_prime_tokens'
        ]
        
        for field in required_fields:
            if field in model_fields:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - FALTA EN MODELO")
        
        print(f"\n📄 Todos los campos del modelo:")
        for field in sorted(model_fields):
            print(f"  - {field}")
            
    except Exception as e:
        print(f"❌ Error verificando modelo: {e}")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE PRODUCCIÓN - ORPHEUS MIGRATION")
    print("=" * 60)
    
    diagnose_database()
    check_migrations()  
    check_model_fields()
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DEL DIAGNÓSTICO COMPLETADO")
    print("Si hay columnas faltantes, ejecuta:")
    print("   python manage.py migrate music_processing")
    print("   python manage.py collectstatic --noinput")
    print("Luego reinicia la aplicación web desde el panel de PythonAnywhere")
