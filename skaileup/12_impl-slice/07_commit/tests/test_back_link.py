"""Tests for impl-slice-commit validator Mode D (--back-link)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent

_spec = importlib.util.spec_from_file_location(
    "impl_slice_commit_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)

GOOD_FEATURE = """\
---
priority: must-have
roles: [all_users]
story_refs: [onboarding_flow]
screens:
  - path: experience/screens/01_user_auth/login.md
data_entities: [User]
slice_ref: _implementation/slices/login/
commits: [abc1234, deadbeef1234567]
source_files:
  - src/routes/login.ts
  - src/components/LoginForm.tsx
last_updated: 2026-07-05
---

# Login
"""


def make_slice_dir(tmp_path: Path, slice_id: str = "login", frozen: bool = True) -> Path:
    d = tmp_path / "_implementation" / "slices" / slice_id
    d.mkdir(parents=True)
    if frozen:
        (d / "index.md").write_text(
            "---\nslice_id: login\nphase: frozen\nstatus: shipped\n"
            "commits: [abc1234, deadbeef1234567]\nlast_updated: 2026-07-05\n---\n",
            encoding="utf-8",
        )
    return d


def write_feature(tmp_path: Path, text: str) -> Path:
    fdir = tmp_path / "_concept" / "experience" / "features" / "01_user_auth"
    fdir.mkdir(parents=True)
    f = fdir / "login.md"
    f.write_text(text, encoding="utf-8")
    return f


def test_good_back_link_passes(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path)
    feature = write_feature(tmp_path, GOOD_FEATURE)
    errors = validator.validate_back_link(feature, slice_dir)
    assert errors == []


def test_missing_slice_ref_fails(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path)
    feature = write_feature(
        tmp_path, GOOD_FEATURE.replace("slice_ref: _implementation/slices/login/\n", "")
    )
    errors = validator.validate_back_link(feature, slice_dir)
    assert any("slice_ref" in e for e in errors)


def test_empty_commits_fails(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path)
    feature = write_feature(
        tmp_path, GOOD_FEATURE.replace("commits: [abc1234, deadbeef1234567]", "commits: []")
    )
    errors = validator.validate_back_link(feature, slice_dir)
    assert any("commits" in e for e in errors)


def test_non_sha_commit_fails(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path)
    feature = write_feature(
        tmp_path,
        GOOD_FEATURE.replace("commits: [abc1234, deadbeef1234567]", "commits: [not-a-sha!]"),
    )
    errors = validator.validate_back_link(feature, slice_dir)
    assert any("SHA" in e for e in errors)


def test_empty_source_files_fails(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path)
    feature = write_feature(
        tmp_path,
        GOOD_FEATURE.replace(
            "source_files:\n  - src/routes/login.ts\n  - src/components/LoginForm.tsx\n",
            "source_files: []\n",
        ),
    )
    errors = validator.validate_back_link(feature, slice_dir)
    assert any("source_files" in e for e in errors)


def test_unfrozen_slice_fails(tmp_path: Path):
    slice_dir = make_slice_dir(tmp_path, frozen=False)
    feature = write_feature(tmp_path, GOOD_FEATURE)
    errors = validator.validate_back_link(feature, slice_dir)
    assert any("index.md" in e for e in errors)
