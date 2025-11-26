#!/usr/bin/env bash
set -e

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create a simple sqlite DB for tests
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect('user.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)')
cur.execute('DELETE FROM users')
cur.execute('INSERT INTO users (name, email) VALUES (?, ?)', ('alice','alice@example.com'))
conn.commit()
conn.close()
PY

# Create a sample file to test backup
printf 'hello world' > sample.txt

printf "Setup completed. Use run_test.sh to run tests.\n"
