#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py search_index --rebuild
python manage.py runserver 0.0.0.0:8000
