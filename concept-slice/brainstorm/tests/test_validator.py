"""Tests for concept-slice-brainstorm validator.

Run: pytest concept-slice/brainstorm/tests/ -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
sys.path.insert(0, str(SKILL_DIR))

import validator  # noqa: E402


GOOD_FRONTMATTER = """---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
phase: brainstorm
tier: standard-app
created_at: 2026-05-08T12:34:56Z
last_updated: 2026-05-08T12:34:56Z
---
"""

GOOD_BODY = """
## Feature in one sentence
Members can attach short comments to any team todo item.

## Who uses it
Members of a team workspace; admin can moderate.

## Trigger
A todo item needs context that doesn't belong in the title.

## Happy path (3-7 bullets)
- Member opens a todo item
- Member adds a comment
- Other members see it

## Clearly out of scope
- Threaded replies
- @mentions

## Open questions for align
- Edit window? Delete rules? Notifications?
"""


def write_good(tmp_path: Path) -> Path:
    slug_dir = tmp_path / "team-todo-comments"
    slug_dir.mkdir()
    f = slug_dir / "brainstorm.md"
    f.write_text(GOOD_FRONTMATTER + GOOD_BODY, encoding="utf-8")
    return f


def test_good_fixture_passes(tmp_path: Path):
    f = write_good(tmp_path)
    errors = validator.validate(f)
    assert errors == [], errors


def test_missing_phase_key_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("phase: brainstorm\n", "")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("missing frontmatter keys" in e for e in errors), errors


def test_wrong_phase_value_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("phase: brainstorm", "phase: align")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("phase must be 'brainstorm'" in e for e in errors), errors


def test_slice_id_dir_mismatch_fails(tmp_path: Path):
    # write the file under a directory whose name doesn't match slice_id
    wrong_dir = tmp_path / "different-slug"
    wrong_dir.mkdir()
    f = wrong_dir / "brainstorm.md"
    f.write_text(GOOD_FRONTMATTER + GOOD_BODY, encoding="utf-8")
    errors = validator.validate(f)
    assert any("does not match parent dir name" in e for e in errors), errors


def test_missing_section_header_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("## Trigger", "## Triggerz")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("missing required body section" in e for e in errors), errors


def test_tier_mvp_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("tier: standard-app", "tier: mvp")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("tier must be one of" in e for e in errors), errors


def test_complex_app_tier_passes(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("tier: standard-app", "tier: complex-app")
    f.write_text(text)
    errors = validator.validate(f)
    assert errors == [], errors


def test_bad_slice_id_format_fails(tmp_path: Path):
    bad_dir = tmp_path / "Bad_Slug"
    bad_dir.mkdir()
    f = bad_dir / "brainstorm.md"
    text = GOOD_FRONTMATTER.replace("slice_id: team-todo-comments", "slice_id: Bad_Slug")
    f.write_text(text + GOOD_BODY)
    errors = validator.validate(f)
    assert any("does not match ^[a-z]" in e for e in errors), errors
