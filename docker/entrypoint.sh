#!/bin/bash
set -e

echo "Starting Horilla HR..."

# Wait for PostgreSQL to be ready (using cloud DB host from env)
echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL is ready!"

# Run migrations
python manage.py makemigrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
