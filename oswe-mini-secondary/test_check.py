import ast
import re
import sys

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "inputs.py"

with open(FILENAME, "r", encoding="utf-8") as f:
    src = f.read()

issues = []

# 1) Hardcoded secrets
if re.search(r"^\s*(THIRD_PARTY_API_KEY|DB_PASSWORD|JWT_SECRET)\s*=\s*[\"']", src, re.MULTILINE):
    issues.append("hardcoded_secret")

# 2) direct eval() call only (literal_eval is allowed)
if re.search(r"\beval\s*\(", src):
    issues.append("eval_usage")

# 3) os.system usage
if "os.system(" in src:
    issues.append("os_system")

# 4) sql concatenation / f-string select patterns
if re.search(r"f\s*\"SELECT.*\{", src) or "WHERE name = '" in src:
    issues.append("sql_injection_like")

# 5) requests.get without safe guard (simple heuristic)
if "requests.get(" in src and "_is_safe_url" not in src:
    issues.append("unsafe_requests_get")

# 6) debug True
if "app.run(debug=True)" in src:
    issues.append("debug_enabled")

# 7) direct request.json subscript usage
if re.search(r"request\.json\s*\[", src):
    issues.append("unsafe_request_json_access")

# 8) return eval specifically (avoid matching literal_eval)
if re.search(r"\breturn\s+eval\s*\(", src):
    issues.append("return_eval")

# Build output
if issues:
    print("VULNERABILITIES FOUND in {}: {}".format(FILENAME, ", ".join(issues)))
    # Print lines where found for diagnostics
    for issue in issues:
        print("-", issue)
    sys.exit(1)
else:
    print("OK: No obvious insecure patterns detected in {}".format(FILENAME))
    sys.exit(0)
