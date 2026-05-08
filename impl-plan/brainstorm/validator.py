#!/usr/bin/env python3
"""Validator for impl-plan-brainstorm handoff files.

Usage:
    python3 validator.py <path/to/_slice/impl/<slice_id>/brainstorm.md>

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

# Top-level section headers required, in document order.
REQUIRED_TOP_SECTIONS = [
    "## App-level summary (1 paragraph)",
    "## Feature summary (1 paragraph)",
    "## Risks and unknowns",
    "## Open questions",
    "## Recommended mitigations",
]

# Sub-headings under "## Risks and unknowns".
REQUIRED_RISK_SUBSECTIONS = [
    "### Data",
    "### Auth",
    "### Integrations",
    "### Stack",
    "### Performance",
    "### UX",
]

ALLOWED_TIERS = {"standard-app", "complex-app"}
SLICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")

# Detects the priority-table header in "## Open questions".
PRIORITY_TABLE_RE = re.compile(r"^\s*\|\s*Priority\b", re.IGNORECASE | re.MULTILINE)


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
    same-or-higher level marker (## or # of equal/greater priority) or EOF.
    """
    lines = body.splitlines()
    out: list[str] = []
    inside = False
    # Same-level header is `## ` for top sections, `### ` for sub-sections.
    is_subsection = header.startswith("### ")
    for line in lines:
        stripped = line.rstrip()
        if stripped == header:
            inside = True
            continue
        if inside:
            if is_subsection:
                # Stop at next ### or any ##
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
    if fm.get("phase") != "brainstorm":
        errors.append(f"phase must be 'brainstorm', got {fm.get('phase')!r}")

    # tier whitelist (brainstorm only runs for standard/complex)
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

    # body section headers (exact line match)
    body_lines = {line.rstrip() for line in body.splitlines()}
    for section in REQUIRED_TOP_SECTIONS:
        if section not in body_lines:
            errors.append(f"missing required body section: {section!r}")

    # Risks-and-unknowns sub-headings — only check if the parent section exists
    if "## Risks and unknowns" in body_lines:
        for sub in REQUIRED_RISK_SUBSECTIONS:
            if sub not in body_lines:
                errors.append(
                    f"missing required sub-section under '## Risks and unknowns': {sub!r}"
                )

    # `## Open questions` body must contain the priority-table header line.
    open_q = extract_section(body, "## Open questions")
    if open_q and not PRIORITY_TABLE_RE.search(open_q):
        errors.append(
            "'## Open questions' must contain a markdown table with "
            "header `| Priority | Question | Blocks |`"
        )

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
