#!/bin/bash
# Make Migrations
python backend/manage.py makemigrations
# Run migrations
python backend/manage.py migrate
# Collect static files
python backend/manage.py collectstatic --noinput
# Start the application
gunicorn --worker-class gevent --bind 0.0.0.0:3376 backend.wsgi:application