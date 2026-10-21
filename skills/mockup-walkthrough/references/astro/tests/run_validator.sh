#!/usr/bin/env bash
# mockup-walkthrough-astro — fixture validator harness.
#
# Bootstrap mode: copies the hand-curated expected snapshot to
#   tests/rendered/minimal/  (proves the validator is internally
#   consistent before the renderer is wired up)
# then runs the validator in fixture + negative-test modes against it.
#
# When the renderer ships (bun install && bun run build wired up), replace
# the cp step with the actual render-then-validate invocation.
set -euo pipefail

cd "$(dirname "$0")"
_WORK=""
_cleanup() { [[ -n "$_WORK" ]] && rm -rf "$_WORK"; true; }
trap _cleanup EXIT

SKILL_DIR="$(cd .. && pwd)"
SITE_DIR="rendered/minimal"
FIXTURE_SRC="fixtures/minimal"
RULEBOOK="$(cd ../../../../.. && pwd)/rulebook"

echo "=== mockup-walkthrough-astro validator tests ==="

# Bootstrap rendered/ from expected/ — proves snapshot-to-snapshot consistency.
rm -rf "$SITE_DIR"
mkdir -p "$SITE_DIR"
cp -r expected/minimal/. "$SITE_DIR/"

echo ""
echo "1. Structural + fixture-mode pass (rendered/minimal)..."
python3 "$SKILL_DIR/validator.py" "$SITE_DIR" \
  --fixture minimal \
  --source-root "$FIXTURE_SRC/07_screens" \
  --project-root "$FIXTURE_SRC" \
  --rulebook "$RULEBOOK" \
  --cwd "$(pwd)"
echo "   PASS"

echo ""
echo "2. dist/ check — FAIL expected..."
_WORK=$(mktemp -d)
cp -r "$SITE_DIR/." "$_WORK/"
mkdir "$_WORK/dist"
_rc=0
python3 "$SKILL_DIR/validator.py" "$_WORK" \
  --source-root "$FIXTURE_SRC/07_screens" \
  --project-root "$FIXTURE_SRC" \
  --cwd "$(pwd)" || _rc=$?
if [[ $_rc -eq 0 ]]; then echo "   UNEXPECTED PASS"; exit 1; fi
if [[ $_rc -ne 2 ]]; then echo "   UNEXPECTED EXIT CODE $_rc (expected 2)"; exit 1; fi
echo "   FAIL as expected (exit 2)"
rm -rf "$_WORK"
_WORK=""

echo ""
echo "3. Wrong renderer name — FAIL expected..."
_WORK=$(mktemp -d)
cp -r "$SITE_DIR/." "$_WORK/"
python3 -c "
import json, pathlib
p = pathlib.Path('$_WORK/manifest.json')
m = json.loads(p.read_text())
m['renderer'] = 'wrong-renderer'
p.write_text(json.dumps(m, indent=2))
"
_rc=0
python3 "$SKILL_DIR/validator.py" "$_WORK" \
  --source-root "$FIXTURE_SRC/07_screens" \
  --project-root "$FIXTURE_SRC" \
  --cwd "$(pwd)" || _rc=$?
if [[ $_rc -eq 0 ]]; then echo "   UNEXPECTED PASS"; exit 1; fi
if [[ $_rc -ne 2 ]]; then echo "   UNEXPECTED EXIT CODE $_rc (expected 2)"; exit 1; fi
echo "   FAIL as expected (exit 2)"
rm -rf "$_WORK"
_WORK=""

echo ""
echo "4. Missing stylesheet — FAIL expected..."
_WORK=$(mktemp -d)
cp -r "$SITE_DIR/." "$_WORK/"
python3 -c "
import pathlib
p = pathlib.Path('$_WORK/index.html')
text = p.read_text().replace('<link rel=\"stylesheet\" href=\"/_astro/style.css\">', '')
p.write_text(text)
"
_rc=0
python3 "$SKILL_DIR/validator.py" "$_WORK" \
  --source-root "$FIXTURE_SRC/07_screens" \
  --project-root "$FIXTURE_SRC" \
  --cwd "$(pwd)" || _rc=$?
