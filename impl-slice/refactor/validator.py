#!/usr/bin/env python3
"""Validator for impl-slice-refactor handoff files (`_slice/impl/<id>/refactor.md`).

Usage:
    python3 validator.py <path/to/refactor.md>

Exit codes:
    0 — valid (warnings may still be printed to stderr)
    2 — validation failure (errors printed to stderr)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REQUIRED_FRONTMATTER_KEYS = {
    "slice_id",
    "feature_title",
    "feature_path",
    "phase",
    "tier",
    "created_at",
    "last_updated",
}

REQUIRED_TOP_SECTIONS = [
    "## Slice goal recap (1-2 lines)",
    "## Smallest improvement candidates",
    "## What I considered but rejected (1-3 items)",
    "## User approval gate",
    "## Applied changes",
]

ALLOWED_TIERS = {"mvp", "simple-app", "standard-app", "complex-app"}
ALLOWED_TYPES = {"subtraction", "simplification", "clarification"}
SLICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")
APPROVAL_RE = re.compile(
    r"^Approval status: (pending|approved|rejected|modified)$", re.MULTILINE
)
CANDIDATE_HEADER_RE = re.compile(r"^### \d+\. ", re.MULTILINE)
TYPE_LINE_RE = re.compile(r"^\*\*Type:\*\*\s*([A-Za-z]+)\s*$", re.MULTILINE)

REQUIRED_CANDIDATE_FIELDS = [
    re.compile(r"^\*\*Type:\*\*", re.MULTILINE),
    re.compile(r"^\*\*Files:\*\*", re.MULTILINE),
    re.compile(r"^\*\*Rationale:\*\*", re.MULTILINE),
    re.compile(r"^\*\*Risk:\*\*", re.MULTILINE),
    re.compile(r"^\*\*Behavior preservation:\*\*", re.MULTILINE),
]
# `Diff sketch` is optional; not in REQUIRED_CANDIDATE_FIELDS.

REJECTED_BANNED_TYPE_RE = re.compile(r"\baddition\b", re.IGNORECASE)
APPLIED_NONE_PENDING = "_(none — approval pending)_"
APPLIED_NONE_DECLINED = "_(none — user declined refactor)_"


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("File does not start with YAML frontmatter (---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Could not parse frontmatter — need two `---` lines")
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return fm, body


def extract_section(body: str, header: str) -> str:
    """Return text under `header` until the next `## ` header or EOF."""
    lines = body.splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        stripped = line.rstrip()
        if stripped == header:
            inside = True
            continue
        if inside:
            if stripped.startswith("## ") and stripped != header:
                break
            out.append(line)
    return "\n".join(out).strip("\n")


def split_candidates(section: str) -> list[str]:
    """Split a section by `### N. ` headers; return each candidate body."""
    parts = re.split(r"(?m)^### \d+\.\s", section)
    # First element is preamble (typically empty); drop it.
    return [p.strip() for p in parts[1:]]


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return ([f"file not found: {path}"], warnings)

    text = path.read_text(encoding="utf-8")
    try:
        fm, body = split_frontmatter(text)
    except ValueError as exc:
        return ([str(exc)], warnings)

    # Frontmatter shape
    missing = REQUIRED_FRONTMATTER_KEYS - set(fm)
    if missing:
        errors.append(f"missing frontmatter keys: {sorted(missing)}")

    if fm.get("phase") != "refactor":
        errors.append(f"phase must be 'refactor', got {fm.get('phase')!r}")

    tier = fm.get("tier")
    if tier not in ALLOWED_TIERS:
        errors.append(
            f"tier must be one of {sorted(ALLOWED_TIERS)}, got {tier!r}"
        )

    slice_id = fm.get("slice_id")
    if not isinstance(slice_id, str) or not SLICE_ID_RE.match(slice_id):
        errors.append(
            f"slice_id {slice_id!r} does not match ^[a-z][a-z0-9-]{{1,47}}$"
        )
    else:
        parent_name = path.parent.name
        if parent_name != slice_id:
            errors.append(
                f"slice_id {slice_id!r} does not match parent dir name {parent_name!r}"
            )

    body_lines = {line.rstrip() for line in body.splitlines()}
    for section in REQUIRED_TOP_SECTIONS:
        if section not in body_lines:
            errors.append(f"missing required body section: {section!r}")

    headers_in_order: list[str] = [
        line.rstrip()
        for line in body.splitlines()
        if line.rstrip() in REQUIRED_TOP_SECTIONS
    ]
    if (
        headers_in_order != REQUIRED_TOP_SECTIONS
        and set(headers_in_order) == set(REQUIRED_TOP_SECTIONS)
    ):
        errors.append(
            f"required body sections present but out of order. Got: {headers_in_order}"
        )

    # Smallest improvement candidates: 1-3 numbered items, each with all required fields.
    candidates: list[str] = []
    if "## Smallest improvement candidates" in body_lines:
        sec = extract_section(body, "## Smallest improvement candidates")
        candidates = split_candidates(sec)
        n = len(candidates)
        if n < 1:
            errors.append(
                "'## Smallest improvement candidates' must contain ≥ 1 numbered item"
            )
        elif n > 3:
            errors.append(
                f"'## Smallest improvement candidates' must contain ≤ 3 items (got {n})"
            )
        for idx, cand in enumerate(candidates, start=1):
            for pat in REQUIRED_CANDIDATE_FIELDS:
                if not pat.search(cand):
                    errors.append(
                        f"candidate {idx} missing required field "
                        f"matching {pat.pattern!r}"
                    )
            # Type value must be in the allowed enum AND must not contain "addition".
            type_match = TYPE_LINE_RE.search(cand)
            if type_match:
                type_val = type_match.group(1).strip().lower()
                if type_val not in ALLOWED_TYPES:
                    errors.append(
                        f"candidate {idx} has Type={type_val!r}; must be one of "
                        f"{sorted(ALLOWED_TYPES)}"
                    )
            # Anti-addition guard — even if someone sneaks 'addition' past the enum.
            type_line_text = (type_match.group(0) if type_match else "")
            if REJECTED_BANNED_TYPE_RE.search(type_line_text):
                errors.append(
                    f"candidate {idx} Type contains 'addition' — additions are out of scope"
                )

    # What I considered but rejected: ≥ 1 numbered item.
    if "## What I considered but rejected (1-3 items)" in body_lines:
        sec = extract_section(
            body, "## What I considered but rejected (1-3 items)"
        )
        # Numbered items here use plain `1. `/`2. ` etc., not `### `.
        numbered_lines = re.findall(r"^\s*\d+\.\s", sec, re.MULTILINE)
        if len(numbered_lines) < 1:
            errors.append(
                "'## What I considered but rejected (1-3 items)' must contain "
                "≥ 1 numbered item"
            )

    # Approval status: exactly one valid line.
    approval_matches = APPROVAL_RE.findall(body)
    approval: str | None = None
    if len(approval_matches) == 0:
        errors.append(
            "no valid 'Approval status: pending|approved|rejected|modified' line found"
        )
    elif len(approval_matches) > 1:
        errors.append(
            f"multiple Approval status lines found: {approval_matches}"
        )
    else:
        approval = approval_matches[0]

    # Applied changes consistency.
    if "## Applied changes" in body_lines:
        applied = extract_section(body, "## Applied changes").strip()
        if approval == "pending":
            if applied != APPLIED_NONE_PENDING:
                errors.append(
                    f"'Approval status: pending' requires '## Applied changes' body to be "
                    f"exactly {APPLIED_NONE_PENDING!r}"
                )
        elif approval == "rejected":
            if applied != APPLIED_NONE_DECLINED:
                errors.append(
                    f"'Approval status: rejected' requires '## Applied changes' body to be "
                    f"exactly {APPLIED_NONE_DECLINED!r}"
                )
        elif approval in ("approved", "modified"):
            if not applied or applied in (APPLIED_NONE_PENDING, APPLIED_NONE_DECLINED):
                errors.append(
                    f"'Approval status: {approval}' requires '## Applied changes' to be "
                    "non-empty (list the actual edits)"
                )

    return (errors, warnings)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validator.py <path/to/refactor.md>", file=sys.stderr)
        return 2
    errors, warnings = validate(Path(argv[1]))
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
