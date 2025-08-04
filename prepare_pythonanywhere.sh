#!/bin/bash
# Script para preparar despliegue en PythonAnywhere

echo "🐍 PREPARACIÓN PARA PYTHONANYWHERE"
echo "=================================="

# Solicitar nombre de usuario
read -p "🔑 Ingresa tu nombre de usuario de PythonAnywhere: " username

if [ -z "$username" ]; then
    echo "❌ Necesitas proporcionar tu nombre de usuario"
    exit 1
fi

echo "🔧 Configurando para usuario: $username"

# 1. Actualizar settings_pythonanywhere.py
echo "📝 Actualizando configuración de Django..."

# Crear backup
cp souniq_web/settings_pythonanywhere.py souniq_web/settings_pythonanywhere.py.bak

# Reemplazar tuusername con el usuario real
sed -i.bak "s/tuusername/$username/g" souniq_web/settings_pythonanywhere.py

echo "✅ Configuración actualizada en settings_pythonanywhere.py"

# 2. Crear archivo WSGI personalizado
echo "📄 Creando archivo WSGI..."

cat > wsgi_pythonanywhere.py << EOF
import os
import sys

# Añadir path del proyecto
path = '/home/$username/souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere')

# Variables de entorno importantes
os.environ['DEBUG'] = 'False'
# Recuerda configurar DB_PASSWORD en PythonAnywhere

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOF

echo "✅ Archivo WSGI creado: wsgi_pythonanywhere.py"

# 3. Crear archivo de comandos para PythonAnywhere
echo "📋 Creando script de comandos para PythonAnywhere..."

cat > pythonanywhere_commands.txt << EOF
# COMANDOS PARA EJECUTAR EN PYTHONANYWHERE
# =====================================

# 1. Clonar repositorio (si usas Git)
git clone https://github.com/tu-usuario/souniq-web.git
cd souniq-web

# 2. Crear y activar entorno virtual
mkvirtualenv --python=/usr/bin/python3.11 souniq-env
workon souniq-env

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variable de entorno de base de datos
# En la consola Bash:
export DB_PASSWORD='tu_password_mysql_aqui'

# 5. Ejecutar migraciones
python manage.py migrate --settings=souniq_web.settings_pythonanywhere

# 6. Recopilar archivos estáticos
python manage.py collectstatic --noinput --settings=souniq_web.settings_pythonanywhere

# 7. Crear superusuario
python manage.py createsuperuser --settings=souniq_web.settings_pythonanywhere

# 8. Configurar aplicación web en el dashboard:
# - Source code: /home/$username/souniq-web
# - Virtualenv: /home/$username/.virtualenvs/souniq-env
# - WSGI file: copiar contenido de wsgi_pythonanywhere.py
# - Static files: /static/ -> /home/$username/souniq-web/staticfiles/
# - Static files: /media/ -> /home/$username/souniq-web/media/

EOF

echo "✅ Comandos guardados en: pythonanywhere_commands.txt"

# 4. Verificar archivos necesarios
echo "🔍 Verificando archivos necesarios..."

required_files=(
    "requirements.txt"
    "manage.py"
    "souniq_web/settings.py"
    "souniq_web/settings_pythonanywhere.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - FALTA"
    fi
done

# 5. Crear requirements.txt optimizado si no existe
if [ ! -f "requirements-pythonanywhere.txt" ]; then
    echo "📦 Creando requirements específicos para PythonAnywhere..."
    
    cat > requirements-pythonanywhere.txt << EOF
Django==4.2.23
Pillow==10.0.0
whitenoise==6.5.0
mysqlclient==2.2.0
python-decouple==3.8
django-cleanup==8.0.0
librosa==0.10.1
pretty_midi==0.2.10
basic-pitch==0.3.0
spleeter==2.3.2
tensorflow==2.13.0
requests==2.31.0
numpy==1.24.3
pandas==2.0.3
scipy==1.11.1
EOF
    
    echo "✅ Archivo requirements-pythonanywhere.txt creado"
fi

echo ""
echo "🎉 ¡PREPARACIÓN COMPLETADA!"
echo ""
echo "📁 ARCHIVOS GENERADOS:"
echo "  - wsgi_pythonanywhere.py"
echo "  - pythonanywhere_commands.txt"
echo "  - requirements-pythonanywhere.txt"
echo "  - settings_pythonanywhere.py (actualizado)"
echo ""
echo "🚀 PRÓXIMOS PASOS:"
echo "1. Sube tu código a PythonAnywhere (Git o Files)"
echo "2. Sigue los comandos en pythonanywhere_commands.txt"
echo "3. Copia el contenido de wsgi_pythonanywhere.py al WSGI file"
echo "4. Configura la base de datos MySQL en el dashboard"
echo "5. ¡Disfruta tu app en $username.pythonanywhere.com!"
echo ""
echo "📖 GUÍA COMPLETA: PYTHONANYWHERE_GUIDE.md"
