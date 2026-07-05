"""Tests for impl-slice-test validator --ac cross-check."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
GOLDEN_AC = (
    SKILL_DIR.parent.parent
    / "11_impl-plan"
    / "03_plan-vertical"
    / "examples"
    / "team-todo-comments.ac.md"
)

_spec = importlib.util.spec_from_file_location(
    "impl_slice_test_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def test_validate_ac_updates_accepts_updated_ledger(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace(
        "| untested | - | - |", "| pass | impl-slice-test | 2026-07-05 |", 1
    )
    f = tmp_path / "updated.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = validator.validate_ac_updates(f)
    assert errors == []


def test_validate_ac_updates_rejects_bad_updater(tmp_path: Path):
    text = GOLDEN_AC.read_text(encoding="utf-8").replace(
        "| untested | - | - |", "| pass | someone | 2026-07-05 |", 1
    )
    f = tmp_path / "bad-updater.ac.md"
    f.write_text(text, encoding="utf-8")
    errors = validator.validate_ac_updates(f)
    assert any("Updated by" in e for e in errors)


def test_validate_ac_updates_rejects_structurally_broken(tmp_path: Path):
    f = tmp_path / "broken.ac.md"
    f.write_text("---\nfeature_ref: x\n---\nno table here\n", encoding="utf-8")
    errors = validator.validate_ac_updates(f)
    assert errors  # structural errors from ac_lib bubble up


def test_cli_accepts_ac_flag(tmp_path: Path):
    """--ac wired into the CLI (exit 2 on a broken ledger, error mentions [ac])."""
    ac = tmp_path / "broken.ac.md"
    ac.write_text("---\nfeature_ref: x\n---\nno table\n", encoding="utf-8")
    done = SKILL_DIR / "examples" / "team-todo-comments-test-done.md"
    slug_dir = tmp_path / "team-todo-comments"
    slug_dir.mkdir()
    target = slug_dir / "test.md"
    target.write_text(done.read_text(encoding="utf-8"), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SKILL_DIR / "validator.py"), str(target), "--ac", str(ac)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert "[ac]" in proc.stderr
