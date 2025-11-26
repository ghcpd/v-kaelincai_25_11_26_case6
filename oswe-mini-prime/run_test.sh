#!/usr/bin/env bash
set -e

TARGET_FILE=${1:-inputs.py}
python3 -m pip install -r requirements.txt >/dev/null 2>&1 || true
python3 tests/security_test.py "$TARGET_FILE"
