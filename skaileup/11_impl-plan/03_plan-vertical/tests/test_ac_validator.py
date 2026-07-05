"""Tests for the acceptance-criteria ledger validation (ac_lib via plan-vertical)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
REPO = SKILL_DIR.parent.parent.parent  # repo root
GOLDEN_AC = SKILL_DIR / "examples" / "team-todo-comments.ac.md"

sys.path.insert(0, str(REPO / "skaileup" / "contracts" / "scripts"))
import ac_lib  # noqa: E402


def test_golden_ac_passes_initial():
    errors = ac_lib.validate_ac_file(GOLDEN_AC, require_untested=True)
    assert errors == []


def test_missing_status_table_fails(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8")
    broken = text.split("## Criteria Status")[0]
    f = tmp_path / "broken.ac.md"
    f.write_text(broken, encoding="utf-8")
    errors = ac_lib.validate_ac_file(f)
    assert any("Criteria Status" in e for e in errors)


def test_bad_status_enum_fails(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace("| untested |", "| maybe |", 1)
    f = tmp_path / "bad.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = ac_lib.validate_ac_file(f)
    assert any("status" in e.lower() for e in errors)


def test_pass_row_rejected_when_initial(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace(
        "| untested | - | - |", "| pass | impl-slice-test | 2026-07-05 |", 1
    )
    f = tmp_path / "not-initial.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = ac_lib.validate_ac_file(f, require_untested=True)
    assert any("untested" in e for e in errors)


def test_row_id_without_section_fails(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace(
        "| AC-2 |", "| AC-9 |", 1
    )
    f = tmp_path / "dangling-row.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = ac_lib.validate_ac_file(f)
    assert any("AC-9" in e for e in errors)


def test_missing_frontmatter_key_fails(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace("story_refs:", "story_refsX:", 1)
    f = tmp_path / "no-story-refs.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = ac_lib.validate_ac_file(f)
    assert any("story_refs" in e for e in errors)
