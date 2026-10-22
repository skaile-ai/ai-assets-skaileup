#!/usr/bin/env python3
"""validator.py — structural validator for triage output.

Usage:
  python validate_triage.py <triage-json> [<inbox-dir>]

Checks:
  - Every open note of the inbox appears in exactly one of groups or unresolved.
  - No inboxId appears in both groups and unresolved, or twice across groups.
  - All group file paths are non-empty strings; `entity` is set exactly when the
    file is the data model.
  - unresolved entries have inboxId + reason.

Exit codes: 0 PASS, 2 FAIL, 1 internal error.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MODEL_FILE = "10_blueprint/datamodel/model.ts"


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


def open_item_ids(inbox: Path) -> set[str]:
    ids: set[str] = set()
    for path in sorted((inbox / "items").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("status", "open") == "open":
            ids.add(data.get("inboxId", path.stem))
    return ids


def validate(triage: dict, inbox_ids: set[str] | None, r: Report) -> None:
    groups = triage.get("groups", [])
    unresolved = triage.get("unresolved", [])

    grouped_ids: set[str] = set()
    for g in groups:
        if not g.get("file"):
            r.add("group has empty or missing 'file'")
        if (g.get("file") == MODEL_FILE) != bool(g.get("entity")):
            r.add(f"group {g.get('file')!r}: 'entity' must be set exactly for {MODEL_FILE}")
        if not g.get("items"):
            r.add(f"group {g.get('file')!r} has no items")
        for nid in g.get("items", []):
            if nid in grouped_ids:
                r.add(f"note {nid!r} appears in multiple groups")
            grouped_ids.add(nid)

    unresolved_ids: set[str] = set()
    for u in unresolved:
        nid = u.get("inboxId")
        if not nid:
            r.add("unresolved entry missing 'inboxId'")
        if not u.get("reason"):
            r.add(f"unresolved entry {nid!r} missing 'reason'")
        if nid in unresolved_ids:
            r.add(f"note {nid!r} appears in unresolved more than once")
        unresolved_ids.add(nid)

    overlap = grouped_ids & unresolved_ids
    if overlap:
        r.add(f"note(s) appear in both groups and unresolved: {overlap}")

    if inbox_ids is not None:
        all_output = grouped_ids | unresolved_ids
        missing = inbox_ids - all_output
        extra = all_output - inbox_ids
        if missing:
            r.add(f"open notes in the inbox but missing from triage output: {missing}")
        if extra:
            r.add(f"note ids in triage output but not open in the inbox: {extra}")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python validate_triage.py <triage-json> [<inbox-dir>]", file=sys.stderr)
        return 1

    try:
        triage = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        inbox_ids = open_item_ids(Path(sys.argv[2])) if len(sys.argv) >= 3 else None
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    r = Report()
    validate(triage, inbox_ids, r)

    if r.ok():
        print(f"PASS  {sys.argv[1]}")
        return 0
    r.dump()
    return 2


if __name__ == "__main__":
    sys.exit(main())
