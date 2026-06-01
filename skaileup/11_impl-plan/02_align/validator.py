#!/usr/bin/env python3
"""Validator for impl-plan-align handoff files.

Usage:
    python3 validator.py <path/to/_implementation/slices/<slice_id>/align.md>

Exit codes:
    0 — valid
    2 — validation failure (one or more errors printed to stderr)
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
    "## Feature recap (1-2 lines)",
    "## Concept summary",
    "## Open questions surfaced by the grill",
    "## Edge cases to handle",
    "## Constraints",
    "## Decisions made",
    "## Acceptance handoff",
]

REQUIRED_CONSTRAINTS_SUBSECTIONS = [
    "### Technical",
    "### Scope",
    "### Deadline / supervision",
]

ALLOWED_TIERS = {"simple-app", "standard-app", "complex-app"}
SLICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")

# Event-driven EARS — same regex as concept-slice-align
EARS_RE = re.compile(r"WHEN\b.+\bTHE\s+\S+\s+SHALL\b.+", re.IGNORECASE)

# Numbered open-question item with priority tag.
P_ITEM_RE = re.compile(r"^\s*\d+\.\s+\[P[123]\]", re.MULTILINE)
P12_ITEM_RE = re.compile(r"^\s*\d+\.\s+\[P[12]\]", re.MULTILINE)


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
    """Return the text of the section starting at `header` until the next
    same-level marker or EOF.
    """
    lines = body.splitlines()
    out: list[str] = []
    inside = False
    is_subsection = header.startswith("### ")
    for line in lines:
        stripped = line.rstrip()
        if stripped == header:
            inside = True
            continue
        if inside:
            if is_subsection:
                if stripped.startswith("### ") and stripped != header:
                    break
                if stripped.startswith("## "):
                    break
            else:
                if stripped.startswith("## ") and stripped != header:
                    break
            out.append(line)
    return "\n".join(out)


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"file not found: {path}"]

    text = path.read_text(encoding="utf-8")
    try:
        fm, body = split_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]

    # Frontmatter shape
    missing = REQUIRED_FRONTMATTER_KEYS - set(fm)
    if missing:
        errors.append(f"missing frontmatter keys: {sorted(missing)}")

    # phase
    if fm.get("phase") != "align":
        errors.append(f"phase must be 'align', got {fm.get('phase')!r}")

    # tier whitelist
    tier = fm.get("tier")
    if tier not in ALLOWED_TIERS:
        errors.append(
            f"tier must be one of {sorted(ALLOWED_TIERS)}, got {tier!r}"
        )

    # slice_id format + dir match
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

    # body sections (exact line match)
    body_lines = {line.rstrip() for line in body.splitlines()}
    for section in REQUIRED_TOP_SECTIONS:
        if section not in body_lines:
            errors.append(f"missing required body section: {section!r}")

    # Constraints sub-sections (only check if parent exists)
    if "## Constraints" in body_lines:
        for sub in REQUIRED_CONSTRAINTS_SUBSECTIONS:
            if sub not in body_lines:
                errors.append(
                    f"missing required sub-section under '## Constraints': {sub!r}"
                )

    # EARS criterion required in `## Acceptance handoff`. The section MUST be
    # present (checked above) AND MUST contain at least one EARS line.
    if "## Acceptance handoff" in body_lines:
        accept_section = extract_section(body, "## Acceptance handoff")
        if not EARS_RE.search(accept_section):
            errors.append(
                "no EARS-format line found in '## Acceptance handoff' "
                "(expected pattern: WHEN ..., THE ... SHALL ...)"
            )

    # Non-empty grill rule:
    # at least one P1/P2 question in `## Open questions surfaced by the grill`
    # OR at least one entry in `## Decisions made`.
    open_q = extract_section(body, "## Open questions surfaced by the grill")
    decisions = extract_section(body, "## Decisions made")

    has_p12 = bool(P12_ITEM_RE.search(open_q))
    decisions_text = decisions.strip()
    has_decisions = bool(decisions_text) and decisions_text != "_(none)_"

    if not has_p12 and not has_decisions:
        errors.append(
            "grill is empty: '## Open questions surfaced by the grill' has no P1/P2 "
            "item AND '## Decisions made' is empty (or `_(none)_`). At least one is required."
        )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validator.py <path/to/align.md>", file=sys.stderr)
        return 2
    errors = validate(Path(argv[1]))
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
