#!/usr/bin/env bash
# run_apply.sh — integration tests for mockup-feedback-apply
# Uses throwaway git repos in temp dirs. Run from mockup-feedback/apply/.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURES="$SKILL_DIR/tests/fixtures"
APPLY="$SKILL_DIR/apply.py"

normalize_applied() {
    python3 -c "
import json, sys
d = json.load(sys.stdin)
d.pop('appliedAt', None)
print(json.dumps(d, indent=2, sort_keys=True))
"
}

# ── Helper: set up a temp git repo from a before/ dir ────────────────────────
setup_repo() {
    local before_dir="$1"
    local tmp
    tmp=$(mktemp -d)
    cp -r "$before_dir/concept"   "$tmp/concept"
    cp -r "$before_dir/_feedback" "$tmp/_feedback"
    git -C "$tmp" init -q
    git -C "$tmp" config user.email "test@test.com"
    git -C "$tmp" config user.name "Test"
    git -C "$tmp" add .
    git -C "$tmp" commit -q -m "initial"
    echo "$tmp"
}

# ── Test 1: happy path — 2 patches, both applied ─────────────────────────────
echo "--- Test 1: test-pass (expect exit 0, 2 applied) ---"
TMP1=$(setup_repo "$FIXTURES/test-pass/before")
trap 'rm -rf "$TMP1"' EXIT

cd "$TMP1"
python3 "$APPLY" \
    "_feedback/patches/test-pass.json" \
    "_feedback/patches/test-pass.review.md" \
    "concept" "_feedback"
cd - > /dev/null

# Verify concept file matches expected
diff \
    "$FIXTURES/test-pass/after/concept/experience/screens/01_user_auth/login.md" \
    "$TMP1/concept/experience/screens/01_user_auth/login.md" \
    && echo "OK: login.md matches expected" \
    || { echo "FAIL: login.md content differs"; exit 1; }

# Verify applied JSON (strip volatile fields)
ACTUAL_NORM=$(normalize_applied < "$TMP1/_feedback/applied/test-pass.json")
EXPECTED_NORM=$(normalize_applied < "$FIXTURES/test-pass/after/_feedback/applied/test-pass.json")
[ "$ACTUAL_NORM" = "$EXPECTED_NORM" ] \
    && echo "OK: applied JSON matches expected" \
    || { echo "FAIL: applied JSON differs"; diff <(echo "$EXPECTED_NORM") <(echo "$ACTUAL_NORM"); exit 1; }

# Verify commit message
COMMIT_MSG=$(git -C "$TMP1" log -1 --format="%s")
[[ "$COMMIT_MSG" == *"session test-pass"* ]] \
    && echo "OK: commit message contains session ID" \
    || { echo "FAIL: commit message: $COMMIT_MSG"; exit 1; }

echo ""

# ── Test 2: partial failure — 1 applied, 1 failed ────────────────────────────
echo "--- Test 2: test-partial-fail (expect exit 0, 1 applied + 1 failed) ---"
TMP2=$(setup_repo "$FIXTURES/test-partial-fail/before")
trap 'rm -rf "$TMP1" "$TMP2"' EXIT

cd "$TMP2"
python3 "$APPLY" \
    "_feedback/patches/test-partial-fail.json" \
    "_feedback/patches/test-partial-fail.review.md" \
    "concept" "_feedback"
cd - > /dev/null

# Verify concept file (only the good patch should be applied)
diff \
    "$FIXTURES/test-partial-fail/after/concept/experience/screens/01_user_auth/login.md" \
    "$TMP2/concept/experience/screens/01_user_auth/login.md" \
    && echo "OK: login.md matches expected (good patch applied)" \
    || { echo "FAIL: login.md content differs"; exit 1; }

# Verify applied JSON has 1 applied + 1 failed
ACTUAL_NORM=$(normalize_applied < "$TMP2/_feedback/applied/test-partial-fail.json")
EXPECTED_NORM=$(normalize_applied < "$FIXTURES/test-partial-fail/after/_feedback/applied/test-partial-fail.json")
[ "$ACTUAL_NORM" = "$EXPECTED_NORM" ] \
    && echo "OK: applied JSON matches expected (failed item recorded)" \
    || { echo "FAIL: applied JSON differs"; diff <(echo "$EXPECTED_NORM") <(echo "$ACTUAL_NORM"); exit 1; }

COMMIT_MSG2=$(git -C "$TMP2" log -1 --format="%s")
[[ "$COMMIT_MSG2" == *"session test-partial-fail"* ]] \
    && echo "OK: commit message contains session ID" \
    || { echo "FAIL: commit message: $COMMIT_MSG2"; exit 1; }

echo ""

# ── Test 3: all-fail short-circuit ────────────────────────────────────────────
echo "--- Test 3: test-all-fail (expect exit 2, no commit, no applied JSON) ---"
TMP3=$(setup_repo "$FIXTURES/test-all-fail/before")
trap 'rm -rf "$TMP1" "$TMP2" "$TMP3"' EXIT

cd "$TMP3"
set +e
python3 "$APPLY" \
    "_feedback/patches/test-all-fail.json" \
    "_feedback/patches/test-all-fail.review.md" \
    "concept" "_feedback"
EC=$?
set -e
cd - > /dev/null

[ "$EC" -eq 2 ] \
    && echo "OK: exit code 2 (all-failed)" \
    || { echo "FAIL: expected exit 2, got $EC"; exit 1; }

[ ! -f "$TMP3/_feedback/applied/test-all-fail.json" ] \
    && echo "OK: no applied JSON written" \
    || { echo "FAIL: applied JSON was written (should not exist)"; exit 1; }

COMMIT_COUNT=$(git -C "$TMP3" log --oneline | wc -l | tr -d ' ')
[ "$COMMIT_COUNT" -eq 1 ] \
    && echo "OK: only the initial commit exists (no feedback commit)" \
    || { echo "FAIL: unexpected commit count: $COMMIT_COUNT"; exit 1; }

# Verify retry without --force succeeds cleanly (exits 2 again, not 1)
set +e
(cd "$TMP3" && python3 "$APPLY" \
    "_feedback/patches/test-all-fail.json" \
    "_feedback/patches/test-all-fail.review.md" \
    "concept" "_feedback")
EC2=$?
set -e
[ "$EC2" -eq 2 ] \
    && echo "OK: retry exits 2 cleanly without --force (no lockout)" \
    || { echo "FAIL: retry failed unexpectedly with exit $EC2"; exit 1; }

echo ""
echo "All apply integration tests passed."
