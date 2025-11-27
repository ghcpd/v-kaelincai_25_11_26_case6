import os
import requests
import json
import time
import sys

BASE_URL = os.environ.get('TEST_BASE_URL', 'http://127.0.0.1:5000')

errors = []

# Test /user
try:
    r = requests.get(BASE_URL + '/user', params={'username': 'alice'}, timeout=5)
    if r.status_code != 200:
        errors.append(('/user', r.status_code, r.text))
    else:
        data = r.json().get('data')
        if not data or not any(u.get('name') == 'alice' for u in data):
            errors.append(('/user-missing', r.status_code, r.text))
except Exception as e:
    errors.append(('/user-ex', str(e)))

# Test /backup (create a small file first)
with open('sample.txt', 'w') as f:
    f.write('integration test')

ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'admin-token')
headers = {'X-ADMIN-TOKEN': ADMIN_TOKEN}

try:
    r = requests.post(BASE_URL + '/backup', json={'filename': 'sample.txt'}, headers=headers, timeout=10)
    if r.status_code not in (200, 201):
        errors.append(('/backup', r.status_code, r.text))
except Exception as e:
    errors.append(('/backup-ex', str(e)))

# Test /config
try:
    cfg = {'a':1}
    r = requests.post(BASE_URL + '/config', data=json.dumps(cfg), timeout=5)
    # It should return 200 and JSON with fields
    if r.status_code != 200:
        errors.append(('/config-status', r.status_code, r.text))
except Exception as e:
    errors.append(('/config-ex', str(e)))

# Test /fetch
try:
    r = requests.post(BASE_URL + '/fetch', json={'url': 'https://example.com'}, timeout=10)
    if r.status_code != 200:
        errors.append(('/fetch-status', r.status_code, r.text))
except Exception as e:
    errors.append(('/fetch-ex', str(e)))

if errors:
    print('FAILED Integration Tests')
    for e in errors:
        print(' -', e)
    sys.exit(1)
else:
    print('Integration tests passed')
    sys.exit(0)
