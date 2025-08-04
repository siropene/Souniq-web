from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        
        # Personalizar etiquetas
        self.fields['username'].label = 'Usuario'
        self.fields['password'].label = 'Contraseña'


class UserRegistrationForm(UserCreationForm):
    """Formulario de registro de usuarios"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellidos'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
        
        # Personalizar etiquetas
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['first_name'].label = 'Nombre'
        self.fields['last_name'].label = 'Apellidos'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este correo electrónico.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario"""
    
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'birth_date', 'bio', 'avatar', 'email_notifications', 'processing_notifications']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+34 123 456 789'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cuéntanos algo sobre ti...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'processing_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'phone_number': 'Número de teléfono',
            'birth_date': 'Fecha de nacimiento',
            'bio': 'Biografía',
            'avatar': 'Foto de perfil',
            'email_notifications': 'Recibir notificaciones por email',
            'processing_notifications': 'Notificar cuando terminen los procesamientos'
        }
    
    # Campos adicionales para datos del usuario
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        label='Apellidos'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        }),
        label='Correo electrónico'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(id=self.user.id).exists():
            raise ValidationError('Ya existe otro usuario con este correo electrónico.')
        return email
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError('La imagen no puede superar los 5MB.')
        return avatar
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if self.user:
            # Actualizar datos del usuario
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        
        if commit:
            profile.save()
        return profile


class PasswordResetRequestForm(forms.Form):
    """Formulario para solicitar reseteo de contraseña"""
    
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Introduce tu correo electrónico'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No existe un usuario con este correo electrónico.')
        return email


class PasswordResetForm(forms.Form):
    """Formulario para establecer nueva contraseña"""
    
    password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        min_length=8
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        # Validaciones de contraseña
        if len(password1) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        
        if password1.isdigit():
            raise ValidationError('La contraseña no puede ser solo números.')
        
        if password1.lower() in ['password', 'contraseña', '12345678', 'qwerty']:
            raise ValidationError('La contraseña es demasiado común.')
        
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return password2


class UserPreferencesForm(forms.ModelForm):
    """Formulario para configurar preferencias del usuario"""
    
    class Meta:
        model = UserProfile
        fields = ['email_notifications', 'processing_notifications']
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'processing_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'email_notifications': 'Recibir notificaciones por email',
            'processing_notifications': 'Notificar cuando terminen los procesamientos'
        }
