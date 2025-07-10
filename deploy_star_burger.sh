#!/bin/bash
set -e
set -o pipefail
echo "Начинаем деплой."
cd /root/opt/star-burger
git pull origin master
source env/bin/activate
pip install -r requirements.txt
npm install
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url "./"
python manage.py collectstatic --noinput
python manage.py migrate
echo "Перезапускаем сервисы"
systemctl restart docker.service
systemctl restart postgresql.service
systemctl reload nginx.service
systemctl restart star-burger.service
echo "Деплой успешно завершён!"
