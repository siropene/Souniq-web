# WSGI config for PythonAnywhere
import os
import sys

# Añadir el directorio del proyecto al path
path = '/home/tuusername/souniq_web'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar Django settings para producción
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
