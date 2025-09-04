#!/usr/bin/env python3
"""
Script Python avanzado para limpieza de archivos de medios en PythonAnywhere
Incluye análisis detallado y opciones de limpieza selectiva

Uso:
cd ~/Souniq-web && source ~/.virtualenvs/souniq-env-new/bin/activate && python tmp_scripts/cleanup_media.py
"""

import os
import sys
import shutil
import datetime
from pathlib import Path
from collections import defaultdict

class MediaCleaner:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.media_path = self.base_path / "media"
        self.stats = {
            'files_deleted': 0,
            'space_freed': 0,
            'errors': 0
        }
        
    def get_file_age_days(self, file_path):
        """Obtener la edad del archivo en días"""
        try:
            mtime = os.path.getmtime(file_path)
            age = (datetime.datetime.now() - datetime.datetime.fromtimestamp(mtime)).days
            return age
        except:
            return 0
    
    def format_size(self, size_bytes):
        """Formatear tamaño en bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def analyze_media_usage(self):
        """Analizar el uso de espacio por directorio"""
        print("📊 ANÁLISIS DE MEDIOS")
        print("=" * 50)
        
        if not self.media_path.exists():
            print("❌ Directorio media/ no encontrado")
            return
        
        dir_sizes = {}
        file_count = defaultdict(int)
        
        for root, dirs, files in os.walk(self.media_path):
            root_path = Path(root)
            total_size = 0
            
            for file in files:
                file_path = root_path / file
                try:
                    size = file_path.stat().st_size
                    total_size += size
                    ext = file_path.suffix.lower()
                    file_count[ext] += 1
                except:
                    continue
            
            if total_size > 0:
                rel_path = root_path.relative_to(self.media_path)
                dir_sizes[str(rel_path)] = total_size
        
        # Mostrar resumen por directorio
        print("\n📁 Uso por directorio:")
        for dir_name, size in sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True):
            print(f"   {dir_name:<20} : {self.format_size(size)}")
        
        # Mostrar resumen por tipo de archivo
        print("\n📄 Archivos por tipo:")
        for ext, count in sorted(file_count.items(), key=lambda x: x[1], reverse=True):
            if ext:
                print(f"   {ext:<10} : {count} archivos")
        
        return dir_sizes
    
    def clean_directory(self, dir_path, extensions, days_old, description):
        """Limpiar un directorio específico"""
        dir_full_path = self.media_path / dir_path
        
        if not dir_full_path.exists():
            print(f"   ⚠️ {dir_path} no existe")
            return
        
        files_found = []
        total_size = 0
        
        for ext in extensions:
            pattern = f"*{ext}"
            for file_path in dir_full_path.rglob(pattern):
                if file_path.is_file():
                    age = self.get_file_age_days(file_path)
                    if age >= days_old:
                        try:
                            size = file_path.stat().st_size
                            files_found.append((file_path, size, age))
                            total_size += size
                        except:
                            continue
        
        if not files_found:
            print(f"   ✅ No hay {description} antiguos para eliminar")
            return
        
        print(f"   🔍 Encontrados {len(files_found)} {description} (>{days_old} días) - {self.format_size(total_size)}")
        
        # Mostrar algunos ejemplos
        print("   📝 Ejemplos:")
        for file_path, size, age in files_found[:3]:
            print(f"      - {file_path.name} ({self.format_size(size)}, {age} días)")
        
        if len(files_found) > 3:
            print(f"      ... y {len(files_found) - 3} más")
        
        # Confirmar eliminación
        response = input(f"   ❓ ¿Eliminar estos {len(files_found)} archivos? (y/N): ").lower()
        
        if response == 'y':
            deleted_count = 0
            deleted_size = 0
            
            for file_path, size, age in files_found:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += size
                    self.stats['files_deleted'] += 1
                    self.stats['space_freed'] += size
                except Exception as e:
                    print(f"      ❌ Error eliminando {file_path.name}: {e}")
                    self.stats['errors'] += 1
            
            print(f"   ✅ Eliminados {deleted_count} archivos - {self.format_size(deleted_size)} liberados")
        else:
            print("   ⏭️ Saltando eliminación")
    
    def clean_empty_directories(self):
        """Eliminar directorios vacíos"""
        print("\n🗂️ Limpiando directorios vacíos...")
        
        empty_dirs = []
        for root, dirs, files in os.walk(self.media_path, topdown=False):
            if not dirs and not files:
                empty_dirs.append(root)
        
        if empty_dirs:
            print(f"   🔍 Encontrados {len(empty_dirs)} directorios vacíos")
            for dir_path in empty_dirs:
                try:
                    os.rmdir(dir_path)
                    print(f"   🗑️ Eliminado: {Path(dir_path).relative_to(self.media_path)}")
                except:
                    pass
        else:
            print("   ✅ No hay directorios vacíos")
    
    def run_cleanup(self):
        """Ejecutar limpieza completa"""
        print("🧹 LIMPIEZA AVANZADA DE MEDIOS - SOUNIQ")
        print("=" * 50)
        print(f"📍 Directorio base: {self.base_path.absolute()}")
        print(f"🗓️ Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verificar que estamos en el lugar correcto
        if not (self.base_path / "manage.py").exists():
            print("❌ Error: No se encuentra manage.py. Ejecuta desde el directorio del proyecto.")
            sys.exit(1)
        
        # Análisis inicial
        self.analyze_media_usage()
        
        print("\n🚀 INICIANDO LIMPIEZA SELECTIVA")
        print("=" * 50)
        
        # 1. Stems (archivos de separación de audio)
        print("\n1️⃣ Limpiando stems generados...")
        self.clean_directory(
            "stems", 
            [".wav", ".mp3", ".flac"], 
            7, 
            "stems generados"
        )
        
        # 2. Tracks generados
        print("\n2️⃣ Limpiando tracks generados...")
        self.clean_directory(
            "generated_tracks", 
            [".mid", ".wav", ".mp3"], 
            7, 
            "tracks generados"
        )
        
        # 3. Archivos MIDI
        print("\n3️⃣ Limpiando archivos MIDI...")
        self.clean_directory(
            "midi", 
            [".mid", ".midi"], 
            7, 
            "archivos MIDI"
        )
        
        # 4. Canciones subidas (más conservador)
        print("\n4️⃣ Limpiando canciones subidas por usuarios...")
        self.clean_directory(
            "songs", 
            [".mp3", ".wav", ".flac", ".m4a"], 
            14, 
            "canciones subidas"
        )
        
        # 5. Directorios vacíos
        self.clean_empty_directories()
        
        # Resumen final
        print("\n✅ LIMPIEZA COMPLETADA")
        print("=" * 50)
        print(f"📊 Archivos eliminados: {self.stats['files_deleted']}")
        print(f"💾 Espacio liberado: {self.format_size(self.stats['space_freed'])}")
        print(f"❌ Errores: {self.stats['errors']}")
        
        if self.stats['space_freed'] > 0:
            print(f"\n🎉 ¡Excelente! Se liberaron {self.format_size(self.stats['space_freed'])} de espacio")

def main():
    """Función principal"""
    cleaner = MediaCleaner()
    
    # Opción de solo análisis
    if len(sys.argv) > 1 and sys.argv[1] == "--analyze":
        print("🔍 MODO ANÁLISIS - Solo mostrando información")
        print("=" * 50)
        cleaner.analyze_media_usage()
        return
    
    # Limpieza completa
    cleaner.run_cleanup()
    
    print("\n💡 CONSEJOS:")
    print("   - Ejecuta 'python tmp_scripts/cleanup_media.py --analyze' para solo ver el análisis")
    print("   - Ejecuta este script regularmente para mantener el espacio optimizado")
    print("   - Los archivos eliminados no se pueden recuperar")

if __name__ == "__main__":
    main()
