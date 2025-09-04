# Versión síncrona de las tareas para PythonAnywhere gratuito
import os
import tempfile
import logging
from django.core.files.base import ContentFile
from django.utils import timezone
from gradio_client import Client, handle_file
from .models import Song, Stem, MidiFile, GeneratedTrack

logger = logging.getLogger(__name__)

def process_song_to_stems_sync(song_id):
    """Procesar canción a stems de forma síncrona"""
    from django.db import transaction
    
    try:
        with transaction.atomic():
            logger.info(f"🎵 Iniciando procesamiento de stems para canción ID: {song_id}")
            
            song = Song.objects.get(id=song_id)
            logger.info(f"📁 Canción encontrada: {song.title}")
            logger.info(f"📄 Archivo original: {song.original_file.name}")
            
            song.status = 'processing_stems'
            song.save()
            logger.info("📊 Estado actualizado a 'processing_stems'")

            # Crear cliente de Hugging Face
            logger.info("🔗 Conectando con SouniQ/Modulo1...")
            client = Client("SouniQ/Modulo1")
            logger.info("✅ Cliente conectado exitosamente")
            
            # Crear archivo temporal
            logger.info("📂 Creando archivo temporal...")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                # Leer el contenido del archivo
                song.original_file.seek(0)
                content = song.original_file.read()
                logger.info(f"📏 Tamaño del archivo: {len(content)} bytes")
                temp_file.write(content)
                temp_file_path = temp_file.name
                logger.info(f"💾 Archivo temporal creado: {temp_file_path}")

            try:
                # Llamar a la API
                logger.info("🚀 Enviando archivo a la API de Hugging Face...")
                result = client.predict(
                    input_wav_path=handle_file(temp_file_path),
                    api_name="/predict"
                )
                logger.info(f"📥 Resultado recibido: {type(result)}, longitud: {len(result) if result else 'None'}")
                
                if result and len(result) >= 7:
                    # Tipos de stems según la API: vocals, drums, bass, guitar, piano, other, instrumental
                    # Mapear instrumental a Clean para que coincida con el modelo
                    api_stem_types = ['vocals', 'drums', 'bass', 'guitar', 'piano', 'other', 'instrumental']
                    model_stem_types = ['vocals', 'drums', 'bass', 'guitar', 'piano', 'other', 'Clean']
                    logger.info(f"🎼 Procesando {len(result[:7])} stems...")
                    
                    stems_created = 0
                    for i, stem_file_path in enumerate(result[:7]):
                        try:
                            if os.path.exists(stem_file_path) and i < len(model_stem_types):
                                stem_type = model_stem_types[i]  # Usar el tipo del modelo
                                logger.info(f"🎹 Procesando stem {i+1}/{len(model_stem_types)}: {stem_type}")
                                logger.info(f"📁 Archivo del stem: {stem_file_path}")
                                
                                # Crear objeto Stem
                                stem = Stem.objects.create(
                                    song=song,
                                    stem_type=stem_type,
                                    order=i
                                )
                                logger.info(f"✨ Modelo Stem creado: ID {stem.id}")
                                
                                # Guardar archivo
                                with open(stem_file_path, 'rb') as f:
                                    stem_content = f.read()
                                
                                filename = f"{song.title}_{stem_type}.wav"
                                stem.file.save(filename, ContentFile(stem_content))
                                stem.save()
                                stems_created += 1
                                logger.info(f"💾 Stem {stem_type} guardado exitosamente")
                            else:
                                logger.warning(f"⚠️ Archivo de stem no encontrado o índice fuera de rango: {i}, archivo: {stem_file_path if i < len(result) else 'N/A'}")
                        except Exception as stem_error:
                            logger.error(f"❌ Error procesando stem {i}: {stem_error}", exc_info=True)
                            continue

                    song.status = 'stems_completed'
                    song.save()
                    logger.info(f"🎉 Procesamiento completado. {stems_created} stems creados exitosamente")
                    
                    # Verificar que los stems se guardaron
                    final_stem_count = song.stems.count()
                    logger.info(f"🔍 Verificación final: {final_stem_count} stems en la DB")
                    
                    return {'status': 'success', 'stems_created': stems_created}
                else:
                    raise Exception("No se pudieron generar los stems - resultado vacío o insuficiente")

            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.info("🧹 Archivo temporal limpiado")

    except Exception as e:
        logger.error(f"❌ Error procesando canción {song_id}: {str(e)}", exc_info=True)
        try:
            song = Song.objects.get(id=song_id)
            song.status = 'error'
            song.save()
            logger.info("📊 Estado de la canción actualizado a 'error'")
        except Exception as save_error:
            logger.error(f"❌ Error adicional al guardar estado: {save_error}")
        raise


