#!/bin/bash

# Script para preparar directorios necesarios en PythonAnywhere
echo "Creando directorios necesarios para el proyecto..."

# Crear directorio de logs si no existe
mkdir -p /home/aherrasf/Souniq-web/logs
echo "✓ Directorio de logs creado"

# Crear directorios de media si no existen
mkdir -p /home/aherrasf/Souniq-web/media/songs/original
mkdir -p /home/aherrasf/Souniq-web/media/stems
mkdir -p /home/aherrasf/Souniq-web/media/midi
mkdir -p /home/aherrasf/Souniq-web/media/generated_tracks
echo "✓ Directorios de media creados"

# Asegurarse de que staticfiles existe
mkdir -p /home/aherrasf/Souniq-web/staticfiles
echo "✓ Directorio de staticfiles creado"

echo "¡Directorios preparados correctamente!"
