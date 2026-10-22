#!/usr/bin/env python3
"""validator.py — structural validator for patch skill output.

Usage:
  python validate_patches.py <triage-json> <patches-json> <review-md>

Checks:
  1. Partition invariant: every note in the triage groups is answered by at
     least one patch (as its inboxId or in resolves[]) OR sits in needs_manual[]
     once, never both.
  2. A content / create-section patch edits the file its note was triaged to; a
     model-proposal patch edits the data model; a glossary-proposal patch any file.
  3. Every diff starts with a valid @@ anchor header, and the anchor family fits
     the patch kind (ts: for model-proposal only).
  4. Every patch carries resolves[]: its own inboxId, status implemented|rejected,
     a non-empty resolution; one note carries one resolution across patches.
  5. Every patches[] entry has a - [x] checklist item in review.md.
  6. Every needs_manual[] entry has a bullet under ## Needs manual review in
     review.md.
  7. add/remove/question diffs match their templates; model-proposal lines carry
     the proposal marker with `source` naming a resolved note; glossary-proposal
     diffs carry the four marker lines.

Exit codes: 0 PASS, 2 FAIL, 1 internal error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MODEL_FILE = "10_blueprint/datamodel/model.ts"
KINDS = {"content", "create-section", "model-proposal", "glossary-proposal"}
ANCHOR = re.compile(
    r"^@@ (?:#{2,6} \S.*|frontmatter:\S+|before:#{1,6} \S.*|ts:entity/\w+/fields|ts:model/entities) @@$"
)


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
    """Returns note ids listed under ## Needs manual review."""
    section = re.search(
        r"## Needs manual review\s*(.*?)(?=^##|\Z)", review_md, re.DOTALL | re.MULTILINE
    )
    if not section:
        return set()
    return set(re.findall(r"note `([^`]+)`", section.group(1)))


def answered_ids(patch: dict) -> set[str]:
    ids = {e.get("id") for e in patch.get("resolves", []) if isinstance(e, dict)}
    ids.add(patch.get("inboxId"))
    return ids


