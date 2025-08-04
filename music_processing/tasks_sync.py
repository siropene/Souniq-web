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
                    # Mapear instrumental a strings para que coincida con el modelo
                    api_stem_types = ['vocals', 'drums', 'bass', 'guitar', 'piano', 'other', 'instrumental']
                    model_stem_types = ['vocals', 'drums', 'bass', 'guitar', 'piano', 'other', 'strings']
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
        logger.info(f"🎼 Iniciando conversión MIDI para stem ID: {stem_id}")
        
        stem = Stem.objects.get(id=stem_id)
        logger.info(f"📁 Stem encontrado: {stem.stem_type} de '{stem.song.title}'")
        logger.info(f"📄 Archivo del stem: {stem.file.name}")
        
        # Crear o obtener MidiFile
        midi_file, created = MidiFile.objects.get_or_create(
            stem=stem,
            defaults={'status': 'processing'}
        )
        logger.info(f"🎵 MidiFile {'creado' if created else 'actualizado'}: ID {midi_file.id}")
        
        if not created:
            midi_file.status = 'processing'
            midi_file.save()

        # Crear cliente de Hugging Face
        logger.info("🔗 Conectando con SouniQ/Modulo2...")
        client = Client("SouniQ/Modulo2")
        logger.info("✅ Cliente conectado exitosamente")
        
        # Crear archivo temporal
        logger.info("📂 Creando archivo temporal...")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            stem.file.seek(0)
            content = stem.file.read()
            logger.info(f"📏 Tamaño del archivo: {len(content)} bytes")
            temp_file.write(content)
            temp_file_path = temp_file.name
            logger.info(f"💾 Archivo temporal creado: {temp_file_path}")

        try:
            # Llamar a la API
            logger.info("🚀 Enviando archivo a la API de conversión MIDI...")
            result = client.predict(
                input_wav_path=handle_file(temp_file_path),
                api_name="/predict"
            )
            logger.info(f"📥 Resultado recibido: {type(result)}")
            logger.info(f"📁 Archivo MIDI generado: {result}")
            
            # El resultado debería ser la ruta del archivo MIDI
            if result and os.path.exists(result):
                logger.info("✅ Archivo MIDI encontrado, guardando...")
                with open(result, 'rb') as f:
                    midi_content = f.read()
                    logger.info(f"📏 Tamaño MIDI: {len(midi_content)} bytes")
                
                filename = f"{stem.song.title}_{stem.get_stem_type_display()}.mid"
                midi_file.file.save(filename, ContentFile(midi_content))
                midi_file.status = 'completed'
                midi_file.completed_at = timezone.now()
                midi_file.save()
                logger.info(f"💾 MIDI guardado exitosamente: {midi_file.file.name}")
                
                return {'status': 'success', 'midi_file': midi_file.file.url}
            else:
                raise Exception("No se pudo generar el archivo MIDI - resultado vacío o archivo no encontrado")
                
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.info("🧹 Archivo temporal limpiado")

    except Exception as e:
        logger.error(f"❌ Error convirtiendo stem {stem_id} a MIDI: {str(e)}", exc_info=True)
        try:
            midi_file.status = 'error'
            midi_file.error_message = str(e)
            midi_file.save()
            logger.info("📊 Estado del MIDI actualizado a 'error'")
        except:
            logger.error("❌ Error adicional al guardar estado del MIDI")
        raise

