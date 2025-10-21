#!/bin/bash

echo "Waiting for database to be ready..."

# Set the correct working directory and Python path
cd /app
export PYTHONPATH=/app:$PYTHONPATH
export DJANGO_SETTINGS_MODULE=horilla.settings

echo "Running database migrations..."
python3 manage.py makemigrations
python3 manage.py migrate

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Creating admin user..."
python3 manage.py createhorillauser --first_name admin --last_name admin --username admin --password admin --email admin@example.com --phone 1234567890

echo "Starting Gunicorn server..."
gunicorn --bind 0.0.0.0:8001 --workers 3 --timeout 120 horilla.wsgi:application
