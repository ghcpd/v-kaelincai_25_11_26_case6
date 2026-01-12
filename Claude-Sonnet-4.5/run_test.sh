#!/bin/bash

# run_test.sh - Security test script for Linux/macOS
# This script tests for security vulnerabilities in input.py

echo "=========================================="
echo "Security Vulnerability Test Suite"
echo "=========================================="
echo ""

EXIT_CODE=0

# Test 1: Check for hardcoded secrets
echo "[TEST 1] Checking for hardcoded secrets..."
if grep -q "sk_live_1234567890abcdef\|password123\|my_jwt_secret_key" input.py; then
    echo "❌ FAIL: Hardcoded secrets found in input.py"
    EXIT_CODE=1
else
    echo "✓ PASS: No hardcoded secrets found"
fi
echo ""

# Test 2: Check for SQL injection vulnerability
echo "[TEST 2] Checking for SQL injection vulnerability..."
if grep -q "cursor.execute(query, (" input.py; then
    echo "✓ PASS: Parameterized queries detected"
elif grep -E "f['\"]SELECT.*\{|\"SELECT.*\" \+ |'SELECT.*' \+" input.py | grep -v "^#" | grep -v "^[[:space:]]*#" > /dev/null; then
    echo "❌ FAIL: SQL injection vulnerability detected (string concatenation in query)"
    EXIT_CODE=1
else
    echo "⚠ WARNING: Unable to verify SQL query safety"
fi
echo ""

# Test 3: Check for eval() usage
echo "[TEST 3] Checking for dangerous eval() usage..."
if grep -E "return eval\(|= eval\(" input.py | grep -v "^#" | grep -v "^[[:space:]]*#"; then
    echo "❌ FAIL: Dangerous eval() function found"
    EXIT_CODE=1
else
    echo "✓ PASS: No eval() usage detected"
fi
echo ""

# Test 4: Check for command injection vulnerability
echo "[TEST 4] Checking for command injection vulnerability..."
if grep -q "subprocess.run(\[" input.py; then
    echo "✓ PASS: Safe subprocess usage detected"
elif grep -E "os.system\(f\"|os.system\(\".*\{" input.py | grep -v "^#" | grep -v "^[[:space:]]*#" > /dev/null; then
    echo "❌ FAIL: Command injection vulnerability detected (os.system with f-string)"
    EXIT_CODE=1
else
    echo "⚠ WARNING: Unable to verify command execution safety"
fi
echo ""

# Test 5: Check for SSRF protection
echo "[TEST 5] Checking for SSRF protection..."
if grep -q "ALLOWED_DOMAINS\|urlparse" input.py; then
    echo "✓ PASS: SSRF protection mechanisms detected"
else
    echo "❌ FAIL: No SSRF protection found"
    EXIT_CODE=1
fi
echo ""

# Test 6: Check for debug mode
echo "[TEST 6] Checking Flask debug mode..."
if grep -q "app.run(debug=True)" input.py; then
    echo "❌ FAIL: Debug mode is enabled (security risk)"
    EXIT_CODE=1
else
    echo "✓ PASS: Debug mode is disabled"
fi
echo ""

# Test 7: Check for environment variable usage
echo "[TEST 7] Checking for secure credential management..."
if grep -q "os.getenv.*THIRD_PARTY_API_KEY\|os.getenv.*DB_PASSWORD\|os.getenv.*JWT_SECRET" input.py; then
    echo "✓ PASS: Environment variables used for credentials"
else
    echo "❌ FAIL: Credentials not loaded from environment variables"
    EXIT_CODE=1
fi
echo ""

echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
    echo "Status: TEST PASSED"
else
    echo "❌ SOME TESTS FAILED"
    echo "Status: TEST FAILED"
fi
echo "=========================================="

exit $EXIT_CODE
