"""Tests for impl-slice-commit validator."""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
GOLDEN_PLAN = SKILL_DIR / "examples" / "team-todo-comments-commit-plan.json"

# Reuse the existing handoff golden fixtures from the sibling skills.
# (Sibling skill dirs carry numeric run-order prefixes; names are unchanged.)
TEST_GOLDEN = SKILL_DIR.parent / "04_test" / "examples" / "team-todo-comments-test-done.md"
RECAP_GOLDEN = SKILL_DIR.parent / "05_recap" / "examples" / "team-todo-comments-recap.md"
REFACTOR_GOLDEN_APPROVED = (
    SKILL_DIR.parent / "06_refactor" / "examples" / "team-todo-comments-refactor.md"
)
REFACTOR_GOLDEN_REJECTED = (
    SKILL_DIR.parent
    / "06_refactor"
    / "examples"
    / "team-todo-comments-refactor-rejected.md"
)
PLAN_GOLDEN = (
    SKILL_DIR.parent.parent
    / "11_impl-plan"
    / "03_plan-vertical"
    / "examples"
    / "team-todo-comments-plan.md"
)

_spec = importlib.util.spec_from_file_location(
    "impl_slice_commit_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


# ── Mode A: commit-plan JSON ────────────────────────────────────


def test_mode_a_golden_passes():
    errors = validator.validate_plan(GOLDEN_PLAN, None)
    assert errors == [], errors


def test_mode_a_empty_commits_fails(tmp_path: Path):
    plan = json.loads(GOLDEN_PLAN.read_text())
    plan["commits"] = []
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan))
    errors = validator.validate_plan(p, None)
    assert any("≥ 1 entry" in e for e in errors), errors


def test_mode_a_invalid_type_fails(tmp_path: Path):
    plan = json.loads(GOLDEN_PLAN.read_text())
    plan["commits"][0]["type"] = "invalid"
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan))
    errors = validator.validate_plan(p, None)
    assert any("type='invalid'" in e or "must be one of" in e for e in errors), errors


def test_mode_a_body_missing_slice_line_fails(tmp_path: Path):
    plan = json.loads(GOLDEN_PLAN.read_text())
    plan["commits"][0]["body"] = (
        "Feature: something\nFeature spec: somewhere"  # missing 'Slice:'
    )
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan))
    errors = validator.validate_plan(p, None)
    assert any("Slice:" in e for e in errors), errors


def test_mode_a_summary_too_long_fails(tmp_path: Path):
    plan = json.loads(GOLDEN_PLAN.read_text())
    plan["commits"][0]["summary"] = "x" * 100
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan))
    errors = validator.validate_plan(p, None)
    assert any(">" in e and "chars" in e for e in errors), errors


# ── Mode B: post-commit dir-frozen ──────────────────────────────


def test_mode_b_frozen_dir_passes(tmp_path: Path):
    # Frozen slice: dir kept, index.md present, no progress.yaml.
    slice_dir = tmp_path / "team-todo-comments"
    slice_dir.mkdir()
    (slice_dir / "index.md").write_text("---\nphase: frozen\n---\n")
    (slice_dir / "recap.md").write_text("kept handoff")
    errors = validator.validate_post_commit(slice_dir)
    assert errors == [], errors


def test_mode_b_dir_absent_fails(tmp_path: Path):
    # Deleting the dossier is now a failure — freeze, never delete.
    slice_dir = tmp_path / "team-todo-comments"
    errors = validator.validate_post_commit(slice_dir)
    assert any("does not exist" in e for e in errors), errors


def test_mode_b_missing_index_fails(tmp_path: Path):
    slice_dir = tmp_path / "team-todo-comments"
    slice_dir.mkdir()
    errors = validator.validate_post_commit(slice_dir)
    assert any("index.md" in e for e in errors), errors


def test_mode_b_lingering_progress_fails(tmp_path: Path):
    slice_dir = tmp_path / "team-todo-comments"
    slice_dir.mkdir()
    (slice_dir / "index.md").write_text("---\nphase: frozen\n---\n")
    (slice_dir / "progress.yaml").write_text("{}")
    errors = validator.validate_post_commit(slice_dir)
    assert any("progress.yaml" in e for e in errors), errors


# ── Mode C: pre-flight 4-handoff gate ───────────────────────────


def _build_pre_flight_root(
    tmp_path: Path,
    refactor_src: Path = REFACTOR_GOLDEN_APPROVED,
    test_src: Path = TEST_GOLDEN,
) -> Path:
    """Build a fixture _implementation/slices/<id>/ with all 4 handoffs."""
    slice_dir = tmp_path / "_implementation" / "slices" / "team-todo-comments"
    slice_dir.mkdir(parents=True)
    shutil.copy(test_src, slice_dir / "test.md")
    shutil.copy(RECAP_GOLDEN, slice_dir / "recap.md")
    shutil.copy(refactor_src, slice_dir / "refactor.md")
    shutil.copy(PLAN_GOLDEN, slice_dir / "plan.md")
    return tmp_path


def test_mode_c_golden_passes(tmp_path: Path):
    root = _build_pre_flight_root(tmp_path)
    errors = validator.validate_pre_flight("team-todo-comments", root)
    assert errors == [], errors


def test_mode_c_rejected_refactor_passes(tmp_path: Path):
    # Approval status: rejected is a resolved state — should pass.
    root = _build_pre_flight_root(
        tmp_path, refactor_src=REFACTOR_GOLDEN_REJECTED
    )
    errors = validator.validate_pre_flight("team-todo-comments", root)
    assert errors == [], errors


def test_mode_c_decision_needs_more_work_fails(tmp_path: Path):
    root = _build_pre_flight_root(tmp_path)
    test_md = (
        root / "_implementation" / "slices" / "team-todo-comments" / "test.md"
    )
    text = test_md.read_text().replace("Decision: Done", "Decision: Needs more work")
    test_md.write_text(text)
    errors = validator.validate_pre_flight("team-todo-comments", root)
    assert any("Decision: Done" in e for e in errors), errors


def test_mode_c_pending_approval_fails(tmp_path: Path):
    root = _build_pre_flight_root(tmp_path)
    refactor_md = (
        root / "_implementation" / "slices" / "team-todo-comments" / "refactor.md"
    )
    text = refactor_md.read_text().replace(
        "Approval status: approved", "Approval status: pending"
    )
    refactor_md.write_text(text)
    errors = validator.validate_pre_flight("team-todo-comments", root)
    assert any(
        "Approval status: approved|rejected|modified" in e for e in errors
    ), errors


def test_mode_c_missing_handoff_fails(tmp_path: Path):
    root = _build_pre_flight_root(tmp_path)
    (root / "_implementation" / "slices" / "team-todo-comments" / "refactor.md").unlink()
    errors = validator.validate_pre_flight("team-todo-comments", root)
    assert any("missing handoff" in e and "refactor.md" in e for e in errors), errors


def test_mode_c_missing_slice_dir_fails(tmp_path: Path):
    errors = validator.validate_pre_flight("nonexistent-slice", tmp_path)
    assert any("slice dir does not exist" in e for e in errors), errors
