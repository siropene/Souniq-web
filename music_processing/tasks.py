from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings
from gradio_client import Client, handle_file
import tempfile
import os
import logging
import requests
import zipfile
from .models import Song, Stem, MidiFile, GeneratedTrack, ProcessingTask

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_song_to_stems(self, song_id):
    """
    Tarea para procesar una canción y generar sus stems usando la API de Hugging Face
    """
    import time
    task = None
    
    try:
        song = Song.objects.get(id=song_id)
        # Usar filter().first() en lugar de get() para evitar MultipleObjectsReturned
        task = ProcessingTask.objects.filter(
            song=song, 
            task_type='stem_generation',
            status__in=['pending', 'in_progress']
        ).first()
        
        if not task:
            logger.error(f"No se encontró tarea pendiente para la canción {song_id}")
            return
        
        # Actualizar estado
        task.status = 'in_progress'
        task.started_at = timezone.now()
        task.save()
        
        song.status = 'processing_stems'
        song.save()
        
        # Inicializar el cliente de Hugging Face para separación de stems
        logger.info(f"Iniciando separación de stems para canción {song_id}")
        self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': 'Conectando con Hugging Face...'})
        
        try:
            # Usar el espacio público de Hugging Face para separación de stems
            # No requiere token ya que es un espacio público
            logger.info("Conectando con el espacio de Hugging Face...")
            
            client = Client("SouniQ/Modulo1")
            logger.info("Cliente de Hugging Face creado exitosamente")
            
            self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Preparando archivo de audio...'})
            
            # Crear archivo temporal con el audio original
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                # Copiar el contenido del archivo original al temporal
                song.original_file.seek(0)
                temp_file.write(song.original_file.read())
                temp_audio_path = temp_file.name
            
            logger.info(f"Archivo temporal creado: {temp_audio_path} (tamaño: {os.path.getsize(temp_audio_path)} bytes)")
            
            self.update_state(state='PROGRESS', meta={'current': 30, 'total': 100, 'status': 'Enviando a espacio público de Hugging Face...'})
            
            # Procesar con el espacio público de Hugging Face usando el parámetro correcto
            result = client.predict(
                input_wav_path=handle_file(temp_audio_path),
                api_name="/predict"
            )
            
            logger.info(f"Resultado de Hugging Face: {result}")
            
            self.update_state(state='PROGRESS', meta={'current': 70, 'total': 100, 'status': 'Procesando stems separados...'})
            
            # El resultado es una tupla con múltiples archivos de stems separados
            if result and isinstance(result, tuple) and len(result) > 0:
                # Procesar cada archivo de stem individualmente
                stems_created = process_stems_from_files(result, song, self)
                
                logger.info(f"Stems creados: {stems_created}")
            else:
                raise Exception("El espacio de Hugging Face no devolvió resultados válidos. El servicio puede estar temporalmente inactivo.")
                
        except Exception as api_error:
            logger.error(f"Error con espacio público de Hugging Face: {str(api_error)}")
            
            # Error controlado: El espacio no está disponible
            error_message = f"El espacio de Hugging Face no está disponible actualmente: {str(api_error)}"
            
            # Actualizar estados de error
            song.status = 'error'
            song.save()
            
            task.status = 'failed'
            task.error_message = error_message
            task.save()
            
            # Lanzar excepción para que Celery la registre
            raise Exception(error_message)
        
        finally:
            # Limpiar archivo temporal
            if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
        
        # Actualizar estados finales
        song.status = 'stems_completed'
        song.save()
        
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.progress_percentage = 100
        task.save()
        
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'status': 'Completado'})
        
        return {'status': 'success', 'stems_created': stems_created}
        
    except Exception as e:
        logger.error(f"Error procesando canción {song_id}: {str(e)}")
        
        # Actualizar estados de error
        try:
            song = Song.objects.get(id=song_id)
            song.status = 'error'
            song.save()
        except:
            pass
        
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
        
        raise


