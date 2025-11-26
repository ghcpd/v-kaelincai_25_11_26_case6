import os
import platform
import subprocess
import sys
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "test_run.log")

os.makedirs(LOG_DIR, exist_ok=True)

def run_command(cmd, shell=False):
    start = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{start}] Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}\n")
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell, text=True)
        for line in p.stdout:
            f.write(line)
        p.wait()
        return p.returncode


def main():
    sys_platform = platform.system()

    if sys_platform == "Windows":
        cmd = ["run_test.bat"]
        rc = run_command(cmd)
    else:
        # assume Linux / Mac
        cmd = ["bash", "run_test.sh", "inputs.py"]
        rc = run_command(cmd)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        status = "TEST PASSED" if rc == 0 else "TEST FAILED"
        f.write(f"[{datetime.utcnow().isoformat()}] {status}\n")
    print(status)
    return rc


if __name__ == "__main__":
    exit(main())
