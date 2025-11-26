import json
import sqlite3
import requests
import os
import subprocess
import shlex
from flask import Flask, request
from urllib.parse import urlparse
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Use environment variables instead of hardcoded secrets
THIRD_PARTY_API_KEY = os.getenv("THIRD_PARTY_API_KEY", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
JWT_SECRET = os.getenv("JWT_SECRET", "")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Whitelist of allowed domains for SSRF protection
ALLOWED_DOMAINS = ["api.example.com", "data.example.com"]


def get_user_by_name(username):
    """
    Securely query user by name using parameterized queries.
    Prevents SQL injection attacks.
    """
    try:
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()
        # Use parameterized queries to prevent SQL injection
        query = "SELECT id, name, email FROM users WHERE name = ?"
        cursor.execute(query, (username,))
        result = cursor.fetchall()
        conn.close()
        return result
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return []


def fetch_remote_resource(url):
    """
    Securely fetch remote resources with SSRF protection.
    Validates URL and enforces domain whitelist.
    """
    try:
        # Validate URL format
        parsed_url = urlparse(url)
        
        # Check if URL scheme is http or https
        if parsed_url.scheme not in ["http", "https"]:
            raise ValueError("Invalid URL scheme. Only HTTP(S) allowed.")
        
        # Check if domain is in whitelist
        if parsed_url.netloc not in ALLOWED_DOMAINS:
            logger.warning(f"Access denied to domain: {parsed_url.netloc}")
            raise ValueError(f"Domain {parsed_url.netloc} is not allowed.")
        
        # Set timeout to prevent hanging requests
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        return res.text
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return None
    except (ValueError, Exception) as e:
        logger.error(f"Validation error: {e}")
        return None


def run_backup(filename):
    """
    Securely run backup command with proper input validation.
    Prevents command injection attacks.
    """
    try:
        # Validate filename to prevent path traversal and command injection
        if ".." in filename or "/" in filename or "\\" in filename or ";" in filename:
            raise ValueError("Invalid filename. Path traversal and special characters not allowed.")
        
        # Use shlex.quote to safely escape the filename for shell execution
        safe_filename = shlex.quote(filename)
        command = f"tar -czf backup.tar.gz {safe_filename}"
        
        # Use subprocess with shell=False is safer, but here we use shell=True with proper escaping
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            logger.error(f"Backup failed: {result.stderr}")
            return False
        return True
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return False
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return False


def load_config(config_str):
    """
    Safely load configuration from JSON only.
    Eliminates dangerous eval() usage.
    """
    try:
        return json.loads(config_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {}


@app.route("/user", methods=["GET"])
def user_route():
    """
    User query endpoint with SQL injection protection.
    """
    username = request.args.get("username", "")
    if not username:
        return {"error": "Username parameter is required"}, 400
    return {"data": get_user_by_name(username)}


@app.route("/fetch", methods=["POST"])
def fetch_route():
    """
    Remote resource fetching endpoint with SSRF protection.
    """
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return {"error": "URL parameter is required"}, 400
        
        url = data["url"]
        result = fetch_remote_resource(url)
        
        if result is None:
            return {"error": "Failed to fetch resource"}, 400
        
        return {"data": result}
    except Exception as e:
        logger.error(f"Error in fetch_route: {e}")
        return {"error": "Internal server error"}, 500


@app.route("/backup", methods=["POST"])
def backup_route():
    """
    Backup endpoint with command injection protection.
    """
    try:
        data = request.get_json()
        if not data or "filename" not in data:
            return {"error": "Filename parameter is required"}, 400
        
        filename = data["filename"]
        success = run_backup(filename)
        
        if not success:
            return {"error": "Backup operation failed"}, 500
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in backup_route: {e}")
        return {"error": "Internal server error"}, 500


@app.route("/config", methods=["POST"])
def config_route():
    """
    Configuration loading endpoint with safe JSON parsing only.
    """
    try:
        cfg = load_config(request.data.decode())
        if not cfg:
            return {"error": "Invalid configuration"}, 400
        return cfg
    except Exception as e:
        logger.error(f"Error in config_route: {e}")
        return {"error": "Invalid configuration"}, 400


if __name__ == "__main__":
    # Disable debug mode in production
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="127.0.0.1")
