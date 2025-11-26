#!/usr/bin/env bash
set -e

# Install dependencies
python -m pip install -r requirements.txt

# Test original backup (should fail)
MODULE_PATH=input_backup.py pytest -q tests/test_security.py
RET=$?
if [ $RET -eq 0 ]; then
  echo "ERROR: Original input_backup.py passed pytest tests but should fail"
  exit 1
else
  echo "As expected, original input_backup.py failed pytest tests"
fi

# Test patched inputs.py (should pass)
MODULE_PATH=inputs.py pytest -q tests/test_security.py
RET=$?
if [ $RET -ne 0 ]; then
  echo "ERROR: Patched inputs.py failed pytest tests"
  exit 1
else
  echo "Patched inputs.py passed pytest tests"
fi

exit 0
