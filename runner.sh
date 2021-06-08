#!/usr/bin/env sh

# Getting static files for Admin panel hosting!
./manage.py collectstatic --noinput
#uwsgi --http "0.0.0.0:8000" --module dial.wsgi --master --processes 2 --threads 2
uwsgi --ini /app/dial/uwsgi.ini --show-config