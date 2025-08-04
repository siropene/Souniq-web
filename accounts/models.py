from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """Perfil extendido del usuario"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Configuraciones de usuario
    email_notifications = models.BooleanField(default=True)
    processing_notifications = models.BooleanField(default=True)
    
    # Metadatos
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


class PasswordResetToken(models.Model):
    """Tokens para reseteo de contraseña con doble factor"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Reset token para {self.user.username}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.used and not self.is_expired() and self.email_verified


class LoginAttempt(models.Model):
    """Registro de intentos de login para seguridad"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField()
    attempted_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        status = "exitoso" if self.success else "fallido"
        username = self.user.username if self.user else "usuario desconocido"
        return f"Login {status} - {username} desde {self.ip_address}"
