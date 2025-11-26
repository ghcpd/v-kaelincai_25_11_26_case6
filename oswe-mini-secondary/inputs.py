import ast
import json
import logging
import os
import sqlite3
import tarfile
import pathlib
import socket
import ipaddress
from urllib.parse import urlparse

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load sensitive configuration from environment variables (do not hard-code in source)
THIRD_PARTY_API_KEY = os.environ.get("THIRD_PARTY_API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
JWT_SECRET = os.environ.get("JWT_SECRET")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_db_connection():
    db_path = os.environ.get("USER_DB_PATH", "user.db")
    # Ensure db path is a simple filename (no path traversal)
    db_file = pathlib.Path(db_path).name
    return sqlite3.connect(db_file)


def get_user_by_name(username: str):
    # Basic validation: require a short username string
    if not isinstance(username, str) or len(username) == 0 or len(username) > 200:
        raise ValueError("invalid username")

    # Use parameterized queries to avoid SQL injection
    conn = _get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, name, email FROM users WHERE name = ? LIMIT 100"
    logger.debug("Executing DB query with parameterized input")

    cursor.execute(query, (username,))
    result = cursor.fetchall()
    conn.close()
    return result


def _is_safe_url(url: str):
    # Simple checks: allow only http/https and disallow private/reserved addresses
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False

    hostname = parsed.hostname
    if not hostname:
        return False

    try:
        # Resolve hostname to IP(s)
        for family in (socket.AF_INET, socket.AF_INET6):
            try:
                for res in socket.getaddrinfo(hostname, None, family):
                    ip = res[4][0]
                    ip_obj = ipaddress.ip_address(ip)
                    if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_unspecified or ip_obj.is_reserved:
                        return False
            except socket.gaierror:
                continue
    except Exception:
        return False

    return True


def fetch_remote_resource(url: str, timeout: float = 5.0):
    if not _is_safe_url(url):
        raise ValueError("disallowed url")

    # Always provide a timeout and verify SSL certs
    res = requests.get(url, timeout=timeout)
    res.raise_for_status()
    return res.text


def run_backup(filename: str, base_dir: str = "./"):
    # Prevent path traversal and avoid executing shell directly
    safe_base = pathlib.Path(base_dir).resolve()
    target = pathlib.Path(filename)

    # Ensure target resolves under safe_base
    try:
        target_resolved = target.resolve()
    except RuntimeError:
        raise ValueError("invalid filename")

    if not str(target_resolved).startswith(str(safe_base)):
        raise ValueError("filename outside allowed directory")

    archive_path = safe_base / "backup.tar.gz"
    # Use tarfile module rather than shelling out
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(target_resolved, arcname=target_resolved.name)

    return str(archive_path)


def load_config(config_str: str):
    # Config should be JSON. Do not fallback to eval which permits code execution.
    try:
        return json.loads(config_str)
    except json.JSONDecodeError:
        # As a safe fallback we can attempt literal eval of basic Python literals
        try:
            return ast.literal_eval(config_str)
        except Exception:
            raise ValueError("invalid config format")


@app.route("/user", methods=["GET"])
def user_route():
    username = request.args.get("username", "")
    try:
        data = get_user_by_name(username)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"data": data})


@app.route("/fetch", methods=["POST"])
def fetch_route():
    payload = request.get_json(silent=True)
    if not payload or "url" not in payload:
        return jsonify({"error": "missing url"}), 400

    url = payload["url"]
    try:
        data = fetch_remote_resource(url)
    except Exception as e:
        logger.warning("fetch error: %s", e)
        return jsonify({"error": "failed to fetch resource"}), 400

    return jsonify({"data": data})


@app.route("/backup", methods=["POST"])
def backup_route():
    payload = request.get_json(silent=True)
    if not payload or "filename" not in payload:
        return jsonify({"error": "missing filename"}), 400

    filename = payload["filename"]
    try:
        archive = run_backup(filename)
    except Exception as e:
        logger.warning("backup failed: %s", e)
        return jsonify({"error": "backup failed"}), 400

    return jsonify({"status": "ok", "archive": archive})


@app.route("/config", methods=["POST"])
def config_route():
    raw = request.data.decode() or ""
    try:
        cfg = load_config(raw)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(cfg)


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    # Ensure debug mode is controlled by environment only
    app.run(debug=debug)
