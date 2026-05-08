"""Tests for impl-slice-recap validator."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
GOLDEN = SKILL_DIR / "examples" / "team-todo-comments-recap.md"

_spec = importlib.util.spec_from_file_location(
    "impl_slice_recap_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def write_golden(tmp_path: Path) -> Path:
    slug_dir = tmp_path / "team-todo-comments"
    slug_dir.mkdir()
    target = slug_dir / "recap.md"
    shutil.copy(GOLDEN, target)
    return target


def test_golden_passes(tmp_path: Path):
    f = write_golden(tmp_path)
    errors, _ = validator.validate(f)
    assert errors == [], errors


def test_missing_ascii_diagram_section_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text().replace("## ASCII diagram\n", "## Renamed Diagram\n")
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "missing required body section" in e and "ASCII diagram" in e
        for e in errors
    ), errors


def test_diagram_section_without_fenced_block_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    # Replace the entire diagram fenced block with prose only.
    text = (
        text.split("## ASCII diagram")[0]
        + "## ASCII diagram\n\nA diagram describing the flow goes here.\n\n## Files touched\n"
        + text.split("## Files touched\n", 1)[1]
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "ASCII diagram" in e and "fenced code block" in e for e in errors
    ), errors


def test_fenced_block_too_short_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    short_diagram = (
        "## ASCII diagram\n\n"
        "```\n"
        "+--+\n"
        "|A|\n"
        "+--+\n"
        "```\n\n"
        "## Files touched\n"
    )
    text = (
        text.split("## ASCII diagram")[0]
        + short_diagram
        + text.split("## Files touched\n", 1)[1]
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "ASCII diagram" in e and "≥ 5 non-empty lines" in e for e in errors
    ), errors


def test_fenced_block_no_diagram_chars_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    paragraph_block = (
        "## ASCII diagram\n\n"
        "```\n"
        "Line one of plain text\n"
        "Line two of plain text\n"
        "Line three of plain text\n"
        "Line four of plain text\n"
        "Line five of plain text\n"
        "Line six of plain text\n"
        "```\n\n"
        "## Files touched\n"
    )
    text = (
        text.split("## ASCII diagram")[0]
        + paragraph_block
        + text.split("## Files touched\n", 1)[1]
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "ASCII diagram" in e and "diagram char" in e for e in errors
    ), errors


def test_what_was_built_too_long_warns(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    # Replace the "What was built" body with 5 sentences.
    long_text = (
        "## What was built (1-3 sentences)\n"
        "First sentence here. Second sentence here. Third sentence here. "
        "Fourth sentence here. Fifth sentence here.\n\n"
        "## ASCII diagram"
    )
    text = (
        text.split("## What was built (1-3 sentences)")[0]
        + long_text
        + text.split("## ASCII diagram", 1)[1]
    )
    f.write_text(text)
    errors, warnings = validator.validate(f)
    assert errors == [], errors
    assert any(
        "What was built" in w and "sentences" in w for w in warnings
    ), warnings


def test_files_touched_empty_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text()
    # Replace the entire Files touched section with no bullets.
    empty_ft = "## Files touched\n\n_(none — recap requires at least one)_\n\n## Outcome vs. plan\n"
    text = (
        text.split("## Files touched")[0]
        + empty_ft
        + text.split("## Outcome vs. plan\n", 1)[1]
    )
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any(
        "Files touched" in e and "≥ 1 bullet" in e for e in errors
    ), errors


def test_phase_test_in_frontmatter_fails(tmp_path: Path):
    f = write_golden(tmp_path)
    text = f.read_text().replace("phase: recap", "phase: test")
    f.write_text(text)
    errors, _ = validator.validate(f)
    assert any("phase must be 'recap'" in e for e in errors), errors
