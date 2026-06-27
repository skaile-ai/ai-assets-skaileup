"""Tests for concept-slice-scope-feature validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent

_spec = importlib.util.spec_from_file_location(
    "concept_slice_scope_feature_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


GOOD_FRONTMATTER = """---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
phase: scope-feature
tier: appbuilder-standard
created_at: 2026-05-08T12:34:56Z
last_updated: 2026-05-08T13:30:00Z
---
"""

GOOD_BODY = """
## In scope
- Plain-text comments up to 2000 chars — covers the primary use case.
- Member edits and deletes their own comments — basic affordance.

## Out of scope
- Threaded replies — adds complexity not needed for v1.

## Deferred
- @mentions — revisit after observing first 50 comments in production.

## Owned by another feature
- User profile rendering — owned by experience/features/users/profile.md.

## Acceptance criteria (final)
- WHEN a member opens a todo item, THE SYSTEM SHALL display all existing comments in chronological order.
- WHEN a member submits a comment with text length > 0 and <= 2000, THE SYSTEM SHALL persist it and broadcast to other viewers.

## Required entities
- Comment
- Todo
- User

## Required screens
- team-todo-comments/list
- team-todo-comments/detail
"""


def write_good(tmp_path: Path) -> Path:
    slug_dir = tmp_path / "team-todo-comments"
    slug_dir.mkdir()
    f = slug_dir / "scope-feature.md"
    f.write_text(GOOD_FRONTMATTER + GOOD_BODY, encoding="utf-8")
    return f


def test_good_fixture_passes(tmp_path: Path):
    f = write_good(tmp_path)
    errors = validator.validate(f)
    assert errors == [], errors


def test_empty_in_scope_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text()
    # blank out the In scope section by replacing its bullets with nothing
    text = text.replace(
        "- Plain-text comments up to 2000 chars — covers the primary use case.\n- Member edits and deletes their own comments — basic affordance.\n",
        "",
    )
    f.write_text(text)
    errors = validator.validate(f)
    assert any("In scope" in e and "bullet" in e for e in errors), errors


def test_bad_screen_format_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace(
        "- team-todo-comments/list",
        "- list",  # missing group
    )
    f.write_text(text)
    errors = validator.validate(f)
    assert any("screen lines must match" in e for e in errors), errors


def test_phase_align_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("phase: scope-feature", "phase: align")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("phase must be 'scope-feature'" in e for e in errors), errors


def test_slice_id_dir_mismatch_fails(tmp_path: Path):
    wrong_dir = tmp_path / "different-slug"
    wrong_dir.mkdir()
    f = wrong_dir / "scope-feature.md"
    f.write_text(GOOD_FRONTMATTER + GOOD_BODY, encoding="utf-8")
    errors = validator.validate(f)
    assert any("does not match parent dir name" in e for e in errors), errors


def test_missing_section_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("## Deferred", "## Deferredz")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("missing required body section" in e for e in errors), errors