def process_stems_from_files(stem_files, song, task_instance):
    """
    Procesa los stems desde archivos individuales del espacio público de Hugging Face
    """
    stems_created = 0
    
    # Mapeo de archivos esperados a tipos de stem basado en los nombres de los archivos
    stem_mapping = {
        'vocals': 'vocals',
        'drums': 'drums', 
        'bass': 'bass',
        'guitar': 'guitar',
        'piano': 'piano',
        'other': 'other',
        'instrumental': 'other',  # base_instrumental_clean.wav -> other
    }
    
    try:
        logger.info(f"Procesando {len(stem_files)} archivos de stems")
        
        for i, stem_file_path in enumerate(stem_files):
            if not stem_file_path or not os.path.exists(stem_file_path):
                logger.warning(f"Archivo de stem no encontrado: {stem_file_path}")
                continue
                
            # Extraer el nombre del archivo para determinar el tipo de stem
            filename = os.path.basename(stem_file_path).lower()
            logger.info(f"Procesando archivo: {filename}")
            
            # Determinar el tipo de stem basado en el nombre del archivo
            stem_type = 'other'  # default
            for key, value in stem_mapping.items():
                if key in filename:
                    stem_type = value
                    break
            
            # Crear el objeto Stem
            stem = Stem.objects.create(
                song=song,
                stem_type=stem_type,
                order=stems_created
            )
            
            # Guardar el archivo del stem
            filename_clean = f"{song.title}_stem_{stems_created + 1}_{stem_type}.wav"
            
            with open(stem_file_path, 'rb') as stem_file:
                stem.file.save(filename_clean, ContentFile(stem_file.read()))
            
            # Crear el objeto MidiFile para futura conversión
            MidiFile.objects.create(stem=stem)
            
            stems_created += 1
            
            # Actualizar progreso
            progress = 70 + (stems_created * 3)
            task_instance.update_state(
                state='PROGRESS', 
                meta={'current': min(progress, 95), 'total': 100, 'status': f'Procesando stem {stem_type}...'}
            )
            
            logger.info(f"Stem {stem_type} creado exitosamente")
            
    except Exception as e:
        logger.error(f"Error procesando stems desde archivos: {str(e)}")
        # Si hay error procesando los archivos, lanzar excepción en lugar de crear stems simulados
        raise Exception(f"Error procesando los stems del espacio de Hugging Face: {str(e)}")
    
    return stems_created


def process_stems_from_zip(zip_path, song, task_instance):
    """
    Procesa los stems desde un archivo ZIP del espacio público de Hugging Face
    """
    stems_created = 0
    
    # Mapeo de archivos esperados a tipos de stem
    stem_mapping = {
        'drums.wav': 'drums',
        'bass.wav': 'bass',
        'other.wav': 'other',
        'vocals.wav': 'vocals',
    }
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            temp_dir = tempfile.mkdtemp()
            zip_ref.extractall(temp_dir)
            
            # Buscar archivos de stems en el directorio extraído
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith('.wav'):
                        # Determinar el tipo de stem basado en el nombre del archivo
                        stem_type = None
                        for key, value in stem_mapping.items():
                            if key.lower() in file.lower():
                                stem_type = value
                                break
                        
                        if not stem_type:
                            # Si no se reconoce, usar 'other'
                            stem_type = 'other'
                        
                        # Crear el objeto Stem
                        stem = Stem.objects.create(
                            song=song,
                            stem_type=stem_type,
                            order=stems_created
                        )
                        
                        # Guardar el archivo del stem
                        file_path = os.path.join(root, file)
                        filename = f"{song.title}_stem_{stems_created + 1}_{stem_type}.wav"
                        
                        with open(file_path, 'rb') as stem_file:
                            stem.file.save(filename, ContentFile(stem_file.read()))
                        
                        # Crear el objeto MidiFile para futura conversión
                        MidiFile.objects.create(stem=stem)
                        
                        stems_created += 1
                        
                        # Actualizar progreso
                        progress = 70 + (stems_created * 5)
                        task_instance.update_state(
                            state='PROGRESS', 
                            meta={'current': min(progress, 95), 'total': 100, 'status': f'Procesando stem {stem_type}...'}
                        )
            
            # Limpiar directorio temporal
            import shutil
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        logger.error(f"Error procesando stems desde ZIP: {str(e)}")
        # Si hay error procesando el ZIP, lanzar excepción en lugar de crear stems simulados
        raise Exception(f"Error procesando los stems del espacio de Hugging Face: {str(e)}")
    
    return stems_created


