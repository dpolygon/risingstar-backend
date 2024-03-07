# risingstar-backend
backend for rising stars

# How Do I Run This Backend?
3 easy steps to run:
1. redis-server
2. flask --app server.py run
3. celery -A server.celery worker --loglevel=INFO

# To update requirements.txt
1. pip3 install pipreqs
2. python3 -m pipreqs.pipreqs .