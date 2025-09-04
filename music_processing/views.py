from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
import os
import uuid

from .models import Song, Stem, MidiFile, GeneratedTrack, ProcessingTask
from .forms import SongUploadForm, TrackGenerationForm
from .tasks_sync import process_song_to_stems_sync, convert_stem_to_midi_sync, generate_new_track_sync


@login_required
def dashboard(request):
    """Vista principal del dashboard"""
    # Estadísticas del usuario
    songs_count = Song.objects.filter(user=request.user).count()
    stems_count = Stem.objects.filter(song__user=request.user).count()
    midi_count = MidiFile.objects.filter(stem__song__user=request.user, status='completed').count()
    generated_count = GeneratedTrack.objects.filter(user=request.user).count()
    
    # Canciones recientes
    recent_songs = Song.objects.filter(user=request.user)[:5]
    
    # Tareas en progreso
    active_tasks = ProcessingTask.objects.filter(
        user=request.user,
        status__in=['pending', 'in_progress']
    )[:5]
    
    context = {
        'songs_count': songs_count,
        'stems_count': stems_count,
        'midi_count': midi_count,
        'generated_count': generated_count,
        'recent_songs': recent_songs,
        'active_tasks': active_tasks,
    }
    
    return render(request, 'music_processing/dashboard.html', context)


@login_required
def song_list(request):
    """Lista de canciones del usuario"""
    songs = Song.objects.filter(user=request.user)
    
    # Búsqueda
    search_query = request.GET.get('search')
    if search_query:
        songs = songs.filter(
            Q(title__icontains=search_query) | 
            Q(original_file__icontains=search_query)
        )
    
    # Filtro por estado
    status_filter = request.GET.get('status')
    if status_filter:
        songs = songs.filter(status=status_filter)
    
    # Paginación
    paginator = Paginator(songs, 10)
    page_number = request.GET.get('page')
    songs_page = paginator.get_page(page_number)
    
    # Formulario de subida
    upload_form = SongUploadForm()
    
    context = {
        'songs': songs_page,
        'upload_form': upload_form,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'music_processing/song_list.html', context)


@login_required
@require_POST
def upload_song(request):
    """Subir una nueva canción"""
    form = SongUploadForm(request.POST, request.FILES)
    
    if form.is_valid():
        song = form.save(commit=False)
        song.user = request.user
        
        # Obtener información del archivo
        if song.original_file:
            song.file_size = song.original_file.size
        
        song.save()
        
        messages.success(request, f'La canción "{song.title}" se ha subido correctamente.')
        return redirect('music_processing:song_list')
    else:
        messages.error(request, 'Hubo un error al subir la canción. Por favor, revisa los datos.')
        return redirect('music_processing:song_list')


@login_required
def stems_view(request):
    """Vista de generación y gestión de stems"""
    songs = Song.objects.filter(user=request.user).prefetch_related(
        'stems', 
        'processing_tasks'
    ).select_related()
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        songs = songs.filter(status=status_filter)
    
    # Agregar información de tareas activas para cada canción
    for song in songs:
        if song.status == 'processing_stems':
            # Buscar la tarea activa de generación de stems
            active_task = song.processing_tasks.filter(
                task_type='stem_generation',
                status__in=['pending', 'in_progress']
            ).first()
            song.active_task = active_task
    
    context = {
        'songs': songs,
        'status_filter': status_filter,
    }
    
    return render(request, 'music_processing/stems.html', context)


@login_required
@require_POST
def generate_stems(request, song_id):
    """Iniciar la generación de stems para una canción"""
    song = get_object_or_404(Song, id=song_id, user=request.user)
    
    if song.status != 'uploaded':
        messages.error(request, 'Esta canción ya está siendo procesada o ya tiene stems generados.')
        return redirect('music_processing:stems')
    
    # Verificar si ya hay una tarea pendiente o en progreso para esta canción
    existing_task = ProcessingTask.objects.filter(
        song=song,
        task_type='stem_generation',
        status__in=['pending', 'in_progress']
    ).first()
    
    if existing_task:
        messages.warning(request, f'Ya hay una tarea de generación de stems en progreso para "{song.title}".')
        return redirect('music_processing:stems')

    try:
        # Procesar de forma síncrona
        messages.info(request, f'Procesando stems para "{song.title}". Por favor espere...')
        result = process_song_to_stems_sync(song.id)
        
        if result['status'] == 'success':
            messages.success(request, f'Se han generado {result["stems_created"]} stems para "{song.title}".')
        else:
            messages.error(request, f'Error al generar stems para "{song.title}".')
        
    except Exception as e:
        messages.error(request, f'Error al procesar la canción: {str(e)}')
    
    return redirect('music_processing:stems')


