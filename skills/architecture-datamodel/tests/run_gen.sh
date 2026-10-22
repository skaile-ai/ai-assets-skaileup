#!/usr/bin/env bash
# run_gen.sh — data-model DSL regression tests (skaile-model.ts + gen.ts)
# Run from anywhere. Needs node >= 20 and network for `npx -y` (tsx, typescript) on first use.
# Each case copies the tool files and the tree's two schemas into a temp dir, exactly as the skill
# does for a project; no copy of the runtime is committed under fixtures/.
set -e

TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$TESTS_DIR/.." && pwd)"
REPO_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
DSL_DIR="$SKILL_DIR/references/dsl"
SCHEMA_DIR="$REPO_DIR/tree/10_blueprint/datamodel"
FIXTURES="$TESTS_DIR/fixtures"
EXPECTED="$TESTS_DIR/expected"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

TSX=(npx -y tsx)
TSC=(npx -y -p typescript@5.9.3 tsc --noEmit --strict --target es2022 --module esnext --moduleResolution bundler)

# project <name> <fixture>...: a datamodel dir with the tool files, the schemas, then each fixture dir's files
project() {
    local dir="$WORK/$1"
    shift
    mkdir -p "$dir"
    cp "$DSL_DIR/skaile-model.ts" "$DSL_DIR/gen.ts" "$SCHEMA_DIR"/datamodel-model.schema.json "$SCHEMA_DIR"/datamodel-seed.schema.json "$dir/"
    for fixture in "$@"; do cp "$FIXTURES/$fixture"/* "$dir/"; done
    echo "$dir"
}

echo "--- Test 1: generated files equal the checked-in expected files, byte for byte ---"
DIR="$(project basic basic)"
(cd "$DIR" && "${TSX[@]}" gen.ts > /dev/null)
for f in model.json model.dbml seed.json; do
    if ! diff -u "$EXPECTED/$f" "$DIR/$f"; then
        echo "FAIL: $f differs from expected/$f"
        exit 1
    fi
    echo "OK: $f"
done

echo ""
echo "--- Test 2: a second run changes nothing (deterministic) ---"
(cd "$DIR" && "${TSX[@]}" gen.ts > /dev/null)
for f in model.json model.dbml seed.json; do
    diff -q "$EXPECTED/$f" "$DIR/$f" > /dev/null || { echo "FAIL: $f changed on the second run"; exit 1; }
done
echo "OK: stable"

echo ""
echo "--- Test 3: the editor key of an existing model.json survives, the rest is regenerated ---"
DIR="$(project with-editor basic with-editor)"
(cd "$DIR" && "${TSX[@]}" gen.ts > /dev/null)
python3 - "$DIR/model.json" "$EXPECTED/model.json" <<'PY'
import json, sys
actual, expected = (json.load(open(p)) for p in sys.argv[1:3])
assert actual.get("editor") == {"viewport": {"x": -120, "y": 48.5, "zoom": 0.75}}, f"editor lost: {actual.get('editor')}"
del actual["editor"]
assert actual == expected, "model.json differs from expected once editor is removed"
print("OK: editor kept")
PY

echo ""
echo "--- Test 4: the fixture type-checks (model.ts + seed.ts) ---"
DIR="$(project basic basic)"
(cd "$DIR" && "${TSC[@]}" model.ts seed.ts)
echo "OK: tsc clean"

echo ""
echo "--- Test 5: a seed row with a misspelled field fails tsc and names the field ---"
DIR="$(project bad-seed basic bad-seed-field)"
if OUT="$(cd "$DIR" && "${TSC[@]}" model.ts seed.ts 2>&1)"; then
    echo "FAIL: tsc accepted the misspelled field"
    exit 1
fi
echo "$OUT" | grep -q "'titel' does not exist" || { echo "FAIL: tsc error does not name 'titel':"; echo "$OUT"; exit 1; }
echo "OK: tsc names titel"

echo ""
echo "--- Test 6: gen.ts rejects the same seed at run time, naming the path and the field ---"
if OUT="$(cd "$DIR" && "${TSX[@]}" gen.ts 2>&1)"; then
    echo "FAIL: gen.ts accepted the misspelled field"
    exit 1
fi
echo "$OUT" | grep -q 'seed.ts: \$.scenarios.edge_cases.data.task\[0\].titel: Task has no field "titel"' || { echo "FAIL: unexpected message:"; echo "$OUT"; exit 1; }
[ ! -e "$DIR/model.json" ] || { echo "FAIL: gen.ts wrote model.json despite the violation"; exit 1; }
echo "OK: refused, nothing written"

echo ""
echo "--- Test 7: a schema violation exits non-zero with the JSON path and the schema pointer ---"
DIR="$(project bad-schema bad-schema)"
if OUT="$(cd "$DIR" && "${TSX[@]}" gen.ts 2>&1)"; then
    echo "FAIL: gen.ts accepted a camelCase field name"
    exit 1
fi
echo "$OUT" | grep -q 'model.json: \$.entities\[0\].fields\[0\].name: "displayName" does not match .*datamodel-model.schema.json#/\$defs/snakeName' \
    || { echo "FAIL: unexpected message:"; echo "$OUT"; exit 1; }
echo "OK: $(echo "$OUT" | head -1)"

echo ""
echo "--- Test 8: a schema keyword gen.ts does not implement fails loudly ---"
DIR="$(project strict basic)"
python3 - "$DIR/datamodel-seed.schema.json" <<'PY'
import json, sys
p = sys.argv[1]
s = json.load(open(p))
s["properties"]["version"]["maxLength"] = 3
json.dump(s, open(p, "w"))
PY
if OUT="$(cd "$DIR" && "${TSX[@]}" gen.ts 2>&1)"; then
    echo "FAIL: gen.ts ignored an unknown schema keyword"
    exit 1
fi
echo "$OUT" | grep -q 'does not implement schema keyword "maxLength"' || { echo "FAIL: unexpected message:"; echo "$OUT"; exit 1; }
echo "OK: maxLength refused"

echo ""
echo "All data-model DSL tests passed."
