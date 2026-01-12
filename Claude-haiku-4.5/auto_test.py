#!/usr/bin/env python3
"""
Auto Test Script for Security Audit
Detects environment and runs appropriate test suite
"""

import os
import sys
import platform
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / "test_run.log"

# Set up logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def detect_environment():
    """Detect the current operating system."""
    system = platform.system()
    return system


def detect_if_docker():
    """Check if running inside Docker container."""
    return os.path.isfile('/.dockerenv')


def run_windows_tests():
    """Run tests on Windows platform."""
    logger.info("Detected Windows environment")
    logger.info("Running Windows test suite: run_test.bat")
    
    try:
        result = subprocess.run(
            ['cmd.exe', '/c', 'run_test.bat'],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Log the output
        if result.stdout:
            logger.info("Test Output:\n" + result.stdout)
        if result.stderr:
            logger.warning("Test Errors:\n" + result.stderr)
        
        # Log final status
        if result.returncode == 0:
            logger.info("=" * 50)
            logger.info("TEST PASSED")
            logger.info("=" * 50)
            return True
        else:
            logger.error("=" * 50)
            logger.error("TEST FAILED")
            logger.error("=" * 50)
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Test execution timed out after 300 seconds")
        logger.error("TEST FAILED")
        return False
    except Exception as e:
        logger.error(f"Error running Windows tests: {e}")
        logger.error("TEST FAILED")
        return False


def run_unix_tests():
    """Run tests on Linux/macOS platform."""
    system = platform.system()
    logger.info(f"Detected {system} environment")
    logger.info("Running Unix test suite: run_test.sh")
    
    try:
        # Make the script executable
        os.chmod('run_test.sh', 0o755)
        
        result = subprocess.run(
            ['bash', 'run_test.sh'],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Log the output
        if result.stdout:
            logger.info("Test Output:\n" + result.stdout)
        if result.stderr:
            logger.warning("Test Errors:\n" + result.stderr)
        
        # Log final status
        if result.returncode == 0:
            logger.info("=" * 50)
            logger.info("TEST PASSED")
            logger.info("=" * 50)
            return True
        else:
            logger.error("=" * 50)
            logger.error("TEST FAILED")
            logger.error("=" * 50)
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Test execution timed out after 300 seconds")
        logger.error("TEST FAILED")
        return False
    except FileNotFoundError:
        logger.error("run_test.sh not found or bash not available")
        logger.error("TEST FAILED")
        return False
    except Exception as e:
        logger.error(f"Error running Unix tests: {e}")
        logger.error("TEST FAILED")
        return False


def main():
    """Main entry point for auto_test.py"""
    logger.info("=" * 50)
    logger.info("Security Audit Auto Test Suite")
    logger.info("=" * 50)
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Python Version: {sys.version}")
    
    # Detect environment
    system = detect_environment()
    is_docker = detect_if_docker()
    
    logger.info(f"Operating System: {system}")
    logger.info(f"Running in Docker: {is_docker}")
    logger.info("")
    
    # Run appropriate tests based on environment
    success = False
    
    if system == "Windows":
        success = run_windows_tests()
    elif system in ["Linux", "Darwin"]:  # Darwin is macOS
        success = run_unix_tests()
    else:
        logger.error(f"Unsupported operating system: {system}")
        logger.error("TEST FAILED")
        success = False
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
