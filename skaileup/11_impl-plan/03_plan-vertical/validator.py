#!/usr/bin/env python3
"""Validator for impl-plan-plan-vertical handoff files.

Usage:
    python3 validator.py <path/to/_implementation/slices/<slice_id>/plan.md>

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

# Top-level section headers required, in document order.
REQUIRED_TOP_SECTIONS = [
    "## Slice scope",
    "## Vertical decomposition",
    "## Testing strategy",
    "## Anti-horizontal nudge",
    "## Definition of done",
    "## Open carry-overs",
]

REQUIRED_TESTING_SUBSECTIONS = [
    "### Manual checks",
    "### Automated tests",
    "### Exit criteria",
]

# Routes that run this skill. cli-app is a variant route (no UI) that still
# runs the impl-plan/impl-slice loop; concept-only/reverse-engineer don't.
ALLOWED_TIERS = {"mvp", "simple-app", "standard-app", "complex-app", "cli-app"}
SLICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")

# The VERBATIM anti-horizontal nudge body that MUST appear under
# `## Anti-horizontal nudge` in the output plan.md.
# (The leading `## Anti-horizontal nudge` heading itself is matched separately;
# this constant is the BODY that follows.)
ANTI_HORIZONTAL_NUDGE_BODY = """\
> **DO NOT build all UI first, then all logic, then all data.**
>
> The default LLM failure mode for implementation planning is horizontal layering: "first scaffold every screen, then wire every handler, then run every migration." This produces N half-finished slices and zero working ones.
>
> Instead: pick ONE row from `## Vertical decomposition` and complete it end-to-end (UI renders → handler responds → data round-trips → test green) BEFORE starting the next row.
>
> If you find yourself thinking any of the following, **stop**:
> - "I'll come back and wire the data after I've built all the screens."
> - "Let me get the UI looking right across the whole feature first."
> - "I'll batch the migrations and run them at the end."
> - "I'll add tests once everything is hooked up."
>
> A row is **not done** until: UI renders real data, the handler is callable from the UI, the data layer persists round-trips, and the test for that row is green. Then — and only then — start the next row."""

# Verbatim Definition of Done items — every one MUST appear as its own
# `- [ ] ...` line under `## Definition of done`.
REQUIRED_DOD_ITEMS = [
    "- [ ] All vertical rows complete end-to-end (UI + Logic + Data wired)",
    "- [ ] All tests in § \"Automated tests\" pass",
    "- [ ] All manual checks in § \"Manual checks\" verified by user",
    "- [ ] No row left half-implemented (no \"UI built but data not wired\", etc.)",
    "- [ ] `_concept/product-spec/features/<group>/<feature_slug>.md` § Acceptance Criteria all green",
]

# Header row for the vertical-decomposition table.
TABLE_HEADER_RE = re.compile(
    r"^\s*\|\s*#\s*\|\s*UI\s*\|\s*Logic\s*\|\s*Data\s*\|", re.MULTILINE
)
# Test-tag detector for `### Automated tests`.
TEST_TAG_RE = re.compile(r"\[(unit|integration|e2e)\]", re.IGNORECASE)


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
    same-or-higher level marker or EOF. Newline-joined; trailing stripped.
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
    return "\n".join(out).strip("\n")


def parse_decomposition_rows(section: str) -> list[list[str]]:
    """Return the data rows of the vertical-decomposition markdown table.

    Each row is a list of cell strings (left-to-right, header columns:
    #, UI, Logic, Data, [notes...]). Header row + alignment row are skipped.
    """
    rows: list[list[str]] = []
    saw_header = False
    saw_align = False
    for raw in section.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        if not saw_header:
            if TABLE_HEADER_RE.match(line):
                saw_header = True
            continue
        if not saw_align:
            # Alignment row like `|---|---|...|`
            if re.match(r"^\|\s*[-:]+\s*(\|\s*[-:]+\s*)+\|?$", line):
                saw_align = True
                continue
            # If no alignment row, treat the next line as data anyway
            saw_align = True
        # Data row
        # Split and trim, drop the leading/trailing empty cells from the pipe
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def validate(path: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
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

    # phase
    if fm.get("phase") != "plan":
        errors.append(f"phase must be 'plan', got {fm.get('phase')!r}")

    # tier whitelist (plan-vertical runs for ALL tiers)
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

    # All required body sections present.
    body_lines = {line.rstrip() for line in body.splitlines()}
    for section in REQUIRED_TOP_SECTIONS:
        if section not in body_lines:
            errors.append(f"missing required body section: {section!r}")

    # Required body sections in order (ordered check).
    headers_in_order: list[str] = [
        line.rstrip() for line in body.splitlines() if line.rstrip() in REQUIRED_TOP_SECTIONS
    ]
    if headers_in_order != REQUIRED_TOP_SECTIONS and set(headers_in_order) == set(REQUIRED_TOP_SECTIONS):
        errors.append(
            f"required body sections present but out of order. Got order: {headers_in_order}"
        )

    # Testing strategy sub-sections (only if parent exists).
    if "## Testing strategy" in body_lines:
        for sub in REQUIRED_TESTING_SUBSECTIONS:
            if sub not in body_lines:
                errors.append(
                    f"missing required sub-section under '## Testing strategy': {sub!r}"
                )

    # Vertical decomposition: table parses with required header + ≥1 data row.
    if "## Vertical decomposition" in body_lines:
        decomp = extract_section(body, "## Vertical decomposition")
        if not TABLE_HEADER_RE.search(decomp):
            errors.append(
                "'## Vertical decomposition' must contain a markdown table with header "
                "`| # | UI | Logic | Data |`"
            )
        else:
            rows = parse_decomposition_rows(decomp)
            if len(rows) < 1:
                errors.append(
                    "'## Vertical decomposition' table has no data rows (≥ 1 required)"
                )
            else:
                # Warn if any UI/Logic/Data cell is empty, '-', or 'n/a'.
                # Columns: 0=#, 1=UI, 2=Logic, 3=Data, [4=notes...]
                for idx, row in enumerate(rows, start=1):
                    if len(row) < 4:
                        warnings.append(
                            f"row {idx} has fewer than 4 cells: {row}"
                        )
                        continue
                    for col_name, cell in (("UI", row[1]), ("Logic", row[2]), ("Data", row[3])):
                        if cell.strip().lower() in ("", "-", "n/a", "_-_"):
                            warnings.append(
                                f"row {idx} {col_name!r} cell is empty/placeholder; "
                                "verify this row is genuinely vertical or merge/split it"
                            )

    # Anti-horizontal nudge: verbatim body match.
    if "## Anti-horizontal nudge" in body_lines:
        nudge = extract_section(body, "## Anti-horizontal nudge")
        # Normalise trailing whitespace per line for comparison.
        def _norm(s: str) -> str:
            return "\n".join(line.rstrip() for line in s.strip("\n").splitlines())
        if _norm(nudge) != _norm(ANTI_HORIZONTAL_NUDGE_BODY):
            errors.append(
                "'## Anti-horizontal nudge' body does not match the verbatim template "
                "(see impl-plan/plan-vertical/validator.py ANTI_HORIZONTAL_NUDGE_BODY). "
                "Do not soften the language."
            )

    # Definition of done: 5 verbatim items.
    if "## Definition of done" in body_lines:
        dod = extract_section(body, "## Definition of done")
        for item in REQUIRED_DOD_ITEMS:
            if item not in dod:
                errors.append(
                    f"'## Definition of done' is missing required item (verbatim): {item!r}"
                )

    # Automated tests: at least one [unit/integration/e2e] tag.
    if "### Automated tests" in body_lines:
        auto = extract_section(body, "### Automated tests")
        if not TEST_TAG_RE.search(auto):
            errors.append(
                "'### Automated tests' must contain ≥ 1 line tagged "
                "`[unit]`, `[integration]`, or `[e2e]`"
            )

    return (errors, warnings)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validator.py <path/to/plan.md>", file=sys.stderr)
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
