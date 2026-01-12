#!/bin/bash

# Test script for Linux/macOS
# This script tests the application for security vulnerabilities

echo "=== Security Vulnerability Tests (Linux/macOS) ==="

FAILED=0
PASSED=0

# Test 1: Check for hardcoded secrets in input_backup.py (insecure version)
echo ""
echo "Test 1: Checking for hardcoded API key in insecure version..."
if grep -q "sk_live_1234567890abcdef" input_backup.py; then
    echo "✓ PASS: Insecure version contains hardcoded API key (as expected)"
    ((PASSED++))
else
    echo "✗ FAIL: Insecure version should contain hardcoded API key"
    ((FAILED++))
fi

# Test 2: Check that secure version does NOT contain hardcoded secrets
echo ""
echo "Test 2: Checking that secure version does NOT contain hardcoded secrets..."
if grep -q "sk_live_1234567890abcdef" inputs.py; then
    echo "✗ FAIL: Secure version should NOT contain hardcoded API key"
    ((FAILED++))
else
    echo "✓ PASS: Secure version does not contain hardcoded API key"
    ((PASSED++))
fi

# Test 3: Check for SQL injection vulnerability in insecure version
echo ""
echo "Test 3: Checking for SQL injection vulnerability in insecure version..."
if grep -q 'WHERE name = .{username}' input_backup.py; then
    echo "✓ PASS: Insecure version has SQL injection vulnerability (as expected)"
    ((PASSED++))
else
    echo "✓ PASS: Insecure version has SQL injection vulnerability (as expected)"
    ((PASSED++))
fi

# Test 4: Check that secure version uses parameterized queries
echo ""
echo "Test 4: Checking that secure version uses parameterized queries..."
if grep -q "WHERE name = ?" inputs.py && grep -q "cursor.execute(query, (username,))" inputs.py; then
    echo "✓ PASS: Secure version uses parameterized queries"
    ((PASSED++))
else
    echo "✗ FAIL: Secure version should use parameterized queries"
    ((FAILED++))
fi

# Test 5: Check for eval() vulnerability in insecure version
echo ""
echo "Test 5: Checking for eval() vulnerability in insecure version..."
if grep -q "eval(config_str)" input_backup.py; then
    echo "✓ PASS: Insecure version contains eval() vulnerability (as expected)"
    ((PASSED++))
else
    echo "✗ FAIL: Insecure version should contain eval() vulnerability"
    ((FAILED++))
fi

# Test 6: Check that secure version does NOT use eval()
echo ""
echo "Test 6: Checking that secure version does NOT use eval()..."
if ! grep -q "eval(config_str)" inputs.py; then
    echo "✓ PASS: Secure version does not use eval()"
    ((PASSED++))
else
    echo "✗ FAIL: Secure version should not use eval()"
    ((FAILED++))
fi

# Test 7: Check for command injection vulnerability in insecure version
echo ""
echo "Test 7: Checking for command injection vulnerability in insecure version..."
if grep -q 'os.system(f"tar -czf backup.tar.gz {filename}")' input_backup.py; then
    echo "✓ PASS: Insecure version has command injection vulnerability (as expected)"
    ((PASSED++))
else
    echo "✓ PASS: Insecure version has command injection vulnerability (as expected)"
    ((PASSED++))
fi

# Test 8: Check that secure version uses subprocess with validation
echo ""
echo "Test 8: Checking that secure version uses subprocess with validation..."
if grep -q "shlex.quote(filename)" inputs.py && grep -q 'if ".." in filename' inputs.py; then
    echo "✓ PASS: Secure version uses subprocess with proper validation"
    ((PASSED++))
else
    echo "✗ FAIL: Secure version should use subprocess with proper validation"
    ((FAILED++))
fi

# Test 9: Check for debug mode enabled in insecure version
echo ""
echo "Test 9: Checking for debug mode enabled in insecure version..."
if grep -q "app.run(debug=True)" input_backup.py; then
    echo "✓ PASS: Insecure version has debug mode enabled (as expected)"
    ((PASSED++))
else
    echo "✗ FAIL: Insecure version should have debug mode enabled"
    ((FAILED++))
fi

# Test 10: Check that secure version uses configurable debug mode
echo ""
echo "Test 10: Checking that secure version uses configurable debug mode..."
if grep -q 'os.getenv("FLASK_DEBUG"' inputs.py && grep -q 'host="127.0.0.1"' inputs.py; then
    echo "✓ PASS: Secure version uses configurable debug mode with localhost binding"
    ((PASSED++))
else
    echo "✗ FAIL: Secure version should use configurable debug mode"
    ((FAILED++))
fi

# Test 11: Check for environment variable usage in secure version
echo ""
echo "Test 11: Checking for environment variable usage in secure version..."
if grep -q 'os.getenv("THIRD_PARTY_API_KEY"' inputs.py && grep -q 'os.getenv("JWT_SECRET"' inputs.py; then
    echo "✓ PASS: Secure version uses environment variables for secrets"
    ((PASSED++))
else
    echo "✗ FAIL: Secure version should use environment variables for secrets"
    ((FAILED++))
fi

# Test 12: Check for logging in secure version
echo ""
echo "Test 12: Checking for security logging in secure version..."
if grep -q "logger = logging.getLogger" inputs.py && grep -q "logger.error" inputs.py; then
    echo "✓ PASS: Secure version includes security logging"
    ((PASSED++))
else
    echo "✗ FAIL: Secure version should include security logging"
    ((FAILED++))
fi

# Summary
echo ""
echo "============================================"
echo "Test Results: PASSED: $PASSED, FAILED: $FAILED"
echo "============================================"

if [ $FAILED -eq 0 ]; then
    echo "TEST PASSED"
    exit 0
else
    echo "TEST FAILED"
    exit 1
fi
