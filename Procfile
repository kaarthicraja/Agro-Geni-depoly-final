web: npm run build && pip install -r backend/requirements.txt && python -m gunicorn --chdir backend app:app -w 4 -b 0.0.0.0:$PORT
