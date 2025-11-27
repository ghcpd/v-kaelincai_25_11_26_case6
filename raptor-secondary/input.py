import ast
import json
import os
import sqlite3
import tarfile
from pathlib import Path
import ipaddress
import socket
from urllib.parse import urlparse

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Secrets are loaded from environment variables. These defaults are placeholders and MUST be overridden in production.
THIRD_PARTY_API_KEY = os.environ.get("THIRD_PARTY_API_KEY", "CHANGE_ME_THIRD_PARTY_API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "CHANGE_ME_DB_PASSWORD")
JWT_SECRET = os.environ.get("JWT_SECRET", "CHANGE_ME_JWT_SECRET")


def get_user_by_name(username: str):
    """Fetch a user by name using a parameterized query to prevent SQL injection."""
    if not username:
        return []

    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE name = ?", (username,))
    result = cursor.fetchall()
    conn.close()
    return result


def _is_url_allowed(url: str) -> bool:
    """Basic SSRF protection: allow only http(s) and block private/internal addresses."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if host is None:
        return False
    try:
        addrinfos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False

    for family, _, _, _, sockaddr in addrinfos:
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
        except ValueError:
            return False
    return True


def fetch_remote_resource(url: str):
    if not _is_url_allowed(url):
        raise ValueError("URL not allowed")
    res = requests.get(url, timeout=5, allow_redirects=False)
    res.raise_for_status()
    return res.text


def run_backup(filename: str):
    """Create a tar.gz backup of a file safely without shell execution."""
    base_dir = Path.cwd()
    target_path = (base_dir / filename).resolve()

    if not target_path.exists() or not target_path.is_file():
        raise FileNotFoundError(f"File not found: {filename}")

    # Ensure the file is within the current working directory to prevent path traversal
    if base_dir not in target_path.parents and target_path != base_dir:
        raise PermissionError("Invalid backup path")

    backup_name = base_dir / "backup.tar.gz"
    with tarfile.open(backup_name, "w:gz") as tar:
        tar.add(target_path, arcname=target_path.name)
    return str(backup_name)


def load_config(config_str: str):
    """Load configuration safely using JSON or literal_eval instead of eval."""
    try:
        return json.loads(config_str)
    except Exception:
        try:
            return ast.literal_eval(config_str)
        except Exception:
            raise ValueError("Invalid config format")


@app.route("/user", methods=["GET"])
def user_route():
    username = request.args.get("username", "").strip()
    if not username:
        return jsonify({"error": "username is required"}), 400
    if len(username) > 255:
        return jsonify({"error": "username too long"}), 400
    return jsonify({"data": get_user_by_name(username)})


@app.route("/fetch", methods=["POST"])
def fetch_route():
    body = request.get_json(silent=True) or {}
    url = body.get("url", "").strip()
    if not url:
        return jsonify({"error": "url is required"}), 400
    try:
        data = fetch_remote_resource(url)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"data": data})


@app.route("/backup", methods=["POST"])
def backup_route():
    body = request.get_json(silent=True) or {}
    filename = body.get("filename", "").strip()
    if not filename:
        return jsonify({"error": "filename is required"}), 400
    try:
        backup_path = run_backup(filename)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"status": "ok", "backup": backup_path})


@app.route("/config", methods=["POST"])
def config_route():
    cfg_str = request.data.decode()
    try:
        cfg = load_config(cfg_str)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(cfg)


if __name__ == "__main__":
    debug_flag = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_flag)
