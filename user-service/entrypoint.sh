#!/bin/sh

python ./user_service/manage.py makemigrations

python ./user_service/manage.py migrate

python ./user_service/manage.py runserver 0.0.0.0:8000