#!/usr/bin/env python3
"""Validator for impl-slice-recap handoff files (`_implementation/slices/<id>/recap.md`).

Usage:
    python3 validator.py <path/to/recap.md>

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
    "## What was built (1-3 sentences)",
    "## ASCII diagram",
    "## Files touched",
    "## Outcome vs. plan",
]

REQUIRED_OUTCOME_SUBSECTIONS = [
    "### Met expectations",
    "### Deviated",
    "### Carried over",
]

ALLOWED_TIERS = {"mvp", "simple-app", "standard-app", "complex-app"}
SLICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")
FENCED_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)\n```", re.DOTALL)
DIAGRAM_CHARS = {"→", ">", "|", "─", "+"}
FILE_BULLET_RE = re.compile(
    r"^- \S[^\s].*?(?: \((new|modified|deleted)\))?\s*$"
)
SENTENCE_END_RE = re.compile(r"[.!?](?:\s|$)")


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
    """Return text under `header` until the next same-or-higher-level header or EOF."""
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
    return "\n".join(out).strip("\n")


def count_sentences(text: str) -> int:
    """Approximate sentence count (period/!/? followed by space or EOL).

    Excludes content inside backtick code spans (rough — strips them entirely).
    """
    cleaned = re.sub(r"`[^`]*`", "", text)
    return len(SENTENCE_END_RE.findall(cleaned))


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

    if fm.get("phase") != "recap":
        errors.append(f"phase must be 'recap', got {fm.get('phase')!r}")

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

    # Outcome vs plan must contain three sub-headings.
    if "## Outcome vs. plan" in body_lines:
        outcome = extract_section(body, "## Outcome vs. plan")
        outcome_lines = {line.rstrip() for line in outcome.splitlines()}
        for sub in REQUIRED_OUTCOME_SUBSECTIONS:
            if sub not in outcome_lines:
                errors.append(
                    f"missing required sub-heading under '## Outcome vs. plan': {sub!r}"
                )

    # ASCII diagram: ≥ 1 fenced code block, ≥ 5 non-empty lines, contains diagram chars.
    if "## ASCII diagram" in body_lines:
        diag = extract_section(body, "## ASCII diagram")
        blocks = FENCED_BLOCK_RE.findall(diag)
        if not blocks:
            errors.append(
                "'## ASCII diagram' must contain at least one fenced code block"
            )
        else:
            ok_block = False
            for _lang, content in blocks:
                non_empty = [ln for ln in content.splitlines() if ln.strip()]
                if len(non_empty) < 5:
                    continue
                if any(c in content for c in DIAGRAM_CHARS):
                    ok_block = True
                    break
            if not ok_block:
                errors.append(
                    "'## ASCII diagram' fenced block must have ≥ 5 non-empty lines "
                    "and contain at least one diagram char from "
                    + repr(sorted(DIAGRAM_CHARS))
                )

    # What was built: 1-3 sentences (warn if > 3).
    if "## What was built (1-3 sentences)" in body_lines:
        wb = extract_section(body, "## What was built (1-3 sentences)")
        n = count_sentences(wb)
        if n == 0:
            errors.append(
                "'## What was built (1-3 sentences)' must contain ≥ 1 sentence"
            )
        elif n > 3:
            warnings.append(
                f"'## What was built (1-3 sentences)' has {n} sentences; "
                "tighten to 1-3 (soft check)"
            )

    # Files touched: ≥ 1 bullet, each matching the path-bullet regex.
    if "## Files touched" in body_lines:
        ft = extract_section(body, "## Files touched")
        bullets = [
            line.rstrip()
            for line in ft.splitlines()
            if line.strip().startswith("- ")
        ]
        if not bullets:
            errors.append("'## Files touched' must contain ≥ 1 bullet")
        else:
            for b in bullets:
                if not FILE_BULLET_RE.match(b):
                    errors.append(
                        f"'## Files touched' bullet does not match path pattern: {b[:80]!r}"
                    )

    return (errors, warnings)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validator.py <path/to/recap.md>", file=sys.stderr)
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
