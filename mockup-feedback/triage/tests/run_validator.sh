#!/usr/bin/env bash
# run_validator.sh — triage regression tests
# Run from mockup-feedback/triage/
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES_DIR="$SKILL_DIR/../_test-fixtures"
CONCEPT_ROOT="$FIXTURES_DIR/concept"
SESSIONS_DIR="$FIXTURES_DIR/sessions"
EXPECTED_DIR="$SKILL_DIR/tests/expected"
TMP_OUT="$(mktemp -d)"
trap "rm -rf $TMP_OUT" EXIT

normalize_json() {
    # Strip volatile triagedAt field for comparison
    python3 -c "
import json, sys
d = json.load(sys.stdin)
d.pop('triagedAt', None)
print(json.dumps(d, indent=2, sort_keys=True))
"
}

compare_triage() {
    local sid="$1"
    local actual="$TMP_OUT/${sid}.json"
    local expected="$EXPECTED_DIR/${sid}.json"

    python3 "$SKILL_DIR/triage.py" \
        "$SESSIONS_DIR/${sid}.json" \
        "$CONCEPT_ROOT" \
        "$TMP_OUT" > /dev/null

    local actual_norm
    actual_norm=$(normalize_json < "$actual")
    local expected_norm
    expected_norm=$(normalize_json < "$expected")

    if [ "$actual_norm" != "$expected_norm" ]; then
        echo "FAIL: triage output for $sid differs from expected"
        diff <(echo "$expected_norm") <(echo "$actual_norm") || true
        return 1
    fi
    echo "OK: $sid triage matches expected"
}

echo "--- Test 1: test-minimal golden output ---"
compare_triage "test-minimal"

echo ""
echo "--- Test 2: test-bad-ref unresolved path ---"
compare_triage "test-bad-ref"

echo ""
echo "--- Test 3: structural validator on test-minimal output ---"
python3 "$SKILL_DIR/validator.py" \
    "$TMP_OUT/test-minimal.json" \
    "$SESSIONS_DIR/test-minimal.json"

echo ""
echo "--- Test 4: structural validator on test-bad-ref output ---"
python3 "$SKILL_DIR/validator.py" \
    "$TMP_OUT/test-bad-ref.json" \
    "$SESSIONS_DIR/test-bad-ref.json"

echo ""
echo "All triage tests passed."
