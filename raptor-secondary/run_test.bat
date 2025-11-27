@echo off
setlocal ENABLEDELAYEDEXPANSION
set TARGET=%TEST_TARGET%
if "%TARGET%"=="" set TARGET=input.py
python test_security.py --file "%TARGET%"
exit /b %ERRORLEVEL%
