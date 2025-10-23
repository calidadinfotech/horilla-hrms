#!/bin/bash
set -e

echo "Waiting for database to be ready..."

# Set the correct working directory and Python path
cd /app
export PYTHONPATH=/app:$PYTHONPATH
export DJANGO_SETTINGS_MODULE=horilla.settings

echo "Running database migrations..."
python3 manage.py makemigrations
python3 manage.py migrate

echo "Running collectstatic..."
python3 manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 horilla.wsgi:application
