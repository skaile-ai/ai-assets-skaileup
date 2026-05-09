#!/usr/bin/env python3
"""validator.py — structural validator for triage output.

Usage:
  python validator.py <triage-json> [<session-json>]

Checks:
  - Every annotation in the session appears in exactly one of groups or unresolved.
  - No annotation ID appears in both groups and unresolved.
  - No annotation ID appears more than once across groups.
  - All group file paths are non-empty strings.
  - unresolved entries have annotationId + reason.

Exit codes: 0 PASS, 2 FAIL, 1 internal error.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


class Report:
    def __init__(self) -> None:
        self.violations: list[str] = []

    def add(self, msg: str) -> None:
        self.violations.append(msg)

    def ok(self) -> bool:
        return not self.violations

    def dump(self) -> None:
        for v in self.violations:
            print("FAIL", v)


def validate(triage: dict, session: dict | None, r: Report) -> None:
    groups = triage.get("groups", [])
    unresolved = triage.get("unresolved", [])

    grouped_ids: set[str] = set()
    for g in groups:
        if not g.get("file"):
            r.add("group has empty or missing 'file'")
        for aid in g.get("annotations", []):
            if aid in grouped_ids:
                r.add(f"annotation {aid!r} appears in multiple groups")
            grouped_ids.add(aid)

    unresolved_ids: set[str] = set()
    for u in unresolved:
        aid = u.get("annotationId")
        if not aid:
            r.add("unresolved entry missing 'annotationId'")
        if not u.get("reason"):
            r.add(f"unresolved entry {aid!r} missing 'reason'")
        if aid in unresolved_ids:
            r.add(f"annotation {aid!r} appears in unresolved more than once")
        unresolved_ids.add(aid)

    overlap = grouped_ids & unresolved_ids
    if overlap:
        r.add(f"annotation(s) appear in both groups and unresolved: {overlap}")

    if session:
        session_ids = {a.get("id") for a in session.get("annotations", [])}
        all_output = grouped_ids | unresolved_ids
        missing = session_ids - all_output
        extra = all_output - session_ids
        if missing:
            r.add(f"annotations in session but missing from triage output: {missing}")
        if extra:
            r.add(f"annotation IDs in triage output but not in session: {extra}")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python validator.py <triage-json> [<session-json>]", file=sys.stderr)
        return 1

    try:
        triage = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    session = None
    if len(sys.argv) >= 3:
        try:
            session = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    r = Report()
    validate(triage, session, r)

    if r.ok():
        print(f"PASS  {sys.argv[1]}")
        return 0
    r.dump()
    return 2


if __name__ == "__main__":
    sys.exit(main())
