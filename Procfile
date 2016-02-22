web: gunicorn manage:app --log-file -
worker: python manage.py runserver --host=0.0.0.0 --port=80