def convert_stem_to_midi_sync(stem_id):
    """Convertir stem a MIDI de forma síncrona"""
    try:
        stem = Stem.objects.get(id=stem_id)
        
        # Crear o obtener MidiFile
        midi_file, created = MidiFile.objects.get_or_create(
            stem=stem,
            defaults={'status': 'processing'}
        )
        
        if not created:
            midi_file.status = 'processing'
            midi_file.save()

        # Crear cliente de Hugging Face
        client = Client("SouniQ/Modulo2")
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            stem.file.seek(0)
            temp_file.write(stem.file.read())
            temp_file_path = temp_file.name

        try:
            # Llamar a la API
            result = client.predict(
                input_wav_path=handle_file(temp_file_path),
                api_name="/predict"
            )
            
            # El resultado debería ser la ruta del archivo MIDI
            if result and os.path.exists(result):
                with open(result, 'rb') as f:
                    midi_content = f.read()
                
                filename = f"{stem.song.title}_{stem.get_stem_type_display()}.mid"
                midi_file.file.save(filename, ContentFile(midi_content))
                midi_file.status = 'completed'
                midi_file.completed_at = timezone.now()
                midi_file.save()
                
                return {'status': 'success', 'midi_file': midi_file.file.url}
            else:
                raise Exception("No se pudo generar el archivo MIDI")
                
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Error convirtiendo stem {stem_id} a MIDI: {str(e)}")
        midi_file.status = 'error'
        midi_file.error_message = str(e)
        midi_file.save()
        raise


def generate_new_track_sync(generated_track_id):
    """Generar nueva canción de forma síncrona"""
    try:
        generated_track = GeneratedTrack.objects.get(id=generated_track_id)
        
        # Crear cliente de Hugging Face
        client = Client("asigalov61/Orpheus-Music-Transformer")
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as temp_file:
            generated_track.midi_file.file.seek(0)
            temp_file.write(generated_track.midi_file.file.read())
            temp_file_path = temp_file.name

        try:
            # Llamar a la API con los parámetros correctos de Orpheus
            result = client.predict(
                input_midi=handle_file(temp_file_path),
                apply_sustains=True,
                remove_duplicate_pitches=True,
                remove_overlapping_durations=True,
                prime_instruments=[],  # Sin instrumentos prime por defecto
                num_prime_tokens=6656,
                num_gen_tokens=512,
                model_temperature=generated_track.temperature if hasattr(generated_track, 'temperature') else 0.9,
                model_top_p=0.96,
                add_drums=False,
                add_outro=hasattr(generated_track, 'outro_type') and generated_track.outro_type != 'none',
                api_name="/generate_music_and_state"
            )
            
            # La API devuelve 20 elementos: [audio0, plot0, audio1, plot1, ..., audio9, plot9]
            # Solo usamos los 8 primeros audios como solicitas (índices 0, 2, 4, 6, 8, 10, 12, 14)
            if result and len(result) >= 16:  # Al menos 8 audios disponibles
                audio_files = []
                for i in range(0, 16, 2):  # Índices 0, 2, 4, 6, 8, 10, 12, 14
                    if i < len(result) and result[i] and os.path.exists(result[i]):
                        audio_files.append(result[i])
                
                if audio_files:
                    # Usar el primer audio generado como resultado principal
                    first_audio_path = audio_files[0]
                    with open(first_audio_path, 'rb') as f:
                        generated_content = f.read()
                    
                    filename = f"{generated_track.title}_generated.wav"
                    generated_track.generated_file.save(filename, ContentFile(generated_content))
                    generated_track.status = 'completed'
                    generated_track.completed_at = timezone.now()
                    generated_track.save()
                    
                    logger.info(f"✅ Nueva canción generada exitosamente. {len(audio_files)} variaciones disponibles")
                    return {'status': 'success', 'generated_track': generated_track.generated_file.url, 'total_variations': len(audio_files)}
                else:
                    raise Exception("No se encontraron archivos de audio válidos en el resultado")
            else:
                raise Exception("No se pudo generar la nueva canción - resultado insuficiente")
                
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"❌ Error generando nueva canción: {str(e)}")
        try:
            generated_track = GeneratedTrack.objects.get(id=generated_track_id)
            generated_track.status = 'error'
            generated_track.error_message = str(e)
            generated_track.save()
        except Exception as save_error:
            logger.error(f"❌ Error adicional al guardar estado: {save_error}")
        raise
