"""Tests for concept-slice-design-feature validator."""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent

_spec = importlib.util.spec_from_file_location(
    "concept_slice_design_feature_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)

EXAMPLE_DIR = SKILL_DIR / "examples" / "team-todo-comments"
EXPECTED_OUTPUT = EXAMPLE_DIR / "expected_output"
MANIFEST = EXAMPLE_DIR / "manifest.json"


def test_example_feature_md_passes():
    path = EXPECTED_OUTPUT / "product-spec/features/team-todo/team-todo-comments.md"
    errors = validator.validate_feature_md(path)
    assert errors == [], errors


def test_example_screen_list_md_passes():
    path = EXPECTED_OUTPUT / "experience/screens/team-todo-comments/list.md"
    errors = validator.validate_screen_md(path, feature_slug="team-todo-comments")
    assert errors == [], errors


def test_example_screen_detail_md_passes():
    path = EXPECTED_OUTPUT / "experience/screens/team-todo-comments/detail.md"
    errors = validator.validate_screen_md(path, feature_slug="team-todo-comments")
    assert errors == [], errors


def test_example_manifest_passes():
    errors = validator.validate_manifest(MANIFEST)
    assert errors == [], errors


def test_feature_md_with_empty_screens_fails(tmp_path: Path):
    src = EXPECTED_OUTPUT / "product-spec/features/team-todo/team-todo-comments.md"
    text = src.read_text()
    text = text.replace(
        "screens:\n  - path: experience/screens/team-todo-comments/list.md\n  - path: experience/screens/team-todo-comments/detail.md",
        "screens: []",
    )
    bad = tmp_path / "team-todo-comments.md"
    bad.write_text(text)
    errors = validator.validate_feature_md(bad)
    assert any("non-empty list" in e for e in errors), errors


def test_screen_under_wrong_feature_dir_fails(tmp_path: Path):
    """A screen file at wrong-feature/login.md fails when feature_slug=team-todo-comments."""
    wrong_dir = tmp_path / "wrong-feature"
    wrong_dir.mkdir()
    src = EXPECTED_OUTPUT / "experience/screens/team-todo-comments/list.md"
    bad = wrong_dir / "login.md"
    bad.write_text(src.read_text())
    errors = validator.validate_screen_md(bad, feature_slug="team-todo-comments")
    assert any("path-segment rule violated" in e for e in errors), errors


def test_manifest_missing_walkthrough_fails(tmp_path: Path):
    """Build a tmp manifest dir that omits the walkthrough stub."""
    base = tmp_path / "ex"
    base.mkdir()
    # Copy expected_output structure minus walkthrough
    for rel in [
        "expected_output/product-spec/features/team-todo/team-todo-comments.md",
        "expected_output/experience/screens/team-todo-comments/list.md",
        "expected_output/experience/screens/team-todo-comments/detail.md",
    ]:
        dst = base / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(EXPECTED_OUTPUT / Path(rel).relative_to("expected_output"), dst)
    manifest = {
        "feature_slug": "team-todo-comments",
        "feature_group": "team-todo",
        "tier": "standard-app",
        "files": [
            "expected_output/product-spec/features/team-todo/team-todo-comments.md",
            "expected_output/experience/screens/team-todo-comments/list.md",
            "expected_output/experience/screens/team-todo-comments/detail.md",
        ],
    }
    mf = base / "manifest.json"
    mf.write_text(json.dumps(manifest))
    errors = validator.validate_manifest(mf)
    assert any("walkthrough stub" in e for e in errors), errors


def test_feature_md_missing_acceptance_section_fails(tmp_path: Path):
    src = EXPECTED_OUTPUT / "product-spec/features/team-todo/team-todo-comments.md"
    text = src.read_text().replace("## Acceptance Criteria", "## Criteria")
    bad = tmp_path / "team-todo-comments.md"
    bad.write_text(text)
    errors = validator.validate_feature_md(bad)
    assert any("Acceptance Criteria" in e for e in errors), errors


def test_manifest_wrong_tier_walkthrough_ext_fails(tmp_path: Path):
    """Walkthrough has .astro extension but manifest.tier=simple-app expects .html."""
    base = tmp_path / "ex"
    base.mkdir()
    # Copy expected files into base
    for rel in [
        "expected_output/product-spec/features/team-todo/team-todo-comments.md",
        "expected_output/experience/screens/team-todo-comments/list.md",
        "expected_output/experience/screens/team-todo-comments/detail.md",
        "expected_output/walkthrough-mockup/standard-app/team-todo-comments.astro",
    ]:
        dst = base / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(EXPECTED_OUTPUT / Path(rel).relative_to("expected_output"), dst)
    # Move walkthrough into a `simple-app/` dir but keep `.astro` ext to trigger mismatch
    src_wt = base / "expected_output/walkthrough-mockup/standard-app/team-todo-comments.astro"
    dst_wt = base / "expected_output/walkthrough-mockup/simple-app/team-todo-comments.astro"
    dst_wt.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src_wt, dst_wt)
    manifest = {
        "feature_slug": "team-todo-comments",
        "feature_group": "team-todo",
        "tier": "simple-app",
        "files": [
            "expected_output/product-spec/features/team-todo/team-todo-comments.md",
            "expected_output/experience/screens/team-todo-comments/list.md",
            "expected_output/experience/screens/team-todo-comments/detail.md",
            "expected_output/walkthrough-mockup/simple-app/team-todo-comments.astro",
        ],
    }
    mf = base / "manifest.json"
    mf.write_text(json.dumps(manifest))
    errors = validator.validate_manifest(mf)
    assert any("extension mismatch" in e for e in errors), errors
