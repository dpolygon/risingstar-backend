. venv/bin/activate
redis-server 
flask --app server.py run 
celery -A server.celery worker --loglevel=INFO
$SHELL