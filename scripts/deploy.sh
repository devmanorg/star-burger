#!/bin/bash

set -e

git pull
docker compose build
systemctl restart starburger
docker exec star-burger-django-1 python manage.py migrate --noinput

docker exec star-burger-django-1 python scripts/report_deploy_rollbar.py
