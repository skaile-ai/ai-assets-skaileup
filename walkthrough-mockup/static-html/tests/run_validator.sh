#!/usr/bin/env bash
# walkthrough-mockup-static-html — fixture validator harness.
#
# Bootstrap mode: copies the hand-curated expected snapshot to
#   tests/rendered/minimal/  (proves the validator is internally
#   consistent before the renderer is wired up)
# then runs the validator in fixture mode against it.
#
# When the renderer ships, replace the cp step with the actual
# render-then-validate invocation.
set -euo pipefail

cd "$(dirname "$0")"

# Bootstrap rendered/ from expected/ — proves snapshot-to-snapshot consistency.
rm -rf rendered/minimal
mkdir -p rendered/minimal
cp -r expected/minimal/. rendered/minimal/

# Fixture mode: structural checks + snapshot diff.
python3 ../validator.py rendered/minimal \
  --fixture minimal \
  --source-root fixtures/minimal/experience/screens \
  --cwd "$(pwd)"