def generate_new_track_sync(generated_track_id):
    """Generar nueva canción de forma síncrona con 8 versiones"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from .models import GeneratedTrack, GeneratedVersion
        
        generated_track = GeneratedTrack.objects.get(id=generated_track_id)
        logger.info(f"🎵 Iniciando generación de track ID: {generated_track_id}")
        logger.info(f"📝 Título: {generated_track.title}")
        
        generated_track.status = 'processing'
        generated_track.save()

        # Crear cliente de Hugging Face
        logger.info(f"🔗 Conectando con Giant-Music-Transformer...")
        client = Client("asigalov61/Giant-Music-Transformer")
        logger.info(f"✅ Cliente conectado exitosamente")
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as temp_file:
            generated_track.midi_file.file.seek(0)
            temp_file.write(generated_track.midi_file.file.read())
            temp_file_path = temp_file.name
        
        logger.info(f"📂 Archivo temporal creado: {temp_file_path}")

        try:
            # Llamar a la API con los parámetros configurados
            logger.info(f"🚀 Enviando archivo MIDI para generación...")
            logger.info(f"⚙️ Parámetros: tokens_primarios={generated_track.num_prime_tokens}, tokens_gen={generated_track.num_gen_tokens}, temperatura={generated_track.model_temperature}")
            
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
            
            logger.info(f"📥 Resultado recibido: {type(result)}")
            logger.info(f"📊 Número de versiones generadas: {len(result) if result else 0}")
            
            # Debug: inspeccionar el resultado completo
            if result:
                logger.info(f"🔍 Estructura completa del resultado:")
                for idx, item in enumerate(result):
                    logger.info(f"  - Item {idx}: {type(item)} -> {item}")
            
            # El resultado contiene 8 versiones, guardamos todas
            if result and len(result) > 0:
                versions_saved = 0
                version_counter = 1  # Contador para versiones válidas
                
                for i, version_data in enumerate(result[:8], 0):  # Índices 0-7
                    try:
                        # Manejar diferentes tipos de respuesta de la API
                        version_path = None
                        if isinstance(version_data, str):
                            # Es una ruta de archivo
                            version_path = version_data
                        elif isinstance(version_data, dict) and 'path' in version_data:
                            # Es un diccionario con la clave 'path'
                            version_path = version_data['path']
                        elif hasattr(version_data, 'path'):
                            # Es un objeto con atributo path
                            version_path = version_data.path
                        else:
                            logger.info(f"🔍 Item {i} no reconocido como archivo: {type(version_data)} - {version_data}")
                            continue
                        
                        logger.info(f"📁 Evaluando item {i}: {version_path} (tipo: {type(version_data)})")
                        
                        if version_path and os.path.exists(version_path):
                            logger.info(f"✅ Archivo encontrado: {version_path}")
                            
                            # Verificar el tamaño del archivo antes de leerlo
                            file_size = os.path.getsize(version_path)
                            logger.info(f"📏 Tamaño del archivo: {file_size} bytes")
                            
                            if file_size > 0:
                                with open(version_path, 'rb') as f:
                                    track_content = f.read()
                                
                                logger.info(f"📖 Contenido leído: {len(track_content)} bytes")
                                
                                # Crear objeto GeneratedVersion usando el contador de versiones válidas
                                version, created = GeneratedVersion.objects.get_or_create(
                                    track=generated_track,
                                    version_number=version_counter,
                                    defaults={'file_size': len(track_content)}
                                )
                                
                                if not created:
                                    # Si ya existe, actualizar el tamaño
                                    version.file_size = len(track_content)
                                
                                # Guardar archivo
                                filename = f"{generated_track.title}_v{version_counter}_generated.mp3"
                                logger.info(f"💾 Guardando como: {filename}")
                                
                                version.file.save(filename, ContentFile(track_content), save=False)
                                version.file_size = len(track_content)
                                version.save()
                                
                                # Verificar que se guardó correctamente
                                version.refresh_from_db()
                                if version.file and hasattr(version.file, 'size'):
                                    actual_size = version.file.size
                                    logger.info(f"✅ Archivo guardado: {actual_size} bytes en DB")
                                else:
                                    logger.warning(f"⚠️ El archivo parece no haberse guardado correctamente")
                                
                                versions_saved += 1
                                version_counter += 1  # Incrementar contador solo para archivos válidos
                                logger.info(f"💾 Versión {version_counter-1} guardada exitosamente: {filename}")
                            else:
                                logger.warning(f"⚠️ Item {i} archivo vacío: {version_path}")
                            
                        else:
                            logger.info(f"📝 Item {i} no es archivo válido: {version_path}")
                            
                    except Exception as e:
                        logger.error(f"❌ Error procesando versión {i}: {str(e)}")
                        continue
                
                if versions_saved > 0:
                    generated_track.status = 'completed'
                    generated_track.completed_at = timezone.now()
                    generated_track.save()
                    
                    logger.info(f"✅ Generación completada: {versions_saved} versiones guardadas")
                    return {
                        'status': 'success', 
                        'versions_count': versions_saved,
                        'track_id': generated_track.id
                    }
                else:
                    raise Exception("No se pudo guardar ninguna versión")
            else:
                raise Exception("No se generaron versiones")
                
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.info(f"🧹 Archivo temporal limpiado")

    except Exception as e:
        logger.error(f"💥 Error generando track {generated_track_id}: {str(e)}", exc_info=True)
        try:
            generated_track = GeneratedTrack.objects.get(id=generated_track_id)
            generated_track.status = 'error'
            generated_track.error_message = str(e)
            generated_track.save()
        except:
            pass
        return {'status': 'error', 'message': str(e)}
