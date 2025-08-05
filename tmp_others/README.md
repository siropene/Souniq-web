# tmp_others - Archivos No Esenciales para Producción

Esta carpeta contiene archivos que no son necesarios para el funcionamiento actual de la web en producción, pero que podrían ser útiles para referencia futura o desarrollo en diferentes plataformas.

## Categorías de Archivos Movidos:

### Scripts de Despliegue Alternativos
- `deploy.sh` - Script de despliegue general
- `prepare_pythonanywhere.sh` - Script de preparación para PythonAnywhere  
- `deploy_heroku.sh` - Script específico para Heroku
- `prepare_railway.sh` - Script específico para Railway

### Configuración de Plataformas Alternativas
- `Procfile` - Configuración para Heroku
- `runtime.txt` - Especificación de runtime para Heroku
- `wsgi_production.py` - WSGI alternativo para producción
- `wsgi_pythonanywhere.py` - WSGI específico de PythonAnywhere alternativo

### Requirements Alternativos
- `requirements-essential.txt` - Dependencias esenciales mínimas
- `requirements-minimal.txt` - Dependencias mínimas
- `requirements-minimal-test.txt` - Dependencias para testing mínimo
- `requirements-production.txt` - Requirements de producción alternativos
- `requirements-pythonanywhere-full.txt` - Requirements completos para PythonAnywhere

### Documentación de Plataformas/Desarrollo
- `CHOOSE_PLATFORM.md` - Guía para elegir plataforma de despliegue
- `DEPLOYMENT_GUIDE.md` - Guía básica de despliegue
- `DEPLOYMENT_GUIDE_COMPLETE.md` - Guía completa de despliegue
- `HUGGINGFACE_SETUP.md` - Configuración de Hugging Face
- `SESSION_STATE.md` - Documentación de estado de sesión

### Scripts de Desarrollo/Debug
- `start_dev.sh` - Script de inicio para desarrollo
- `create_directories.sh` - Script de creación de directorios
- `check_dependencies.sh` - Verificación de dependencias
- `check_disk_space.sh` - Verificación de espacio en disco
- `fix_pythonanywhere_instructions.py` - Corrección de instrucciones

### Archivos Temporales/Testing
- `Prompt.rtf` - Archivo de prompts temporal
- `pythonanywhere_commands.txt` - Comandos temporales de PythonAnywhere

## Nota Importante:
Estos archivos fueron movidos aquí para mantener limpio el directorio principal de producción. La aplicación web actual está desplegada en **PythonAnywhere** y utiliza:
- `requirements-pythonanywhere.txt` (archivo principal de requirements)
- `PYTHONANYWHERE_GUIDE.md` (guía principal de despliegue)
- Los settings y configuraciones en `souniq_web/`

## Estado Actual del Proyecto:
- ✅ Pipeline completo funcional (separación de stems → conversión MIDI → generación musical)
- ✅ APIs de Hugging Face integradas correctamente
- ✅ Gradio-client actualizado a versión 1.11.0
- ✅ Correcciones de parámetros y campos de modelo aplicadas
- ✅ Organización de proyecto completada

Última actualización: Diciembre 2024
