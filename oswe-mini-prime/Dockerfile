FROM python:3.11-slim
WORKDIR /workspace
COPY . /workspace
RUN pip install --upgrade pip && pip install -r requirements.txt
# Create a sqlite DB for the container
RUN python - <<'PY'
import sqlite3
conn = sqlite3.connect('user.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)')
cur.execute('DELETE FROM users')
cur.execute('INSERT INTO users (name, email) VALUES (?, ?)', ('alice','alice@example.com'))
conn.commit()
conn.close()
PY
CMD ["/bin/bash","-lc","sh run_test.sh inputs.py || exit 1"]
