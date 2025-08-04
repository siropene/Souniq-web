# Configuración para producción en PythonAnywhere
import os
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Hosts permitidos - ajustar con tu dominio de PythonAnywhere
ALLOWED_HOSTS = ['tuusername.pythonanywhere.com', 'localhost', '127.0.0.1']

# Base de datos para producción (MySQL en PythonAnywhere)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tuusername$souniq_db',
        'USER': 'tuusername',
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': 'tuusername.mysql.pythonanywhere-services.com',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = '/home/tuusername/souniq_web/staticfiles'

# Configuración de archivos de media
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/tuusername/souniq_web/media'

# Configuración de Redis para Celery (limitado en cuenta gratuita)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Configuración de archivos estáticos con WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuración de seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/home/tuusername/souniq_web/logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'music_processing': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
