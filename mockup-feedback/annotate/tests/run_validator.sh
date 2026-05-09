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
echo "--- Test 3: overlay not last script before </body> should FAIL ---"
TMP_DIR=$(mktemp -d)
cp -r "$PASS_FIXTURE/"* "$TMP_DIR/"
# Inject a script tag AFTER annotation-overlay.js in index.html
sed -i 's|<script type="module" src="annotation-overlay.js"></script>|<script type="module" src="annotation-overlay.js"></script>\n<script src="extra.js"></script>|' "$TMP_DIR/index.html"
python "$VALIDATOR" "$TMP_DIR" && {
    echo "ERROR: validator returned 0 when overlay is not last script (expected 2)"
    rm -rf "$TMP_DIR"
    exit 1
} || {
    EC=$?
    if [ "$EC" -ne 2 ]; then
        echo "ERROR: expected exit code 2, got $EC"
        rm -rf "$TMP_DIR"
        exit 1
    fi
    echo "OK: validator correctly reported violation (exit 2)"
}
rm -rf "$TMP_DIR"

echo ""
echo "All tests passed."
