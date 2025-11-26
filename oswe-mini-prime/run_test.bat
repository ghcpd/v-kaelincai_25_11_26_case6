@echo off
setlocal
if "%1"=="" (
  set TARGET=inputs.py
) else (
  set TARGET=%1
)
python -m pip install -r requirements.txt >nul 2>&1 || echo "pip install failure"
python tests\security_test.py %TARGET%
if %ERRORLEVEL% NEQ 0 (
  echo TEST FAILED
  exit /b 1
) else (
  echo TEST PASSED
  exit /b 0
)
