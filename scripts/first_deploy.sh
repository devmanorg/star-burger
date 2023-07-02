#!/bin/bash

cp starburger.service.template /etc/systemd/system/starburger.service
systemctl daemon-reload
systemctl enable starburger
systemctl start starburger

docker exec star-burger-django-1 python manage.py migrate
docker exec star-burger-django-1 python manage.py loaddata data/db_dump.json

venv/bin/python scripts/report_deploy_rollbar.py
