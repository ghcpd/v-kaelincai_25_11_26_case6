#!/usr/bin/env bash
set -euo pipefail
TARGET=${TEST_TARGET:-input.py}
python test_security.py --file "$TARGET"
