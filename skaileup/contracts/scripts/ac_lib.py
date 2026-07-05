#!/usr/bin/env python3
"""ac_lib — shared validation for acceptance-criteria ledgers (.ac.md).

Contract: skaileup/contracts/acceptance_criteria.md (§ AC File Format and
§ Criteria Status Table). Used by the impl-plan-plan-vertical validator
(creation, all rows untested) and the impl-slice-test validator (updates).
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REQUIRED_FRONTMATTER_KEYS = {
    "feature_ref",
    "screen_refs",
    "story_refs",
    "derived_from",
    "last_updated",
}

ALLOWED_STATUSES = {"untested", "pass", "fail"}
AC_HEADING_RE = re.compile(r"^#{2,3} (AC-B?\d+)\b", re.MULTILINE)
STATUS_HEADER_RE = re.compile(
    r"^\|\s*ID\s*\|\s*Source\s*\|\s*Status\s*\|\s*Updated by\s*\|\s*Date\s*\|",
    re.MULTILINE,
)


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("File does not start with YAML frontmatter (---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Could not parse frontmatter — need two `---` lines")
    return yaml.safe_load(parts[1]) or {}, parts[2]


def parse_status_rows(body: str) -> list[list[str]]:
    """Return data rows of the `## Criteria Status` table as cell lists
    [ID, Source, Status, Updated by, Date]."""
    section = body.split("## Criteria Status", 1)
    if len(section) < 2:
        return []
    rows: list[list[str]] = []
    saw_header = saw_align = False
    for raw in section[1].splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        if not saw_header:
            if STATUS_HEADER_RE.match(line):
                saw_header = True
            continue
        if not saw_align:
            if re.match(r"^\|\s*[-:]+\s*(\|\s*[-:]+\s*)+\|?$", line):
                saw_align = True
                continue
            saw_align = True
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


def validate_ac_file(path: Path, require_untested: bool = False) -> list[str]:
    errors: list[str] = []
    path = Path(path)
    if not path.exists():
        return [f"file not found: {path}"]
    try:
        fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [str(exc)]

    missing = REQUIRED_FRONTMATTER_KEYS - set(fm)
    if missing:
        errors.append(f"missing frontmatter keys: {sorted(missing)}")

    heading_ids = AC_HEADING_RE.findall(body)
    if not heading_ids:
        errors.append("no `## AC-n:` criterion sections found (≥ 1 required)")

    if "## Criteria Status" not in body:
        errors.append("missing `## Criteria Status` section")
        return errors

    rows = parse_status_rows(body)
    if not rows:
        errors.append(
            "`## Criteria Status` must contain a table with header "
            "`| ID | Source | Status | Updated by | Date |` and ≥ 1 data row"
        )
        return errors

    row_ids: list[str] = []
    for row in rows:
        if len(row) < 5:
            errors.append(f"status row has fewer than 5 cells: {row}")
            continue
        rid, source, status, updated_by, date = row[0], row[1], row[2], row[3], row[4]
        row_ids.append(rid)
        if status not in ALLOWED_STATUSES:
            errors.append(
                f"{rid}: status {status!r} not in {sorted(ALLOWED_STATUSES)}"
            )
        if not source or source == "-":
            errors.append(f"{rid}: Source cell must cite the EARS line / story-id")
        if require_untested and status != "untested":
            errors.append(
                f"{rid}: status must be 'untested' at creation, got {status!r}"
            )
        if status != "untested" and (updated_by == "-" or date == "-"):
            errors.append(
                f"{rid}: non-untested rows must fill 'Updated by' and 'Date'"
            )

    for rid in row_ids:
        if rid not in heading_ids:
            errors.append(f"status row {rid} has no matching `## {rid}:` section")
    for hid in heading_ids:
        if hid not in row_ids:
            errors.append(f"criterion section {hid} has no status row")

    return errors
