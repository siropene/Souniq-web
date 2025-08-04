from django.urls import path
from . import views

app_name = 'music_processing'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # Gestión de canciones
    path('songs/', views.song_list, name='song_list'),
    path('songs/upload/', views.upload_song, name='upload_song'),
    path('songs/<int:song_id>/delete/', views.delete_song, name='delete_song'),
    
    # Generación de stems
    path('stems/', views.stems_view, name='stems'),
    path('stems/generate/<int:song_id>/', views.generate_stems, name='generate_stems'),
    
    # Conversión a MIDI
    path('midi/', views.midi_conversion_view, name='midi_conversion'),
    path('midi/convert/<int:stem_id>/', views.convert_to_midi, name='convert_to_midi'),
    
    # Generación de tracks
    path('generate/', views.track_generation_view, name='track_generation'),
    path('generate/track/<int:midi_id>/', views.generate_track, name='generate_track'),
    path('generate/delete/<int:track_id>/', views.delete_generated_track, name='delete_generated_track'),
    
    # Descargas
    path('download/<str:file_type>/<int:file_id>/', views.download_file, name='download_file'),
    path('download/version/<int:version_id>/', views.download_version, name='download_version'),
    
    # API para estado de tareas
    path('api/task/<str:task_id>/status/', views.task_status, name='task_status'),
]
