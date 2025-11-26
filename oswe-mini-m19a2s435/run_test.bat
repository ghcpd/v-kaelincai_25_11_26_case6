@echo off
python -m pip install -r requirements.txt

REM Test original backup (should fail)
set MODULE_PATH=input_backup.py
pytest -q tests/test_security.py
IF %ERRORLEVEL% == 0 (
  echo ERROR: Original input_backup.py passed pytest tests but should fail
  exit /b 1
) ELSE (
  echo As expected, original input_backup.py failed pytest tests
)

REM Test patched inputs.py (should pass)
set MODULE_PATH=inputs.py
pytest -q tests/test_security.py
IF NOT %ERRORLEVEL% == 0 (
  echo ERROR: Patched inputs.py failed pytest tests
  exit /b 1
) ELSE (
  echo Patched inputs.py passed pytest tests
)

exit /b 0
