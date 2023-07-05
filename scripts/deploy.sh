#!/bin/bash

set -e

git pull
docker compose build django
docker compose restart django
docker exec starburger_django python manage.py migrate --noinput

docker exec starburger_django python scripts/report_deploy_rollbar.py
