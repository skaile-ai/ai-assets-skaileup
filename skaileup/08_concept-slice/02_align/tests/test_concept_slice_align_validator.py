"""Tests for concept-slice-align validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent

_spec = importlib.util.spec_from_file_location(
    "concept_slice_align_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


GOOD_FRONTMATTER = """---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
phase: align
tier: appbuilder-standard
created_at: 2026-05-08T12:34:56Z
last_updated: 2026-05-08T13:00:00Z
---
"""

GOOD_BODY = """
## Feature recap (one sentence)
Members can attach short comments to any team todo item.

## Acceptance criteria (EARS)
- WHEN a member opens a todo item, THE SYSTEM SHALL display all existing comments in chronological order.
- WHEN a member submits a comment with text length > 0 and <= 2000, THE SYSTEM SHALL persist it and broadcast to other viewers.

## Edge cases
1. Empty submission — should be rejected client-side.
2. Comment exceeds 2000 chars — show count + reject.

## Error states
- Network drop mid-submit — show retry banner; preserve draft locally.

## Permissions / roles
| Role   | View | Create | Edit own | Delete own | Moderate |
|--------|------|--------|----------|------------|----------|
| guest  | x    |        |          |            |          |
| member | x    | x      | x        | x          |          |
| admin  | x    | x      | x        | x          | x        |

## Unstated assumptions exposed
- Edit window is unlimited unless admin moderates.

## Resolved questions
- Q: Threaded replies? A: Out of scope for v1.

## Open questions blocking scope-feature
- None.
"""


def write_good(tmp_path: Path) -> Path:
    slug_dir = tmp_path / "team-todo-comments"
    slug_dir.mkdir()
    f = slug_dir / "align.md"
    f.write_text(GOOD_FRONTMATTER + GOOD_BODY, encoding="utf-8")
    return f


def test_good_fixture_passes(tmp_path: Path):
    f = write_good(tmp_path)
    errors = validator.validate(f)
    assert errors == [], errors


def test_missing_ears_line_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text()
    # replace the EARS bullets with prose lacking the EARS pattern
    text = text.replace(
        "- WHEN a member opens a todo item, THE SYSTEM SHALL display all existing comments in chronological order.",
        "- The system shows comments somehow.",
    ).replace(
        "- WHEN a member submits a comment with text length > 0 and <= 2000, THE SYSTEM SHALL persist it and broadcast to other viewers.",
        "- Submission is allowed under certain conditions.",
    )
    f.write_text(text)
    errors = validator.validate(f)
    assert any("no EARS-format line" in e for e in errors), errors


def test_missing_permission_table_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text()
    # remove all lines with `|` from the permissions section
    lines = text.splitlines()
    out = []
    inside_perms = False
    for line in lines:
        if line.strip() == "## Permissions / roles":
            inside_perms = True
            out.append(line)
            continue
        if inside_perms and line.startswith("## ") and line.strip() != "## Permissions / roles":
            inside_perms = False
        if inside_perms and "|" in line:
            continue
        out.append(line)
    f.write_text("\n".join(out))
    errors = validator.validate(f)
    assert any("Permissions / roles" in e and "markdown table" in e for e in errors), errors


def test_phase_brainstorm_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("phase: align", "phase: brainstorm")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("phase must be 'align'" in e for e in errors), errors


def test_slice_id_dir_mismatch_fails(tmp_path: Path):
    wrong_dir = tmp_path / "different-slug"
    wrong_dir.mkdir()
    f = wrong_dir / "align.md"
    f.write_text(GOOD_FRONTMATTER + GOOD_BODY, encoding="utf-8")
    errors = validator.validate(f)
    assert any("does not match parent dir name" in e for e in errors), errors


def test_simple_app_tier_passes(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("tier: appbuilder-standard", "tier: appbuilder-simple")
    f.write_text(text)
    errors = validator.validate(f)
    assert errors == [], errors


def test_mvp_tier_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("tier: appbuilder-standard", "tier: appbuilder-mvp")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("tier must be one of" in e for e in errors), errors
