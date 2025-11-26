import os
import platform
import subprocess
import sys
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "test_run.log")

os.makedirs(LOG_DIR, exist_ok=True)

start_time = datetime.utcnow().isoformat() + "Z"
with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(f"\n=== TEST RUN START: {start_time} ===\n")

try:
    system = platform.system()
    if system == "Windows":
        cmd = ["cmd.exe", "/c", "run_test.bat"]
    else:
        cmd = ["bash", "run_test.sh"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(result.stdout)
        f.write(result.stderr)

    if result.returncode == 0:
        status = "TEST PASSED"
    else:
        status = "TEST FAILED"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"=== {status} at {datetime.utcnow().isoformat()}Z ===\n")

    print(status)
    sys.exit(result.returncode)
except Exception as e:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(str(e) + "\n")
        f.write("=== TEST FAILED at " + datetime.utcnow().isoformat() + "Z ===\n")
    print("TEST FAILED")
    sys.exit(1)
