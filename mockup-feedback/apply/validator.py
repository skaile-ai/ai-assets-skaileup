#!/usr/bin/env python3
"""validator.py — structural validator for apply output (applied/<sid>.json).

Usage:
  python validator.py <applied-json> <patches-json> <review-md>

Checks:
  1. Every checked patch ID in review.md has an item in applied JSON.
  2. No applied item references a patch ID not in patches JSON.
  3. Item status is 'applied' or 'failed'; failed items have 'error'.
  4. sessionId matches between applied JSON and patches JSON.

Exit codes: 0 PASS, 2 FAIL, 1 internal error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: python validator.py <applied-json> <patches-json> <review-md>", file=sys.stderr)
        return 1

    try:
        applied_data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        patches_data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        review_md    = Path(sys.argv[3]).read_text(encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    violations: list[str] = []

    # session IDs match
    if applied_data.get("sessionId") != patches_data.get("sessionId"):
        violations.append(
            f"sessionId mismatch: applied={applied_data.get('sessionId')!r} "
            f"patches={patches_data.get('sessionId')!r}"
        )

    patches_by_id = {p["id"]: p for p in patches_data.get("patches", [])}
    checked_ids = set(re.findall(r"- \[x\] \*\*([^*]+)\*\*", review_md))
    applied_by_pid = {item["patchId"]: item for item in applied_data.get("items", [])}

    # Every checked patch ID has an applied item
    for pid in checked_ids:
        if pid not in applied_by_pid:
            violations.append(f"checked patch {pid!r} has no corresponding item in applied JSON")

    # No applied item references unknown patch ID; every item must have patchId
    for item in applied_data.get("items", []):
        pid = item.get("patchId")
        if not pid:
            violations.append(f"item missing or empty 'patchId' field: {item!r}")
            continue
        if pid not in patches_by_id:
            violations.append(f"applied item references unknown patchId {pid!r}")

    # Status validity
    for item in applied_data.get("items", []):
        status = item.get("status")
        if status not in ("applied", "failed"):
            violations.append(f"item {item.get('patchId')!r} has invalid status {status!r}")
        if status == "failed" and not item.get("error"):
            violations.append(f"failed item {item.get('patchId')!r} missing 'error' field")

    if violations:
        for v in violations:
            print("FAIL", v)
        return 2

    print(f"PASS  {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
