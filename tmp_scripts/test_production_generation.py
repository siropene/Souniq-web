#!/usr/bin/env python
"""
Script para probar el pipeline completo de generación
"""
import os
import sys

# Configurar Django
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')

import django
django.setup()

def test_production_generation():
    """Probar generación en producción con valores reales"""
    print("=== PRUEBA DE GENERACIÓN EN PRODUCCIÓN ===")
    
    try:
        from music_processing.models import GeneratedTrack, MidiFile
        from music_processing.tasks_sync import generate_new_track_sync
        
        # Buscar un GeneratedTrack listo para generar
        generated_track = GeneratedTrack.objects.filter(
            status__in=['pending', 'error'],
            midi_file__isnull=False
        ).first()
        
        if not generated_track:
            print("❌ No hay GeneratedTrack disponible para probar")
            print("💡 Crea uno desde la interfaz web primero")
            return
        
        print(f"📝 Track encontrado: {generated_track.title}")
        print(f"🎵 MIDI: {generated_track.midi_file.file.name}")
        print(f"🔧 Parámetros:")
        print(f"   - num_prime_tokens: {generated_track.num_prime_tokens}")
        print(f"   - num_gen_tokens: {generated_track.num_gen_tokens}")
        print(f"   - num_mem_tokens: {generated_track.num_mem_tokens}")
        print(f"   - gen_outro: {generated_track.gen_outro}")
        print(f"   - gen_drums: {generated_track.gen_drums}")
        print(f"   - temperature: {generated_track.model_temperature}")
        print(f"   - sampling_top_p: {generated_track.model_sampling_top_p}")
        
        print("\n🚀 Iniciando generación...")
        result = generate_new_track_sync(generated_track.id)
        
        print(f"\n📊 Resultado:")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   Versions created: {result.get('versions_created', 0)}")
        
        if result['status'] == 'success':
            print("\n✅ ¡GENERACIÓN EXITOSA!")
            print("🎉 El pipeline completo está funcionando")
            
            # Mostrar versiones creadas
            generated_track.refresh_from_db()
            versions = generated_track.generated_versions.all()  # Usar 'generated_versions'
            print(f"\n📁 Versiones generadas ({len(versions)}):")
            for version in versions:
                print(f"   - Versión {version.version_number}: {version.file.name}")
        else:
            print(f"\n❌ Error en generación: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_production_generation()
