# Security Audit Report and Remediation

## Overview

This project contains a comprehensive security audit of a Flask application (`inputs.py`), detailing all vulnerabilities found, their fixes, and a complete testing and deployment framework.

### Purpose

The security audit identified **8 critical vulnerabilities** in the original application and provided secure remediation for each. This package includes:

- **input_backup.py**: Original insecure version (for reference and testing)
- **inputs.py**: Secured version with all vulnerabilities fixed
- **report.json**: Detailed vulnerability analysis in JSON format
- **Environment setup files**: For deployment across multiple platforms
- **Automated test suites**: To validate security fixes
- **Auto-test runner**: For environment-agnostic testing

---

## Vulnerabilities Summary

| ID | Type | Severity | Status |
|:--:|------|----------|--------|
| 1 | SQL Injection | Critical | ✅ Fixed |
| 2 | Hardcoded API Key | Critical | ✅ Fixed |
| 3 | Hardcoded JWT Secret | Critical | ✅ Fixed |
| 4 | Hardcoded DB Password | Critical | ✅ Fixed |
| 5 | Command Injection | Critical | ✅ Fixed |
| 6 | Unsafe eval() | Critical | ✅ Fixed |
| 7 | Server-Side Request Forgery (SSRF) | High | ✅ Fixed |
| 8 | Debug Mode in Production | High | ✅ Fixed |

**Summary Statistics:**
- **Total Vulnerabilities**: 8
- **Critical**: 5
- **High**: 2
- **Medium**: 1
- **Low**: 0

---

## Generated Files and Purpose

### Application Files

| File | Purpose |
|------|---------|
| `inputs.py` | Secured Flask application with all fixes applied |
| `input_backup.py` | Original insecure version for reference and testing |
| `report.json` | Detailed vulnerability analysis in JSON format |

### Environment Configuration

| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies |
| `.env.example` | Environment variable template (copy to `.env`) |
| `Dockerfile` | Docker container configuration |
| `setup.sh` | Setup script for Linux/macOS environments |

### Testing Scripts

| File | Purpose | Platform |
|------|---------|----------|
| `run_test.sh` | Security test suite | Linux/macOS |
| `run_test.bat` | Security test suite | Windows |
| `auto_test.py` | Environment-agnostic auto-test runner | All |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | This comprehensive guide |
| `logs/test_run.log` | Test execution logs (created automatically) |

---

## Vulnerability Details

### Vulnerability #1: SQL Injection
**Lines**: 14-15  
**Severity**: Critical

**Insecure Code:**
```python
query = f"SELECT id, name, email FROM users WHERE name = '{username}'"
cursor.execute(query)
```

**Secure Code:**
```python
query = "SELECT id, name, email FROM users WHERE name = ?"
cursor.execute(query, (username,))
```

**Explanation**: Direct string concatenation allows SQL injection. Parameterized queries separate SQL logic from data, making injection impossible.

---

### Vulnerability #2: Hardcoded API Key
**Lines**: 5  
**Severity**: Critical

**Insecure Code:**
```python
THIRD_PARTY_API_KEY = "sk_live_1234567890abcdef"
```

**Secure Code:**
```python
THIRD_PARTY_API_KEY = os.getenv("THIRD_PARTY_API_KEY", "")
```

**Explanation**: Secrets in source code are exposed in version control and build artifacts. Use environment variables instead.

---

### Vulnerability #3: Hardcoded JWT Secret
**Lines**: 9  
**Severity**: Critical

**Insecure Code:**
```python
JWT_SECRET = "my_jwt_secret_key"
```

**Secure Code:**
```python
JWT_SECRET = os.getenv("JWT_SECRET", "")
```

**Explanation**: Exposed JWT secrets allow attackers to forge valid authentication tokens. Store in environment variables.

---

### Vulnerability #4: Hardcoded Database Password
**Lines**: 7  
**Severity**: Critical

**Insecure Code:**
```python
DB_PASSWORD = "password123"
```

**Secure Code:**
```python
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
```

**Explanation**: Database credentials in code allow unauthorized access. Use environment variables for credentials.

---

### Vulnerability #5: Command Injection
**Lines**: 24-25  
**Severity**: Critical

**Insecure Code:**
```python
import os
os.system(f"tar -czf backup.tar.gz {filename}")
```

