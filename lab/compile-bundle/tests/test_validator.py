"""Tests for validator.py — read-only bundle coverage check."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))


def make_flow(flows_dir: Path, stem: str, skills: list[str]) -> None:
    nodes = [{"id": s, "type": "skill", "data": {"skill": s}} for s in skills]
    (flows_dir / f"{stem}.flow.yaml").write_text(
        yaml.dump({"id": stem, "nodes": nodes, "edges": []}), encoding="utf-8"
    )


def make_bundle(bundles_dir: Path, stem: str, skills: list[str], parents: list[str] | None = None) -> None:
    requires = [f"bundle:{p}" for p in (parents or [])] + [f"skill:{s}" for s in skills]
    (bundles_dir / f"{stem}.bundle.yaml").write_text(
        yaml.dump({"name": stem, "requires": requires or None}), encoding="utf-8"
    )


def run_validator(flows_dir: Path, bundles_dir: Path) -> int:
    """Run validator main() and return the exit code (captured from SystemExit)."""
    import validator as v
    try:
        v.main(flows_dir, bundles_dir)
        return 0
    except SystemExit as e:
        return int(e.code)


def test_passes_when_all_skills_covered(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a", "skill-b"])
    make_bundle(b, "mvp", ["skill-a", "skill-b"])
    assert run_validator(f, b) == 0


def test_fails_when_skill_missing_from_bundle(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a", "skill-b"])
    make_bundle(b, "mvp", ["skill-a"])  # skill-b missing
    assert run_validator(f, b) == 2


def test_passes_when_skill_covered_by_ancestor(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a"])
    make_flow(f, "simple-app", ["skill-a", "skill-b"])
    make_bundle(b, "mvp", ["skill-a"])
    make_bundle(b, "simple-app", ["skill-b"], parents=["mvp"])
    # skill-a is in mvp (ancestor) — simple-app is fully covered
    assert run_validator(f, b) == 0


def test_warns_and_continues_when_no_bundle_for_flow(tmp_path, capsys):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "orphan", ["skill-a"])
    rc = run_validator(f, b)
    captured = capsys.readouterr()
    assert "orphan" in captured.err
    assert rc == 0  # warning only, no gap found


def test_ignores_bundle_with_no_matching_flow(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_bundle(b, "user-bundle", ["skill-a"])  # no matching flow
    assert run_validator(f, b) == 0


def test_exits_1_on_circular_inheritance(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "alpha", ["skill-a"])
    make_bundle(b, "alpha", ["skill-a"], parents=["beta"])
    make_bundle(b, "beta", [], parents=["alpha"])
    assert run_validator(f, b) == 1


def test_exits_1_on_malformed_flow_yaml(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    (f / "bad.flow.yaml").write_text(": bad: yaml: [\n", encoding="utf-8")
    assert run_validator(f, b) == 1
