from django.contrib import admin
from .models import Song, Stem, MidiFile, GeneratedTrack, ProcessingTask


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'uploaded_at', 'file_size']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = ['uploaded_at', 'file_size']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Stem)
class StemAdmin(admin.ModelAdmin):
    list_display = ['song', 'stem_type', 'order', 'created_at']
    list_filter = ['stem_type', 'created_at']
    search_fields = ['song__title', 'song__user__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('song__user')


@admin.register(MidiFile)
class MidiFileAdmin(admin.ModelAdmin):
    list_display = ['stem', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['stem__song__title', 'stem__song__user__username']
    readonly_fields = ['created_at', 'completed_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('stem__song__user')


@admin.register(GeneratedTrack)
class GeneratedTrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'completed_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ProcessingTask)
class ProcessingTaskAdmin(admin.ModelAdmin):
    list_display = ['user', 'task_type', 'status', 'progress_percentage', 'created_at']
    list_filter = ['task_type', 'status', 'created_at']
    search_fields = ['user__username', 'celery_task_id']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