**Secure Code:**
```python
import subprocess
import shlex

if ".." in filename or "/" in filename or "\\" in filename or ";" in filename:
    raise ValueError("Invalid filename...")
safe_filename = shlex.quote(filename)
command = f"tar -czf backup.tar.gz {safe_filename}"
result = subprocess.run(command, shell=True, capture_output=True, timeout=30)
```

**Explanation**: User input passed to `os.system()` allows command injection. Validate input and use `shlex.quote()` for escaping.

---

### Vulnerability #6: Unsafe eval()
**Lines**: 29-30  
**Severity**: Critical

**Insecure Code:**
```python
def load_config(config_str):
    try:
        return json.loads(config_str)
    except Exception:
        return eval(config_str)
```

**Secure Code:**
```python
def load_config(config_str):
    try:
        return json.loads(config_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {}
```

**Explanation**: `eval()` executes arbitrary Python code. Use JSON parsing only; never use `eval()` on untrusted input.

---

### Vulnerability #7: Server-Side Request Forgery (SSRF)
**Lines**: 18-19  
**Severity**: High

**Insecure Code:**
```python
def fetch_remote_resource(url):
    res = requests.get(url)
    return res.text
```

**Secure Code:**
```python
from urllib.parse import urlparse

ALLOWED_DOMAINS = ["api.example.com", "data.example.com"]

def fetch_remote_resource(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ["http", "https"]:
        raise ValueError("Invalid URL scheme...")
    if parsed_url.netloc not in ALLOWED_DOMAINS:
        raise ValueError(f"Domain {parsed_url.netloc} is not allowed.")
    res = requests.get(url, timeout=5)
    res.raise_for_status()
    return res.text
```

**Explanation**: Unvalidated URL fetching allows access to internal resources. Validate scheme and implement domain whitelist.

---

### Vulnerability #8: Debug Mode in Production
**Lines**: 36  
**Severity**: High

**Insecure Code:**
```python
app.run(debug=True)
```

**Secure Code:**
```python
debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
app.run(debug=debug_mode, host="127.0.0.1")
```

**Explanation**: Debug mode exposes sensitive information and enables arbitrary code execution. Make it configurable and default to False.

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip or conda (for package management)
- Git (for version control)
- Docker (optional, for containerized deployment)

### Linux/macOS Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd /path/to/project
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Create the `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual secrets
   nano .env
   ```

4. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

### Windows Setup

1. **Navigate to the project directory:**
   ```powershell
   cd C:\path\to\project
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Create the `.env` file:**
   ```powershell
   Copy-Item .env.example .env
   # Edit .env with your actual secrets using your preferred editor
   notepad .env
   ```

### Docker Setup

1. **Build the Docker image:**
   ```bash
   docker build -t secure-flask-app .
   ```

2. **Create `.env` file with your secrets:**
   ```bash
   cp .env.example .env
   # Edit .env
   ```

3. **Run the container:**
   ```bash
   docker run -p 5000:5000 --env-file .env secure-flask-app
   ```

---

## Running the Application

### Linux/macOS

```bash
source venv/bin/activate
python inputs.py
```

### Windows

```powershell
.\venv\Scripts\Activate.ps1
python inputs.py
```

### Docker

```bash
docker run -p 5000:5000 --env-file .env secure-flask-app
```

---

## Running Security Tests

### Automated Testing (Recommended)

Use the `auto_test.py` script for automatic environment detection and testing:

```bash
python auto_test.py
```

This script will:
- Detect your operating system (Windows/Linux/macOS)
- Run the appropriate test suite
- Log all results to `logs/test_run.log`
- Display test status: `TEST PASSED` or `TEST FAILED`

### Manual Testing

#### Linux/macOS

```bash
chmod +x run_test.sh
./run_test.sh
```

Output will show individual test results and a summary status.

#### Windows

```powershell
.\run_test.bat
```

Output will show individual test results and a summary status.

#### Docker

```bash
docker run --rm -v $(pwd):/app secure-flask-app bash run_test.sh
```

---

## Checking Test Logs

All test outputs are saved to `logs/test_run.log`:

```bash
# View the log file
cat logs/test_run.log

# Watch log updates (Linux/macOS)
tail -f logs/test_run.log

