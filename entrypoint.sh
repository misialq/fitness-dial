#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 1
    done
    echo "PostgreSQL started"
fi

python manage.py flush --no-input

if [ "$APPLY_MIGRATIONS" = "true" ]
then
  echo "Applying migrations..."
  python manage.py migrate
  echo "Migrations applied"
fi

exec "$@"