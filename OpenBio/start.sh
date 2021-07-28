#!/bin/bash

python manage.py migrate --run-syncdb && \
python manage.py makemigrations && \
python manage.py migrate

python manage.py runserver 0.0.0.0:8200
