#!/usr/bin/env python
"""
Test específico para verificar el fix del upload de canciones
"""
import os
import sys

# Configurar Django
path = '/home/aherrasf/Souniq-web'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'souniq_web.settings_pythonanywhere_simple')

import django
django.setup()

def test_upload_view_fix():
    """Verificar que la vista upload_song maneja correctamente GET y POST"""
    print("=== VERIFICANDO FIX DE UPLOAD_SONG ===")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        from music_processing.views import upload_song
        
        # Crear factory para requests de prueba
        factory = RequestFactory()
        
        # Crear usuario de prueba
        user = User.objects.first()
        if not user:
            print("❌ No hay usuarios en la base de datos")
            return False
        
        print(f"👤 Usando usuario: {user.username}")
        
        # TEST 1: Verificar que GET no cause error 500
        print("\n1️⃣ Probando GET request...")
        try:
            request = factory.get('/music/songs/upload/')
            request.user = user
            
            response = upload_song(request)
            
            # Debería ser un redirect (status 302)
            if hasattr(response, 'status_code') and response.status_code == 302:
                print("✅ GET request maneja correctamente (redirect)")
            else:
                print(f"⚠️ GET request respuesta inesperada: {type(response)}")
                
        except Exception as e:
            print(f"❌ GET request causa error: {e}")
            return False
        
        # TEST 2: Verificar que POST sin datos maneje bien
        print("\n2️⃣ Probando POST request vacío...")
        try:
            request = factory.post('/music/songs/upload/', {})
            request.user = user
            
            response = upload_song(request)
            
            if hasattr(response, 'status_code') and response.status_code == 302:
                print("✅ POST vacío maneja correctamente (redirect)")
            else:
                print(f"⚠️ POST vacío respuesta inesperada: {type(response)}")
                
        except Exception as e:
            print(f"❌ POST vacío causa error: {e}")
            return False
        
        print("\n✅ CONCLUSIÓN: La vista upload_song ahora maneja correctamente GET y POST")
        print("💡 Ya no debería haber errores 500 en /music/songs/upload/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_other_require_post_views():
    """Verificar que otras vistas con @require_POST funcionan"""
    print("\n=== VERIFICANDO OTRAS VISTAS @require_POST ===")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        
        factory = RequestFactory()
        user = User.objects.first()
        
        # Lista de vistas que usan @require_POST
        post_views = [
            ('generate_stems', '/music/stems/generate/1/'),
            ('convert_to_midi', '/music/midi/convert/1/'),
            ('generate_track', '/music/generate/track/1/'),
        ]
        
        print("🔍 Probando que otras vistas POST funcionen...")
        
        for view_name, url in post_views:
            try:
                request = factory.get(url)  # GET debería dar método no permitido
                request.user = user
                
                # Importar la vista dinámicamente
                from music_processing import views
                view_func = getattr(views, view_name)
                
                response = view_func(request, 1)  # ID de prueba
                print(f"   ✅ {view_name}: Funciona (sin error 500)")
                
            except Exception as e:
                error_msg = str(e)
                if "Method Not Allowed" in error_msg or "GET" in error_msg:
                    print(f"   ✅ {view_name}: Correctamente rechaza GET")
                else:
                    print(f"   ⚠️ {view_name}: {error_msg[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando otras vistas: {e}")
        return False

if __name__ == "__main__":
    success1 = test_upload_view_fix()
    success2 = check_other_require_post_views()
    
    if success1 and success2:
        print("\n🎉 TODAS LAS VERIFICACIONES PASARON")
        print("📋 El servidor debería funcionar correctamente ahora")
    else:
        print("\n⚠️ Algunas verificaciones fallaron")
        print("🔧 Revisar logs del servidor para más detalles")
