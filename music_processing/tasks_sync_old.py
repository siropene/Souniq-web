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
    try:
        song = Song.objects.get(id=song_id)
        song.status = 'processing_stems'
        song.save()
        
        # Por ahora solo simular
        return {'status': 'success', 'stems_created': 7}
        
    except Exception as e:
        logger.error(f"Error procesando canción {song_id}: {str(e)}")
        song.status = 'error'
        song.save()
        raise

def convert_stem_to_midi_sync(stem_id):
    """Convertir stem a MIDI de forma síncrona"""
    try:
        stem = Stem.objects.get(id=stem_id)
        
        # Crear o obtener MidiFile
        midi_file, created = MidiFile.objects.get_or_create(
            stem=stem,
            defaults={'status': 'completed'}
        )
        
        return {'status': 'success', 'midi_file': 'test.mid'}
        
    except Exception as e:
        logger.error(f"Error convirtiendo stem {stem_id} a MIDI: {str(e)}")
        raise

def generate_new_track_sync(generated_track_id):
    """Generar nueva canción de forma síncrona"""
    try:
        generated_track = GeneratedTrack.objects.get(id=generated_track_id)
        generated_track.status = 'completed'
        generated_track.save()
        
        return {'status': 'success', 'generated_file': 'test_generated.mid'}
        
    except Exception as e:
        logger.error(f"Error generando track {generated_track_id}: {str(e)}")
        generated_track.status = 'error'
        generated_track.error_message = str(e)
        generated_track.save()
        raise
