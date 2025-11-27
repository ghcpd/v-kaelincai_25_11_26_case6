import ast
import sys
import re
from pathlib import Path


PATTERNS = {
    "hardcoded_api_key": re.compile(r"sk_live", re.IGNORECASE),
    "hardcoded_password": re.compile(r"password123", re.IGNORECASE),
    "hardcoded_jwt": re.compile(r"my_jwt_secret_key", re.IGNORECASE),
}


class SecurityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    def visit_Call(self, node):
        # Detect eval
        if isinstance(node.func, ast.Name) and node.func.id == "eval":
            self.issues.append((node.lineno, "Use of eval"))
        # Detect os.system
        if isinstance(node.func, ast.Attribute) and node.func.attr == "system":
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                self.issues.append((node.lineno, "Use of os.system"))
        self.generic_visit(node)


def check_text_content(text: str, filepath: Path, issues: list):
    for name, pattern in PATTERNS.items():
        if pattern.search(text):
            issues.append((1, f"Found disallowed pattern: {name}"))
    # Check for debug=True
    if "app.run(debug=True" in text.replace(" ", ""):
        issues.append((1, "Debug mode enabled"))
    # Check SQL parameterization
    if "SELECT id, name, email FROM users WHERE name = ?" not in text:
        issues.append((1, "User query not parameterized with ?"))
    # Check SSRF helper presence
    if "def _is_url_allowed" not in text or "ip.is_private" not in text:
        issues.append((1, "SSRF guard missing or incomplete"))
    # Check fetch_remote_resource uses _is_url_allowed
    if "if not _is_url_allowed" not in text:
        issues.append((1, "fetch_remote_resource does not enforce URL allowlist"))
    # Check backup uses tarfile not os.system
    if "tarfile.open" not in text:
        issues.append((1, "run_backup not using tarfile.open"))
    if "os.system" in text:
        issues.append((1, "os.system present"))
    # eval detection is handled via AST visitor; avoid false positives from ast.literal_eval



def main():
    target_file = Path("input.py")
    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        if idx + 1 < len(sys.argv):
            target_file = Path(sys.argv[idx + 1])
    if not target_file.exists():
        print(f"[ERROR] File not found: {target_file}")
        sys.exit(1)

    text = target_file.read_text(encoding="utf-8")
    issues = []

    # AST-based checks
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        print(f"[ERROR] Syntax error in {target_file}: {e}")
        sys.exit(1)
    visitor = SecurityVisitor()
    visitor.visit(tree)
    issues.extend(visitor.issues)

    # Text-based checks
    check_text_content(text, target_file, issues)

    if issues:
        print("[FAIL] Security checks failed:")
        for lineno, msg in issues:
            print(f"  Line {lineno}: {msg}")
        sys.exit(1)

    print("[PASS] Security checks passed for", target_file)


if __name__ == "__main__":
    main()
