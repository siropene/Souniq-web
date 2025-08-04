from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from datetime import timedelta
import uuid

from .models import UserProfile, PasswordResetToken, LoginAttempt
from .forms import LoginForm, UserRegistrationForm, UserProfileForm, PasswordResetRequestForm, PasswordResetForm


def login_view(request):
    """Vista de login personalizada"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        # Registrar intento de login
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Registrar login exitoso
                LoginAttempt.objects.create(
                    user=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True
                )
                
                # Crear perfil si no existe
                UserProfile.objects.get_or_create(user=user)
                
                messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
                
                next_url = request.GET.get('next', 'core:dashboard')
                return redirect(next_url)
        else:
            # Registrar login fallido
            LoginAttempt.objects.create(
                ip_address=ip_address,
                user_agent=user_agent,
                success=False
            )
            
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """Vista de registro de usuarios"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Crear perfil del usuario
            UserProfile.objects.create(user=user)
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡Cuenta creada para {username}! Ya puedes iniciar sesión.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Vista del perfil del usuario"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    # Estadísticas del usuario
    from music_processing.models import MidiFile
    
    user_stats = {
        'songs_uploaded': request.user.songs.count(),
        'stems_generated': sum(song.stems.count() for song in request.user.songs.all()),
        'midi_files': MidiFile.objects.filter(
            stem__song__user=request.user, 
            status='completed'
        ).count(),
        'tracks_generated': request.user.generated_tracks.count(),
        'member_since': request.user.date_joined,
    }
    
    # Actividad reciente
    recent_logins = LoginAttempt.objects.filter(
        user=request.user,
        success=True
    ).order_by('-attempted_at')[:5]
    
    context = {
        'form': form,
        'profile': profile,
        'user_stats': user_stats,
        'recent_logins': recent_logins,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """Vista para cambiar contraseña"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantener la sesión activa
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor corrige los errores mostrados.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


def password_reset_request_view(request):
    """Vista para solicitar reseteo de contraseña"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Crear token de reseteo
                token = str(uuid.uuid4())
                expires_at = timezone.now() + timedelta(hours=24)
                
                reset_token = PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=expires_at
                )
                
                # Enviar email
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', args=[token])
                )
                
                subject = 'Reseteo de contraseña - SouniQ'
                message = f'''
                Hola {user.get_full_name() or user.username},
                
                Has solicitado resetear tu contraseña. Haz clic en el siguiente enlace para continuar:
                
                {reset_url}
                
                Este enlace expirará en 24 horas.
                
                Si no solicitaste este reseteo, puedes ignorar este email.
                
                Saludos,
                El equipo de SouniQ
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                # Marcar email como verificado
                reset_token.email_verified = True
                reset_token.save()
                
                messages.success(request, 'Se ha enviado un enlace de reseteo a tu email.')
                return redirect('accounts:login')
                
            except User.DoesNotExist:
                messages.error(request, 'No existe un usuario con ese email.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_confirm_view(request, token):
    """Vista para confirmar reseteo de contraseña"""
    reset_token = get_object_or_404(PasswordResetToken, token=token)
    
    if not reset_token.is_valid():
        messages.error(request, 'El enlace de reseteo es inválido o ha expirado.')
        return redirect('accounts:password_reset_request')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            user = reset_token.user
            user.set_password(password)
            user.save()
            
            # Marcar token como usado
            reset_token.used = True
            reset_token.save()
            
            messages.success(request, 'Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.')
            return redirect('accounts:login')
    else:
        form = PasswordResetForm()
    
    context = {
        'form': form,
        'token': token,
        'user': reset_token.user,
    }
    
    return render(request, 'accounts/password_reset_confirm.html', context)


@login_required
def delete_account_view(request):
    """Vista para eliminar cuenta de usuario"""
    if request.method == 'POST':
        confirm = request.POST.get('confirm_delete')
        if confirm == 'DELETE':
            user = request.user
            username = user.username
            
            # Eliminar usuario (esto también eliminará todas las canciones y archivos relacionados)
            user.delete()
            
            messages.success(request, f'La cuenta de {username} ha sido eliminada permanentemente.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Debes escribir "DELETE" para confirmar la eliminación.')
    
    return render(request, 'accounts/delete_account.html')


def get_client_ip(request):
    """Obtener la IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def activity_log_view(request):
    """Vista del registro de actividad del usuario"""
    login_attempts = LoginAttempt.objects.filter(user=request.user).order_by('-attempted_at')
    successful_logins_count = LoginAttempt.objects.filter(user=request.user, success=True).count()
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(login_attempts, 20)
    page_number = request.GET.get('page')
    attempts_page = paginator.get_page(page_number)
    
    context = {
        'login_attempts': attempts_page,
        'successful_logins_count': successful_logins_count,
    }
    
    return render(request, 'accounts/activity_log.html', context)
