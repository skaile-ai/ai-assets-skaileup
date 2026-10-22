#!/usr/bin/env bash
# run_apply.sh — integration tests for mockup-feedback-apply
# Uses throwaway git repos in temp dirs. Paths resolve relative to this file.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
FIXTURES="$SKILL_DIR/tests/apply/fixtures"
APPLY="$SKILL_DIR/scripts/apply.py"
DSL_DIR="$REPO_DIR/skills/architecture-datamodel/references/dsl"
SCHEMA_DIR="$REPO_DIR/tree/10_blueprint/datamodel"

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

# ── Helper: copy the DSL tool files and schemas into the temp repo's datamodel dir, as architecture-datamodel does
install_dsl() {
    local dir="$1/concept/10_blueprint/datamodel"
    cp "$DSL_DIR/skaile-model.ts" "$DSL_DIR/gen.ts" "$SCHEMA_DIR"/datamodel-model.schema.json "$SCHEMA_DIR"/datamodel-seed.schema.json "$dir/"
    git -C "$1" add .
    git -C "$1" commit -q -m "install DSL tool files"
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

# ── Test 4: model proposals — gen.ts accepts, glossary patched, notes recorded as pending ──
echo "--- Test 4: test-model-proposal (field + entity + glossary; gen.ts runs; resolution pending) ---"
TMP4=$(setup_repo "$FIXTURES/test-model-proposal/before")
trap 'rm -rf "$TMP1" "$TMP2" "$TMP3" "$TMP4" "$TMP5"' EXIT
install_dsl "$TMP4"

(cd "$TMP4" && python3 "$APPLY" \
    "concept/09_mockup/feedback/patches/test-model-proposal.json" \
    "concept/09_mockup/feedback/patches/test-model-proposal.review.md" \
    "concept" "concept/09_mockup/feedback")

for f in 10_blueprint/datamodel/model.ts glossary.md; do
    diff "$FIXTURES/test-model-proposal/after/concept/$f" "$TMP4/concept/$f" \
        && echo "OK: $f matches expected" \
        || { echo "FAIL: $f differs"; exit 1; }
done

ACTUAL_NORM=$(normalize_applied < "$TMP4/concept/09_mockup/feedback/applied/test-model-proposal.json")
EXPECTED_NORM=$(normalize_applied < "$FIXTURES/test-model-proposal/after/concept/09_mockup/feedback/applied/test-model-proposal.json")
[ "$ACTUAL_NORM" = "$EXPECTED_NORM" ] \
    && echo "OK: applied JSON matches expected (resolutions pending)" \
    || { echo "FAIL: applied JSON differs"; diff <(echo "$EXPECTED_NORM") <(echo "$ACTUAL_NORM"); exit 1; }

# gen.ts ran: the generated model.json carries the proposal markers (field and entity)
python3 - "$TMP4/concept/10_blueprint/datamodel/model.json" <<'PY' \
    && echo "OK: model.json carries the proposal markers" \
    || { echo "FAIL: model.json lacks the proposal markers"; exit 1; }
import json, sys
m = json.load(open(sys.argv[1]))
ents = {e["id"]: e for e in m["entities"]}
est = next(f for f in ents["Task"]["fields"] if f["name"] == "estimate")
assert (est["status"], est["proposed_by"], est["proposed_on"], est["source"]) == ("proposed", "mockup-feedback", "2026-10-23", "k3m9x2-1"), est
c = ents["Comment"]
assert (c["status"], c["proposed_by"], c["source"]) == ("proposed", "mockup-feedback", "k3m9x2-4"), c
PY

echo ""

# ── Test 5: gen.ts rejects the new field — model.ts is left as it was, nothing is committed ──
echo "--- Test 5: test-model-bad (gen.ts rejects; expect exit 2, model.ts reverted, no commit) ---"
TMP5=$(setup_repo "$FIXTURES/test-model-bad/before")
install_dsl "$TMP5"
BEFORE_SUM=$(shasum "$TMP5/concept/10_blueprint/datamodel/model.ts")

set +e
(cd "$TMP5" && python3 "$APPLY" \
    "concept/09_mockup/feedback/patches/test-model-bad.json" \
    "concept/09_mockup/feedback/patches/test-model-bad.review.md" \
    "concept" "concept/09_mockup/feedback")
EC5=$?
set -e
[ "$EC5" -eq 2 ] \
    && echo "OK: exit code 2 (the only patch failed)" \
    || { echo "FAIL: expected exit 2, got $EC5"; exit 1; }
[ "$BEFORE_SUM" = "$(shasum "$TMP5/concept/10_blueprint/datamodel/model.ts")" ] \
    && echo "OK: model.ts reverted to its previous content" \
    || { echo "FAIL: model.ts changed"; exit 1; }
[ "$(git -C "$TMP5" log --oneline | wc -l | tr -d ' ')" -eq 2 ] \
    && echo "OK: no feedback commit" \
    || { echo "FAIL: unexpected commit count"; exit 1; }

echo ""
echo "All apply integration tests passed."
