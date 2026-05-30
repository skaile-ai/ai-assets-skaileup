#!/usr/bin/env bash
# check-bundles.sh — CI guard: fail if bundles are out of sync with flows/
#
# Flows and bundles are co-located under skaileup/flows/<app-type>/:
#   skaileup/flows/mvp/mvp.flow.yaml + mvp.bundle.yaml
#   skaileup/flows/simple-app/simple-app.flow.yaml + simple-app.bundle.yaml
#   etc.
#
# Usage (from repo root):
#   bash ai-assets-dev/scripts/check-bundles.sh
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

# Guard: this script regenerates bundles and then `git restore`s them, so it must
# only run on a clean flows/ tree — otherwise the restore below would silently
# discard uncommitted work-in-progress (e.g. flow or deferred_skills.yaml edits)
# and the drift check would false-positive on those same edits.
if ! git diff --quiet -- skaileup/flows/ || \
   [ -n "$(git ls-files --others --exclude-standard -- skaileup/flows/)" ]; then
    echo "ERROR: skaileup/flows/ has uncommitted changes."
    echo "       check-bundles.sh regenerates and then restores skaileup/flows/,"
    echo "       which would discard your work. Commit or stash first, then re-run."
    echo ""
    git status --short -- skaileup/flows/
    exit 1
fi

# Only restore the bundle files the compile step regenerates — never blow away
# the whole flows/ tree.
trap 'git restore skaileup/flows/*/*.bundle.yaml 2>/dev/null || true; rm -rf /tmp/skaile-check-venv' EXIT

# Use a throw-away venv so pyyaml/jsonschema are available regardless of the
# system Python environment (avoids the PEP 668 externally-managed-environment
# error on macOS Homebrew Python and similar setups).
VENV=/tmp/skaile-check-venv
if [ ! -x "$VENV/bin/python3" ]; then
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install --quiet pyyaml jsonschema
fi
PY="$VENV/bin/python3"

echo "=== check-bundles: running compile_bundle.py ==="
"$PY" ai-assets-dev/lab/compile-bundle/compile_bundle.py

echo "=== check-bundles: checking for drift ==="
if ! git diff --exit-code skaileup/flows/*/*.bundle.yaml > /dev/null; then
    echo ""
    echo "ERROR: bundle drift detected — the following bundles are out of sync with skaileup/flows/:"
    git diff --stat skaileup/flows/*/*.bundle.yaml
    echo ""
    echo "Fix: run 'python3 ai-assets-dev/lab/compile-bundle/compile_bundle.py' and commit the result."
    exit 1
fi

echo "=== check-bundles: running validator.py ==="
if ! "$PY" ai-assets-dev/lab/compile-bundle/validator.py; then
    echo ""
    echo "ERROR: bundle validator found coverage gaps. Run 'python3 ai-assets-dev/lab/compile-bundle/validator.py' locally for details."
    exit 1
fi

echo ""
echo "OK: all bundles are up to date and fully cover their flows."
