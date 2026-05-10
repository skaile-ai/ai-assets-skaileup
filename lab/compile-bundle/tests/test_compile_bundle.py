"""Tests for compile_bundle.py — skill insertion logic and main integration."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from compile_bundle import insert_skills, main as compile_main


# ── insert_skills ─────────────────────────────────────────────────────


def test_insert_after_last_skill_line():
    raw = "requires:\n  - skill:skill-a\n  - skill:skill-b\n"
    result = insert_skills(raw, ["skill-c"])
    lines = result.splitlines()
    assert lines == ["requires:", "  - skill:skill-a", "  - skill:skill-b", "  - skill:skill-c"]


def test_insert_before_first_bundle_line_when_no_skills():
    raw = "requires:\n  - bundle:mvp\n"
    result = insert_skills(raw, ["skill-x"])
    lines = result.splitlines()
    assert lines == ["requires:", "  - skill:skill-x", "  - bundle:mvp"]


def test_insert_after_requires_key_when_list_is_empty():
    raw = "requires:\n"
    result = insert_skills(raw, ["skill-x"])
    lines = result.splitlines()
    assert lines == ["requires:", "  - skill:skill-x"]


def test_insert_preserves_other_fields():
    raw = "name: test\ndescription: foo\nrequires:\n  - skill:a\n"
    result = insert_skills(raw, ["skill-b"])
    assert "name: test" in result
    assert "description: foo" in result
    assert "  - skill:skill-b" in result


def test_insert_multiple_missing_in_flow_order():
    raw = "requires:\n  - skill:a\n"
    result = insert_skills(raw, ["skill-b", "skill-c"])
    lines = result.splitlines()
    assert lines.index("  - skill:skill-b") < lines.index("  - skill:skill-c")


def test_insert_format_has_no_space_after_colon():
    raw = "requires:\n"
    result = insert_skills(raw, ["my-skill"])
    assert "  - skill:my-skill\n" in result


# ── main (integration) ────────────────────────────────────────────────


def make_flow(flows_dir: Path, stem: str, skills: list[str]) -> None:
    nodes = [{"id": s, "type": "skill", "data": {"skill": s}} for s in skills]
    (flows_dir / f"{stem}.flow.yaml").write_text(
        yaml.dump({"id": stem, "nodes": nodes, "edges": []}), encoding="utf-8"
    )


def make_bundle(bundles_dir: Path, stem: str, content: str) -> Path:
    p = bundles_dir / f"{stem}.bundle.yaml"
    p.write_text(content, encoding="utf-8")
    return p


def run_main(flows_dir: Path, bundles_dir: Path) -> None:
    compile_main(flows_dir, bundles_dir)


def test_adds_missing_skill(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a", "skill-b"])
    make_bundle(b, "mvp", "name: mvp\nrequires:\n  - skill:skill-a\n")
    run_main(f, b)
    content = (b / "mvp.bundle.yaml").read_text()
    assert "skill:skill-b" in content
    assert "skill:skill-a" in content  # original preserved


def test_noop_when_bundle_is_already_complete(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a"])
    original = "name: mvp\nrequires:\n  - skill:skill-a\n"
    make_bundle(b, "mvp", original)
    run_main(f, b)
    assert (b / "mvp.bundle.yaml").read_text() == original


def test_skips_skills_covered_by_ancestor(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a"])
    make_flow(f, "simple-app", ["skill-a", "skill-b"])  # skill-a inherited from mvp
    make_bundle(b, "mvp", "name: mvp\nrequires:\n  - skill:skill-a\n")
    make_bundle(b, "simple-app", "name: simple-app\nrequires:\n  - bundle:mvp\n")
    run_main(f, b)
    content = (b / "simple-app.bundle.yaml").read_text()
    assert "skill:skill-b" in content
    # skill-a is covered by mvp ancestor — must NOT be duplicated
    assert content.count("skill-a") == 0


def test_preserves_user_added_skill_not_in_flow(tmp_path):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "mvp", ["skill-a"])
    make_bundle(b, "mvp", "name: mvp\nrequires:\n  - skill:skill-a\n  - skill:my-custom-tool\n")
    run_main(f, b)
    content = (b / "mvp.bundle.yaml").read_text()
    assert "my-custom-tool" in content


def test_warns_but_continues_when_no_bundle_for_flow(tmp_path, capsys):
    f, b = tmp_path / "flows", tmp_path / "bundles"
    f.mkdir(); b.mkdir()
    make_flow(f, "orphan-flow", ["skill-a"])
    # No matching bundle — should warn and not crash
    run_main(f, b)
    captured = capsys.readouterr()
    assert "orphan-flow" in captured.err
