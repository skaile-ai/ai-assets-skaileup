"""Tests for impl-slice-test validator."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
GOLDEN_NEEDS = SKILL_DIR / "examples" / "team-todo-comments-test.md"
GOLDEN_DONE = SKILL_DIR / "examples" / "team-todo-comments-test-done.md"
PLAN_FIXTURE = (
    SKILL_DIR.parent.parent
    / "impl-plan"
    / "plan-vertical"
    / "examples"
    / "team-todo-comments-plan.md"
)

_spec = importlib.util.spec_from_file_location(
    "impl_slice_test_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def write_to_slug_dir(tmp_path: Path, golden: Path, slug: str = "team-todo-comments") -> Path:
    slug_dir = tmp_path / slug
    slug_dir.mkdir()
    target = slug_dir / "test.md"
    shutil.copy(golden, target)
    return target


def test_golden_done_passes(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_DONE)
    errors, _ = validator.validate(f)
    assert errors == [], errors


def test_golden_needs_more_work_passes(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_NEEDS)
    errors, _ = validator.validate(f)
    assert errors == [], errors


def test_missing_decision_line_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_DONE)
    text = f.read_text().replace("Decision: Done", "Verdict: Done")
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any("no valid 'Decision:" in e for e in errors), errors


def test_done_with_blocker_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_DONE)
    # Inject a [BLOCKER] into Outstanding issues while keeping Decision: Done.
    text = f.read_text().replace(
        "## Outstanding issues\n_(none)_",
        "## Outstanding issues\n1. [BLOCKER] Sneaky leftover.",
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "Decision: Done" in e and "BLOCKER" in e for e in errors
    ), errors


def test_manual_check_without_tag_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_DONE)
    text = f.read_text().replace(
        "[PASS] Open a todo, verify all existing comments",
        "Open a todo, verify all existing comments",
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "'## Manual checks done' bullet missing" in e for e in errors
    ), errors


def test_phase_recap_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_DONE)
    text = f.read_text().replace("phase: test", "phase: recap")
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any("phase must be 'test'" in e for e in errors), errors


def test_slice_id_dir_mismatch_fails(tmp_path: Path):
    wrong = tmp_path / "different-slug"
    wrong.mkdir()
    target = wrong / "test.md"
    shutil.copy(GOLDEN_DONE, target)
    errors, _ = validator.validate(target)
    assert any("does not match parent dir name" in e for e in errors), errors


def test_cross_plan_check_missing_bullet_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_DONE)
    # Remove one manual-check bullet from test.md and verify --plan flags it.
    text = f.read_text()
    text = text.replace(
        "- [PASS] Edit own comment; verify body updates and `last_updated` bumps. — body updates; timestamp ticks.\n",
        "",
    )
    f.write_text(text)
    errors, _ = validator.validate(f, plan_path=PLAN_FIXTURE)
    assert any(
        "'### Manual checks' bullet not present" in e for e in errors
    ), errors
