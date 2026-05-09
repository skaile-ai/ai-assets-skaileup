#!/usr/bin/env bash
set -euo pipefail
_WORK=""
_cleanup() { [[ -n "$_WORK" ]] && rm -rf "$_WORK"; true; }
trap _cleanup EXIT

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SKILL_DIR="$REPO_ROOT/walkthrough-mockup/astro"
SITE_DIR="$SKILL_DIR/tests/expected/minimal"
FIXTURE_SRC="$SKILL_DIR/tests/fixtures/minimal"

echo "=== walkthrough-mockup-astro validator tests ==="

echo ""
echo "1. Structural pass (expected/minimal site-root mode)..."
python "$SKILL_DIR/validator.py" "$SITE_DIR" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC"
echo "   PASS"

echo ""
echo "2. dist/ check — FAIL expected..."
_WORK=$(mktemp -d)
cp -r "$SITE_DIR/." "$_WORK/"
mkdir "$_WORK/dist"
_rc=0
python "$SKILL_DIR/validator.py" "$_WORK" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" || _rc=$?
if [[ $_rc -eq 0 ]]; then echo "   UNEXPECTED PASS"; exit 1; fi
if [[ $_rc -eq 1 ]]; then echo "   INTERNAL ERROR (exit 1 — not a validation failure)"; exit 1; fi
echo "   FAIL as expected (exit $_rc)"
rm -rf "$_WORK"
_WORK=""

echo ""
echo "3. Wrong renderer name — FAIL expected..."
_WORK=$(mktemp -d)
cp -r "$SITE_DIR/." "$_WORK/"
python -c "
import json, pathlib
p = pathlib.Path('$_WORK/manifest.json')
m = json.loads(p.read_text())
m['renderer'] = 'wrong-renderer'
p.write_text(json.dumps(m, indent=2))
"
_rc=0
python "$SKILL_DIR/validator.py" "$_WORK" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" || _rc=$?
if [[ $_rc -eq 0 ]]; then echo "   UNEXPECTED PASS"; exit 1; fi
if [[ $_rc -eq 1 ]]; then echo "   INTERNAL ERROR (exit 1 — not a validation failure)"; exit 1; fi
echo "   FAIL as expected (exit $_rc)"
rm -rf "$_WORK"
_WORK=""

echo ""
echo "4. Missing stylesheet — FAIL expected..."
_WORK=$(mktemp -d)
cp -r "$SITE_DIR/." "$_WORK/"
python -c "
import pathlib
p = pathlib.Path('$_WORK/index.html')
text = p.read_text().replace('<link rel=\"stylesheet\" href=\"/_astro/style.css\">', '')
p.write_text(text)
"
_rc=0
python "$SKILL_DIR/validator.py" "$_WORK" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" || _rc=$?
if [[ $_rc -eq 0 ]]; then echo "   UNEXPECTED PASS"; exit 1; fi
if [[ $_rc -eq 1 ]]; then echo "   INTERNAL ERROR (exit 1 — not a validation failure)"; exit 1; fi
echo "   FAIL as expected (exit $_rc)"
rm -rf "$_WORK"
_WORK=""

echo ""
echo "5. Empty stylesheet — FAIL expected..."
_WORK=$(mktemp -d)
cp -r "$SITE_DIR/." "$_WORK/"
> "$_WORK/_astro/style.css"
_rc=0
python "$SKILL_DIR/validator.py" "$_WORK" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" || _rc=$?
if [[ $_rc -eq 0 ]]; then echo "   UNEXPECTED PASS"; exit 1; fi
if [[ $_rc -eq 1 ]]; then echo "   INTERNAL ERROR (exit 1 — not a validation failure)"; exit 1; fi
echo "   FAIL as expected (exit $_rc)"
rm -rf "$_WORK"
_WORK=""

echo ""
echo "6. Fixture-mode snapshot diff (expected/minimal)..."
python "$SKILL_DIR/validator.py" "$SITE_DIR" \
  --fixture minimal \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC"
echo "   PASS"

echo ""
echo "=== All tests passed ==="
