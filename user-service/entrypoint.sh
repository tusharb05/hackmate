#!/bin/sh

python -u ./user_service/manage.py makemigrations

python -u ./user_service/manage.py migrate

python -u ./user_service/manage.py runserver 0.0.0.0:8000