def validate(triage: dict, patches_data: dict, review_md: str, r: Report) -> None:
    patches = patches_data.get("patches", [])
    nm_ids = {nm["inboxId"] for nm in patches_data.get("needs_manual", [])}

    note_to_file: dict[str, str] = {}
    for grp in triage.get("groups", []):
        for nid in grp.get("items", []):
            note_to_file[nid] = grp["file"]

    answered: set[str] = set()
    for p in patches:
        answered |= answered_ids(p)

    # 1. Partition invariant
    for nid in note_to_file:
        in_patches = nid in answered
        in_nm = nid in nm_ids
        if in_patches and in_nm:
            r.add(f"note {nid!r} appears in both patches[] and needs_manual[]")
        elif not in_patches and not in_nm:
            r.add(f"note {nid!r} not in patches[] or needs_manual[] (partition invariant)")

    # 2. Patch file fits its kind
    for p in patches:
        kind = p.get("kind")
        if kind not in KINDS:
            r.add(f"patch {p['id']!r}: kind {kind!r} is not one of {sorted(KINDS)}")
            continue
        if kind in ("content", "create-section"):
            expected = note_to_file.get(p.get("inboxId"))
            if expected and p.get("file") != expected:
                r.add(
                    f"patch {p['id']!r}: file={p['file']!r} but triage resolved "
                    f"{p['inboxId']!r} to {expected!r}"
                )
        elif kind == "model-proposal" and p.get("file") != MODEL_FILE:
            r.add(f"patch {p['id']!r}: model-proposal must edit {MODEL_FILE}, not {p.get('file')!r}")

    # 3. Anchor header present and fitting the kind
    for p in patches:
        diff = p.get("diff", "")
        first_line = (diff.split("\n")[0] if diff else "").strip()
        if not ANCHOR.match(first_line):
            r.add(f"patch {p['id']!r}: diff missing valid @@ anchor header")
            continue
        is_ts = first_line.startswith("@@ ts:")
        if (p.get("kind") == "model-proposal") != is_ts:
            r.add(f"patch {p['id']!r}: ts: anchors belong to model-proposal patches only")

    # 4. resolves[]
    resolution_of: dict[str, tuple[str, str]] = {}
    for p in patches:
        resolves = p.get("resolves")
        if not isinstance(resolves, list) or not resolves:
            r.add(f"patch {p['id']!r}: missing resolves[]")
            continue
        if p.get("inboxId") not in {e.get("id") for e in resolves}:
            r.add(f"patch {p['id']!r}: resolves[] does not list its own inboxId")
        for e in resolves:
            if e.get("status") not in ("implemented", "rejected"):
                r.add(f"patch {p['id']!r}: resolves[{e.get('id')!r}].status must be implemented or rejected")
            if not str(e.get("resolution", "")).strip():
                r.add(f"patch {p['id']!r}: resolves[{e.get('id')!r}].resolution must be non-empty")
            pair = (e.get("status", ""), e.get("resolution", ""))
            if resolution_of.setdefault(e.get("id"), pair) != pair:
                r.add(f"note {e.get('id')!r} carries different resolutions across patches")

    # 5. Every patches[] entry has a - [x] checklist item in review.md
    checked_ids, unchecked_ids = parse_checklist(review_md)
    for p in patches:
        if p["id"] not in checked_ids:
            r.add(f"patch {p['id']!r} is in patches[] but has no - [x] item in review.md")

    # 6. Every needs_manual[] entry is in the review.md preamble, not in the checklist
    nm_in_review = parse_needs_manual_bullets(review_md)
    for nm in patches_data.get("needs_manual", []):
        nid = nm["inboxId"]
        if nid not in nm_in_review:
            r.add(f"needs_manual note {nid!r} is not listed under ## Needs manual review in review.md")

    # 7. Template checks
    for p in patches:
        diff = p.get("diff", "")
        kind, cat = p.get("kind"), p.get("category")
        if kind == "model-proposal":
            sources = {e.get("id") for e in p.get("resolves", []) if isinstance(e, dict)}
            added = [l[1:] for l in diff.splitlines()[1:] if l.startswith("+")]
            if not added:
                r.add(f"patch {p['id']!r}: model-proposal diff has no + lines")
            if re.search(r"^-", diff, re.MULTILINE):
                r.add(f"patch {p['id']!r}: model-proposal diff must not remove lines")
            marked = [l for l in added if "proposed: {" in l]
            if not marked:
                r.add(f"patch {p['id']!r}: no added line carries `proposed: {{ by, on, source }}`")
            for l in marked:
                m = re.search(r"proposed: \{ by: 'mockup-feedback', on: '\d{4}-\d{2}-\d{2}', source: '([^']+)' \}", l)
                if not m:
                    r.add(f"patch {p['id']!r}: malformed proposal marker in {l.strip()!r}")
                elif m.group(1) not in sources:
                    r.add(f"patch {p['id']!r}: proposal source {m.group(1)!r} is not a resolved note")
        elif kind == "glossary-proposal":
            for marker in ("- status: proposed", "- proposed_by: mockup-feedback", "- proposed_on: ", "- source: "):
                if not re.search(rf"^\+{re.escape(marker)}", diff, re.MULTILINE):
                    r.add(f"patch {p['id']!r}: glossary diff lacks the line `{marker.strip()}`")
        elif cat == "add":
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
            "Usage: python validate_patches.py <triage-json> <patches-json> <review-md>",
            file=sys.stderr,
        )
        return 1

    try:
        triage       = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        patches_data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        review_md    = Path(sys.argv[3]).read_text(encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    r = Report()
    validate(triage, patches_data, review_md, r)

    if r.ok():
        print(f"PASS  {sys.argv[2]}")
        return 0
    r.dump()
    return 2


if __name__ == "__main__":
    sys.exit(main())
