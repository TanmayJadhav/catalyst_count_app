Steps to install the application

1. Clone the repository
2. Create a virtual environment : python -m venv {env name}
3. Activate the virtual environment : {env name}/Scripts/activate
4. Install requirements : pip install -r requirements.txt
5. Change database configurations in settings.py
6. Start django server : python manage.py runserver
7. Install redis and run redis server
8. Start celery : cd catalyst_count then run celery -A catalyst_count worker --concurrency=6 --loglevel=info -P eventlet
