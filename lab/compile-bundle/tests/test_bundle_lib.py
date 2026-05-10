"""Tests for _bundle_lib.py — data loading and ancestry resolution."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from _bundle_lib import load_bundles, load_flows, resolve_ancestors


# ── Helpers ──────────────────────────────────────────────────────────


def write_flow(flows_dir: Path, stem: str, skills: list[str], optional: list[str] | None = None) -> None:
    nodes = [{"id": s, "type": "skill", "data": {"skill": s}} for s in skills]
    if optional:
        for s in optional:
            nodes.append({"id": s, "type": "skill", "data": {"skill": s}, "optional": True})
    flow = {"id": stem, "name": stem, "nodes": nodes, "edges": []}
    (flows_dir / f"{stem}.flow.yaml").write_text(yaml.dump(flow), encoding="utf-8")


def write_bundle(bundles_dir: Path, stem: str, skills: list[str], parents: list[str] | None = None) -> None:
    requires = [f"bundle:{p}" for p in (parents or [])] + [f"skill:{s}" for s in skills]
    data = {"name": stem, "requires": requires or None}
    (bundles_dir / f"{stem}.bundle.yaml").write_text(yaml.dump(data), encoding="utf-8")


# ── load_flows ────────────────────────────────────────────────────────


def test_load_flows_extracts_skills_in_document_order(tmp_path):
    d = tmp_path / "flows"
    d.mkdir()
    write_flow(d, "mvp", ["skill-a", "skill-b", "skill-c"])
    result = load_flows(d)
    assert result["mvp"] == ["skill-a", "skill-b", "skill-c"]


def test_load_flows_includes_optional_nodes(tmp_path):
    d = tmp_path / "flows"
    d.mkdir()
    write_flow(d, "mvp", ["skill-a"], optional=["skill-opt"])
    result = load_flows(d)
    assert "skill-opt" in result["mvp"]


def test_load_flows_skips_non_skill_type_nodes(tmp_path):
    d = tmp_path / "flows"
    d.mkdir()
    nodes = [
        {"id": "s", "type": "skill", "data": {"skill": "my-skill"}},
        {"id": "g", "type": "group", "data": {"label": "group-label"}},
    ]
    (d / "mvp.flow.yaml").write_text(yaml.dump({"id": "mvp", "nodes": nodes, "edges": []}))
    result = load_flows(d)
    assert result["mvp"] == ["my-skill"]


def test_load_flows_stem_strips_flow_yaml_suffix(tmp_path):
    d = tmp_path / "flows"
    d.mkdir()
    write_flow(d, "standard-app", ["s"])
    result = load_flows(d)
    assert "standard-app" in result


def test_load_flows_deduplicates_duplicate_skill_nodes(tmp_path):
    d = tmp_path / "flows"
    d.mkdir()
    # Two nodes with the same skill name — should appear once in result
    nodes = [
        {"id": "a1", "type": "skill", "data": {"skill": "skill-a"}},
        {"id": "a2", "type": "skill", "data": {"skill": "skill-a"}},
        {"id": "b1", "type": "skill", "data": {"skill": "skill-b"}},
    ]
    (d / "mvp.flow.yaml").write_text(
        yaml.dump({"id": "mvp", "nodes": nodes, "edges": []}), encoding="utf-8"
    )
    result = load_flows(d)
    assert result["mvp"] == ["skill-a", "skill-b"]  # skill-a appears once


# ── load_bundles ──────────────────────────────────────────────────────


def test_load_bundles_splits_refs_correctly(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "simple-app", ["skill-a", "skill-b"], parents=["mvp"])
    result = load_bundles(d)
    b = result["simple-app"]
    assert b["bundle_refs"] == ["mvp"]
    assert b["skill_refs"] == ["skill-a", "skill-b"]
    assert b["other_refs"] == []


def test_load_bundles_absent_requires_treated_as_empty(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    (d / "empty.bundle.yaml").write_text("name: empty\n", encoding="utf-8")
    result = load_bundles(d)
    assert result["empty"]["skill_refs"] == []
    assert result["empty"]["bundle_refs"] == []


def test_load_bundles_stem_strips_bundle_yaml_suffix(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "standard-app", ["s"])
    result = load_bundles(d)
    assert "standard-app" in result


def test_load_bundles_preserves_raw_text(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    text = "name: mvp\ndescription: my bundle\nrequires:\n  - skill:abc\n"
    (d / "mvp.bundle.yaml").write_text(text, encoding="utf-8")
    result = load_bundles(d)
    assert result["mvp"]["raw_text"] == text


# ── resolve_ancestors ─────────────────────────────────────────────────


def test_resolve_ancestors_leaf_has_no_ancestors(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "mvp", ["skill-a", "skill-b"])
    bundles = load_bundles(d)
    assert resolve_ancestors("mvp", bundles) == set()


def test_resolve_ancestors_single_level(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "mvp", ["skill-a"])
    write_bundle(d, "simple-app", ["skill-b"], parents=["mvp"])
    bundles = load_bundles(d)
    assert resolve_ancestors("simple-app", bundles) == {"skill-a"}


def test_resolve_ancestors_multi_level(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "mvp", ["skill-a"])
    write_bundle(d, "simple-app", ["skill-b"], parents=["mvp"])
    write_bundle(d, "standard-app", ["skill-c"], parents=["simple-app"])
    bundles = load_bundles(d)
    # standard-app sees skill-a (from mvp) and skill-b (from simple-app)
    assert resolve_ancestors("standard-app", bundles) == {"skill-a", "skill-b"}


def test_resolve_ancestors_cycle_raises_with_path(tmp_path):
    d = tmp_path / "bundles"
    d.mkdir()
    write_bundle(d, "a", [], parents=["b"])
    write_bundle(d, "b", [], parents=["a"])
    bundles = load_bundles(d)
    with pytest.raises(ValueError, match="Circular"):
        resolve_ancestors("a", bundles)