if [[ $_rc -eq 0 ]]; then echo "   UNEXPECTED PASS"; exit 1; fi
if [[ $_rc -ne 2 ]]; then echo "   UNEXPECTED EXIT CODE $_rc (expected 2)"; exit 1; fi
echo "   FAIL as expected (exit 2)"
rm -rf "$_WORK"
_WORK=""

echo ""
echo "5. Empty stylesheet — FAIL expected..."
_WORK=$(mktemp -d)
cp -r "$SITE_DIR/." "$_WORK/"
> "$_WORK/_astro/style.css"
_rc=0
python3 "$SKILL_DIR/validator.py" "$_WORK" \
  --source-root "$FIXTURE_SRC/07_screens" \
  --project-root "$FIXTURE_SRC" \
  --cwd "$(pwd)" || _rc=$?
if [[ $_rc -eq 0 ]]; then echo "   UNEXPECTED PASS"; exit 1; fi
if [[ $_rc -ne 2 ]]; then echo "   UNEXPECTED EXIT CODE $_rc (expected 2)"; exit 1; fi
echo "   FAIL as expected (exit 2)"
rm -rf "$_WORK"
_WORK=""

# expect_fail <label> <python statements over `site` (pathlib.Path) and `manifest` (dict)>
# Mutates a copy of the snapshot, writes the manifest back, and requires exit 2.
expect_fail() {
  local label="$1" snippet="$2" rc=0
  _WORK=$(mktemp -d)
  cp -r "$SITE_DIR/." "$_WORK/"
  python3 - "$_WORK" "$snippet" <<'PY'
import json, pathlib, sys
site = pathlib.Path(sys.argv[1])
mpath = site / "manifest.json"
manifest = json.loads(mpath.read_text())
exec(sys.argv[2])
mpath.write_text(json.dumps(manifest, indent=2))
PY
  python3 "$SKILL_DIR/validator.py" "$_WORK" \
    --source-root "$FIXTURE_SRC/07_screens" \
    --project-root "$FIXTURE_SRC" \
    --rulebook "$RULEBOOK" \
    --cwd "$(pwd)" >/dev/null 2>&1 || rc=$?
  if [[ $rc -eq 0 ]]; then echo "   UNEXPECTED PASS: $label"; exit 1; fi
  if [[ $rc -ne 2 ]]; then echo "   UNEXPECTED EXIT CODE $rc (expected 2): $label"; exit 1; fi
  echo "   FAIL as expected (exit 2): $label"
  rm -rf "$_WORK"
  _WORK=""
}

echo ""
echo "6. Floorplan checks — FAIL expected for each..."
expect_fail "unknown floorplan id" \
  'manifest["screens"][0]["floorplan"] = "no-such-plan"'
expect_fail "region key not in the floorplan" \
  'manifest["screens"][0]["regions"]["not-a-region"] = {"shows": "user", "representation": "row"}'
expect_fail "element region not in the floorplan" \
  'manifest["screens"][0]["elements"][0]["region"] = "not-a-region"'
expect_fail "shell frame used as a screen floorplan" \
  'manifest["screens"][0]["floorplan"] = "shell-sidebar"'
expect_fail "posture outside the enum" \
  'manifest["screens"][0]["posture"] = "frozen"'
expect_fail "density outside the enum" \
  'manifest["screens"][0]["density"] = "tight"'
expect_fail "no floorplan declared" \
  'manifest["screens"][0].pop("floorplan")'
expect_fail "frame file missing" \
  '(site / "floorplan" / "login.html").unlink()'
expect_fail "narrow iframe missing" \
  'p = site / "screen" / "login.html"; p.write_text(p.read_text().replace("width=\"390\"", "width=\"1040\""))'
expect_fail "frame carries a script" \
  'p = site / "floorplan" / "login.html"; p.write_text(p.read_text().replace("</body>", "<script>1</script></body>"))'
expect_fail "nested (non-flat) screen id" \
  'manifest["screens"][0]["screen_id"] = "00_auth/login"'

echo ""
echo "=== All tests passed ==="
