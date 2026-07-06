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

echo "=== mockup-walkthrough-astro validator tests ==="

# Bootstrap rendered/ from expected/ — proves snapshot-to-snapshot consistency.
rm -rf "$SITE_DIR"
mkdir -p "$SITE_DIR"
cp -r expected/minimal/. "$SITE_DIR/"

echo ""
echo "1. Structural + fixture-mode pass (rendered/minimal)..."
python3 "$SKILL_DIR/validator.py" "$SITE_DIR" \
  --fixture minimal \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" \
  --cwd "$(pwd)"
echo "   PASS"

echo ""
echo "2. dist/ check — FAIL expected..."
_WORK=$(mktemp -d)
cp -r "$SITE_DIR/." "$_WORK/"
mkdir "$_WORK/dist"
_rc=0
python3 "$SKILL_DIR/validator.py" "$_WORK" \
  --source-root "$FIXTURE_SRC/experience/screens" \
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
  --source-root "$FIXTURE_SRC/experience/screens" \
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
  --source-root "$FIXTURE_SRC/experience/screens" \
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
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" \
  --cwd "$(pwd)" || _rc=$?
if [[ $_rc -eq 0 ]]; then echo "   UNEXPECTED PASS"; exit 1; fi
if [[ $_rc -ne 2 ]]; then echo "   UNEXPECTED EXIT CODE $_rc (expected 2)"; exit 1; fi
echo "   FAIL as expected (exit 2)"
rm -rf "$_WORK"
_WORK=""

echo ""
echo "=== All tests passed ==="
