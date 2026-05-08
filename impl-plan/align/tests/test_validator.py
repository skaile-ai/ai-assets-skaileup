"""Tests for impl-plan-align validator."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
GOLDEN = SKILL_DIR / "examples" / "team-todo-comments-align.md"

_spec = importlib.util.spec_from_file_location(
    "impl_plan_align_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def write_golden(tmp_path: Path) -> Path:
    """Copy the golden align.md into a slug-named dir under tmp_path."""
    slug_dir = tmp_path / "team-todo-comments"
    slug_dir.mkdir()
    target = slug_dir / "align.md"
    shutil.copy(GOLDEN, target)
    return target


def test_golden_fixture_passes(tmp_path: Path):
    f = write_golden(tmp_path)
    errors = validator.validate(f)
    assert errors == [], errors


def test_missing_ears_in_handoff_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    # Strip every "WHEN ... SHALL ..." line under `## Acceptance handoff`
    out = []
    inside_handoff = False
    for line in text.splitlines():
        if line.strip() == "## Acceptance handoff":
            inside_handoff = True
            out.append(line)
            continue
        if inside_handoff and line.startswith("## "):
            inside_handoff = False
        if inside_handoff and "WHEN" in line.upper() and "SHALL" in line.upper():
            continue
        out.append(line)
    f.write_text("\n".join(out))
    errors = validator.validate(f)
    assert any("no EARS-format line" in e for e in errors), errors


def test_missing_top_section_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text().replace(
        "## Edge cases to handle\n", "## Renamed edge cases\n"
    )
    f.write_text(text)
    errors = validator.validate(f)
    assert any(
        "missing required body section" in e and "Edge cases to handle" in e
        for e in errors
    ), errors


def test_empty_grill_fails(tmp_path: Path):
    """Empty open-questions (no P1/P2) AND empty decisions = fail."""
    f = write_golden(tmp_path)
    text = f.read_text()
    # Remove all P-tagged numbered items from `## Open questions surfaced by the grill`
    out = []
    inside_oq = False
    for line in text.splitlines():
        if line.strip() == "## Open questions surfaced by the grill":
            inside_oq = True
            out.append(line)
            continue
        if inside_oq and line.startswith("## ") and "Open questions" not in line:
            inside_oq = False
        if inside_oq and line.lstrip().startswith(("1.", "2.", "3.", "4.", "5.")):
            continue
        out.append(line)
    text = "\n".join(out)
    # Empty `## Decisions made`
    out2 = []
    inside_dec = False
    for line in text.splitlines():
        if line.strip() == "## Decisions made":
            inside_dec = True
            out2.append(line)
            out2.append("_(none)_")
            continue
        if inside_dec and line.startswith("## ") and "Decisions made" not in line:
            inside_dec = False
        if inside_dec:
            continue
        out2.append(line)
    f.write_text("\n".join(out2))
    errors = validator.validate(f)
    assert any("grill is empty" in e for e in errors), errors


def test_phase_brainstorm_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text().replace("phase: align", "phase: brainstorm")
    f.write_text(text)
    errors = validator.validate(f)
    assert any("phase must be 'align'" in e for e in errors), errors


def test_slice_id_dir_mismatch_fails(tmp_path: Path):
    wrong_dir = tmp_path / "different-slug"
    wrong_dir.mkdir()
    target = wrong_dir / "align.md"
    shutil.copy(GOLDEN, target)
    errors = validator.validate(target)
    assert any("does not match parent dir name" in e for e in errors), errors


def test_missing_feature_path_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    # Drop the `feature_path:` line entirely
    new_lines = [ln for ln in text.splitlines() if not ln.startswith("feature_path:")]
    f.write_text("\n".join(new_lines))
    errors = validator.validate(f)
    assert any(
        "missing frontmatter keys" in e and "feature_path" in e for e in errors
    ), errors
