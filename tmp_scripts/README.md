# Scripts Temporales de Debugging y Testing

Esta carpeta contiene todos los scripts que se crearon durante el proceso de debugging y corrección del pipeline de Souniq.

## 📁 Categorías de Scripts

### 🧪 Scripts de Testing
- `test_*.py` - Scripts para probar diferentes aspectos del pipeline
- `test_production_generation.py` - Test completo del pipeline de generación
- `test_correct_syntax.py` - Test de la sintaxis correcta de la API
- `test_final_syntax.py` - Test final con argumentos posicionales
- `test_conservative_values.py` - Test con valores conservadores

### 🔍 Scripts de Diagnóstico
- `diagnostic_*.py` - Diagnósticos generales del sistema
- `diagnose_midi_quality.py` - Análisis de calidad de archivos MIDI
- `diagnostic_hf_apis.py` - Diagnóstico de APIs de Hugging Face
- `diagnostic_pythonanywhere.py` - Diagnóstico específico de PythonAnywhere

### 🔎 Scripts de Investigación
- `inspect_*.py` - Inspección de respuestas de APIs
- `investigate_*.py` - Investigación de estructuras de APIs
- `find_working_endpoints.py` - Búsqueda de endpoints funcionales

### ✅ Scripts de Verificación
- `verify_pipeline_complete.py` - Verificación completa del estado del pipeline

## 🎯 Propósito

Estos scripts fueron creados para:

1. **Debugging del Pipeline**: Identificar y corregir errores en las APIs
2. **Testing de Componentes**: Probar cada parte del sistema por separado
3. **Validación de Sintaxis**: Encontrar la sintaxis correcta para las APIs
4. **Monitoreo del Estado**: Verificar el estado del sistema completo

## 📝 Notas Importantes

- **Estos scripts son temporales** y fueron usados durante el desarrollo
- El pipeline principal está en `music_processing/tasks_sync.py`
- La mayoría de estos scripts requieren configuración de Django
- Algunos pueden requerir cuota GPU disponible en Hugging Face

## 🚀 Estado Final

El pipeline está **completamente funcional** con las siguientes correcciones aplicadas:

✅ **API Giant-Music-Transformer**: 
- Sintaxis corregida (argumentos posicionales)
- Uso de `handle_file()` para archivos MIDI
- `gen_outro` como string (`"Auto"` o `"Disable"`)
- Manejo robusto de diferentes formatos de respuesta

✅ **Modelo GeneratedVersion**: Campo `track` corregido

✅ **Manejo de errores**: Implementado con reintentos automáticos

✅ **Validación MIDI**: Implementada para archivos de entrada

## 🗑️ Limpieza

Estos scripts pueden ser eliminados una vez que el sistema esté en producción estable.
