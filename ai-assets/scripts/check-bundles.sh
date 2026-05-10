#!/usr/bin/env bash
# check-bundles.sh — CI guard: fail if bundles are out of sync with flows/
#
# Flows and bundles are co-located under skaileup/flows/<app-type>/:
#   skaileup/flows/mvp/mvp.flow.yaml + mvp.bundle.yaml
#   skaileup/flows/simple-app/simple-app.flow.yaml + simple-app.bundle.yaml
#   etc.
#
# Usage (from repo root):
#   bash ai-assets/scripts/check-bundles.sh
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
trap 'git restore skaileup/flows/ 2>/dev/null || true' EXIT

echo "=== check-bundles: running compile_bundle.py ==="
python3 ai-assets/lab/compile-bundle/compile_bundle.py

echo "=== check-bundles: checking for drift ==="
if ! git diff --exit-code skaileup/flows/ > /dev/null; then
    echo ""
    echo "ERROR: bundle drift detected — the following bundles are out of sync with skaileup/flows/:"
    git diff --stat skaileup/flows/
    echo ""
    echo "Fix: run 'python3 ai-assets/lab/compile-bundle/compile_bundle.py' and commit the result."
    exit 1
fi

echo "=== check-bundles: running validator.py ==="
if ! python3 ai-assets/lab/compile-bundle/validator.py; then
    echo ""
    echo "ERROR: bundle validator found coverage gaps. Run 'python3 ai-assets/lab/compile-bundle/validator.py' locally for details."
    exit 1
fi

echo ""
echo "OK: all bundles are up to date and fully cover their flows."
