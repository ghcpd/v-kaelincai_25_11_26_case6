#!/usr/bin/env python3
import datetime
import os
import platform
import shutil
import subprocess
import sys

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "test_run.log")

os.makedirs(LOG_DIR, exist_ok=True)

def write_log(msg):
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(f"[{ts}] {msg}\n")


def run_command(cmd):
    write_log(f"RUN: {cmd}")
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        write_log(out)
        return True
    except subprocess.CalledProcessError as e:
        write_log(e.output)
        return False


def main():
    write_log("Starting auto_test")

    # Detect environment
    is_docker = os.path.exists("/.dockerenv")
    system = platform.system().lower()

    if is_docker:
        write_log("Detected Docker environment")
        script = "./run_test.sh"
    elif system == "windows":
        write_log("Detected Windows environment")
        script = "run_test.bat"
    else:
        write_log("Detected POSIX environment")
        script = "./run_test.sh"

    success = run_command(script)

    final_status = "TEST PASSED" if success else "TEST FAILED"
    write_log(final_status)

    print(final_status)
    return 0 if success else 2


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
