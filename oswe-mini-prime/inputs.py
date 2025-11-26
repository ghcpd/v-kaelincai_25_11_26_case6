import ast
import json
import logging
import os
import sqlite3
import tarfile
import urllib.parse
from ipaddress import ip_address, ip_network

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load secrets from environment to avoid hardcoding them in source code
THIRD_PARTY_API_KEY = os.environ.get("THIRD_PARTY_API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
JWT_SECRET = os.environ.get("JWT_SECRET")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING"))
logger = logging.getLogger(__name__)


def get_db_connection(db_path="user.db"):
    return sqlite3.connect(db_path)


def get_user_by_name(username: str):
    # Simple validation to reduce injection surface
    if not username or len(username) > 100:
        raise ValueError("Invalid username")
    if any(c in username for c in "'\";--"):
        raise ValueError("Invalid username characters")

    conn = get_db_connection()
    cursor = conn.cursor()
    # Use parameterized query to prevent SQL injection
    query = "SELECT id, name, email FROM users WHERE name = ?"
    logger.debug("Executing parameterized query for username=%s", username)
    cursor.execute(query, (username,))
    rows = cursor.fetchall()
    conn.close()
    # Return a list of dicts instead of raw tuples
    return [
        {"id": r[0], "name": r[1], "email": r[2]} for r in rows
    ]


def is_ip_private(hostname: str) -> bool:
    try:
        ip_val = ip_address(hostname)
    except Exception:
        return False

    private_ranges = (
        ip_network("127.0.0.0/8"),
        ip_network("10.0.0.0/8"),
        ip_network("172.16.0.0/12"),
        ip_network("192.168.0.0/16"),
        ip_network("169.254.0.0/16"),
        ip_network("::1/128"),
        ip_network("fc00::/7"),
    )
    return any(ip_val in r for r in private_ranges)


def is_url_allowed(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        host = parsed.hostname
        if not host:
            return False
        # Resolve host to IP and prevent SSRF to internal networks
        # For simplicity avoid private IPs
        try:
            addr = ip_address(host)
            return not is_ip_private(host)
        except Exception:
            # hostname not ip literal; do not allow private hostnames like 'localhost'
            if host in ("localhost", "127.0.0.1", "::1"):
                return False
            # allow public hostnames; a production implementation should resolve and check the IP
            return True
    except Exception:
        return False


def fetch_remote_resource(url: str, timeout: int = 5):
    # Validate URL before making a request to prevent SSRF
    if not is_url_allowed(url):
        raise ValueError("URL not allowed")
    res = requests.get(url, timeout=timeout)
    res.raise_for_status()
    return res.text


def run_backup(filename: str, archive_name: str = "backup.tar.gz"):
    # sanitize filename and prevent path traversal
    if not filename:
        raise ValueError("No filename provided")
    if os.path.isabs(filename) or ".." in filename or "/" in filename or "\\" in filename:
        raise ValueError("Invalid filename")

    if not os.path.exists(filename):
        raise FileNotFoundError("File does not exist")

    # Create tar.gz archive using tarfile to avoid shell-based command injection
    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(filename, arcname=os.path.basename(filename))
    return archive_name


def load_config(config_str: str):
    try:
        return json.loads(config_str)
    except Exception:
        # Literal_eval only handles Python literals (dicts, lists, strings, numbers)
        # and avoids arbitrary code execution like eval()
        return ast.literal_eval(config_str)


@app.route("/user", methods=["GET"])
def user_route():
    username = request.args.get("username", "")
    try:
        users = get_user_by_name(username)
        return jsonify({"data": users}), 200
    except ValueError as e:
        logger.warning("Invalid username: %s", e)
        return jsonify({"error": "Invalid username"}), 400
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Server error"}), 500


@app.route("/fetch", methods=["POST"])
def fetch_route():
    if not request.is_json:
        return jsonify({"error": "Invalid JSON"}), 400
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "Missing url"}), 400
    try:
        data = fetch_remote_resource(url)
        return jsonify({"data": data}), 200
    except ValueError:
        return jsonify({"error": "URL not allowed"}), 400
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Failed to fetch resource"}), 502


@app.route("/backup", methods=["POST"])
def backup_route():
    # protect backup route with a simple admin token header check
    token = request.headers.get("X-ADMIN-TOKEN")
    if ADMIN_TOKEN and token != ADMIN_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    if not request.is_json:
        return jsonify({"error": "Invalid JSON"}), 400
    filename = request.json.get("filename")
    try:
        archive = run_backup(filename)
        return jsonify({"status": "ok", "archive": archive}), 200
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Failed to create backup"}), 500


@app.route("/config", methods=["POST"])
def config_route():
    try:
        cfg = load_config(request.data.decode())
        return jsonify(cfg), 200
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Invalid config"}), 400


def run_app():
    # Allow debug mode only if environment variable explicitly enables it
    debug = os.environ.get("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")
    app.run(debug=debug)


if __name__ == "__main__":
    run_app()
