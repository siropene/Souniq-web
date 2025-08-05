# Procfile para Railway/Heroku
web: gunicorn souniq_web.wsgi --log-file -
worker: celery -A souniq_web worker --loglevel=info
beat: celery -A souniq_web beat --loglevel=info
