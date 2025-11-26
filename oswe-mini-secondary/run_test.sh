#!/usr/bin/env bash
set -euo pipefail

PY=python

echo "Testing original file: input_backup.py"
$PY test_check.py input_backup.py
ORIG_EXIT=$?
if [ $ORIG_EXIT -eq 0 ]; then
  echo "ERROR: original file passed security checks unexpectedly" >&2
  exit 1
else
  echo "OK: original file failed checks as expected"
fi

echo "Testing repaired file: inputs.py"
$PY test_check.py inputs.py
FIX_EXIT=$?
if [ $FIX_EXIT -ne 0 ]; then
  echo "ERROR: repaired file still has issues" >&2
  exit 1
else
  echo "OK: repaired file passed checks"
fi

exit 0
