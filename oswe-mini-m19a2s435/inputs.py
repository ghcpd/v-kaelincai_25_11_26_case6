import os
import json
import sqlite3
import logging
import tarfile
from urllib.parse import urlparse
import ipaddress
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load secrets from environment variables - do NOT hardcode!
THIRD_PARTY_API_KEY = os.getenv("THIRD_PARTY_API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")
JWT_SECRET = os.getenv("JWT_SECRET")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path (configurable)
DB_PATH = os.getenv("DB_PATH", "user.db")

# Allowlist for safe domains (comma-separated)
SAFE_DOMAINS = os.getenv("SAFE_DOMAINS", "example.com,api.example.com")
SAFE_DOMAINS = set(s.strip().lower() for s in SAFE_DOMAINS.split(",") if s.strip())


def is_private_ip(hostname: str) -> bool:
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private
    except Exception:
        # hostname could be domain, ignore here
        return False


def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        host = parsed.hostname
        if not host:
            return False
        if host.lower() in SAFE_DOMAINS:
            return True
        try:
            addr = ipaddress.ip_address(host)
            # reject private IPs
            if addr.is_private:
                return False
        except ValueError:
            pass
        # final domain allowlist check (suffix match)
        for safe in SAFE_DOMAINS:
            if host.lower().endswith(safe):
                return True
        return False
    except Exception:
        return False


def get_user_by_name(username: str):
    # Use parameterized SQL statements to prevent SQL injection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT id, name, email FROM users WHERE name = ?"
    logger.info("Executing parameterized query")
    cursor.execute(query, (username,))
    result = cursor.fetchall()
    conn.close()
    return result


def fetch_remote_resource(url: str, timeout: int = 5):
    # Validate URL and apply timeout
    if not is_safe_url(url):
        raise ValueError("URL not allowed")
    res = requests.get(url, timeout=timeout)
    res.raise_for_status()
    return res.text


def run_backup(filename: str, archive_name: str = "backup.tar.gz"):
    # Prevent shell injection by not using shell commands and validating filename
    # Allow only a single basename (no path separators)
    if os.path.basename(filename) != filename:
        raise ValueError("Invalid filename")
    invalid_chars = [';', '&', '|', '$', '<', '>', '`', '\n', '\r']
    if any(c in filename for c in invalid_chars):
        raise ValueError("Invalid filename")
    logger.info("Creating backup archive %s for %s", archive_name, filename)
    with tarfile.open(archive_name, "w:gz") as tar:
        # We add the file without following symbolic links for safety
        tar.add(filename, arcname=os.path.basename(filename), recursive=False)


def load_config(config_str: str):
    # Only accept JSON to avoid arbitrary code execution
    return json.loads(config_str)


@app.route("/user", methods=["GET"])
def user_route():
    username = request.args.get("username", "")
    try:
        data = get_user_by_name(username)
        return jsonify({"data": data})
    except Exception as e:
        logger.exception("Error in user_route")
        return jsonify({"error": str(e)}), 500


@app.route("/fetch", methods=["POST"])
def fetch_route():
    url = request.json.get("url")
    try:
        return jsonify({"data": fetch_remote_resource(url)})
    except Exception as e:
        logger.exception("Error fetching remote resource")
        return jsonify({"error": str(e)}), 400


@app.route("/backup", methods=["POST"])
def backup_route():
    filename = request.json.get("filename")
    try:
        run_backup(filename)
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.exception("Error creating backup")
        return jsonify({"error": str(e)}), 400


@app.route("/config", methods=["POST"])
def config_route():
    try:
        cfg = load_config(request.data.decode())
        return jsonify(cfg)
    except Exception as e:
        logger.exception("Error parsing config")
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    # Do not run with debug=True in production
    app.run(debug=False)
