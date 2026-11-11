#!/usr/bin/env bash
# run_validator.sh — structural validation of patch skill output (validate_patches.py).
# This script does NOT run the LLM: it checks a patch set that is already written.
# Run from anywhere; paths resolve relative to this file.
#
# Ad hoc use:  bash tests/patch/run_validator.sh <patches-json> <review-md> <triage-json>
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VALIDATE="$SKILL_DIR/scripts/validate_patches.py"
FX="$SKILL_DIR/tests/patch/fixtures/test-routing"

if [ "$#" -ge 3 ]; then
    python3 "$VALIDATE" "$3" "$1" "$2"
    exit $?
fi

echo "--- Test 1: a good patch set (data-model proposal + screen patch + needs_manual) passes ---"
python3 "$VALIDATE" "$FX/triage.json" "$FX/patches.json" "$FX/review.md"

echo ""
echo "--- Test 2: a proposal with a bad anchor and no resolves, a yaml: anchor on a content patch, a blank resolution and a dropped note fail ---"
set +e
OUT=$(python3 "$VALIDATE" "$FX/triage.json" "$FX/patches-bad.json" "$FX/review.md")
EC=$?
set -e
echo "$OUT"
[ "$EC" -eq 2 ] || { echo "FAIL: expected exit 2, got $EC"; exit 1; }
for needle in "missing resolves" "is not entities.<Entity>" "diff missing valid @@ anchor header" "resolution must be non-empty" "p7q1z8-1"; do
    echo "$OUT" | grep -q "$needle" || { echo "FAIL: expected a finding mentioning '$needle'"; exit 1; }
done
echo "OK: all five violations reported"

echo ""
echo "All patch validator tests passed."
