"""Tests for impl-plan-brainstorm validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent

_spec = importlib.util.spec_from_file_location(
    "impl_plan_brainstorm_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


GOOD_FRONTMATTER = """---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
feature_path: _concept/product-spec/features/team-todo/team-todo-comments.md
phase: brainstorm
tier: appbuilder-standard
created_at: 2026-05-08T12:34:56Z
last_updated: 2026-05-08T13:00:00Z
---
"""

GOOD_BODY = """
## App-level summary (1 paragraph)
Team-todo is a shared list app for small teams. Tier: appbuilder-standard.

## Feature summary (1 paragraph)
Members can attach short comments to any team todo item. Comments appear
in chronological order on the item detail panel.

## Risks and unknowns

### Data
- New `comments` table; FK ownership shared with `todos` (cascade on delete?).

### Auth
- Role gating (guest vs member vs admin) for create/edit/delete needs confirmation.

### Integrations
_(no risks identified for this feature)_

### Stack
- Real-time updates depend on the chosen stack's broadcast layer.

### Performance
- Worst-case comment count per item — paginate at N=50?

### UX
- Optimistic posting + rollback on failure.

## Open questions

| Priority | Question | Blocks |
|----------|----------|--------|
| P1 | Are cascading deletes required? | align/plan |
| P2 | Edit window unlimited or capped? | comment-edit subtask |
| P3 | Reactions out of scope for v1? | nothing critical |

## Recommended mitigations
- Cascade delete: confirm with user during align before plan.
- Pagination: include in plan.md as the comment-list row's Logic spec.
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
    assert any("missing frontmatter keys" in e and "phase" in e for e in errors), errors


def test_wrong_phase_value_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("phase: brainstorm", "phase: align")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("phase must be 'brainstorm'" in e for e in errors), errors


def test_slice_id_dir_mismatch_fails(tmp_path: Path):
    wrong_dir = tmp_path / "different-slug"
    wrong_dir.mkdir()
    f = wrong_dir / "brainstorm.md"
    f.write_text(GOOD_FRONTMATTER + GOOD_BODY, encoding="utf-8")
    errors = validator.validate(f)
    assert any("does not match parent dir name" in e for e in errors), errors


def test_missing_top_section_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace(
        "## Recommended mitigations\n", "## Renamed mitigations\n"
    )
    f.write_text(text)
    errors = validator.validate(f)
    assert any(
        "missing required body section" in e and "Recommended mitigations" in e
        for e in errors
    ), errors


def test_mvp_tier_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("tier: appbuilder-standard", "tier: appbuilder-mvp")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("tier must be one of" in e for e in errors), errors


def test_simple_app_tier_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text().replace("tier: appbuilder-standard", "tier: appbuilder-simple")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("tier must be one of" in e for e in errors), errors


def test_open_questions_without_priority_table_fails(tmp_path: Path):
    f = write_good(tmp_path)
    text = f.read_text()
    # Replace the priority-table header line with a non-table line
    text = text.replace(
        "| Priority | Question | Blocks |",
        "Some prose without a table header",
    )
    f.write_text(text)
    errors = validator.validate(f)
    assert any(
        "Open questions" in e and "Priority" in e for e in errors
    ), errors
