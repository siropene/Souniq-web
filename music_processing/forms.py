from django import forms
from django.core.validators import FileExtensionValidator
from .models import Song, GeneratedTrack


class SongUploadForm(forms.ModelForm):
    """Formulario para subir canciones"""
    
    class Meta:
        model = Song
        fields = ['title', 'original_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introduce el título de la canción'
            }),
            'original_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*'
            })
        }
        labels = {
            'title': 'Título de la canción',
            'original_file': 'Archivo de audio'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['original_file'].validators.append(
            FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'flac', 'aac', 'm4a'])
        )
        self.fields['title'].required = True
        self.fields['original_file'].required = True
    
    def clean_original_file(self):
        file = self.cleaned_data.get('original_file')
        if file:
            # Limitar tamaño a 50MB
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar los 50MB.')
        return file


class TrackGenerationForm(forms.ModelForm):
    """Formulario simplificado para generar nuevas canciones con Orpheus-Music-Transformer"""
    
    class Meta:
        model = GeneratedTrack
        fields = [
            'title', 
            'model_temperature',
            'add_drums'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título para la nueva canción'
            }),
            'model_temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.1,
                'max': 2.0,
                'step': 0.1
            }),
            'add_drums': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Título de la canción',
            'model_temperature': 'Creatividad',
            'add_drums': 'Incluir batería'
        }
        help_texts = {
            'title': 'Nombre para identificar la nueva canción generada',
            'model_temperature': 'Controla la creatividad (0.1 = conservadora, 2.0 = muy creativa)',
            'add_drums': 'Incluir elementos de percusión en la generación'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        
        # Establecer valor por defecto para temperatura si es una nueva instancia
        if not self.instance.pk:  
            self.fields['model_temperature'].initial = 0.9
            self.fields['add_drums'].initial = False
    
    def clean_model_temperature(self):
        temperature = self.cleaned_data.get('model_temperature')
        if temperature and (temperature < 0.1 or temperature > 2.0):
            raise forms.ValidationError('La creatividad debe estar entre 0.1 y 2.0')
        return temperature
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Asignar valores por defecto optimizados para Orpheus a campos ocultos
        instance.apply_sustains = True
        instance.remove_duplicate_pitches = True
        instance.remove_overlapping_durations = True
        instance.num_prime_tokens = 6656
        instance.num_gen_tokens = 512
        instance.model_top_p = 0.96
        instance.add_outro = False
        
        # Inicializar prime_instruments como lista vacía
        if not hasattr(instance, 'prime_instruments_json') or instance.prime_instruments_json is None:
            instance.prime_instruments_json = []
        
        if commit:
            instance.save()
        return instance

class StemSelectionForm(forms.Form):
    """Formulario para seleccionar múltiples stems para conversión a MIDI"""
    
    def __init__(self, stems_queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        choices = []
        for stem in stems_queryset:
            choices.append((stem.id, f"{stem.song.title} - {stem.get_stem_type_display()}"))
        
        self.fields['selected_stems'] = forms.MultipleChoiceField(
            choices=choices,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            label='Seleccionar stems para convertir'
        )


class MidiSelectionForm(forms.Form):
    """Formulario para seleccionar archivo MIDI para generación"""
    
    def __init__(self, midi_files_queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        choices = []
        for midi_file in midi_files_queryset:
            choices.append((
                midi_file.id, 
                f"{midi_file.stem.song.title} - {midi_file.stem.get_stem_type_display()}"
            ))
        
        self.fields['selected_midi'] = forms.ChoiceField(
            choices=choices,
            widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
            label='Seleccionar archivo MIDI base'
        )
