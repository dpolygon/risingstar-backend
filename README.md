# risingstar-backend
backend for rising stars

# How Do I Run This Backend?
3 easy steps to run:
1. redis-server
2. flask --app server.py run
3. celery -A server.celery worker --loglevel=INFO