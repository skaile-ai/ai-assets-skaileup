#!/usr/bin/env bash
set -euo pipefail
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
TMPDIR=$(mktemp -d)
cp -r "$SITE_DIR/." "$TMPDIR/"
mkdir "$TMPDIR/dist"
python "$SKILL_DIR/validator.py" "$TMPDIR" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" && echo "   UNEXPECTED PASS" && exit 1 || echo "   FAIL as expected (exit $?)"
rm -rf "$TMPDIR"

echo ""
echo "3. Wrong renderer name — FAIL expected..."
TMPDIR=$(mktemp -d)
cp -r "$SITE_DIR/." "$TMPDIR/"
python -c "
import json, pathlib
p = pathlib.Path('$TMPDIR/manifest.json')
m = json.loads(p.read_text())
m['renderer'] = 'wrong-renderer'
p.write_text(json.dumps(m, indent=2))
"
python "$SKILL_DIR/validator.py" "$TMPDIR" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" && echo "   UNEXPECTED PASS" && exit 1 || echo "   FAIL as expected (exit $?)"
rm -rf "$TMPDIR"

echo ""
echo "4. Missing stylesheet — FAIL expected..."
TMPDIR=$(mktemp -d)
cp -r "$SITE_DIR/." "$TMPDIR/"
python -c "
import pathlib
p = pathlib.Path('$TMPDIR/index.html')
text = p.read_text().replace('<link rel=\"stylesheet\" href=\"/_astro/style.css\">', '')
p.write_text(text)
"
python "$SKILL_DIR/validator.py" "$TMPDIR" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" && echo "   UNEXPECTED PASS" && exit 1 || echo "   FAIL as expected (exit $?)"
rm -rf "$TMPDIR"

echo ""
echo "5. Empty stylesheet — FAIL expected..."
TMPDIR=$(mktemp -d)
cp -r "$SITE_DIR/." "$TMPDIR/"
> "$TMPDIR/_astro/style.css"
python "$SKILL_DIR/validator.py" "$TMPDIR" \
  --cwd "$REPO_ROOT" \
  --source-root "$FIXTURE_SRC/experience/screens" \
  --project-root "$FIXTURE_SRC" && echo "   UNEXPECTED PASS" && exit 1 || echo "   FAIL as expected (exit $?)"
rm -rf "$TMPDIR"

echo ""
echo "=== All tests passed ==="
