#!/usr/bin/env python3
"""Validator for concept-slice-brainstorm handoff files.

Usage:
    python3 validator.py <path/to/_slice/concept/<slice_id>/brainstorm.md>

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
    "phase",
    "tier",
    "created_at",
    "last_updated",
}

REQUIRED_SECTIONS = [
    "## Feature in one sentence",
    "## Who uses it",
    "## Trigger",
    "## Happy path (3-7 bullets)",
    "## Clearly out of scope",
    "## Open questions for align",
]

ALLOWED_TIERS = {"standard-app", "complex-app"}
SLICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("File does not start with YAML frontmatter (---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Could not parse frontmatter — need two `---` lines")
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return fm, body


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
    if fm.get("phase") != "brainstorm":
        errors.append(f"phase must be 'brainstorm', got {fm.get('phase')!r}")

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
        # parent dir name should equal slice_id
        parent_name = path.parent.name
        if parent_name != slice_id:
            errors.append(
                f"slice_id {slice_id!r} does not match parent dir name {parent_name!r}"
            )

    # body sections — match each required header on its own line (exact)
    body_lines = {line.rstrip() for line in body.splitlines()}
    for section in REQUIRED_SECTIONS:
        if section not in body_lines:
            errors.append(f"missing required body section: {section!r}")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validator.py <path/to/brainstorm.md>", file=sys.stderr)
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
