#!/bin/bash

set -e

if [ "$EUID" -ne 0 ]
  then
    echo "Please run as root."
    exit
fi

git pull
npm ci --dev
npm audit fix
venv/bin/pip install -U -r requirements.txt
node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
venv/bin/python manage.py collectstatic --noinput
venv/bin/python manage.py migrate --noinput
systemctl restart starburger-django.service
systemctl reload nginx

venv/bin/python scripts/report_deploy_rollbar.py

echo "Project updated."
