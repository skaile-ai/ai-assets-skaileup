#!/usr/bin/env bash
# run_validator.sh — regression check for mockup-feedback-annotate validator
# Usage: bash tests/run_validator.sh
# Must be run from the skill root (mockup-feedback/annotate/).
set -e

PASS_FIXTURE="tests/expected/minimal"
FAIL_FIXTURE="tests/fixtures/minimal"
VALIDATOR="validator.py"

echo "--- Test 1: pre-injection fixture should FAIL ---"
python "$VALIDATOR" "$FAIL_FIXTURE" && {
    echo "ERROR: validator returned 0 on un-injected fixture (expected 2)"
    exit 1
} || {
    EC=$?
    if [ "$EC" -ne 2 ]; then
        echo "ERROR: expected exit code 2, got $EC"
        exit 1
    fi
    echo "OK: validator correctly reported violations (exit 2)"
}

echo ""
echo "--- Test 2: post-injection fixture should PASS ---"
python "$VALIDATOR" "$PASS_FIXTURE"
echo "OK: validator passed on injected fixture"

echo ""
echo "All tests passed."
