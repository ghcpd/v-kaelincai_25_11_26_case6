@echo off
setlocal EnableExtensions EnableDelayedExpansion

python test_check.py input_backup.py
if %errorlevel%==0 (
  echo ERROR: original file passed security checks unexpectedly
  exit /b 1
) else (
  echo OK: original file failed checks as expected
)

python test_check.py inputs.py
if %errorlevel% neq 0 (
  echo ERROR: repaired file still has issues
  exit /b 1
) else (
  echo OK: repaired file passed checks
)

exit /b 0
