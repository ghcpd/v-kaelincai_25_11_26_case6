#!/usr/bin/env python3
"""
auto_test.py - Automatic environment detection and test execution script

This script automatically detects the current environment (Windows/Linux/Docker)
and runs the appropriate test script, logging all output.
"""

import os
import sys
import platform
import subprocess
from datetime import datetime
from pathlib import Path


def ensure_log_directory():
    """Create logs directory if it doesn't exist."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return log_dir


def detect_environment():
    """Detect the current operating environment."""
    system = platform.system()
    
    # Check if running in Docker
    if os.path.exists('/.dockerenv'):
        return "Docker"
    
    # Check OS type
    if system == "Windows":
        return "Windows"
    elif system in ["Linux", "Darwin"]:  # Darwin is macOS
        return "Linux/macOS"
    else:
        return "Unknown"


def run_test_script(env_type, log_file):
    """Run the appropriate test script based on environment."""
    print(f"Environment detected: {env_type}")
    print(f"Running tests...")
    print(f"Logging to: {log_file}")
    print("-" * 60)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("AUTOMATED TEST EXECUTION LOG\n")
        f.write("=" * 60 + "\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Environment: {env_type}\n")
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Working Directory: {os.getcwd()}\n")
        f.write("=" * 60 + "\n\n")
        
        try:
            if env_type == "Windows":
                # Run Windows batch script
                script_path = "run_test.bat"
                if not os.path.exists(script_path):
                    error_msg = f"ERROR: {script_path} not found\n"
                    f.write(error_msg)
                    print(error_msg)
                    f.write("\n" + "=" * 60 + "\n")
                    f.write("Status: TEST FAILED\n")
                    f.write("=" * 60 + "\n")
                    return 1
                
                result = subprocess.run(
                    [script_path],
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
            elif env_type in ["Linux/macOS", "Docker"]:
                # Run bash script
                script_path = "run_test.sh"
                if not os.path.exists(script_path):
                    error_msg = f"ERROR: {script_path} not found\n"
                    f.write(error_msg)
                    print(error_msg)
                    f.write("\n" + "=" * 60 + "\n")
                    f.write("Status: TEST FAILED\n")
                    f.write("=" * 60 + "\n")
                    return 1
                
                # Make script executable
                os.chmod(script_path, 0o755)
                
                result = subprocess.run(
                    ["bash", script_path],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
            else:
                error_msg = f"ERROR: Unsupported environment: {env_type}\n"
                f.write(error_msg)
                print(error_msg)
                f.write("\n" + "=" * 60 + "\n")
                f.write("Status: TEST FAILED\n")
                f.write("=" * 60 + "\n")
                return 1
            
            # Write output to log
            output = result.stdout
            if result.stderr:
                output += "\n\nSTDERR:\n" + result.stderr
            
            f.write(output)
            f.write("\n")
            
            # Print to console
            print(output)
            
            # Write final status
            f.write("\n" + "=" * 60 + "\n")
            if result.returncode == 0:
                status_line = "Status: TEST PASSED"
                f.write(status_line + "\n")
                print("\n" + status_line)
            else:
                status_line = "Status: TEST FAILED"
                f.write(status_line + "\n")
                print("\n" + status_line)
            
            f.write("=" * 60 + "\n")
            f.write(f"Exit Code: {result.returncode}\n")
            f.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            return result.returncode
            
        except Exception as e:
            error_msg = f"\nERROR: Exception occurred during test execution:\n{str(e)}\n"
            f.write(error_msg)
            print(error_msg)
            f.write("\n" + "=" * 60 + "\n")
            f.write("Status: TEST FAILED\n")
            f.write("=" * 60 + "\n")
            return 1


def main():
    """Main execution function."""
    print("=" * 60)
    print("AUTOMATIC TEST EXECUTION")
    print("=" * 60)
    print()
    
    # Ensure log directory exists
    log_dir = ensure_log_directory()
    log_file = log_dir / "test_run.log"
    
    # Detect environment
    env_type = detect_environment()
    
    # Run tests
    exit_code = run_test_script(env_type, log_file)
    
    print()
    print("=" * 60)
    print(f"Log file saved to: {log_file}")
    print("=" * 60)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
