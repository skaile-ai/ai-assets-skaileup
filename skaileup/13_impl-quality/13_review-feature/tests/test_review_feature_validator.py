"""Tests for the impl-quality-review-feature validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
APPROVE = THIS_DIR / "fixtures" / "review_approve.yaml"

_spec = importlib.util.spec_from_file_location(
    "review_feature_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def mutate(tmp_path: Path, transform) -> Path:
    data = yaml.safe_load(APPROVE.read_text(encoding="utf-8"))
    transform(data)
    f = tmp_path / "review.yaml"
    f.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return f


def test_approve_fixture_passes():
    assert validator.validate(APPROVE) == []


def test_missing_key_fails(tmp_path: Path):
    f = mutate(tmp_path, lambda d: d.pop("verdict"))
    assert any("verdict" in e for e in validator.validate(f))


def test_bad_severity_fails(tmp_path: Path):
    def t(d):
        d["findings"][0]["severity"] = "urgent"
    f = mutate(tmp_path, t)
    assert any("severity" in e for e in validator.validate(f))


def test_approve_with_high_finding_fails(tmp_path: Path):
    def t(d):
        d["findings"][0]["severity"] = "high"
        d["counts"] = {"critical": 0, "high": 1, "medium": 0, "low": 0}
        # verdict left approve — inconsistent on purpose
    f = mutate(tmp_path, t)
    assert any("approve" in e for e in validator.validate(f))


def test_counts_mismatch_fails(tmp_path: Path):
    def t(d):
        d["counts"] = {"critical": 3, "high": 0, "medium": 0, "low": 1}
    f = mutate(tmp_path, t)
    assert any("counts" in e for e in validator.validate(f))


def test_finding_missing_location_fails(tmp_path: Path):
    def t(d):
        d["findings"][0].pop("line")
    f = mutate(tmp_path, t)
    assert any("line" in e for e in validator.validate(f))
