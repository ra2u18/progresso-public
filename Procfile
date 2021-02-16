web: flask db upgrade; gunicorn run:app
worker: rq worker -u $REDIS_URL progresso-tasks