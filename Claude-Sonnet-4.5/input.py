import json
import sqlite3
import requests
import os
import re
import subprocess
from flask import Flask, request, jsonify
from urllib.parse import urlparse

app = Flask(__name__)

# Load sensitive data from environment variables
THIRD_PARTY_API_KEY = os.getenv("THIRD_PARTY_API_KEY", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
JWT_SECRET = os.getenv("JWT_SECRET", "")

# Whitelist for allowed domains (SSRF protection)
ALLOWED_DOMAINS = ["example.com", "api.trusted-service.com"]


def get_user_by_name(username):
    """Fetch user by name using parameterized query to prevent SQL injection."""
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    
    # Use parameterized query to prevent SQL injection
    query = "SELECT id, name, email FROM users WHERE name = ?"
    print("Executing:", query, "with parameter:", username)
    
    cursor.execute(query, (username,))
    result = cursor.fetchall()
    conn.close()
    return result


def fetch_remote_resource(url):
    """Fetch remote resource with SSRF protection."""
    # Validate URL format
    try:
        parsed = urlparse(url)
        if not parsed.scheme in ['http', 'https']:
            raise ValueError("Only HTTP/HTTPS protocols are allowed")
        
        # Check if domain is in whitelist
        domain = parsed.netloc
        if not any(allowed in domain for allowed in ALLOWED_DOMAINS):
            raise ValueError(f"Domain {domain} is not in the allowed list")
        
        # Prevent access to private IP ranges
        if any(private in domain for private in ['localhost', '127.0.0.1', '0.0.0.0', '10.', '172.16.', '192.168.']):
            raise ValueError("Access to private IP ranges is not allowed")
        
        res = requests.get(url, timeout=5)
        return res.text
    except Exception as e:
        return f"Error: {str(e)}"


def run_backup(filename):
    """Run backup with command injection protection."""
    # Validate filename - only allow alphanumeric, dots, underscores, and hyphens
    if not re.match(r'^[\w\-\.]+$', filename):
        raise ValueError("Invalid filename. Only alphanumeric characters, dots, underscores, and hyphens are allowed.")
    
    # Use subprocess with argument list instead of shell=True to prevent injection
    try:
        subprocess.run(['tar', '-czf', 'backup.tar.gz', filename], 
                      check=True, capture_output=True, timeout=30)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Backup failed: {e}")
    except FileNotFoundError:
        raise RuntimeError("tar command not found. Please ensure tar is installed.")


def load_config(config_str):
    """Load configuration safely - only JSON parsing, no eval()."""
    try:
        return json.loads(config_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON configuration: {str(e)}")


@app.route("/user", methods=["GET"])
def user_route():
    """User endpoint with input validation."""
    username = request.args.get("username", "")
    
    # Input validation - prevent empty or excessively long usernames
    if not username or len(username) > 100:
        return jsonify({"error": "Invalid username"}), 400
    
    try:
        data = get_user_by_name(username)
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": "Database error"}), 500


@app.route("/fetch", methods=["POST"])
def fetch_route():
    """Fetch endpoint with SSRF protection."""
    if not request.json or "url" not in request.json:
        return jsonify({"error": "URL is required"}), 400
    
    url = request.json["url"]
    
    try:
        data = fetch_remote_resource(url)
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/backup", methods=["POST"])
def backup_route():
    """Backup endpoint with command injection protection."""
    if not request.json or "filename" not in request.json:
        return jsonify({"error": "Filename is required"}), 400
    
    filename = request.json["filename"]
    
    try:
        run_backup(filename)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/config", methods=["POST"])
def config_route():
    """Config endpoint - only JSON parsing, no arbitrary code execution."""
    try:
        cfg = load_config(request.data.decode())
        return jsonify(cfg)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    # Disable debug mode in production
    app.run(debug=False, host='127.0.0.1')
