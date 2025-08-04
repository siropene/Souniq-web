from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, PasswordResetToken, LoginAttempt


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at', 'email_notifications']
    list_filter = ['email_notifications', 'processing_notifications', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_verified', 'phone_verified', 'used', 'created_at', 'expires_at']
    list_filter = ['email_verified', 'phone_verified', 'used', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['created_at']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'success', 'attempted_at']
    list_filter = ['success', 'attempted_at']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['attempted_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
