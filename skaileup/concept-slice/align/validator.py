#!/usr/bin/env python3
"""Validator for concept-slice-align handoff files.

Usage:
    python3 validator.py <path/to/_concept/slices/<slice_id>/align.md>

Exit codes:
    0 — valid
    2 — validation failure
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
    "## Feature recap (one sentence)",
    "## Acceptance criteria (EARS)",
    "## Edge cases",
    "## Error states",
    "## Permissions / roles",
    "## Unstated assumptions exposed",
    "## Resolved questions",
    "## Open questions blocking scope-feature",
]

ALLOWED_TIERS = {"simple-app", "standard-app", "complex-app"}
SLICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")

# Event-driven EARS only — full EARS is deferred (Open Question § 7 in plan)
EARS_RE = re.compile(
    r"WHEN\b.+\bTHE\s+\S+\s+SHALL\b.+",
    re.IGNORECASE,
)


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
    """Return the text of the section starting at `header` until next `## ` or EOF."""
    lines = body.splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        if line.rstrip() == header:
            inside = True
            continue
        if inside and line.startswith("## ") and line.rstrip() != header:
            break
        if inside:
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
    for section in REQUIRED_SECTIONS:
        if section not in body_lines:
            errors.append(f"missing required body section: {section!r}")

    # EARS regex inside acceptance criteria section
    ears_section = extract_section(body, "## Acceptance criteria (EARS)")
    if ears_section and not EARS_RE.search(ears_section):
        errors.append(
            "no EARS-format line found in '## Acceptance criteria (EARS)' "
            "(expected pattern: WHEN ..., THE ... SHALL ...)"
        )

    # Permissions table — at least 2 lines containing `|` inside the section
    perms_section = extract_section(body, "## Permissions / roles")
    pipe_lines = [
        ln for ln in perms_section.splitlines() if "|" in ln
    ]
    if len(pipe_lines) < 2:
        errors.append(
            "'## Permissions / roles' must contain a markdown table "
            "(>= 2 lines with `|`)"
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
