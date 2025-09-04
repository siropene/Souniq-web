#!/usr/bin/env python3
"""
Script para corregir stems con 'strings' a 'Clean' en PythonAnywhere

Ejecutar en PythonAnywhere Django shell:
cd ~/Souniq-web
source ~/.virtualenvs/souniq-env-new/bin/activate
python manage.py shell
exec(open('tmp_scripts/fix_stems_strings.py').read())
"""

import os
import sys
import django

# Configurar Django
if not hasattr(django.conf.settings, 'INSTALLED_APPS'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')
    django.setup()

from music_processing.models import Stem

def fix_strings_stems():
    """Corregir stems que tienen 'strings' por 'Clean'"""
    print("🔍 Buscando stems con 'strings'...")
    
    # Buscar stems con 'strings'
    wrong_stems = Stem.objects.filter(stem_type='strings')
    count = wrong_stems.count()
    
    if count == 0:
        print("✅ No hay stems con 'strings' para corregir")
        return
    
    print(f"🔧 Encontrados {count} stems con 'strings'. Corrigiendo...")
    
    # Mostrar algunos ejemplos
    for stem in wrong_stems[:5]:
        print(f"   - Stem ID {stem.id}: {stem.song.title} - {stem.stem_type}")
    
    if count > 5:
        print(f"   ... y {count - 5} más")
    
    # Actualizar todos
    updated = wrong_stems.update(stem_type='Clean')
    print(f"✅ Actualizados {updated} stems de 'strings' a 'Clean'")
    
    # Verificar que no quedan stems con 'strings'
    remaining = Stem.objects.filter(stem_type='strings').count()
    if remaining == 0:
        print("🎉 ¡Corrección completada! Todos los stems ahora usan 'Clean'")
    else:
        print(f"⚠️ Aún quedan {remaining} stems con 'strings'")
    
    return updated

def show_stem_types():
    """Mostrar distribución de tipos de stems"""
    print("\n📊 Distribución actual de tipos de stems:")
    from django.db.models import Count
    
    stem_counts = Stem.objects.values('stem_type').annotate(count=Count('id')).order_by('-count')
    
    for item in stem_counts:
        stem_type = item['stem_type']
        count = item['count']
        
        # Obtener el display name
        try:
            display_name = dict(Stem.STEM_TYPES)[stem_type]
        except KeyError:
            display_name = f"⚠️ TIPO INVÁLIDO: {stem_type}"
        
        print(f"   {stem_type:<10} ({display_name:<15}): {count} stems")

if __name__ == "__main__":
    print("🎵 CORRECCIÓN DE STEMS - STRINGS → CLEAN")
    print("=" * 50)
    
    # Mostrar estado inicial
    show_stem_types()
    
    # Corregir stems
    print("\n🔧 Iniciando corrección...")
    fixed_count = fix_strings_stems()
    
    # Mostrar estado final
    print("\n📊 Estado final:")
    show_stem_types()
    
    print(f"\n✨ Proceso completado. {fixed_count} stems corregidos.")