@shared_task(bind=True)
def convert_stem_to_midi(self, stem_id):
    """
    Tarea para convertir un stem a MIDI usando la API de Hugging Face
    """
    try:
        stem = Stem.objects.get(id=stem_id)
        midi_file = MidiFile.objects.get(stem=stem)
        task = ProcessingTask.objects.get(stem=stem, task_type='midi_conversion')
        
        # Actualizar estado
        midi_file.status = 'processing'
        midi_file.save()
        
        task.status = 'in_progress'
        task.started_at = timezone.now()
        task.save()
        
        # Conectar con la API de conversión a MIDI
        client = Client("SouniQ/Modulo2")
        
        # Preparar el archivo de audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            for chunk in stem.file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Llamar a la API
            self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100})
            
            result = client.predict(
                input_wav_path=handle_file(temp_file_path),
                api_name="/predict"
            )
            
            # El resultado debería ser la ruta del archivo MIDI
            if os.path.exists(result):
                with open(result, 'rb') as f:
                    midi_content = f.read()
                
                filename = f"{stem.song.title}_{stem.get_stem_type_display()}.mid"
                midi_file.file.save(filename, ContentFile(midi_content))
                midi_file.status = 'completed'
                midi_file.completed_at = timezone.now()
                midi_file.save()
                
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.progress_percentage = 100
                task.save()
            else:
                raise Exception("No se pudo generar el archivo MIDI")
                
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        return {'status': 'success', 'midi_file': midi_file.file.url}
        
    except Exception as e:
        logger.error(f"Error convirtiendo stem {stem_id} a MIDI: {str(e)}")
        
        midi_file.status = 'error'
        midi_file.error_message = str(e)
        midi_file.save()
        
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        
        raise


@shared_task(bind=True)
def generate_new_track(self, generated_track_id):
    """
    Tarea para generar una nueva canción a partir de un archivo MIDI
    """
    try:
        generated_track = GeneratedTrack.objects.get(id=generated_track_id)
        task = ProcessingTask.objects.get(generated_track=generated_track, task_type='track_generation')
        
        # Actualizar estado
        generated_track.status = 'processing'
        generated_track.save()
        
        task.status = 'in_progress'
        task.started_at = timezone.now()
        task.save()
        
        # Conectar con la API de generación de música
        client = Client("asigalov61/Giant-Music-Transformer")
        
        # Preparar el archivo MIDI
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as temp_file:
            for chunk in generated_track.midi_file.file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Llamar a la API con los parámetros configurados
            self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100})
            
            result = client.predict(
                input_midi=handle_file(temp_file_path),
                num_prime_tokens=generated_track.num_prime_tokens,
                num_gen_tokens=generated_track.num_gen_tokens,
                num_mem_tokens=generated_track.num_mem_tokens,
                gen_outro=generated_track.gen_outro,
                gen_drums=generated_track.gen_drums,
                model_temperature=generated_track.model_temperature,
                model_sampling_top_p=generated_track.model_sampling_top_p,
                api_name="/generate_callback_wrapper"
            )
            
            # El resultado debería contener 8 versiones, tomamos la primera
            if result and len(result) > 0 and os.path.exists(result[0]):
                with open(result[0], 'rb') as f:
                    track_content = f.read()
                
                filename = f"{generated_track.title}_generated.mid"
                generated_track.generated_file.save(filename, ContentFile(track_content))
                generated_track.status = 'completed'
                generated_track.completed_at = timezone.now()
                generated_track.save()
                
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.progress_percentage = 100
                task.save()
            else:
                raise Exception("No se pudo generar el track")
                
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        return {'status': 'success', 'generated_file': generated_track.generated_file.url}
        
    except Exception as e:
        logger.error(f"Error generando track {generated_track_id}: {str(e)}")
        
        generated_track.status = 'error'
        generated_track.error_message = str(e)
        generated_track.save()
        
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        
        raise


@shared_task
def cleanup_old_files():
    """
    Tarea periódica para limpiar archivos antiguos
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Eliminar archivos temporales de más de 24 horas
    cutoff_date = timezone.now() - timedelta(hours=24)
    
    # Eliminar tareas fallidas antiguas
    old_failed_tasks = ProcessingTask.objects.filter(
        status='failed',
        created_at__lt=cutoff_date
    )
    
    count = old_failed_tasks.count()
    old_failed_tasks.delete()
    
    return f"Limpiadas {count} tareas fallidas antiguas"
