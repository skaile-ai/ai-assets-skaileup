#!/usr/bin/env bash
# check-bundles.sh — CI guard: fail if bundles/ is out of sync with flows/
#
# Usage (from repo root):
#   bash scripts/check-bundles.sh
#
# Exit codes:
#   0  All bundles up to date — nothing would change
#   1  Bundle drift detected, or internal error
#
# In CI: add this as a check step. The script restores any changes it
# makes before exiting, so it is safe to run on a clean working tree.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "=== check-bundles: running compile_bundle.py ==="
python lab/compile-bundle/compile_bundle.py

echo "=== check-bundles: checking for drift ==="
if ! git diff --exit-code bundles/ > /dev/null; then
    echo ""
    echo "ERROR: bundle drift detected — the following bundles are out of sync with flows/:"
    git diff --stat bundles/
    echo ""
    echo "Fix: run 'python lab/compile-bundle/compile_bundle.py' and commit the result."
    git restore bundles/
    exit 1
fi

echo "=== check-bundles: running validator.py ==="
python lab/compile-bundle/validator.py

echo ""
echo "OK: all bundles are up to date and fully cover their flows."
