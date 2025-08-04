from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from music_processing.models import Song, Stem, MidiFile, GeneratedTrack, ProcessingTask


@login_required
def dashboard(request):
    """Vista principal del dashboard"""
    user = request.user
    
    # Estadísticas generales
    stats = {
        'total_songs': Song.objects.filter(user=user).count(),
        'total_stems': Stem.objects.filter(song__user=user).count(),
        'total_midi': MidiFile.objects.filter(stem__song__user=user, status='completed').count(),
        'total_generated': GeneratedTrack.objects.filter(user=user).count(),
    }
    
    # Actividad reciente (últimos 30 días)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    recent_activity = {
        'songs_uploaded': Song.objects.filter(
            user=user, 
            uploaded_at__gte=thirty_days_ago
        ).count(),
        'stems_generated': Stem.objects.filter(
            song__user=user, 
            created_at__gte=thirty_days_ago
        ).count(),
        'midi_converted': MidiFile.objects.filter(
            stem__song__user=user, 
            status='completed',
            completed_at__gte=thirty_days_ago
        ).count(),
        'tracks_generated': GeneratedTrack.objects.filter(
            user=user, 
            created_at__gte=thirty_days_ago
        ).count(),
    }
    
    # Canciones recientes
    recent_songs = Song.objects.filter(user=user).order_by('-uploaded_at')[:5]
    
    # Tareas activas
    active_tasks = ProcessingTask.objects.filter(
        user=user,
        status__in=['pending', 'in_progress']
    ).order_by('-created_at')[:10]
    
    # Tracks generados recientes
    recent_tracks = GeneratedTrack.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Estado de las canciones
    song_status_counts = Song.objects.filter(user=user).values('status').annotate(
        count=Count('status')
    )
    
    context = {
        'stats': stats,
        'recent_activity': recent_activity,
        'recent_songs': recent_songs,
        'active_tasks': active_tasks,
        'recent_tracks': recent_tracks,
        'song_status_counts': song_status_counts,
    }
    
    return render(request, 'core/dashboard.html', context)


def home(request):
    """Vista de la página de inicio (para usuarios no autenticados)"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    # Estadísticas públicas (opcional)
    public_stats = {
        'total_users': User.objects.count(),
        'total_songs_processed': Song.objects.count(),
        'total_stems_generated': Stem.objects.count(),
    }
    
    context = {
        'public_stats': public_stats,
    }
    
    return render(request, 'core/home.html', context)


@login_required
def about(request):
    """Vista de la página Acerca de"""
    return render(request, 'core/about.html')


@login_required
def help_center(request):
    """Vista del centro de ayuda"""
    
    # Preguntas frecuentes
    faqs = [
        {
            'question': '¿Qué formatos de audio son compatibles?',
            'answer': 'Soportamos los formatos más comunes: MP3, WAV, FLAC, AAC y M4A. El tamaño máximo por archivo es de 50MB.'
        },
        {
            'question': '¿Cuánto tiempo tarda en procesarse una canción?',
            'answer': 'El tiempo de procesamiento depende de la duración y complejidad de la canción. Normalmente tarda entre 2-10 minutos.'
        },
        {
            'question': '¿Qué son los stems?',
            'answer': 'Los stems son las pistas individuales que componen una canción: batería, bajo, piano, voces, etc. Nuestra IA separa automáticamente estos elementos.'
        },
        {
            'question': '¿Puedo descargar todos mis archivos?',
            'answer': 'Sí, puedes descargar tanto los stems generados como los archivos MIDI y las nuevas canciones creadas.'
        },
        {
            'question': '¿Cómo funciona la generación de nuevas canciones?',
            'answer': 'Usamos inteligencia artificial para analizar tus archivos MIDI y generar nuevas composiciones basadas en los patrones musicales encontrados.'
        },
    ]
    
    context = {
        'faqs': faqs,
    }
    
    return render(request, 'core/help.html', context)


@login_required
def privacy_policy(request):
    """Vista de la política de privacidad"""
    return render(request, 'core/privacy.html')


@login_required
def terms_of_service(request):
    """Vista de los términos de servicio"""
    return render(request, 'core/terms.html')


def handler404(request, exception):
    """Vista personalizada para error 404"""
    return render(request, 'core/404.html', status=404)


def handler500(request):
    """Vista personalizada para error 500"""
    return render(request, 'core/500.html', status=500)
