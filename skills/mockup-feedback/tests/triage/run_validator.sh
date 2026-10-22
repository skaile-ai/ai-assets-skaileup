#!/usr/bin/env bash
# run_validator.sh — triage regression tests
# Run from anywhere; paths resolve relative to this file.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FIXTURES_DIR="$SKILL_DIR/tests/shared-fixtures"
CONCEPT_ROOT="$FIXTURES_DIR/concept"
INBOX="$FIXTURES_DIR/annotations"
EXPECTED_DIR="$SKILL_DIR/tests/triage/expected"
TMP_OUT="$(mktemp -d)"
trap 'rm -rf "$TMP_OUT"' EXIT

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
    local round="$1"
    local concept="$2"
    local actual="$TMP_OUT/${round}.json"
    local expected="$EXPECTED_DIR/${round}.json"

    python3 "$SKILL_DIR/scripts/triage.py" "$concept" "$TMP_OUT" \
        --inbox "$INBOX" --round "$round" > /dev/null 2>&1

    local actual_norm expected_norm
    actual_norm=$(normalize_json < "$actual")
    expected_norm=$(normalize_json < "$expected")

    if [ "$actual_norm" != "$expected_norm" ]; then
        echo "FAIL: triage output for $round differs from expected"
        diff <(echo "$expected_norm") <(echo "$actual_norm") || true
        return 1
    fi
    echo "OK: $round triage matches expected"
}

echo "--- Test 1: entity note -> model.ts + entity, screen note -> its spec, journey note -> stories.yaml ---"
compare_triage "test-routing" "$CONCEPT_ROOT"

echo ""
echo "--- Test 2: without model.ts the entity note is unresolved ---"
NO_MODEL="$TMP_OUT/concept-no-model"
cp -r "$CONCEPT_ROOT" "$NO_MODEL"
rm -rf "$NO_MODEL/10_blueprint"
compare_triage "test-no-model" "$NO_MODEL"

echo ""
echo "--- Test 3: a closed note is not triaged ---"
if grep -q "x0y4w6-1" "$TMP_OUT/test-routing.json"; then
    echo "FAIL: closed note x0y4w6-1 was triaged"; exit 1
fi
echo "OK: closed note skipped"

echo ""
echo "--- Test 4: default inbox is .data/annotations beside the concept root ---"
PROJ="$TMP_OUT/project"
mkdir -p "$PROJ/.data"
cp -r "$CONCEPT_ROOT" "$PROJ/_concept"
cp -r "$INBOX" "$PROJ/.data/annotations"
python3 "$SKILL_DIR/scripts/triage.py" "$PROJ/_concept" "$TMP_OUT/default" --round test-default > /dev/null 2>&1
[ -f "$TMP_OUT/default/test-default.json" ] \
    && echo "OK: default inbox found" \
    || { echo "FAIL: default inbox not used"; exit 1; }

echo ""
echo "--- Test 5: structural validator on both outputs ---"
python3 "$SKILL_DIR/scripts/validate_triage.py" "$TMP_OUT/test-routing.json" "$INBOX"
python3 "$SKILL_DIR/scripts/validate_triage.py" "$TMP_OUT/test-no-model.json" "$INBOX"

echo ""
echo "All triage tests passed."
