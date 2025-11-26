import os
import sqlite3
import importlib.util
import pytest

ARTIFACTS = ["exploit.txt", "exploit_cfg.txt", "backup.tar.gz"]
DB_PATH = os.path.join(os.getcwd(), "user.db")


def import_module(path):
    spec = importlib.util.spec_from_file_location("mod_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import module from path: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    for f in ARTIFACTS:
        if os.path.exists(f):
            os.remove(f)


@pytest.fixture(scope="module")
def module_under_test():
    path = os.environ.get("MODULE_PATH", "inputs.py")
    setup_db()
    remove_artifacts()
    return import_module(path)


def test_sql_injection_protection(module_under_test):
    mod = module_under_test
    # Baseline behavior with a valid username
    users_alice = mod.get_user_by_name("alice")
    assert len(users_alice) == 1, "Baseline user query should return 1 row"

    # Attempt an SQL injection and assert return doesn't produce more rows than baseline
    injection = "alice' OR '1'='1"
    users_injection = mod.get_user_by_name(injection)
    assert len(users_injection) <= len(users_alice), "SQL Injection detected: injection returns more rows than baseline"


def test_backup_no_command_injection(module_under_test):
    mod = module_under_test
    # Try to inject a command through filename
    import platform
    if platform.system() == "Windows":
        dangerous_name = "dummy & echo exploit>exploit.txt"
    else:
        dangerous_name = "dummy; touch exploit.txt"
    try:
        mod.run_backup(dangerous_name)
    except Exception:
        # expected for secure implementation
        pass
    # Ensure no exploit file was created
    assert not os.path.exists("exploit.txt"), "Command injection occurred: exploit file created"


def test_load_config_no_eval(module_under_test):
    mod = module_under_test
    # Passing a malicious payload that tries to create a file
    malicious = "(__import__('os').system('echo exploit_cfg > exploit_cfg.txt'))"
    try:
        mod.load_config(malicious)
    except Exception:
        # secure code may raise; that's acceptable
        pass
    assert not os.path.exists("exploit_cfg.txt"), "Config eval vulnerability: exploit_cfg.txt created"


if __name__ == "__main__":
    pytest.main([os.path.basename(__file__)])
