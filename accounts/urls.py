from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    path('activity/', views.activity_log_view, name='activity_log'),
]
