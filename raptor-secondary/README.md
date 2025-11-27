# Secure Audit for `input.py`

## Overview
- **`input.py`**: Hardened Flask service with mitigations for SQLi, SSRF, command injection, unsafe eval, and debug leakage.
- **`input_backup.py`**: Original vulnerable file preserved for reference/testing.
- **`report.json`**: Structured vulnerability report with fixes and severities.
- **Tests & Scripts**:
  - `test_security.py`: Static security checks (no dependencies beyond stdlib).
  - `run_test.sh` / `run_test.bat`: Platform-specific test runners (honor `TEST_TARGET`).
  - `auto_test.py`: Auto-detects environment (Windows/Linux/Docker), runs tests, and logs to `logs/test_run.log`.
- **Environment**:
  - `requirements.txt`, `setup.sh`, `Dockerfile` to replicate and test.

---

## Setup

### Linux/macOS
```bash
# optional: make scripts executable
chmod +x setup.sh run_test.sh
./setup.sh
```

### Windows (PowerShell or CMD)
```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Docker
```bash
docker build -t secure-input .
docker run --rm secure-input
```

---

## Running Tests

### Linux/macOS
```bash
bash run_test.sh               # tests current input.py (should PASS)
TEST_TARGET=input_backup.py bash run_test.sh  # tests original (should FAIL)
```

### Windows
```bat
run_test.bat                   REM tests current input.py (should PASS)
set TEST_TARGET=input_backup.py && run_test.bat  REM tests original (should FAIL)
```

### Automatic (cross-platform)
```bash
python auto_test.py
```
- Detects platform and invokes the proper runner.
- Writes output to `logs/test_run.log` with timestamp and final status line `TEST PASSED` or `TEST FAILED`.

---

## Interpreting Logs
- **Location**: `logs/test_run.log`
- **Contents**:
  - Timestamp, environment, command executed
  - Captured stdout/stderr from the test run
  - Final status line: `TEST PASSED` or `TEST FAILED`

---

## Secrets & Configuration
- Set these environment variables in production:
  - `THIRD_PARTY_API_KEY`
  - `DB_PASSWORD`
  - `JWT_SECRET`
  - Optional: `FLASK_DEBUG` (`true` for dev, default `false`)

---

## Notes
- The security tests focus on eliminating known issues from the original file. Extending with dynamic or SAST tools (e.g., Bandit) is recommended for broader coverage.
