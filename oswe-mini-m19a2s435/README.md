# Security Audit and Patching for inputs.py

Overview

- `input_backup.py`: Original, unmodified source file (insecure). Do not use in production.
- `inputs.py`: Repaired and secure version of the application logic.
- `tests/test_runner.py`: Test harness that runs a suite of tests against a module file to verify protections (SQLi, command injection, config eval).
- `run_test.sh` / `run_test.bat`: Cross-platform test runners that ensure `input_backup.py` fails tests and `inputs.py` passes tests.
- `auto_test.py`: Detects platform and runs appropriate test script; writes logs to `logs/test_run.log`.
- `requirements.txt`: Python package dependencies for the environment.
- `Dockerfile`: Build environment for Docker-based testing; runs `run_test.sh`.
- `setup.sh`: Linux/macOS helper to install dependencies.

Setup

1. Create a Python virtual environment (recommended):
   - Linux / macOS: `python -m venv venv; source venv/bin/activate`
   - Windows (PowerShell): `python -m venv venv; .\\venv\\Scripts\\Activate.ps1`

2. Install dependencies:
   - Linux / macOS: `bash setup.sh`
   - Windows: `python -m pip install -r requirements.txt`

3. (Optional) Configure environment variables for secrets (do NOT leave these empty in production):
   - `THIRD_PARTY_API_KEY`, `DB_PASSWORD`, `JWT_SECRET`, `DB_PATH`, `SAFE_DOMAINS`

Running tests (pytest)

- Linux/macOS: `bash run_test.sh` (scripts will run pytest and verify secure/insecure modules)
- Windows: `run_test.bat`
- Automatic detection: `python auto_test.py` (will write logs to `logs/test_run.log`)

You can also test a specific module manually with pytest:
```
MODULE_PATH=input_backup.py pytest -q tests/test_security.py
MODULE_PATH=inputs.py pytest -q tests/test_security.py
```

Reading logs

- The `auto_test.py` runner writes both console output and a result marker (TEST PASSED or TEST FAILED) to `logs/test_run.log` with timestamps.

Notes

- This project implements security hardening for a simple Flask app focusing on SQL injection mitigation, prevention of command injection in backups, disallowing the use of `eval` for config parsing, and safe remote fetches.
- For simplicity, tests operate against the provided file-level modules rather than launching the Flask server. This allows easy CI integration and quick test runs.
