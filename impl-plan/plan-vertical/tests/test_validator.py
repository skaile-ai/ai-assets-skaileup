"""Tests for impl-plan-plan-vertical validator."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
GOLDEN = SKILL_DIR / "examples" / "team-todo-comments-plan.md"

_spec = importlib.util.spec_from_file_location(
    "impl_plan_plan_vertical_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def write_golden(tmp_path: Path) -> Path:
    """Copy the golden plan.md into a slug-named dir under tmp_path."""
    slug_dir = tmp_path / "team-todo-comments"
    slug_dir.mkdir()
    target = slug_dir / "plan.md"
    shutil.copy(GOLDEN, target)
    return target


def test_golden_fixture_passes(tmp_path: Path):
    f = write_golden(tmp_path)
    errors, warnings = validator.validate(f)
    assert errors == [], errors
    # Golden fixture has no empty cells, so no warnings expected.
    assert warnings == [], warnings


def test_missing_top_section_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text().replace(
        "## Open carry-overs\n", "## Renamed carry-overs\n"
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "missing required body section" in e and "Open carry-overs" in e
        for e in errors
    ), errors


def test_anti_horizontal_nudge_altered_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    # Soften "DO NOT" to "Try not to" in the nudge body.
    text = text.replace(
        "**DO NOT build all UI first",
        "**Try not to build all UI first",
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any("Anti-horizontal nudge" in e and "verbatim" in e for e in errors), errors


def test_dod_missing_required_item_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    # Remove the "All vertical rows complete end-to-end" DoD item line.
    target_line = "- [ ] All vertical rows complete end-to-end (UI + Logic + Data wired)"
    text = text.replace(target_line + "\n", "")
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "Definition of done" in e and "missing required item" in e
        for e in errors
    ), errors


def test_decomposition_table_absent_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    # Strip the entire decomposition table — keep header but drop body lines.
    out = []
    inside = False
    for line in text.splitlines():
        if line.strip() == "## Vertical decomposition":
            inside = True
            out.append(line)
            continue
        if inside and line.startswith("## ") and line.strip() != "## Vertical decomposition":
            inside = False
        if inside and line.strip().startswith("|"):
            continue
        out.append(line)
    f.write_text("\n".join(out))
    errors, _ = validator.validate(f)
    assert any(
        "Vertical decomposition" in e and "markdown table" in e
        for e in errors
    ), errors


def test_empty_data_cell_emits_warning(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    # Replace one row's Data cell with `-`.
    text = text.replace(
        "`comments` table read; FK→`todos`",
        "-",
    )
    f.write_text(text)
    errors, warnings = validator.validate(f)
    # Validator returns 0 (no error) but warnings list is non-empty.
    assert errors == [], errors
    assert any(
        "row 1" in w and "'Data'" in w for w in warnings
    ), warnings


def test_no_test_tags_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    # Remove all [unit]/[integration]/[e2e] tags
    text = (
        text.replace("[unit]", "")
        .replace("[integration]", "")
        .replace("[e2e]", "")
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any("Automated tests" in e and "tagged" in e for e in errors), errors


def test_phase_align_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text().replace("phase: plan", "phase: align")
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any("phase must be 'plan'" in e for e in errors), errors


def test_slice_id_dir_mismatch_fails(tmp_path: Path):
    wrong_dir = tmp_path / "different-slug"
    wrong_dir.mkdir()
    target = wrong_dir / "plan.md"
    shutil.copy(GOLDEN, target)
    errors, _ = validator.validate(target)
    assert any("does not match parent dir name" in e for e in errors), errors
