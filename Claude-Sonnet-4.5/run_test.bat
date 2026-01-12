@echo off
REM run_test.bat - Security test script for Windows
REM This script tests for security vulnerabilities in input.py

echo ==========================================
echo Security Vulnerability Test Suite
echo ==========================================
echo.

set EXIT_CODE=0

REM Test 1: Check for hardcoded secrets
echo [TEST 1] Checking for hardcoded secrets...
findstr /C:"sk_live_1234567890abcdef" /C:"password123" /C:"my_jwt_secret_key" input.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo X FAIL: Hardcoded secrets found in input.py
    set EXIT_CODE=1
) else (
    echo + PASS: No hardcoded secrets found
)
echo.

REM Test 2: Check for SQL injection vulnerability
echo [TEST 2] Checking for SQL injection vulnerability...
findstr /C:"cursor.execute(query, (" input.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo + PASS: Parameterized queries detected
) else (
    findstr /C:"f\"SELECT" /C:"f'SELECT" input.py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo X FAIL: SQL injection vulnerability detected
        set EXIT_CODE=1
    ) else (
        echo ? WARNING: Unable to verify SQL query safety
    )
)
echo.

REM Test 3: Check for eval usage
echo [TEST 3] Checking for dangerous eval^(^) usage...
findstr /C:"return eval(" /C:"= eval(" input.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo X FAIL: Dangerous eval^(^) function found
    set EXIT_CODE=1
) else (
    echo + PASS: No eval^(^) usage detected
)
echo.

REM Test 4: Check for command injection vulnerability
echo [TEST 4] Checking for command injection vulnerability...
findstr /C:"subprocess.run([" input.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo + PASS: Safe subprocess usage detected
) else (
    findstr /C:"os.system(f" input.py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo X FAIL: Command injection vulnerability detected
        set EXIT_CODE=1
    ) else (
        echo ? WARNING: Unable to verify command execution safety
    )
)
echo.

REM Test 5: Check for SSRF protection
echo [TEST 5] Checking for SSRF protection...
findstr /C:"ALLOWED_DOMAINS" /C:"urlparse" input.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo + PASS: SSRF protection mechanisms detected
) else (
    echo X FAIL: No SSRF protection found
    set EXIT_CODE=1
)
echo.

REM Test 6: Check for debug mode
echo [TEST 6] Checking Flask debug mode...
findstr /C:"app.run(debug=True)" input.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo X FAIL: Debug mode is enabled ^(security risk^)
    set EXIT_CODE=1
) else (
    echo + PASS: Debug mode is disabled
)
echo.

REM Test 7: Check for environment variable usage
echo [TEST 7] Checking for secure credential management...
findstr /C:"os.getenv" input.py | findstr /C:"THIRD_PARTY_API_KEY" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo + PASS: Environment variables used for credentials
) else (
    echo X FAIL: Credentials not loaded from environment variables
    set EXIT_CODE=1
)
echo.

echo ==========================================
if %EXIT_CODE% EQU 0 (
    echo + ALL TESTS PASSED
    echo Status: TEST PASSED
) else (
    echo X SOME TESTS FAILED
    echo Status: TEST FAILED
)
echo ==========================================

exit /b %EXIT_CODE%
