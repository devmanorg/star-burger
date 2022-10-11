#!/bin/bash

set -e

cd star-burger/
source ~/star-burger.env/bin/activate
git pull
pip install -q -r requirements.txt
/home/burger/.nvm/versions/node/v16.17.1/bin/npm ci --include=dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python manage.py collectstatic --noinput
python manage.py migrate
sudo /usr/bin/systemctl restart postgresql.service
sudo /usr/bin/systemctl restart gunicorn.socket
sudo /usr/bin/systemctl reload nginx.service
https -q POST https://api.rollbar.com/api/1/deploy X-Rollbar-Access-Token:POST_SERVER_ACCESS_TOKEN \
                        Content-Type:application/json environment=ruvds revision=$(git rev-parse HEAD) \
                        local_username=burger status=succeeded
echo Deploy complete!
