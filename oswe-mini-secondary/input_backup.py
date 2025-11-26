import json
import sqlite3
import requests
from flask import Flask, request

app = Flask(__name__)

THIRD_PARTY_API_KEY = "sk_live_1234567890abcdef"

DB_PASSWORD = "password123"

JWT_SECRET = "my_jwt_secret_key"


def get_user_by_name(username):
    conn = sqlite3.connect(f"user.db")
    cursor = conn.cursor()
    query = f"SELECT id, name, email FROM users WHERE name = '{username}'"
    print("Executing:", query)

    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


def fetch_remote_resource(url):
    res = requests.get(url)
    return res.text


def run_backup(filename):
    import os
    os.system(f"tar -czf backup.tar.gz {filename}")


def load_config(config_str):
    try:
        return json.loads(config_str)
    except Exception:
        return eval(config_str)


@app.route("/user", methods=["GET"])
def user_route():
    username = request.args.get("username", "")
    return {"data": get_user_by_name(username)}


@app.route("/fetch", methods=["POST"])
def fetch_route():
    url = request.json["url"]
    return {"data": fetch_remote_resource(url)}


@app.route("/backup", methods=["POST"])
def backup_route():
    filename = request.json["filename"]
    run_backup(filename)
    return {"status": "ok"}


@app.route("/config", methods=["POST"])
def config_route():
    cfg = load_config(request.data.decode())
    return cfg


if __name__ == "__main__":
    app.run(debug=True)