@login_required
@login_required
def midi_conversion_view(request):
    """Vista de conversión de stems a MIDI"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🌐 [MIDI VIEW] User: {request.user.username}")
    
    stems = Stem.objects.filter(song__user=request.user).select_related('song', 'midi_file')
    logger.info(f"🌐 [MIDI VIEW] Found {stems.count()} stems for user")
    
    # Agrupar por canción
    songs_with_stems = {}
    for stem in stems:
        if stem.song not in songs_with_stems:
            songs_with_stems[stem.song] = []
        songs_with_stems[stem.song].append(stem)
        logger.info(f"🌐 [MIDI VIEW] Stem: {stem.stem_type} from {stem.song.title}")
    
    context = {
        'songs_with_stems': songs_with_stems,
    }
    
    return render(request, 'music_processing/midi_conversion.html', context)


@login_required
@require_POST
def convert_to_midi(request, stem_id):
    """Convertir un stem específico a MIDI"""
    import logging
    logger = logging.getLogger(__name__)
    
    print(f"\n🌐 [WEB CONVERT] =========== INICIO ===========")
    print(f"🌐 [WEB CONVERT] Usuario: {request.user.username}")
    print(f"🌐 [WEB CONVERT] Stem ID: {stem_id}")
    print(f"🌐 [WEB CONVERT] Método: {request.method}")
    
    logger.info(f"🌐 [WEB] Función convert_to_midi llamada - User: {request.user.username}, Stem ID: {stem_id}")
    
    stem = get_object_or_404(Stem, id=stem_id, song__user=request.user)
    logger.info(f"🌐 [WEB] Stem encontrado: {stem.stem_type} de '{stem.song.title}'")
    
    try:
        # Verificar si ya existe un MIDI
        try:
            midi_file = stem.midi_file
            if midi_file.status == 'processing':
                messages.error(request, f'El stem "{stem.get_stem_type_display()}" ya está siendo procesado.')
                return redirect('music_processing:midi_conversion')
            elif midi_file.status == 'completed':
                # Permitir reconversión pero avisar al usuario
                messages.info(request, f'Reconvirtiendo el stem "{stem.get_stem_type_display()}" que ya tenía un MIDI.')
                midi_file.status = 'processing'
                midi_file.save()
        except MidiFile.DoesNotExist:
            # Crear objeto MidiFile si no existe
            midi_file = MidiFile.objects.create(stem=stem, status='processing')

        # Procesar de forma síncrona con logging
        messages.info(request, f'Convirtiendo a MIDI el stem "{stem.get_stem_type_display()}". Por favor espere...')
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Vista web: Iniciando conversión MIDI para stem {stem_id}")
        
        result = convert_stem_to_midi_sync(stem.id)
        logger.info(f"Vista web: Resultado conversión MIDI: {result}")
        
        if result['status'] == 'success':
            messages.success(request, f'✅ Conversión exitosa: "{stem.get_stem_type_display()}" → MIDI')
        else:
            messages.error(request, f'❌ Error en la conversión del stem "{stem.get_stem_type_display()}".')
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error en vista convert_to_midi: {str(e)}", exc_info=True)
        
        # Actualizar estado a error si existe el MIDI
        try:
            midi_file = stem.midi_file
            midi_file.status = 'error'
            midi_file.error_message = str(e)
            midi_file.save()
        except:
            pass
            
        messages.error(request, f'❌ Error al convertir el stem: {str(e)}')
    
    print(f"🌐 [WEB CONVERT] =========== FIN ===========\n")
    return redirect('music_processing:midi_conversion')


@login_required
def track_generation_view(request):
    """Vista de generación de nuevas canciones"""
    midi_files = MidiFile.objects.filter(
        stem__song__user=request.user,
        status='completed'
    ).select_related('stem__song')
    
    form = TrackGenerationForm()
    
    # Tracks generados del usuario con sus versiones
    generated_tracks = GeneratedTrack.objects.filter(
        user=request.user
    ).prefetch_related('generated_versions').order_by('-created_at')
    
    context = {
        'midi_files': midi_files,
        'form': form,
        'generated_tracks': generated_tracks,
    }
    
    return render(request, 'music_processing/track_generation.html', context)


@login_required
@require_POST
def generate_track(request, midi_id):
    """Generar una nueva canción a partir de un archivo MIDI"""
    midi_file = get_object_or_404(
        MidiFile, 
        id=midi_id, 
        stem__song__user=request.user,
        status='completed'
    )
    
    # Crear track con valores por defecto
    generated_track = GeneratedTrack.objects.create(
        user=request.user,
        midi_file=midi_file,
        title=f"Nueva canción basada en {midi_file.stem.song.title}_{midi_file.stem.get_stem_type_display()}",
        model_temperature=1.0,  # Valor por defecto
        add_drums=False  # Sin batería por defecto
    )
    
    try:
        # Procesar de forma síncrona
        messages.info(request, f'Generando la canción "{generated_track.title}". Por favor espere...')
        result = generate_new_track_sync(generated_track.id)
        
        if result['status'] == 'success':
            messages.success(request, f'Se ha generado exitosamente la canción "{generated_track.title}".')
        else:
            messages.error(request, f'Error al generar la canción "{generated_track.title}".')
            
    except Exception as e:
        messages.error(request, f'Error al generar la canción: {str(e)}')
    
    return redirect('music_processing:track_generation')


@login_required
def download_file(request, file_type, file_id):
    """Descargar archivos de audio/MIDI"""
    if file_type == 'song':
        obj = get_object_or_404(Song, id=file_id, user=request.user)
        file_field = obj.original_file
        filename = f"{obj.title}_original.wav"
    elif file_type == 'stem':
        obj = get_object_or_404(Stem, id=file_id, song__user=request.user)
        file_field = obj.file
        filename = f"{obj.song.title}_{obj.get_stem_type_display()}.wav"
    elif file_type == 'midi':
        obj = get_object_or_404(MidiFile, id=file_id, stem__song__user=request.user)
        file_field = obj.file
        filename = f"{obj.stem.song.title}_{obj.stem.get_stem_type_display()}.mid"
    elif file_type == 'generated':
        obj = get_object_or_404(GeneratedTrack, id=file_id, user=request.user)
        file_field = obj.generated_file
        filename = f"{obj.title}_generated.mp3"
    else:
        raise Http404("Tipo de archivo no válido")
    
    if not file_field or not os.path.exists(file_field.path):
        raise Http404("Archivo no encontrado")
    
    with open(file_field.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


@login_required
def task_status(request, task_id):
    """API para obtener el estado de una tarea"""
    task = get_object_or_404(ProcessingTask, celery_task_id=task_id, user=request.user)
    
    # Intentar obtener información adicional del estado de Celery
    detailed_status = None
    try:
        from celery.result import AsyncResult
        result = AsyncResult(task_id)
        if result.state == 'PROGRESS' and result.info:
            detailed_status = result.info.get('status', '')
    except Exception:
        pass
    
    return JsonResponse({
        'status': task.status,
        'progress': task.progress_percentage,
        'error_message': task.error_message,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        'detailed_status': detailed_status,
        'task_type': task.task_type,
    })


@login_required
def delete_song(request, song_id):
    """Eliminar una canción y todos sus archivos relacionados"""
    song = get_object_or_404(Song, id=song_id, user=request.user)
    
    if request.method == 'POST':
        title = song.title
        song.delete()  # Django automáticamente eliminará los archivos relacionados
        messages.success(request, f'La canción "{title}" y todos sus archivos relacionados han sido eliminados.')
        return redirect('music_processing:song_list')
    
    return render(request, 'music_processing/confirm_delete.html', {'song': song})


@login_required
def delete_generated_track(request, track_id):
    """Eliminar un track generado y su archivo"""
    track = get_object_or_404(GeneratedTrack, id=track_id, user=request.user)
    
    if request.method == 'POST':
        title = track.title
        # Eliminar el archivo físico si existe
        if track.generated_file:
            try:
                if os.path.exists(track.generated_file.path):
                    os.remove(track.generated_file.path)
            except:
                pass  # Si hay error eliminando el archivo, continuar
        
        track.delete()
        messages.success(request, f'El track generado "{title}" ha sido eliminado.')
        return redirect('music_processing:track_generation')
    
    return render(request, 'music_processing/confirm_delete_track.html', {'track': track})


@login_required
def download_version(request, version_id):
    """Descargar una versión específica de un track generado"""
    from .models import GeneratedVersion
    
    version = get_object_or_404(
        GeneratedVersion, 
        id=version_id, 
        track__user=request.user,
        file__isnull=False
    )
    
    if not version.file:
        raise Http404("Archivo no encontrado")
    
    response = FileResponse(
        version.file.open(), 
        as_attachment=True,
        filename=f"{version.track.title}_v{version.version_number}.mp3"
    )
    response['Content-Type'] = 'audio/mpeg'
    
    return response
