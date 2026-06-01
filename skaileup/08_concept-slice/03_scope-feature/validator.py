#!/usr/bin/env python3
"""Validator for concept-slice-scope-feature handoff files.

Usage:
    python3 validator.py <path/to/_concept/slices/<slice_id>/scope-feature.md>

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
    "## In scope",
    "## Out of scope",
    "## Deferred",
    "## Owned by another feature",
    "## Acceptance criteria (final)",
    "## Required entities",
    "## Required screens",
]

ALLOWED_TIERS = {"simple-app", "standard-app", "complex-app"}
SLICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")
SCREEN_LINE_RE = re.compile(r"^- [a-z0-9-]+/[a-z0-9-]+$")


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


def section_has_bullet(section: str) -> bool:
    """True if section has at least one non-empty bullet line (- ...)."""
    return any(
        ln.lstrip().startswith("- ") and ln.lstrip().strip("- ").strip()
        for ln in section.splitlines()
    )


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

    if fm.get("phase") != "scope-feature":
        errors.append(f"phase must be 'scope-feature', got {fm.get('phase')!r}")

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

    # body sections
    body_lines = {line.rstrip() for line in body.splitlines()}
    for section in REQUIRED_SECTIONS:
        if section not in body_lines:
            errors.append(f"missing required body section: {section!r}")

    # In scope must have at least one bullet
    in_scope = extract_section(body, "## In scope")
    if not section_has_bullet(in_scope):
        errors.append("'## In scope' must contain at least one bullet")

    # Required screens line format
    screens = extract_section(body, "## Required screens")
    bad_screen_lines = []
    for ln in screens.splitlines():
        s = ln.rstrip()
        if not s:
            continue
        if not s.startswith("- "):
            continue
        if not SCREEN_LINE_RE.match(s):
            bad_screen_lines.append(s)
    if bad_screen_lines:
        errors.append(
            "screen lines must match '- <group>/<screen>' (kebab-case both sides); "
            f"offending: {bad_screen_lines}"
        )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validator.py <path/to/scope-feature.md>", file=sys.stderr)
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
