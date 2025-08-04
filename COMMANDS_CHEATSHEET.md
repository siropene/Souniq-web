# Comandos Útiles - SouniQ Web
# ==============================

## 🚀 Inicio Rápido
```bash
cd "/Users/albertoherrastifigueroa/Library/Mobile Documents/com~apple~CloudDocs/Documents/Master/TFM/WEB2"
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=souniq_web.settings_pythonanywhere
export DEBUG=True

# Diagnóstico rápido
./quick_diagnosis.sh

# Iniciar servidor
python manage.py runserver 0.0.0.0:8001
```

## 🔧 Verificar APIs de Hugging Face
```python
# En Django shell
python manage.py shell

from gradio_client import Client

# Ver API de conversión MIDI
client = Client("SouniQ/Modulo2")
print("=== API SouniQ/Modulo2 ===")
print(client.view_api())

# Ver API de generación de canciones  
client = Client("Giant-Music-Transformer")
print("=== API Giant-Music-Transformer ===")
print(client.view_api())
```

## 🎵 Probar Funciones
```python
# En Django shell
from music_processing.models import Song, Stem, MidiFile
from music_processing.tasks_sync import *

# Verificar canción de prueba
song = Song.objects.get(id=13)
print(f"Estado: {song.status}, Stems: {song.stems.count()}")

# Probar conversión MIDI (probablemente falle)
stem = song.stems.first()
try:
    result = convert_stem_to_midi_sync(stem.id)
    print("✅ MIDI:", result)
except Exception as e:
    print("❌ Error MIDI:", e)

# Probar generación (probablemente falle)
if hasattr(stem, 'midi_file'):
    try:
        result = generate_new_track_sync(stem.midi_file.id, {
            'title': 'Test Generation',
            'num_prime_tokens': 512,
            'num_gen_tokens': 1024
        })
        print("✅ Generación:", result)
    except Exception as e:
        print("❌ Error Generación:", e)
```

## 🐛 Depuración de Archivos Cache
```bash
# Si las funciones no se actualizan:
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Reiniciar shell de Django
python manage.py shell
```

## 📊 Verificar Base de Datos
```python
# En Django shell
from music_processing.models import *

# Estadísticas
print(f"Canciones: {Song.objects.count()}")
print(f"Stems: {Stem.objects.count()}")
print(f"MIDI: {MidiFile.objects.count()}")
print(f"Generadas: {GeneratedTrack.objects.count()}")

# Canción de prueba
song = Song.objects.get(id=13)
print(f"\nCanción de prueba:")
print(f"  Título: {song.title}")
print(f"  Estado: {song.status}")
print(f"  Stems: {song.stems.count()}")
for stem in song.stems.all():
    print(f"    - {stem.stem_type}: {stem.file.name}")
```

## 🛠️ Recrear tasks_sync.py (si es necesario)
```bash
# Si el archivo se corrompe de nuevo:
mv music_processing/tasks_sync.py music_processing/tasks_sync_backup.py
# Luego usar el tool create_file para recrear
```

## 🌐 URLs de Prueba
- **Local:** http://localhost:8001
- **Subir canción:** http://localhost:8001/upload/
- **Ver canciones:** http://localhost:8001/songs/
- **Admin:** http://localhost:8001/admin/

## 📝 Log de Errores Comunes
1. **Puerto ocupado:** Usar `pkill -f "manage.py runserver"` 
2. **Funciones no actualizadas:** Borrar cache .pyc
3. **API parámetros:** Verificar con `client.view_api()`
4. **DB locked:** Cerrar otras instancias de Django

## 🎯 Focus para Próxima Sesión
1. **PRIORIDAD 1:** Corregir `convert_stem_to_midi_sync()`
2. **PRIORIDAD 2:** Corregir `generate_new_track_sync()`
3. **PRIORIDAD 3:** Testing completo del flujo
4. **PRIORIDAD 4:** Preparación final para PythonAnywhere
