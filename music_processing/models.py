from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


class Song(models.Model):
    """Modelo para las canciones subidas por los usuarios"""
    
    STATUS_CHOICES = [
        ('uploaded', 'Subida'),
        ('processing_stems', 'Procesando Stems'),
        ('stems_completed', 'Stems Completados'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='songs')
    title = models.CharField(max_length=200)
    original_file = models.FileField(upload_to='songs/original/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    file_size = models.BigIntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # duración en segundos
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def filename(self):
        return os.path.basename(self.original_file.name)


class Stem(models.Model):
    """Modelo para los stems generados a partir de las canciones"""
    
    STEM_TYPES = [
        ('drums', 'Batería'),
        ('bass', 'Bajo'),
        ('piano', 'Piano'),
        ('other', 'Otros'),
        ('vocals', 'Voces'),
        ('guitar', 'Guitarra'),
        ('Clean', 'Instrumental'),
    ]
    
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='stems')
    stem_type = models.CharField(max_length=20, choices=STEM_TYPES)
    file = models.FileField(upload_to='stems/')
    created_at = models.DateTimeField(default=timezone.now)
    order = models.IntegerField(default=0)  # orden de los stems (0-6)
    
    class Meta:
        ordering = ['order']
        unique_together = ['song', 'order']
    
    def __str__(self):
        return f"{self.song.title} - {self.get_stem_type_display()}"


class MidiFile(models.Model):
    """Modelo para los archivos MIDI generados a partir de los stems"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('error', 'Error'),
    ]
    
    stem = models.OneToOneField(Stem, on_delete=models.CASCADE, related_name='midi_file')
    file = models.FileField(upload_to='midi/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"MIDI - {self.stem}"


class GeneratedTrack(models.Model):
    """Modelo para las nuevas canciones generadas a partir de archivos MIDI"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_tracks')
    midi_file = models.ForeignKey(MidiFile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    
    # Parámetros de generación para Orpheus-Music-Transformer
    apply_sustains = models.BooleanField(default=True)
    remove_duplicate_pitches = models.BooleanField(default=True)
    remove_overlapping_durations = models.BooleanField(default=True)
    # prime_instruments será un campo JSON para la lista
    prime_instruments_json = models.JSONField(default=list, blank=True)
    num_prime_tokens = models.IntegerField(default=6656)
    num_gen_tokens = models.IntegerField(default=512)
    model_temperature = models.FloatField(default=0.9)
    model_top_p = models.FloatField(default=0.96)
    add_drums = models.BooleanField(default=False)
    add_outro = models.BooleanField(default=False)
    
    # Campos legacy mantenidos para compatibilidad (no usados en Orpheus)
    num_mem_tokens = models.IntegerField(default=6990)
    gen_outro = models.CharField(max_length=20, default="Auto")
    gen_drums = models.BooleanField(default=False)
    model_sampling_top_p = models.FloatField(default=0.96)
    
    # Archivos resultado - deprecated, ahora usar GeneratedVersion
    generated_file = models.FileField(upload_to='generated_tracks/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def versions_count(self):
        """Retorna el número de versiones generadas"""
        return self.generated_versions.filter(file__isnull=False).count()
    
    @property
    def has_completed_versions(self):
        """Retorna True si tiene versiones completadas"""
        return self.generated_versions.filter(file__isnull=False).exists()
    
    @property
    def prime_instruments(self):
        """Getter para prime_instruments como lista"""
        return self.prime_instruments_json or []
    
    @prime_instruments.setter
    def prime_instruments(self, value):
        """Setter para prime_instruments"""
        self.prime_instruments_json = value or []


class GeneratedVersion(models.Model):
    """Modelo para almacenar las múltiples versiones generadas de un track"""
    
    track = models.ForeignKey(GeneratedTrack, on_delete=models.CASCADE, related_name='generated_versions')
    version_number = models.IntegerField()  # 1-8 para las 8 versiones
    file = models.FileField(upload_to='generated_tracks/', null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['version_number']
        unique_together = ['track', 'version_number']
    
    def __str__(self):
        return f"{self.track.title} - Versión {self.version_number}"
    
    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        return None
    
    @property
    def file_size_mb(self):
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None


class ProcessingTask(models.Model):
    """Modelo para rastrear tareas de procesamiento en background"""
    
    TASK_TYPES = [
        ('stem_generation', 'Generación de Stems'),
        ('midi_conversion', 'Conversión a MIDI'),
        ('track_generation', 'Generación de Track'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    celery_task_id = models.CharField(max_length=255, unique=True)
    
    # Referencias opcionales a los objetos relacionados
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, blank=True, related_name='processing_tasks')
    stem = models.ForeignKey(Stem, on_delete=models.CASCADE, null=True, blank=True, related_name='processing_tasks')
    generated_track = models.ForeignKey(GeneratedTrack, on_delete=models.CASCADE, null=True, blank=True, related_name='processing_tasks')
    
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    progress_percentage = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.get_task_type_display()} - {self.user.username} - {self.status}"
