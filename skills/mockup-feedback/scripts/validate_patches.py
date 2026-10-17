#!/usr/bin/env python3
"""validator.py — structural validator for patch skill output.

Usage:
  python validator.py <triage-json> <patches-json> <review-md> [<session-json>]

Checks (design spec §Test strategy):
  1. Partition invariant: every annotation in triage groups appears in exactly
     one of patches[] (one or more entries) OR needs_manual[] (one entry).
  2. Every patch's file matches its annotation's resolved file (from triage).
  3. Every patch diff starts with a valid @@ anchor header.
  4. For each annotation with provisional=true (from session) that has patches,
     exactly one kind=provisional-promotion patch exists.
  5. Every patches[] entry has a - [x] checklist item in review.md.
  6. Every needs_manual[] entry has a bullet under ## Needs manual review in
     review.md and NO checklist item.
  7. add/remove/question diffs match deterministic template patterns.

Exit codes: 0 PASS, 2 FAIL, 1 internal error.
"""
from __future__ import annotations

import json
import re
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


def parse_checklist(review_md: str) -> tuple[set[str], set[str]]:
    """Returns (checked_ids, unchecked_ids) from review.md."""
    checked = set(re.findall(r"- \[x\] \*\*([^*]+)\*\*", review_md))
    unchecked = set(re.findall(r"- \[ \] \*\*([^*]+)\*\*", review_md))
    return checked, unchecked


def parse_needs_manual_bullets(review_md: str) -> set[str]:
    """Returns annotation IDs listed under ## Needs manual review."""
    section = re.search(
        r"## Needs manual review\s*(.*?)(?=^##|\Z)", review_md, re.DOTALL | re.MULTILINE
    )
    if not section:
        return set()
    return set(re.findall(r"annotation `([^`]+)`", section.group(1)))


def validate(
    triage: dict,
    patches_data: dict,
    review_md: str,
    session: dict | None,
    r: Report,
) -> None:
    # Build lookup maps
    patches_by_ann: dict[str, list[dict]] = {}
    patches_by_id:  dict[str, dict] = {}
    for p in patches_data.get("patches", []):
        patches_by_ann.setdefault(p["annotationId"], []).append(p)
        patches_by_id[p["id"]] = p

    nm_ann_ids = {nm["annotationId"] for nm in patches_data.get("needs_manual", [])}

    # Build annotation → resolved file map from triage
    ann_to_file: dict[str, str] = {}
    for grp in triage.get("groups", []):
        for aid in grp.get("annotations", []):
            ann_to_file[aid] = grp["file"]

    # 1. Partition invariant
    all_group_ann_ids = set(ann_to_file.keys())
    for aid in all_group_ann_ids:
        in_patches = aid in patches_by_ann
        in_nm = aid in nm_ann_ids
        if in_patches and in_nm:
            r.add(f"annotation {aid!r} appears in both patches[] and needs_manual[]")
        elif not in_patches and not in_nm:
            r.add(f"annotation {aid!r} not in patches[] or needs_manual[] (partition invariant)")

    # 2. Every patch file matches triage-resolved file
    for p in patches_data.get("patches", []):
        expected_file = ann_to_file.get(p["annotationId"])
        if expected_file and p.get("file") != expected_file:
            r.add(
                f"patch {p['id']!r}: file={p['file']!r} but triage resolved "
                f"{p['annotationId']!r} to {expected_file!r}"
            )

    # 3. Diff @@ anchor header present
    for p in patches_data.get("patches", []):
        diff = p.get("diff", "")
        first_line = diff.split("\n")[0] if diff else ""
        if not re.match(r"^@@ (?:## \S|##\S|frontmatter:\S)", first_line.strip()):
            r.add(f"patch {p['id']!r}: diff missing valid @@ anchor header")

    # 4. Provisional-promotion patch present for provisional annotations
    if session:
        ann_by_id = {a["id"]: a for a in session.get("annotations", [])}
        for aid, file_path in ann_to_file.items():
            ann = ann_by_id.get(aid)
            if not ann:
                continue
            if ann.get("specRef", {}).get("provisional") and aid in patches_by_ann:
                promo_patches = [
                    p for p in patches_by_ann[aid]
                    if p.get("kind") == "provisional-promotion"
                ]
                if not promo_patches:
                    r.add(
                        f"annotation {aid!r} has provisional=true and patches, "
                        "but no kind=provisional-promotion patch"
                    )

    # 5. Every patches[] entry has a - [x] checklist item in review.md
    checked_ids, unchecked_ids = parse_checklist(review_md)
    for p in patches_data.get("patches", []):
        if p["id"] not in checked_ids:
            r.add(f"patch {p['id']!r} is in patches[] but has no - [x] item in review.md")

    # 6. Every needs_manual[] entry is in review.md preamble, not in checklist
    nm_in_review = parse_needs_manual_bullets(review_md)
    all_checklist_ids = checked_ids | unchecked_ids
    for nm in patches_data.get("needs_manual", []):
        aid = nm["annotationId"]
        if aid not in nm_in_review:
            r.add(
                f"needs_manual annotation {aid!r} is not listed under "
                "## Needs manual review in review.md"
            )
        if aid in all_checklist_ids:
            r.add(
                f"needs_manual annotation {aid!r} has a checklist item in review.md "
                "(should have only a ## Needs manual review bullet)"
            )
        if any(p["id"] for p in patches_data.get("patches", []) if p["annotationId"] == aid):
            r.add(f"needs_manual annotation {aid!r} also has patches[] entries (partition violation)")

    # 7. Template pattern checks for add/remove/question patches
    for p in patches_data.get("patches", []):
        cat = p.get("category")
        diff = p.get("diff", "")
        if cat == "add":
            if not re.search(r"^\+", diff, re.MULTILINE):
                r.add(f"patch {p['id']!r}: category=add diff has no + lines")
        elif cat == "remove":
            if not re.search(r"^-", diff, re.MULTILINE):
                r.add(f"patch {p['id']!r}: category=remove diff has no - lines")
        elif cat == "question":
            if "Open Questions" not in diff:
                r.add(
                    f"patch {p['id']!r}: category=question diff should target "
                    "## Open Questions section"
                )


def main() -> int:
    if len(sys.argv) < 4:
        print(
            "Usage: python validator.py <triage-json> <patches-json> <review-md> [<session-json>]",
            file=sys.stderr,
        )
        return 1

    try:
        triage      = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        patches_data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        review_md   = Path(sys.argv[3]).read_text(encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    session = None
    if len(sys.argv) >= 5:
        try:
            session = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    r = Report()
    validate(triage, patches_data, review_md, session, r)

    if r.ok():
        print(f"PASS  {sys.argv[2]}")
        return 0
    r.dump()
    return 2


if __name__ == "__main__":
    sys.exit(main())
