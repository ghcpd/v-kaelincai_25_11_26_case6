import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("logs/test_run.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def detect_env():
    if os.path.exists("/.dockerenv"):
        return "Docker"
    return platform.system()


def run_command(cmd, shell=False):
    return subprocess.run(cmd, shell=shell, capture_output=True, text=True)


def main():
    env = detect_env()
    timestamp = datetime.now(timezone.utc).isoformat()

    if env == "Windows":
        cmd = ["run_test.bat"]
        shell = True
    else:
        cmd = ["bash", "run_test.sh"]
        shell = False

    result = run_command(cmd, shell=shell)
    status_line = "TEST PASSED" if result.returncode == 0 else "TEST FAILED"

    with LOG_PATH.open("w", encoding="utf-8") as f:
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Environment: {env}\n")
        f.write(f"Command: {' '.join(cmd)}\n\n")
        if result.stdout:
            f.write("[STDOUT]\n" + result.stdout + "\n")
        if result.stderr:
            f.write("[STDERR]\n" + result.stderr + "\n")
        f.write(status_line + "\n")

    print(status_line)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
