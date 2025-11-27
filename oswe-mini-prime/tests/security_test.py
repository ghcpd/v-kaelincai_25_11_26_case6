import sys
import re
import ast

base_file = sys.argv[1] if len(sys.argv) > 1 else "inputs.py"

with open(base_file, "r", encoding="utf-8") as f:
    content = f.read()

issues = []

# Hardcoded secrets
if re.search(r"THIRD_PARTY_API_KEY\s*=\s*\"sk_live_", content):
    issues.append("Hardcoded THIRD_PARTY_API_KEY detected")
if re.search(r"DB_PASSWORD\s*=\s*\"password123\"", content):
    issues.append("Hardcoded DB_PASSWORD detected")
if re.search(r"JWT_SECRET\s*=\s*\"my_jwt_secret_key\"", content):
    issues.append("Hardcoded JWT_SECRET detected")

# Eval usage: parse AST to avoid false positives in comments / strings
parsed = ast.parse(content, filename=base_file)
for node in ast.walk(parsed):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'eval':
        issues.append("Use of eval() detected (AST)")
        break

# os.system / shell injection / tar -czf usage
for node in ast.walk(parsed):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name) and node.func.value.id == 'os' and node.func.attr == 'system':
            issues.append("os.system() usage detected (AST)")
            break
if "tar -czf" in content:
    issues.append("Shell tar -czf usage detected")

# SQL injection: searching for f-string with username interpolation
if "WHERE name = '{username}'" in content or "WHERE name = \"{username}\"" in content:
    issues.append("Potential SQL injection via f-string detected")

# Debug mode
if re.search(r"app\.run\(\s*debug\s*=\s*True\s*\)", content):
    issues.append("Flask debug mode enabled in source")
# SSRF: check for bare requests.get(url) and lack of is_url_allowed definition
if not re.search(r"def is_url_allowed\(", content) and re.search(r"requests\.get\(\s*url\s*\)", content):
    issues.append("Potential SSRF: requests.get(url) without validation")

# Backup protections: check presence of ADMIN token header and absence of os.system
if ("ADMIN_TOKEN" not in content and "X-ADMIN-TOKEN" not in content):
    issues.append("No admin token check found around backup route")
if re.search(r"os\.system\(\s*", content):
    issues.append("os.system usage detected (shell exec) - should be avoided")

# Check that ast.literal_eval is used instead of eval
if "ast.literal_eval" not in content and "eval(" in content:
    issues.append("No ast.literal_eval present; eval usage may exist")

if issues:
    print("FAILED SECURITY CHECKS for", base_file)
    for i in issues:
        print(" -", i)
    sys.exit(1)
else:
    print("All security checks passed for", base_file)
    sys.exit(0)
