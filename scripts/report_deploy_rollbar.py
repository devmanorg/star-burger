import subprocess

import requests
from environs import Env


env = Env()
env.read_env()

commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], encoding='UTF-8').strip()

url = 'https://api.rollbar.com/api/1/deploy'
headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'X-Rollbar-Access-Token': env.str('ROLLBAR_TOKEN'),
}
data = {
    'environment': env.str('ROLLBAR_ENV'),
    'revision': commit_hash,
    # 'status': 'succeeded',
    'rollbar_username': env.str('ROLLBAR_USERNAME')
}

response = requests.post(url, headers=headers, json=data)
response.raise_for_status()
