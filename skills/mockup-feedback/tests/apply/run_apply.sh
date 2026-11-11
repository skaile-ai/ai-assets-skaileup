#!/usr/bin/env bash
# run_apply.sh — integration tests for mockup-feedback-apply
# Uses throwaway git repos in temp dirs. Paths resolve relative to this file.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
FIXTURES="$SKILL_DIR/tests/apply/fixtures"
APPLY="$SKILL_DIR/scripts/apply.py"

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
    cp -r "$before_dir/concept" "$tmp/concept"
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
    "concept/09_mockup/feedback/patches/test-pass.json" \
    "concept/09_mockup/feedback/patches/test-pass.review.md" \
    "concept" "concept/09_mockup/feedback"
cd - > /dev/null

# Verify concept file matches expected
diff \
    "$FIXTURES/test-pass/after/concept/07_screens/01_user_auth/login.md" \
    "$TMP1/concept/07_screens/01_user_auth/login.md" \
    && echo "OK: login.md matches expected" \
    || { echo "FAIL: login.md content differs"; exit 1; }

# Verify applied JSON (strip volatile fields)
ACTUAL_NORM=$(normalize_applied < "$TMP1/concept/09_mockup/feedback/applied/test-pass.json")
EXPECTED_NORM=$(normalize_applied < "$FIXTURES/test-pass/after/concept/09_mockup/feedback/applied/test-pass.json")
[ "$ACTUAL_NORM" = "$EXPECTED_NORM" ] \
    && echo "OK: applied JSON matches expected" \
    || { echo "FAIL: applied JSON differs"; diff <(echo "$EXPECTED_NORM") <(echo "$ACTUAL_NORM"); exit 1; }

# Verify commit message
COMMIT_MSG=$(git -C "$TMP1" log -1 --format="%s")
[[ "$COMMIT_MSG" == *"round test-pass"* ]] \
    && echo "OK: commit message contains round ID" \
    || { echo "FAIL: commit message: $COMMIT_MSG"; exit 1; }

echo ""

# ── Test 2: partial failure — 1 applied, 1 failed ────────────────────────────
echo "--- Test 2: test-partial-fail (expect exit 0, 1 applied + 1 failed) ---"
TMP2=$(setup_repo "$FIXTURES/test-partial-fail/before")
trap 'rm -rf "$TMP1" "$TMP2"' EXIT

cd "$TMP2"
python3 "$APPLY" \
    "concept/09_mockup/feedback/patches/test-partial-fail.json" \
    "concept/09_mockup/feedback/patches/test-partial-fail.review.md" \
    "concept" "concept/09_mockup/feedback"
cd - > /dev/null

# Verify concept file (only the good patch should be applied)
diff \
    "$FIXTURES/test-partial-fail/after/concept/07_screens/01_user_auth/login.md" \
    "$TMP2/concept/07_screens/01_user_auth/login.md" \
    && echo "OK: login.md matches expected (good patch applied)" \
    || { echo "FAIL: login.md content differs"; exit 1; }

# Verify applied JSON has 1 applied + 1 failed
ACTUAL_NORM=$(normalize_applied < "$TMP2/concept/09_mockup/feedback/applied/test-partial-fail.json")
EXPECTED_NORM=$(normalize_applied < "$FIXTURES/test-partial-fail/after/concept/09_mockup/feedback/applied/test-partial-fail.json")
[ "$ACTUAL_NORM" = "$EXPECTED_NORM" ] \
    && echo "OK: applied JSON matches expected (failed item recorded)" \
    || { echo "FAIL: applied JSON differs"; diff <(echo "$EXPECTED_NORM") <(echo "$ACTUAL_NORM"); exit 1; }

COMMIT_MSG2=$(git -C "$TMP2" log -1 --format="%s")
[[ "$COMMIT_MSG2" == *"round test-partial-fail"* ]] \
    && echo "OK: commit message contains round ID" \
    || { echo "FAIL: commit message: $COMMIT_MSG2"; exit 1; }

echo ""

# ── Test 3: all-fail short-circuit ────────────────────────────────────────────
echo "--- Test 3: test-all-fail (expect exit 2, no commit, no applied JSON) ---"
TMP3=$(setup_repo "$FIXTURES/test-all-fail/before")
trap 'rm -rf "$TMP1" "$TMP2" "$TMP3" "$TMP4" "$TMP5"' EXIT

cd "$TMP3"
set +e
python3 "$APPLY" \
    "concept/09_mockup/feedback/patches/test-all-fail.json" \
    "concept/09_mockup/feedback/patches/test-all-fail.review.md" \
    "concept" "concept/09_mockup/feedback"
EC=$?
set -e
cd - > /dev/null

[ "$EC" -eq 2 ] \
    && echo "OK: exit code 2 (all-failed)" \
    || { echo "FAIL: expected exit 2, got $EC"; exit 1; }

[ ! -f "$TMP3/concept/09_mockup/feedback/applied/test-all-fail.json" ] \
    && echo "OK: no applied JSON written" \
    || { echo "FAIL: applied JSON was written (should not exist)"; exit 1; }

COMMIT_COUNT=$(git -C "$TMP3" log --oneline | wc -l | tr -d ' ')
[ "$COMMIT_COUNT" -eq 1 ] \
    && echo "OK: only the initial commit exists (no feedback commit)" \
    || { echo "FAIL: unexpected commit count: $COMMIT_COUNT"; exit 1; }

