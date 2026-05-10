"""Tests for validator.py — read-only bundle coverage check."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── helpers for co-located layout ─────────────────────────────────────
# Flows and bundles now live together: flows_dir/<app>/<app>.flow.yaml
#                                       flows_dir/<app>/<app>.bundle.yaml


def make_flow(flows_dir: Path, stem: str, skills: list[str]) -> None:
    nodes = [{"id": s, "type": "skill", "data": {"skill": s}} for s in skills]
    app_dir = flows_dir / stem
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / f"{stem}.flow.yaml").write_text(
        yaml.dump({"id": stem, "nodes": nodes, "edges": []}), encoding="utf-8"
    )


def make_bundle(flows_dir: Path, stem: str, skills: list[str], parents: list[str] | None = None) -> None:
    requires = [f"bundle:{p}" for p in (parents or [])] + [f"skill:{s}" for s in skills]
    app_dir = flows_dir / stem
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / f"{stem}.bundle.yaml").write_text(
        yaml.dump({"name": stem, "requires": requires or None}), encoding="utf-8"
    )


def run_validator(flows_dir: Path) -> int:
    """Run validator main() and return the exit code (captured from SystemExit)."""
    import validator as v
    try:
        v.main(flows_dir)
        return 0
    except SystemExit as e:
        return int(e.code)


def test_passes_when_all_skills_covered(tmp_path):
    f = tmp_path / "flows"
    f.mkdir()
    make_flow(f, "mvp", ["skill-a", "skill-b"])
    make_bundle(f, "mvp", ["skill-a", "skill-b"])
    assert run_validator(f) == 0


def test_fails_when_skill_missing_from_bundle(tmp_path):
    f = tmp_path / "flows"
    f.mkdir()
    make_flow(f, "mvp", ["skill-a", "skill-b"])
    make_bundle(f, "mvp", ["skill-a"])  # skill-b missing
    assert run_validator(f) == 2


def test_passes_when_skill_covered_by_ancestor(tmp_path):
    f = tmp_path / "flows"
    f.mkdir()
    make_flow(f, "mvp", ["skill-a"])
    make_flow(f, "simple-app", ["skill-a", "skill-b"])
    make_bundle(f, "mvp", ["skill-a"])
    make_bundle(f, "simple-app", ["skill-b"], parents=["mvp"])
    # skill-a is in mvp (ancestor) — simple-app is fully covered
    assert run_validator(f) == 0


def test_warns_and_continues_when_no_bundle_for_flow(tmp_path, capsys):
    f = tmp_path / "flows"
    f.mkdir()
    make_flow(f, "orphan", ["skill-a"])
    rc = run_validator(f)
    captured = capsys.readouterr()
    assert "orphan" in captured.err
    assert rc == 0  # warning only, no gap found


def test_ignores_bundle_with_no_matching_flow(tmp_path):
    f = tmp_path / "flows"
    f.mkdir()
    make_bundle(f, "user-bundle", ["skill-a"])  # no matching flow
    assert run_validator(f) == 0


def test_exits_1_on_circular_inheritance(tmp_path):
    f = tmp_path / "flows"
    f.mkdir()
    make_flow(f, "alpha", ["skill-a"])
    make_bundle(f, "alpha", ["skill-a"], parents=["beta"])
    make_bundle(f, "beta", [], parents=["alpha"])
    assert run_validator(f) == 1


def test_exits_1_on_malformed_flow_yaml(tmp_path):
    f = tmp_path / "flows"
    f.mkdir()
    app_dir = f / "bad"
    app_dir.mkdir()
    (app_dir / "bad.flow.yaml").write_text(": bad: yaml: [\n", encoding="utf-8")
    assert run_validator(f) == 1
