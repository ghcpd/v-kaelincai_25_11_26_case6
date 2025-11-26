# Security Audit - inputs.py

This workspace contains an audit and secure fix for `inputs.py` (original copied to `input_backup.py`).

Overview of generated files:

- `inputs.py` — Repaired secure version.
- `input_backup.py` — Exact backup copy of the original vulnerable file.
- `report.json` — Structured vulnerability report with descriptions and fixes.
- `test_check.py` — Static heuristic checks for insecure patterns (used by tests).
- `run_test.sh` — Linux/macOS test harness (fails on original, passes on repaired).
- `run_test.bat` — Windows test harness (fails on original, passes on repaired).
- `auto_test.py` — Auto-detects the environment and runs the appropriate test harness; saves logs to `logs/test_run.log`.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — Lightweight image to run tests inside Docker.
- `setup.sh` — Create virtualenv and install requirements on Linux/macOS.
- `logs/` — Directory where `auto_test.py` writes `test_run.log`.

Quick setup and test steps (Linux / macOS):

1. Install Python 3.11+ and ensure `python` is available.
2. Create venv and install deps:

```bash
./setup.sh
source .venv/bin/activate
```

3. Run tests:

```bash
./run_test.sh
```

4. Or use auto_test.py (detects environment automatically and writes logs):

```bash
python auto_test.py
```

Windows instructions:

1. Install Python 3.11+ and ensure `python` is on PATH.
2. Install requirements:

```powershell
python -m pip install -r requirements.txt
```

3. Run tests:

```powershell
run_test.bat
```

4. Or use auto_test.py:

```powershell
python auto_test.py
```

Docker:

```bash
# build
docker build -t inputs-audit .
# run tests in container
docker run --rm inputs-audit
```

Viewing logs:

- `logs/test_run.log` contains timestamped outputs and the final status line: `TEST PASSED` or `TEST FAILED`.

Notes:

- The test scripts are heuristic static checks meant for this exercise. Real-world testing should include unit tests, integration tests, and live system scans.