# Verify retry without --force succeeds cleanly (exits 2 again, not 1)
set +e
(cd "$TMP3" && python3 "$APPLY" \
    "concept/09_mockup/feedback/patches/test-all-fail.json" \
    "concept/09_mockup/feedback/patches/test-all-fail.review.md" \
    "concept" "concept/09_mockup/feedback")
EC2=$?
set -e
[ "$EC2" -eq 2 ] \
    && echo "OK: retry exits 2 cleanly without --force (no lockout)" \
    || { echo "FAIL: retry failed unexpectedly with exit $EC2"; exit 1; }

echo ""

# ── Test 4: proposals — filed in one proposal file, owner artifacts untouched, notes recorded as pending ──
echo "--- Test 4: test-model-proposal (field + entity + glossary term; proposal file written; resolution pending) ---"
TMP4=$(setup_repo "$FIXTURES/test-model-proposal/before")
trap 'rm -rf "$TMP1" "$TMP2" "$TMP3" "$TMP4" "$TMP5"' EXIT

(cd "$TMP4" && python3 "$APPLY" \
    "concept/09_mockup/feedback/patches/test-model-proposal.json" \
    "concept/09_mockup/feedback/patches/test-model-proposal.review.md" \
    "concept" "concept/09_mockup/feedback")

# The proposal file is named and dated by the day of the run; the fixture's date is masked.
mask_date() {
    python3 -c "
import re, sys
t = sys.stdin.read()
t = re.sub(r'\d{4}-\d{2}-\d{2}-mockup-feedback', '<date>-mockup-feedback', t)
print(re.sub(r'(?m)^proposed_on: \d{4}-\d{2}-\d{2}$', 'proposed_on: <date>', t))
"
}

for f in 10_blueprint/datamodel/model.yaml glossary.md; do
    diff "$FIXTURES/test-model-proposal/after/concept/$f" "$TMP4/concept/$f" \
        && echo "OK: $f unchanged" \
        || { echo "FAIL: $f was edited"; exit 1; }
done

PROPOSALS=("$TMP4"/concept/proposals/*-mockup-feedback-test-model-proposal.yaml)
[ "${#PROPOSALS[@]}" -eq 1 ] && [ -f "${PROPOSALS[0]}" ] \
    || { echo "FAIL: expected one proposal file, found: ${PROPOSALS[*]}"; exit 1; }
[ "$(mask_date < "${PROPOSALS[0]}")" = "$(mask_date < "$FIXTURES"/test-model-proposal/after/concept/proposals/*-mockup-feedback-test-model-proposal.yaml)" ] \
    && echo "OK: proposal file matches expected" \
    || { echo "FAIL: proposal file differs"; cat "${PROPOSALS[0]}"; exit 1; }

ACTUAL_NORM=$(normalize_applied < "$TMP4/concept/09_mockup/feedback/applied/test-model-proposal.json" | mask_date)
EXPECTED_NORM=$(normalize_applied < "$FIXTURES/test-model-proposal/after/concept/09_mockup/feedback/applied/test-model-proposal.json" | mask_date)
[ "$ACTUAL_NORM" = "$EXPECTED_NORM" ] \
    && echo "OK: applied JSON matches expected (proposals landed, resolutions pending)" \
    || { echo "FAIL: applied JSON differs"; diff <(echo "$EXPECTED_NORM") <(echo "$ACTUAL_NORM"); exit 1; }

git -C "$TMP4" ls-files --error-unmatch "${PROPOSALS[0]#"$TMP4"/}" > /dev/null 2>&1 \
    && echo "OK: proposal file committed" \
    || { echo "FAIL: proposal file not committed"; exit 1; }

echo ""

# ── Test 5: a malformed proposal (bad anchor) fails — nothing is filed, nothing is committed ──
echo "--- Test 5: test-model-bad (anchor outside the model grammar; expect exit 2, no proposal file, no commit) ---"
TMP5=$(setup_repo "$FIXTURES/test-model-bad/before")
BEFORE_SUM=$(shasum "$TMP5/concept/10_blueprint/datamodel/model.yaml")

set +e
OUT5=$(cd "$TMP5" && python3 "$APPLY" \
    "concept/09_mockup/feedback/patches/test-model-bad.json" \
    "concept/09_mockup/feedback/patches/test-model-bad.review.md" \
    "concept" "concept/09_mockup/feedback" 2>&1)
EC5=$?
set -e
echo "$OUT5"
[ "$EC5" -eq 2 ] \
    && echo "OK: exit code 2 (the only patch failed)" \
    || { echo "FAIL: expected exit 2, got $EC5"; exit 1; }
echo "$OUT5" | grep -q "model anchor must be entities" \
    && echo "OK: the bad anchor is named" \
    || { echo "FAIL: the bad anchor is not reported"; exit 1; }
[ "$BEFORE_SUM" = "$(shasum "$TMP5/concept/10_blueprint/datamodel/model.yaml")" ] \
    && echo "OK: model.yaml untouched" \
    || { echo "FAIL: model.yaml changed"; exit 1; }
[ ! -e "$TMP5/concept/proposals" ] \
    && echo "OK: no proposal file" \
    || { echo "FAIL: a proposal file was written"; exit 1; }
[ "$(git -C "$TMP5" log --oneline | wc -l | tr -d ' ')" -eq 1 ] \
    && echo "OK: no feedback commit" \
    || { echo "FAIL: unexpected commit count"; exit 1; }

echo ""
echo "All apply integration tests passed."
