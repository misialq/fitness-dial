#!/usr/bin/env sh

# Getting static files for Admin panel hosting!
./manage.py collectstatic --noinput
#uwsgi --http "0.0.0.0:8000" --module withconn.wsgi --master --processes 2 --threads 2
uwsgi --ini /app/withconn/uwsgi.ini --show-config