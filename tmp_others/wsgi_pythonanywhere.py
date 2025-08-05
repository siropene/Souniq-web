import os
import sys

# Añadir path del proyecto
path = '/home/aherrasf/souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere')

# Variables de entorno importantes
os.environ['DEBUG'] = 'False'
# Recuerda configurar DB_PASSWORD en PythonAnywhere

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
