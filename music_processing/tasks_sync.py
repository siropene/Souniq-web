# Versión síncrona de las tareas para PythonAnywhere gratuito
import os
import tempfile
import logging
import json
import time
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

            # Crear cliente de Hugging Face con patch para evitar JSONDecodeError
            logger.info("🔗 Conectando con SouniQ/Modulo1...")
            
            # Patch temporal: interceptar el método problemático
            original_get_api_info = None
            try:
                # Guardar método original
                original_get_api_info = Client._get_api_info
                
                # Función de reemplazo
                def patched_get_api_info(self):
                    try:
                        return original_get_api_info(self)
                    except json.JSONDecodeError:
                        logger.warning("⚠️ JSONDecodeError en _get_api_info - usando estructura mínima")
                        # Estructura mínima para permitir creación del cliente
                        return {
                            'named_endpoints': {},
                            'unnamed_endpoints': {}
                        }
                
                # Aplicar patch
                Client._get_api_info = patched_get_api_info
                
                # Crear cliente con patch activo
                client = Client("SouniQ/Modulo1")
                logger.info("✅ Cliente creado con patch exitoso")
                
            except Exception as e:
                logger.error(f"❌ Error incluso con patch: {e}")
                raise
            finally:
                # Restaurar método original
                if original_get_api_info:
                    Client._get_api_info = original_get_api_info
            
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
                # Llamar a la API con endpoint específico
                logger.info("🚀 Enviando archivo a la API de Hugging Face...")
                logger.info("⏱️ Esto puede tardar 2-3 minutos, por favor espera...")
                result = client.predict(
                    handle_file(temp_file_path),
                    api_name="/predict"
                )
                logger.info(f"📥 Resultado recibido: {type(result)}")
                
                if result:
                    logger.info(f"📊 Longitud del resultado: {len(result) if hasattr(result, '__len__') else 'No tiene longitud'}")
                    if hasattr(result, '__len__') and len(result) > 0:
                        for i, item in enumerate(result[:3]):  # Solo primeros 3 para no saturar logs
                            logger.info(f"   Item {i}: {type(item)} - {str(item)[:100] if item else 'None'}")
                else:
                    logger.warning("⚠️ Resultado es None o vacío")
                
                if result and hasattr(result, '__len__') and len(result) >= 7:
                    # Tipos de stems según la API: vocals, drums, bass, guitar, piano, other, instrumental
                    # Mapear instrumental a strings para que coincida con el modelo
                    api_stem_types = ['vocals', 'drums', 'bass', 'guitar', 'piano', 'other', 'instrumental']
                    model_stem_types = ['vocals', 'drums', 'bass', 'guitar', 'piano', 'other', 'strings']
                    logger.info(f"🎼 Procesando {len(result[:7])} stems...")
                    
                    for i, stem_file in enumerate(result[:7]):
                        if stem_file:
                            # Mapear tipo de stem
                            api_type = api_stem_types[i] if i < len(api_stem_types) else f'stem_{i}'
                            model_type = model_stem_types[i] if i < len(model_stem_types) else api_type
                            
                            # Crear o obtener stem en base de datos con order correcto
                            stem, created = Stem.objects.get_or_create(
                                song=song,
                                order=i,  # Usar order como parte de la búsqueda
                                defaults={
                                    'stem_type': model_type,
                                }
                            )
                            
                            if created:
                                logger.info(f"📝 Nuevo stem {model_type} creado (order={i})")
                            else:
                                logger.info(f"♻️ Stem {model_type} ya existe (order={i}), actualizando archivo...")
                            
                            # Guardar archivo (siempre, para actualizar si es necesario)
                            filename = f"stem_{model_type}_{song.id}_{stem.id}.wav"
                            with open(stem_file, 'rb') as f:
                                stem.file.save(filename, ContentFile(f.read()))
                            
                            logger.info(f"✅ Stem {model_type} guardado: {filename}")
                    
                    song.status = 'stems_completed'
                    song.save()
                    logger.info("🎉 Stems procesados exitosamente")
                    
                    return {
                        'status': 'success',
                        'message': f'Se procesaron {len(result)} stems exitosamente',
                        'stems_created': len(result)
                    }
                    
                else:
                    logger.error("❌ No se recibieron suficientes stems de la API")
                    song.status = 'error'
                    song.save()
                    
                    return {
                        'status': 'error',
                        'message': 'No se recibieron suficientes stems de la API',
                        'stems_created': 0
                    }
                    
            except Exception as e:
                # Verificar si es un AppError específico de Gradio
                error_message = str(e)
                if "upstream Gradio app has raised an exception" in error_message:
                    logger.error("❌ Error de la API de Hugging Face: El archivo no pudo ser procesado")
                    logger.error("💡 Posibles causas: archivo muy corto, formato incorrecto, o problema temporal de la API")
                else:
                    logger.error(f"❌ Error en predict(): {e}")
                
                import traceback
                logger.error(f"📋 Traceback predict: {traceback.format_exc()}")
                song.status = 'error'
                song.save()
                
                return {
                    'status': 'error',
                    'message': f'Error en la API: {error_message}',
                    'stems_created': 0
                }
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.info("🧹 Archivo temporal eliminado")
                    
    except Exception as e:
        logger.error(f"❌ Error general en process_song_to_stems_sync: {e}")
        import traceback
        logger.error(f"📋 Traceback completo: {traceback.format_exc()}")
        try:
            song.status = 'error'
            song.save()
        except:
            logger.error("❌ Error adicional al guardar estado")
        
        return {
            'status': 'error',
            'message': f'Error general: {str(e)}',
            'stems_created': 0
        }

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

        # Crear cliente de Hugging Face con patch para evitar JSONDecodeError
        logger.info("🔗 Conectando con SouniQ/Modulo2...")
        
        # Patch temporal: interceptar el método problemático
        original_get_api_info = None
        try:
            # Guardar método original
            original_get_api_info = Client._get_api_info
            
            # Función de reemplazo simple
            def patched_get_api_info(self):
                try:
                    return original_get_api_info(self)
                except json.JSONDecodeError:
                    logger.warning("⚠️ JSONDecodeError en _get_api_info - usando estructura mínima")
                    # Estructura mínima que permite crear el cliente
                    return {
                        'named_endpoints': {},
                        'unnamed_endpoints': {}
                    }
            
            # Aplicar patch
            Client._get_api_info = patched_get_api_info
            
            # Crear cliente con patch activo
            client = Client("SouniQ/Modulo2")
            logger.info("✅ Cliente creado con patch exitoso")
            
        except Exception as e:
            logger.error(f"❌ Error incluso con patch: {e}")
            raise
        finally:
            # Restaurar método original
            if original_get_api_info:
                Client._get_api_info = original_get_api_info
        
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
            # Llamar a la API con endpoint específico
            logger.info("🚀 Enviando archivo a la API de conversión MIDI...")
            result = client.predict(
                handle_file(temp_file_path),
                api_name="/predict"
            )
            logger.info(f"📥 Resultado MIDI recibido: {type(result)}")
            
            if result:
                # Guardar archivo MIDI
                filename = f"midi_{stem.stem_type}_{stem.song.id}_{midi_file.id}.mid"
                with open(result, 'rb') as f:
                    midi_file.file.save(filename, ContentFile(f.read()))
                
                midi_file.status = 'completed'
                midi_file.save()
                logger.info(f"✅ MIDI guardado: {filename}")
                
                # Actualizar estado de la canción si todos los stems tienen MIDI
                if stem.song.stems.filter(midi_file__status='completed').count() >= stem.song.stems.count():
                    stem.song.status = 'completed'
                    stem.song.save()
                    logger.info("🎉 Conversión completa - todos los stems convertidos")
                
                return {
                    'status': 'success',
                    'message': f'MIDI generado exitosamente para {stem.stem_type}',
                    'midi_file_id': midi_file.id
                }
                
            else:
                logger.error("❌ No se recibió archivo MIDI de la API")
                midi_file.status = 'error'
                midi_file.save()
                
                return {
                    'status': 'error',
                    'message': 'No se recibió archivo MIDI de la API'
                }
                
        except Exception as e:
            logger.error(f"❌ Error en predict(): {e}")
            midi_file.status = 'error'
            midi_file.save()
            return {
                'status': 'error',
                'message': f'Error en la API: {str(e)}'
            }
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.info("🧹 Archivo temporal eliminado")
                
    except Exception as e:
        logger.error(f"❌ Error general en convert_stem_to_midi_sync: {e}")
        try:
            midi_file.status = 'error'
            midi_file.save()
        except:
            logger.error("❌ Error adicional al guardar estado del MIDI")
        
        return {
            'status': 'error',
            'message': f'Error general: {str(e)}'
        }

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

        # Crear cliente de Hugging Face con patch para evitar JSONDecodeError
        logger.info(f"🔗 Conectando con Giant-Music-Transformer...")
        
        # Patch temporal: interceptar el método problemático
        original_get_api_info = None
        try:
            # Guardar método original
            original_get_api_info = Client._get_api_info
            
            # Función de reemplazo simple
            def patched_get_api_info(self):
                try:
                    return original_get_api_info(self)
                except json.JSONDecodeError:
                    logger.warning("⚠️ JSONDecodeError en _get_api_info - usando estructura mínima")
                    # Estructura mínima que permite crear el cliente
                    return {
                        'named_endpoints': {},
                        'unnamed_endpoints': {}
                    }
            
            # Aplicar patch
            Client._get_api_info = patched_get_api_info
            
            # Crear cliente con patch activo
            client = Client("asigalov61/Giant-Music-Transformer")
            logger.info(f"✅ Cliente creado con patch exitoso")
            
        except Exception as e:
            logger.error(f"❌ Error incluso con patch: {e}")
            raise
        finally:
            # Restaurar método original
            if original_get_api_info:
                Client._get_api_info = original_get_api_info
        
        # Crear archivo temporal y validar MIDI
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mid') as temp_file:
            generated_track.midi_file.file.seek(0)
            midi_content = generated_track.midi_file.file.read()
            temp_file.write(midi_content)
            temp_file_path = temp_file.name
        
        logger.info(f"📂 Archivo temporal creado: {temp_file_path}")
        logger.info(f"📏 Tamaño del archivo MIDI: {len(midi_content)} bytes")
        logger.info(f"📁 Archivo MIDI origen: {generated_track.midi_file.file.name}")
        
        # Validar archivo MIDI
        if len(midi_content) < 100:
            logger.error(f"❌ Archivo MIDI muy pequeño: {len(midi_content)} bytes")
            return {
                'status': 'error',
                'message': f'Archivo MIDI muy pequeño ({len(midi_content)} bytes). Debe tener al menos 100 bytes.'
            }
        
        # Verificar header MIDI
        if not midi_content.startswith(b'MThd'):
            logger.error("❌ Header MIDI inválido")
            return {
                'status': 'error',
                'message': 'Archivo MIDI no tiene header válido (debe comenzar con MThd)'
            }
        
        logger.info("✅ Archivo MIDI validado correctamente")

        try:
            # Llamar a la API con reintentos automáticos
            logger.info("🚀 Enviando MIDI a la API de generación...")
            logger.info(f"⚙️ Parámetros: gen_outro={generated_track.gen_outro}, temp={generated_track.model_temperature}")
            
            # Implementar reintentos para errores temporales
            max_retries = 3
            retry_delay = 30  # segundos
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        logger.info(f"🔄 Intento {attempt + 1}/{max_retries} después de esperar {retry_delay}s...")
                        import time
                        time.sleep(retry_delay)
                    
                    result = client.predict(
                        input_midi=temp_file_path,
                        num_prime_tokens=generated_track.num_prime_tokens,
                        num_gen_tokens=generated_track.num_gen_tokens,
                        num_mem_tokens=generated_track.num_mem_tokens,
                        gen_outro=generated_track.gen_outro,
                        gen_drums=generated_track.gen_drums,
                        model_temperature=generated_track.model_temperature,
                        model_sampling_top_p=generated_track.model_sampling_top_p,
                        api_name="/generate_callback_wrapper"
                    )
                    
                    # Si llegamos aquí, la API funcionó
                    logger.info(f"✅ API respondió exitosamente en intento {attempt + 1}")
                    break
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Solo reintentar para errores temporales
                    if ("upstream gradio app has raised an exception" in error_msg or 
                        "timeout" in error_msg or 
                        "connection" in error_msg):
                        
                        if attempt < max_retries - 1:
                            logger.warning(f"⚠️ Error temporal en intento {attempt + 1}: {str(e)[:100]}...")
                            logger.info(f"🔄 Reintentando en {retry_delay} segundos...")
                            continue
                        else:
                            logger.error(f"❌ Error persistente después de {max_retries} intentos")
                            raise
                    else:
                        # Error no temporal, no reintentar
                        logger.error(f"❌ Error no temporal: {str(e)[:100]}...")
                        raise
            
            if result and len(result) >= 8:
                logger.info(f"🎼 Generando {len(result[:8])} versiones...")
                
                for i, track_file in enumerate(result[:8]):
                    if track_file:
                        version = GeneratedVersion.objects.create(
                            generated_track=generated_track,
                            version_number=i + 1
                        )
                        
                        filename = f"generated_v{i+1}_{generated_track.id}_{version.id}.mid"
                        with open(track_file, 'rb') as f:
                            version.file.save(filename, ContentFile(f.read()))
                        
                        logger.info(f"✅ Versión {i+1} guardada: {filename}")
                
                generated_track.status = 'completed'
                generated_track.save()
                logger.info("🎉 Generación completada exitosamente")
                
                return {
                    'status': 'success',
                    'message': f'Se generaron {len(result[:8])} versiones exitosamente',
                    'versions_created': len(result[:8])
                }
                
            else:
                logger.error("❌ No se recibieron suficientes versiones de la API")
                generated_track.status = 'error'
                generated_track.save()
                
                return {
                    'status': 'error',
                    'message': 'No se recibieron suficientes versiones de la API',
                    'versions_created': 0
                }
                
        except Exception as e:
            error_message = str(e)
            
            # Manejo específico para errores de la API Giant-Music-Transformer
            if "upstream Gradio app has raised an exception" in error_message:
                logger.error("❌ Error de la API Giant-Music-Transformer: El archivo MIDI no pudo ser procesado")
                logger.error("💡 Posibles causas:")
                logger.error("   - Archivo MIDI corrupto o formato incorrecto")
                logger.error("   - MIDI demasiado corto o sin datos musicales válidos")
                logger.error("   - Problema temporal en la API de Hugging Face")
                error_msg = "El archivo MIDI no pudo ser procesado por la API de generación"
            else:
                logger.error(f"❌ Error en predict(): {e}")
                error_msg = f"Error en la API: {str(e)}"
            
            generated_track.status = 'error'
            generated_track.save()
            
            return {
                'status': 'error',
                'message': error_msg,
                'versions_created': 0
            }
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"❌ Error general en generate_new_track_sync: {e}")
        try:
            generated_track.status = 'error'
            generated_track.save()
        except:
            logger.error("❌ Error adicional al guardar estado")
        
        return {
            'status': 'error',
            'message': f'Error general: {str(e)}',
            'versions_created': 0
        }
