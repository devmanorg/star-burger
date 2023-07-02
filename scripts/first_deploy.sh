#!/bin/bash

set -e

if [ ! -f data/db_dump.json ]; then
    echo "Error: data/db_dump.json does not exist"
    exit 1
fi

if [ ! -d media ] || [ ! "$(ls -A media)" ]; then
    echo "Error: media directory does not exist or is empty"
    exit 1
fi

cp starburger.service.template /etc/systemd/system/starburger.service
systemctl daemon-reload
systemctl enable starburger
systemctl start starburger

docker exec star-burger-django-1 python manage.py migrate
docker exec star-burger-django-1 python manage.py loaddata data/db_dump.json

docker exec star-burger-django-1 python scripts/report_deploy_rollbar.py
