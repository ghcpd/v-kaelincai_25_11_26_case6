@echo off
REM Test script for Windows
REM This script tests the application for security vulnerabilities

setlocal enabledelayedexpansion

echo === Security Vulnerability Tests (Windows) ===

set FAILED=0
set PASSED=0

REM Test 1: Check for hardcoded secrets in input_backup.py (insecure version)
echo.
echo Test 1: Checking for hardcoded API key in insecure version...
findstr /M "sk_live_1234567890abcdef" input_backup.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [PASS] Insecure version contains hardcoded API key
    set /a PASSED=!PASSED!+1
) else (
    echo [FAIL] Insecure version should contain hardcoded API key
    set /a FAILED=!FAILED!+1
)

REM Test 2: Check that secure version does NOT contain hardcoded secrets
echo.
echo Test 2: Checking secure version does NOT contain hardcoded secrets...
findstr /M "sk_live_1234567890abcdef" inputs.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [FAIL] Secure version should NOT contain hardcoded API key
    set /a FAILED=!FAILED!+1
) else (
    echo [PASS] Secure version does not contain hardcoded API key
    set /a PASSED=!PASSED!+1
)

REM Test 3: Check for password in insecure version
echo.
echo Test 3: Checking for hardcoded password in insecure version...
findstr /M "password123" input_backup.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [PASS] Insecure version contains hardcoded password
    set /a PASSED=!PASSED!+1
) else (
    echo [FAIL] Insecure version should contain hardcoded password
    set /a FAILED=!FAILED!+1
)

REM Test 4: Check that secure version does NOT contain hardcoded password
echo.
echo Test 4: Checking secure version does NOT contain hardcoded password...
findstr /M "password123" inputs.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [FAIL] Secure version should NOT contain hardcoded password
    set /a FAILED=!FAILED!+1
) else (
    echo [PASS] Secure version does not contain hardcoded password
    set /a PASSED=!PASSED!+1
)

REM Test 5: Check for eval vulnerability in insecure version
echo.
echo Test 5: Checking for eval vulnerability in insecure version...
findstr /M "except Exception:" input_backup.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [PASS] Insecure version has eval fallback pattern
    set /a PASSED=!PASSED!+1
) else (
    echo [FAIL] Insecure version should have eval fallback
    set /a FAILED=!FAILED!+1
)

REM Test 6: Check that secure version uses json.JSONDecodeError
echo.
echo Test 6: Checking secure version uses json.JSONDecodeError...
findstr /M "json.JSONDecodeError" inputs.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [PASS] Secure version uses json.JSONDecodeError
    set /a PASSED=!PASSED!+1
) else (
    echo [FAIL] Secure version should use json.JSONDecodeError
    set /a FAILED=!FAILED!+1
)

REM Test 7: Check for os.system in insecure version
echo.
echo Test 7: Checking for os.system in insecure version...
findstr /M "os.system" input_backup.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [PASS] Insecure version uses os.system
    set /a PASSED=!PASSED!+1
) else (
    echo [FAIL] Insecure version should use os.system
    set /a FAILED=!FAILED!+1
)

REM Test 8: Check that secure version uses subprocess
echo.
echo Test 8: Checking secure version uses subprocess...
findstr /M "subprocess.run" inputs.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [PASS] Secure version uses subprocess.run
    set /a PASSED=!PASSED!+1
) else (
    echo [FAIL] Secure version should use subprocess.run
    set /a FAILED=!FAILED!+1
)

REM Test 9: Check for input validation in secure version
echo.
echo Test 9: Checking for input validation in secure version...
findstr /M "shlex.quote" inputs.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [PASS] Secure version uses shlex.quote
    set /a PASSED=!PASSED!+1
) else (
    echo [FAIL] Secure version should use shlex.quote
    set /a FAILED=!FAILED!+1
)

REM Test 10: Check for parameterized queries in secure version
echo.
echo Test 10: Checking for parameterized queries in secure version...
findstr /M "WHERE name = ?" inputs.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [PASS] Secure version uses parameterized queries
    set /a PASSED=!PASSED!+1
) else (
    echo [FAIL] Secure version should use parameterized queries
    set /a FAILED=!FAILED!+1
)

REM Test 11: Check for environment variables in secure version
echo.
echo Test 11: Checking for environment variable usage in secure version...
findstr /M "os.getenv" inputs.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [PASS] Secure version uses environment variables
    set /a PASSED=!PASSED!+1
) else (
    echo [FAIL] Secure version should use environment variables
    set /a FAILED=!FAILED!+1
)

REM Test 12: Check for logging in secure version
echo.
echo Test 12: Checking for security logging in secure version...
findstr /M "logger = logging.getLogger" inputs.py > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo [PASS] Secure version includes security logging
    set /a PASSED=!PASSED!+1
) else (
    echo [FAIL] Secure version should include security logging
    set /a FAILED=!FAILED!+1
)

REM Summary
echo.
echo ============================================
echo Test Results: PASSED: !PASSED!, FAILED: !FAILED!
echo ============================================

if !FAILED! equ 0 (
    echo TEST PASSED
    exit /b 0
) else (
    echo TEST FAILED
    exit /b 1
)
