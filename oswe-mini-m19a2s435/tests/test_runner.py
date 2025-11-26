import sys
import os
import sqlite3
import importlib.util
import argparse
import json

DB_PATH = os.path.join(os.getcwd(), "user.db")


def setup_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    c.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("alice", "alice@example.com"))
    c.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("bob", "bob@example.com"))
    conn.commit()
    conn.close()


def remove_artifacts():
    for f in ["exploit.txt", "exploit_cfg.txt", "backup.tar.gz"]:
        if os.path.exists(f):
            os.remove(f)


def import_module_from_path(path):
    spec = importlib.util.spec_from_file_location("mod_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError("Cannot import module from path: %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_tests(module_path: str) -> int:
    setup_db()
    remove_artifacts()

    try:
        mod = import_module_from_path(module_path)
    except Exception as e:
        print("Failed to import module:", e)
        return 2

    # Test 1: SQL injection
    injection = "alice' OR '1'='1"
    try:
        users = mod.get_user_by_name(injection)
        users_alice = mod.get_user_by_name('alice')
    except Exception as e:
        print("get_user_by_name raised:", e)
        return 3

    if len(users_alice) != 1:
        print("SQL Injection baseline test failed: expected 1 result for 'alice', got", len(users_alice))
        return 4
    # Secure behavior: injection should not return more rows than the correct query
    if len(users) > len(users_alice):
        print("SQL Injection test failed: injection returned more rows than expected", len(users))
        return 5

    # Test 2: Command injection via run_backup
    try:
        # Attempt to inject shell command via filename
        mod.run_backup("dummy; touch exploit.txt")
    except Exception:
        # Expectation: the secure implementation should raise or reject
        pass
    # Check if exploit.txt exists
    if os.path.exists("exploit.txt"):
        print("Command Injection test failed: exploit.txt created")
        return 5

    # Test 3: eval/config execution
    try:
        mod.load_config("(__import__('os').system('echo exploit_cfg > exploit_cfg.txt'))")
    except Exception:
        # secure will raise
        pass
    if os.path.exists("exploit_cfg.txt"):
        print("Config eval test failed: exploit_cfg.txt created")
        return 6

    print("All tests passed for", module_path)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("module_path", help="Path to module to test (e.g., inputs.py)")
    args = parser.parse_args()
    rc = run_tests(args.module_path)
    sys.exit(rc)
