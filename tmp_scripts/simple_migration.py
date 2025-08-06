#!/usr/bin/env python3
"""
Script simplificado para aplicar migraciones de Orpheus en producción
Ejecutar en PythonAnywhere bash console:
cd ~/Souniq-web && source ~/.virtualenvs/souniq-env-new/bin/activate && python tmp_scripts/simple_migration.py
"""

import os
import sys
import django

# Configurar Django para PythonAnywhere
sys.path.append('/home/aherrasf/Souniq-web')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection

def apply_migrations():
    """Aplica las migraciones de forma simple"""
    print("🔄 APLICANDO MIGRACIONES SIMPLES")
    print("=" * 50)
    
    try:
        print("1️⃣ Verificando conexión a base de datos...")
        cursor = connection.cursor()
        cursor.execute("SELECT 1;")
        print("✅ Conexión a base de datos exitosa")
        
        print("\n2️⃣ Verificando tabla actual...")
        try:
            cursor.execute("DESCRIBE music_processing_generatedtrack;")
            columns = cursor.fetchall()
            existing_columns = [col[0] for col in columns]
            print(f"📋 Tabla existe con {len(existing_columns)} columnas")
            
            # Verificar columnas específicas que necesitamos
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
            
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"⚠️ Faltan {len(missing_columns)} columnas: {missing_columns}")
            else:
                print("✅ Todas las columnas ya están presentes")
                return True
                
        except Exception as e:
            print(f"❌ Error verificando tabla: {e}")
            return False
        
        print("\n3️⃣ Aplicando migraciones...")
        
        # Usar sys.argv para simular comando manage.py
        old_argv = sys.argv
        try:
            sys.argv = ['manage.py', 'migrate', 'music_processing', '--verbosity=2']
            execute_from_command_line(sys.argv)
            print("✅ Migraciones aplicadas exitosamente")
        except Exception as e:
            print(f"❌ Error aplicando migraciones: {e}")
            return False
        finally:
            sys.argv = old_argv
        
        print("\n4️⃣ Verificando resultado...")
        cursor.execute("DESCRIBE music_processing_generatedtrack;")
        columns = cursor.fetchall()
        existing_columns = [col[0] for col in columns]
        
        final_missing = [col for col in required_columns if col not in existing_columns]
        
        if final_missing:
            print(f"❌ Aún faltan columnas: {final_missing}")
            return False
        else:
            print("✅ Todas las columnas están presentes")
            return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 MIGRACIÓN SIMPLE DE ORPHEUS")
    print("=" * 60)
    
    success = apply_migrations()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("📝 Próximos pasos:")
        print("   1. Reiniciar la aplicación web desde el panel de PythonAnywhere")
        print("   2. Probar la funcionalidad de generación de música")
    else:
        print("❌ MIGRACIÓN FALLÓ")
        print("📝 Ejecuta manualmente:")
        print("   python manage.py migrate music_processing")
