"""Tests for the ops-trace validator (trace.yaml schema)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

THIS_DIR = Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
GREEN = THIS_DIR / "fixtures" / "trace_green.yaml"

_spec = importlib.util.spec_from_file_location(
    "ops_trace_validator", SKILL_DIR / "validator.py"
)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def mutate(tmp_path: Path, transform) -> Path:
    data = yaml.safe_load(GREEN.read_text(encoding="utf-8"))
    transform(data)
    f = tmp_path / "trace.yaml"
    f.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return f


def test_green_fixture_passes():
    assert validator.validate(GREEN) == []


def test_missing_top_key_fails(tmp_path: Path):
    f = mutate(tmp_path, lambda d: d.pop("summary"))
    assert any("summary" in e for e in validator.validate(f))


def test_bad_status_enum_fails(tmp_path: Path):
    def t(d):
        d["features"][0]["status"] = "blue"
    f = mutate(tmp_path, t)
    assert any("status" in e for e in validator.validate(f))


def test_overall_green_with_red_rows_fails(tmp_path: Path):
    def t(d):
        d["features"][0]["status"] = "red"
        d["summary"]["red"] = 1
        d["summary"]["green"] = d["summary"]["green"] - 1
        # overall left green — inconsistent on purpose
    f = mutate(tmp_path, t)
    assert any("overall" in e for e in validator.validate(f))


def test_summary_count_mismatch_fails(tmp_path: Path):
    def t(d):
        d["summary"]["features_total"] = 99
    f = mutate(tmp_path, t)
    assert any("features_total" in e for e in validator.validate(f))


def test_bad_verdict_enum_fails(tmp_path: Path):
    def t(d):
        d["features"][0]["eval_verdict"] = "maybe"
    f = mutate(tmp_path, t)
    assert any("eval_verdict" in e for e in validator.validate(f))
