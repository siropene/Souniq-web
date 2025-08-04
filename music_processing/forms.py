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
    """Formulario simplificado para generar nuevas canciones"""
    
    class Meta:
        model = GeneratedTrack
        fields = ['title', 'gen_drums', 'model_temperature']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título para la nueva canción'
            }),
            'gen_drums': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'model_temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0.5,
                'max': 1.5,
                'step': 0.1,
                'value': 1.0
            })
        }
        labels = {
            'title': 'Título de la canción',
            'gen_drums': 'Incluir batería',
            'model_temperature': 'Creatividad'
        }
        help_texts = {
            'title': 'Nombre para identificar la nueva canción generada',
            'gen_drums': 'Marcar para incluir elementos de batería en la generación',
            'model_temperature': 'Controla la creatividad (0.5 = conservadora, 1.5 = muy creativa)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        
        # Establecer valores por defecto
        if not self.instance.pk:  # Solo para nuevas instancias
            self.fields['model_temperature'].initial = 1.0
            self.fields['gen_drums'].initial = True
    
    def clean_model_temperature(self):
        temperature = self.cleaned_data.get('model_temperature')
        if temperature and (temperature < 0.5 or temperature > 1.5):
            raise forms.ValidationError('La creatividad debe estar entre 0.5 y 1.5')
        return temperature
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Establecer valores fijos optimizados para los campos ocultos
        instance.num_prime_tokens = 2000  # Máximo admisible
        instance.num_gen_tokens = 2000    # Máximo admisible  
        instance.num_mem_tokens = 10000   # Máximo admisible
        instance.gen_outro = 'Force'      # Siempre incluir outro
        instance.model_sampling_top_p = 0.9  # Valor óptimo
        
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
