"""Tests for impl-slice-refactor validator."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
GOLDEN_APPROVED = SKILL_DIR / "examples" / "team-todo-comments-refactor.md"
GOLDEN_REJECTED = SKILL_DIR / "examples" / "team-todo-comments-refactor-rejected.md"

_spec = importlib.util.spec_from_file_location(
    "impl_slice_refactor_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def write_to_slug_dir(tmp_path: Path, golden: Path) -> Path:
    slug_dir = tmp_path / "team-todo-comments"
    slug_dir.mkdir()
    target = slug_dir / "refactor.md"
    shutil.copy(golden, target)
    return target


def test_golden_approved_passes(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_APPROVED)
    errors, _ = validator.validate(f)
    assert errors == [], errors


def test_golden_rejected_passes(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_REJECTED)
    errors, _ = validator.validate(f)
    assert errors == [], errors


def test_four_candidates_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_APPROVED)
    text = f.read_text()
    extra_candidate = (
        "\n### 3. Drop unused import\n"
        "**Type:** subtraction\n"
        "**Files:** src/components/CommentList.tsx\n"
        "**Rationale:** unused import.\n"
        "**Risk:** low — pure deletion.\n"
        "**Behavior preservation:** no behavior to preserve.\n\n"
        "### 4. Another candidate\n"
        "**Type:** subtraction\n"
        "**Files:** src/components/CommentList.tsx\n"
        "**Rationale:** another reason.\n"
        "**Risk:** low — pure deletion.\n"
        "**Behavior preservation:** no behavior to preserve.\n"
    )
    text = text.replace(
        "## What I considered but rejected (1-3 items)",
        extra_candidate + "\n## What I considered but rejected (1-3 items)",
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "Smallest improvement candidates" in e and "≤ 3 items" in e
        for e in errors
    ), errors


def test_addition_type_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_APPROVED)
    text = f.read_text().replace(
        "**Type:** subtraction",
        "**Type:** addition",
        1,
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        ("addition" in e or "must be one of" in e) for e in errors
    ), errors


def test_missing_behavior_preservation_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_APPROVED)
    text = f.read_text()
    # Strip the first candidate's Behavior preservation line.
    text = text.replace(
        "**Behavior preservation:** no behavior to preserve — it's dead code. Test suite passes unchanged.",
        "",
        1,
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "Behavior preservation" in e and "missing" in e for e in errors
    ), errors


def test_empty_rejected_section_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_APPROVED)
    text = f.read_text()
    # Replace the rejected section's body with a "_(none)_" placeholder.
    text = text.replace(
        "## What I considered but rejected (1-3 items)\n\n"
        "1. Considered: extract a `<CommentItem>` presentational component out of `<CommentList>`. "
        "Rejected: only one caller; not yet a pattern, and the inline JSX is 6 lines.\n"
        "2. Considered: extract `formatTimestamp()` utility used by `CommentItem` and "
        "`TodoDetailPanel`. Rejected: the two call sites format slightly differently — "
        "extracting now would force a premature unification.\n",
        "## What I considered but rejected (1-3 items)\n\n_(none)_\n",
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "What I considered but rejected" in e and "≥ 1 numbered item" in e
        for e in errors
    ), errors


def test_approved_with_pending_applied_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_APPROVED)
    text = f.read_text()
    # Replace the actual Applied-changes body with the pending placeholder.
    text = text.replace(
        "## Applied changes\n"
        "- src/components/CommentList.tsx — removed `formatComment()` helper (1 hunk, -4 lines).\n"
        "- src/components/CommentComposer.tsx — renamed `handle` → `submitComment` "
        "(1 hunk, 2 references updated).\n",
        "## Applied changes\n_(none — approval pending)_\n",
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "approved" in e and "Applied changes" in e for e in errors
    ), errors


def test_rejected_with_wrong_applied_body_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_REJECTED)
    text = f.read_text().replace(
        "_(none — user declined refactor)_",
        "Some accidental edit notes here",
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "rejected" in e and "Applied changes" in e for e in errors
    ), errors


def test_phase_recap_fails(tmp_path: Path):
    f = write_to_slug_dir(tmp_path, GOLDEN_APPROVED)
    text = f.read_text().replace("phase: refactor", "phase: recap")
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any("phase must be 'refactor'" in e for e in errors), errors
