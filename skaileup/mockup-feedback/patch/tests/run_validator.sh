#!/usr/bin/env bash
# run_validator.sh — structural validation for patch skill output.
#
# IMPORTANT: This script does NOT run the LLM. It validates a patches output
# that a human or agent has already produced. Run it AFTER the patch skill
# has generated patches/<sid>.json and patches/<sid>.review.md.
#
# Usage (from mockup-feedback/patch/):
#   bash tests/run_validator.sh <patches-json> <review-md> <triage-json> [<session-json>]
#
# For CI / batch mode, the agent should:
#   1. Run the patch SKILL.md against each fixture triage JSON.
#   2. Call this script on the output.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$#" -lt 3 ]; then
    echo "Usage: bash run_validator.sh <patches-json> <review-md> <triage-json> [<session-json>]"
    exit 1
fi

PATCHES="$1"
REVIEW="$2"
TRIAGE="$3"
SESSION="${4:-}"

echo "--- Structural validation: $(basename "$PATCHES") ---"
if [ -n "$SESSION" ]; then
    python3 "$SKILL_DIR/validator.py" "$TRIAGE" "$PATCHES" "$REVIEW" "$SESSION"
else
    python3 "$SKILL_DIR/validator.py" "$TRIAGE" "$PATCHES" "$REVIEW"
fi

echo "Patch validation passed."
