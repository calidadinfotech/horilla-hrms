#!/bin/bash

echo "Waiting for database to be ready..."
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput
python3 manage.py createhorillauser --first_name Samay --last_name Thakkar --username samay.thakkar --password horilla@123* --email samay.thakkar@calidadinfotech.com --phone 1234567890
gunicorn --bind 0.0.0.0:8001 horilla.wsgi:application