# Watch log updates (Windows PowerShell)
Get-Content logs/test_run.log -Wait
```

### Log Format

Each log entry includes:
- **Timestamp**: ISO format timestamp of when the test ran
- **Test Results**: Individual test pass/fail status
- **Final Status**: Either `TEST PASSED` or `TEST FAILED`

Example log entry:
```
2025-11-26T10:30:45,123 - INFO - === Security Audit Auto Test Suite ===
2025-11-26T10:30:45,234 - INFO - Detected Windows environment
2025-11-26T10:30:46,123 - INFO - Test 1: Checking for hardcoded API key...
...
2025-11-26T10:30:50,456 - INFO - TEST PASSED
```

---

## Test Coverage

The test suites verify:

1. ✅ Insecure version contains hardcoded secrets (as baseline)
2. ✅ Secure version does NOT contain hardcoded secrets
3. ✅ Insecure version has SQL injection vulnerability
4. ✅ Secure version uses parameterized queries
5. ✅ Insecure version contains eval() vulnerability
6. ✅ Secure version does NOT use eval()
7. ✅ Insecure version has command injection vulnerability
8. ✅ Secure version uses subprocess with validation
9. ✅ Insecure version has debug mode enabled
10. ✅ Secure version uses configurable debug mode
11. ✅ Secure version uses environment variables
12. ✅ Secure version includes security logging

---

## Environment Variables

### Required Variables (in `.env`)

Copy these from `.env.example` and fill with actual values:

```env
# Third-party API key
THIRD_PARTY_API_KEY=your_api_key_here

# Database password
DB_PASSWORD=your_db_password_here

# JWT secret key
JWT_SECRET=your_jwt_secret_here

# Flask debug mode (should be False in production)
FLASK_DEBUG=False
```

**Security Note**: Never commit `.env` to version control. Add it to `.gitignore`.

---

## Security Best Practices Applied

1. **Parameterized Queries**: Prevents SQL injection attacks
2. **Environment Variables**: Keeps secrets out of source code
3. **Input Validation**: Rejects malicious or malformed input
4. **Command Escaping**: Uses `shlex.quote()` for shell commands
5. **SSRF Protection**: Validates URLs and enforces domain whitelist
6. **Secure Parsing**: Uses JSON only, never `eval()`
7. **Subprocess over os.system()**: More secure command execution
8. **Debug Mode Control**: Disabled by default in production
9. **Security Logging**: Logs security events for audit trails
10. **Error Handling**: Graceful error handling without data leakage

---

## Detailed Comparison

### Original vs. Secured Code

| Aspect | Original | Secured |
|--------|----------|---------|
| Secrets | Hardcoded | Environment variables |
| SQL Queries | String concatenation | Parameterized queries |
| Config Parsing | eval() | JSON only |
| Command Execution | os.system() | subprocess with validation |
| URL Fetching | No validation | Domain whitelist + scheme check |
| Debug Mode | Always enabled | Configurable, default False |
| Logging | None | Security logging included |
| Error Handling | None | Comprehensive try-except blocks |

---

## Troubleshooting

### Issue: `run_test.sh` permission denied

**Solution**:
```bash
chmod +x run_test.sh
```

### Issue: Python module not found

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: `.env` file not found

**Solution**:
```bash
cp .env.example .env
# Edit with your actual values
```

### Issue: Tests fail on Windows with bash script

**Solution**: Use `run_test.bat` instead:
```powershell
.\run_test.bat
```

### Issue: SSRF test fails - domain not allowed

**Solution**: Add your domain to `ALLOWED_DOMAINS` in `inputs.py`:
```python
ALLOWED_DOMAINS = ["api.example.com", "your-domain.com"]
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Security Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - run: pip install -r requirements.txt
    - run: python auto_test.py
```

---

## Contact and Support

For security issues or concerns:
1. Review the detailed vulnerability analysis in `report.json`
2. Check logs in `logs/test_run.log`
3. Ensure all environment variables are properly configured
4. Verify that test suites pass with `python auto_test.py`

---

## License

This security audit and remediation package is provided as-is for educational and security assessment purposes.

---

## Changelog

### Version 1.0 (2025-11-26)

- Initial security audit completed
- 8 vulnerabilities identified and fixed
- Comprehensive test suites implemented
- Multi-platform support (Windows, Linux, macOS)
- Docker containerization added
- Detailed documentation provided

---

**Last Updated**: November 26, 2025  
**Status**: ✅ All vulnerabilities remediated and tested

