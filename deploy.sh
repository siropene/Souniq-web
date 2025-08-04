#!/bin/bash
# Script para deployment en PythonAnywhere

# 1. Crear directorios necesarios
mkdir -p /home/tuusername/souniq_web/logs
mkdir -p /home/tuusername/souniq_web/staticfiles
mkdir -p /home/tuusername/souniq_web/media

# 2. Instalar dependencias
pip3.11 install --user -r requirements-production.txt

# 3. Recopilar archivos estáticos
python3.11 manage.py collectstatic --noinput --settings=souniq_web.settings_production

# 4. Ejecutar migraciones
python3.11 manage.py migrate --settings=souniq_web.settings_production

# 5. Crear superusuario (opcional)
# python3.11 manage.py createsuperuser --settings=souniq_web.settings_production

echo "Deployment completado. Recuerda:"
echo "1. Configurar la aplicación web en PythonAnywhere"
echo "2. Establecer DJANGO_SETTINGS_MODULE=souniq_web.settings_production"
echo "3. Configurar la base de datos MySQL"
echo "4. Subir archivos de media si es necesario"
