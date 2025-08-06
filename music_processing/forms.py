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
    """Formulario para generar nuevas canciones con Orpheus-Music-Transformer"""
    
    class Meta:
        model = GeneratedTrack
        fields = [
            'title', 
            'apply_sustains',
            'remove_duplicate_pitches', 
            'remove_overlapping_durations',
            'num_prime_tokens',
            'num_gen_tokens',
            'model_temperature',
            'model_top_p',
            'add_drums',
            'add_outro'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título para la nueva canción'
            }),
            'apply_sustains': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'remove_duplicate_pitches': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'remove_overlapping_durations': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'num_prime_tokens': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 100,
                'max': 8000,
                'step': 50
            }),
            'num_gen_tokens': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 100,
                'max': 2000,
                'step': 50
            }),
            'model_temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.1,
                'max': 2.0,
                'step': 0.1
            }),
            'model_top_p': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.1,
                'max': 1.0,
                'step': 0.05
            }),
            'add_drums': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'add_outro': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Título de la canción',
            'apply_sustains': 'Aplicar sustains',
            'remove_duplicate_pitches': 'Eliminar notas duplicadas',
            'remove_overlapping_durations': 'Eliminar duraciones superpuestas',
            'num_prime_tokens': 'Tokens de entrada',
            'num_gen_tokens': 'Tokens a generar',
            'model_temperature': 'Creatividad',
            'model_top_p': 'Diversidad (Top-p)',
            'add_drums': 'Incluir batería',
            'add_outro': 'Incluir outro'
        }
        help_texts = {
            'title': 'Nombre para identificar la nueva canción generada',
            'apply_sustains': 'Aplica efectos de sustain a las notas',
            'remove_duplicate_pitches': 'Elimina notas duplicadas para limpiar el MIDI',
            'remove_overlapping_durations': 'Elimina superposiciones de notas',
            'num_prime_tokens': 'Cantidad de música de entrada a usar (100-8000)',
            'num_gen_tokens': 'Cantidad de música nueva a generar (100-2000)',
            'model_temperature': 'Controla la creatividad (0.1 = conservadora, 2.0 = muy creativa)',
            'model_top_p': 'Controla la diversidad en la selección de notas (0.1-1.0)',
            'add_drums': 'Incluir elementos de percusión en la generación',
            'add_outro': 'Generar un final para la pieza musical'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        
        # Establecer valores por defecto optimizados para Orpheus
        if not self.instance.pk:  # Solo para nuevas instancias
            self.fields['apply_sustains'].initial = True
            self.fields['remove_duplicate_pitches'].initial = True
            self.fields['remove_overlapping_durations'].initial = True
            self.fields['num_prime_tokens'].initial = 6656
            self.fields['num_gen_tokens'].initial = 512
            self.fields['model_temperature'].initial = 0.9
            self.fields['model_top_p'].initial = 0.96
            self.fields['add_drums'].initial = False
            self.fields['add_outro'].initial = False
    
    def clean_model_temperature(self):
        temperature = self.cleaned_data.get('model_temperature')
        if temperature and (temperature < 0.1 or temperature > 2.0):
            raise forms.ValidationError('La creatividad debe estar entre 0.1 y 2.0')
        return temperature
    
    def clean_model_top_p(self):
        top_p = self.cleaned_data.get('model_top_p')
        if top_p and (top_p < 0.1 or top_p > 1.0):
            raise forms.ValidationError('La diversidad debe estar entre 0.1 y 1.0')
        return top_p
    
    def clean_num_prime_tokens(self):
        tokens = self.cleaned_data.get('num_prime_tokens')
        if tokens and (tokens < 100 or tokens > 8000):
            raise forms.ValidationError('Los tokens de entrada deben estar entre 100 y 8000')
        return tokens
    
    def clean_num_gen_tokens(self):
        tokens = self.cleaned_data.get('num_gen_tokens')
        if tokens and (tokens < 100 or tokens > 2000):
            raise forms.ValidationError('Los tokens a generar deben estar entre 100 y 2000')
        return tokens
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Inicializar prime_instruments como lista vacía si no está definido
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
