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

scripts/init_letsencrypt.sh

cp systemd_units/* /etc/systemd/system/
systemctl daemon-reload
systemctl enable starburger.target
systemctl start starburger.target

docker exec starburger_django python manage.py migrate
docker exec starburger_django python manage.py loaddata data/db_dump.json

docker exec starburger_django python scripts/report_deploy_rollbar.py

echo "Deploy successful."
