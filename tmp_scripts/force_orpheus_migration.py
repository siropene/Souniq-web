#!/usr/bin/env python3
"""
Script para aplicar migraciones de Orpheus en producción
Ejecutar en PythonAnywhere bash console:
cd ~/Souniq-web && source ~/.virtualenvs/souniq-env-new/bin/activate && python tmp_scripts/force_orpheus_migration.py
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

def check_and_apply_migrations():
    """Verifica y aplica las migraciones necesarias"""
    print("🔄 APLICANDO MIGRACIONES DE ORPHEUS")
    print("=" * 50)
    
    try:
        # 1. Verificar estado actual
        print("1️⃣ Verificando estado actual de migraciones...")
        from django.core.management.commands.showmigrations import Command
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            command = Command()
            command.handle(app_label=['music_processing'], verbosity=1, settings=None)
            migration_output = mystdout.getvalue()
        finally:
            sys.stdout = old_stdout
            
        print(migration_output)
        
        # 2. Verificar si necesitamos migrar
        needs_migration = "[ ]" in migration_output or "0005_" not in migration_output
        
        if needs_migration:
            print("2️⃣ Aplicando migraciones necesarias...")
            
            # Aplicar migraciones específicas
            try:
                execute_from_command_line(['manage.py', 'migrate', 'music_processing', '--verbosity=2'])
                print("✅ Migraciones aplicadas exitosamente")
            except Exception as e:
                print(f"⚠️ Error en migrate: {e}")
                
                # Intentar migrar específicamente la 0005
                print("🔄 Intentando aplicar migración 0005 específicamente...")
                try:
                    execute_from_command_line(['manage.py', 'migrate', 'music_processing', '0005', '--verbosity=2'])
                    print("✅ Migración 0005 aplicada exitosamente")
                except Exception as e2:
                    print(f"❌ Error aplicando migración 0005: {e2}")
                    return False
        else:
            print("✅ Las migraciones ya están aplicadas")
        
        # 3. Verificar resultado final
        print("\n3️⃣ Verificando resultado final...")
        cursor = connection.cursor()
        cursor.execute("DESCRIBE music_processing_generatedtrack;")
        columns = cursor.fetchall()
        existing_columns = [col[0] for col in columns]
        
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
            print(f"❌ Aún faltan columnas: {missing_columns}")
            
            # Intentar crear columnas manualmente
            print("🔧 Intentando crear columnas faltantes manualmente...")
            manual_sql_commands = {
                'apply_sustains': 'ALTER TABLE music_processing_generatedtrack ADD COLUMN apply_sustains BOOLEAN NOT NULL DEFAULT 1;',
                'remove_duplicate_pitches': 'ALTER TABLE music_processing_generatedtrack ADD COLUMN remove_duplicate_pitches BOOLEAN NOT NULL DEFAULT 1;', 
                'remove_overlapping_durations': 'ALTER TABLE music_processing_generatedtrack ADD COLUMN remove_overlapping_durations BOOLEAN NOT NULL DEFAULT 1;',
                'model_top_p': 'ALTER TABLE music_processing_generatedtrack ADD COLUMN model_top_p DOUBLE NOT NULL DEFAULT 0.96;',
                'prime_instruments_json': 'ALTER TABLE music_processing_generatedtrack ADD COLUMN prime_instruments_json LONGTEXT;',
                'add_drums': 'ALTER TABLE music_processing_generatedtrack ADD COLUMN add_drums BOOLEAN NOT NULL DEFAULT 0;',
                'add_outro': 'ALTER TABLE music_processing_generatedtrack ADD COLUMN add_outro BOOLEAN NOT NULL DEFAULT 0;',
                'num_prime_tokens': 'ALTER TABLE music_processing_generatedtrack ADD COLUMN num_prime_tokens INTEGER NOT NULL DEFAULT 6656;'
            }
            
            for col in missing_columns:
                if col in manual_sql_commands:
                    try:
                        print(f"  🔧 Creando columna {col}...")
                        cursor.execute(manual_sql_commands[col])
                        print(f"  ✅ Columna {col} creada")
                    except Exception as e:
                        print(f"  ❌ Error creando {col}: {e}")
                        
            # Verificar nuevamente
            cursor.execute("DESCRIBE music_processing_generatedtrack;")
            columns = cursor.fetchall()
            existing_columns = [col[0] for col in columns]
            final_missing = [col for col in required_columns if col not in existing_columns]
            
            if final_missing:
                print(f"❌ Aún faltan columnas después del fix manual: {final_missing}")
                return False
            else:
                print("✅ Todas las columnas creadas exitosamente")
        else:
            print("✅ Todas las columnas requeridas están presentes")
            
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 MIGRACIÓN FORZADA DE ORPHEUS")
    print("=" * 60)
    
    success = check_and_apply_migrations()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("📝 Próximos pasos:")
        print("   1. Reiniciar la aplicación web desde el panel de PythonAnywhere")
        print("   2. Probar la funcionalidad de generación de música")
        print("   3. Verificar que no hay más errores en los logs")
    else:
        print("❌ MIGRACIÓN FALLÓ")
        print("📝 Acciones recomendadas:")
        print("   1. Ejecutar manualmente: python manage.py migrate music_processing --verbosity=2")
        print("   2. Verificar permisos de base de datos")
        print("   3. Contactar soporte de PythonAnywhere si persiste")
