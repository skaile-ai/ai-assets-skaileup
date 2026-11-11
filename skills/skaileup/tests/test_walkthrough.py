"""Tests for skills/skaileup/scripts/walkthrough.py — the concept walk (tree/01_meta/walkthrough.md).

    python -m pytest skills/skaileup/tests -q
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest
import yaml

SKILL = Path(__file__).resolve().parents[1]
REPO = SKILL.parents[1]
NODE = REPO / "tree" / "01_meta" / "walkthrough.md"


def _load():
    spec = importlib.util.spec_from_file_location("walkthrough", SKILL / "scripts" / "walkthrough.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["walkthrough"] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


wt = _load()


def run(root: Path, *args: str) -> int:
    return wt.main(["walkthrough.py", *args, "--root", str(root)])


def write(root: Path, rel: str, text: str = "") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md(approved: bool = True, **fields) -> str:
    fm = {**fields, **({"approved": "2026-11-08"} if approved else {})}
    return "---\n" + yaml.safe_dump(fm, sort_keys=False) + "---\n\n# Body\n"


APP_DESIGN = """---
app: Test
approved: 2026-11-08
---

# App design – Test

## Navigation model
organization: object-led

## Objects
| id | object | home |
|---|---|---|
| OBJ-1 | Poll | page |

## Information hierarchy
Poll: title, deadline.

## Open
"""


def project(root: Path, stages=("frame", "look", "data"), brief_approved: bool = True) -> Path:
    """A minimal project whose artifacts pass every check of `stages`."""
    if "frame" in stages:
        write(root, "_concept/01_meta/expectations.md", md(approved=False))
        write(root, "_concept/brief.md", md(approved=brief_approved, elevator_pitch="x"))
        write(root, "_concept/goals.md", md())
        write(root, "_concept/glossary.md", md())
        write(root, "_concept/04_journeys/stories.yaml", "stages: []\n")
    if "look" in stages or "data" in stages:
        write(root, "APP-DESIGN.md", APP_DESIGN)
    if "look" in stages:
        write(root, "_concept/03_brand/identity.md", md(mood="calm"))
        write(root, "_concept/03_brand/brand.tokens.json", "{}\n")
        write(root, "_concept/07_screens/shell.md", md(navigation="decided"))
        write(root, "_concept/09_mockup/storybook/src/app/nav.ts", "export const nav = []\n")
    if "data" in stages:
        write(root, "_concept/10_blueprint/datamodel/model.yaml", "version: 1\nentities: {}\n")
        write(root, "_concept/10_blueprint/datamodel/seed.yaml", "version: 1\nscenarios: {}\n")
        (root / "_concept/09_mockup/storybook/src/entities/poll").mkdir(parents=True)
    return root


def state(root: Path) -> dict:
    return yaml.safe_load((root / wt.STATE).read_text(encoding="utf-8"))


def test_approve_refuses_an_unapproved_brief(tmp_path, capsys):
    project(tmp_path, stages=("frame",), brief_approved=False)
    assert run(tmp_path, "init") == 0
    assert run(tmp_path, "approve", "frame", "--source", "user, 2026-11-08") == 2
    out = capsys.readouterr().out
    assert "_concept/brief.md approved: unapproved" in out
    assert state(tmp_path)["stages"]["frame"]["status"] == "open"


def test_approve_look_refuses_while_frame_is_open(tmp_path, capsys):
    project(tmp_path)
    run(tmp_path, "init")
    assert run(tmp_path, "approve", "look", "--source", "user, 2026-11-08") == 2
    assert "stage 'frame' is open" in capsys.readouterr().out
    assert state(tmp_path)["stages"]["look"]["status"] == "open"


def test_reopen_look_reopens_every_later_stage(tmp_path):
    write(tmp_path, wt.STATE, yaml.safe_dump({
        "stages": {name: {"status": "approved", "approved": "2026-11-08", "source": "user, 2026-11-08"}
                   for name in wt.STAGE_NAMES},
        "history": [],
    }))
    assert run(tmp_path, "reopen", "look", "--reason", "user: Kunden under Einstellungen") == 0
    doc = state(tmp_path)
    assert doc["stages"]["frame"]["status"] == "approved"
    for name in ("look", "data", "features"):
        assert doc["stages"][name] == {"status": "open"}
    assert [(e["stage"], e["event"]) for e in doc["history"]] == [
        ("look", "reopened"), ("data", "reopened"), ("features", "reopened")]
    assert all(e["reason"] == "user: Kunden under Einstellungen" for e in doc["history"])


def test_waive_refuses_an_unknown_decision_record(tmp_path, capsys):
    project(tmp_path, stages=("frame",))
    write(tmp_path, "_concept/10_blueprint/decisions.md", "# Decisions\n\n## DR-1 — Something\n")
    run(tmp_path, "init")
    assert run(tmp_path, "waive", "features", "--dr", "DR-7", "--source", "user, 2026-11-08") == 2
    assert "DR-7 does not occur" in capsys.readouterr().out
    assert run(tmp_path, "waive", "features", "--dr", "DR-1", "--source", "user, 2026-11-08") == 0
    doc = state(tmp_path)
    assert doc["stages"]["features"] == {"status": "waived", "dr": "DR-1", "source": "user, 2026-11-08"}
    assert doc["history"][-1]["event"] == "waived"


def test_gate_build_opens_after_the_approvals(tmp_path, capsys):
    project(tmp_path)
    run(tmp_path, "init")
    capsys.readouterr()
    assert run(tmp_path, "gate", "build") == 3
    assert capsys.readouterr().out.startswith(
        "Concept stage 'frame' is open — run the skaileup skill to continue the walk (next: skaileup → ")
    for stage in ("frame", "look", "data"):
        assert run(tmp_path, "approve", stage, "--source", "user, 2026-11-08") == 0
    assert run(tmp_path, "gate", "build") == 0
    run(tmp_path, "next")
    assert capsys.readouterr().out.splitlines()[-1].startswith("features: spec-feature → ")


def test_gate_feature_fails_on_an_unapproved_screen(tmp_path, capsys):
    project(tmp_path)
    run(tmp_path, "init")
    for stage in ("frame", "look", "data"):
        run(tmp_path, "approve", stage, "--source", "user, 2026-11-08")
    write(tmp_path, "_concept/05_features/polls/create-poll.md",
          md(screens=[{"path": "07_screens/poll.md"}]))
    write(tmp_path, "_concept/07_screens/poll.md", md(approved=False, screen_id="poll"))
    capsys.readouterr()
    assert run(tmp_path, "gate", "feature", "polls/create-poll") == 3
    assert "_concept/07_screens/poll.md" in capsys.readouterr().out
    write(tmp_path, "_concept/07_screens/poll.md", md(screen_id="poll"))
    assert run(tmp_path, "gate", "feature", "polls/create-poll") == 0


def proposal_file(status: str) -> str:
    entry = {"id": "p1", "target": "_concept/10_blueprint/datamodel/model.yaml",
             "anchor": "entities.Place.fields.price_level", "payload": {"type": "integer", "required": False},
             "source": "PlaceCard needs a price hint", "status": status}
    if status != "proposed":
        entry.update(settled_by="architecture-datamodel", settled_on="2026-11-09")
    return yaml.safe_dump({"proposed_by": "mockup-storybook", "proposed_on": "2026-11-08",
                           "scope": "place-card", "entries": [entry]}, sort_keys=False)


def test_a_pending_proposal_on_model_yaml_blocks_the_data_stage(tmp_path, capsys):
    project(tmp_path)
    run(tmp_path, "init")
    for stage in ("frame", "look"):
        assert run(tmp_path, "approve", stage, "--source", "user, 2026-11-08") == 0
    path = "_concept/proposals/2026-11-08-mockup-storybook-place-card.yaml"
    write(tmp_path, path, proposal_file("proposed"))
    capsys.readouterr()
    assert run(tmp_path, "approve", "data", "--source", "user, 2026-11-08") == 2
    assert "no pending proposal entry targets model.yaml: open markers" in capsys.readouterr().out
    write(tmp_path, path, proposal_file("promoted"))
    assert run(tmp_path, "approve", "data", "--source", "user, 2026-11-08") == 0


def test_status_without_a_state_file(tmp_path, capsys):
    assert run(tmp_path, "status") == 0
    out = capsys.readouterr().out
    assert out.startswith("no _concept/01_meta/walkthrough.yaml — run the skaileup skill\n")
    assert "missing" in out
    assert run(tmp_path, "gate", "build") == 3


def stage_table() -> list[list[str]]:
    lines = NODE.read_text(encoding="utf-8").splitlines()
    start = lines.index("|stage|required (check)|producing skills, in order|checkpoint|")
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows


def test_stages_mirror_the_node_table():
    rows = stage_table()
    assert [r[0] for r in rows] == wt.STAGE_NAMES == ["frame", "look", "data", "features"]
    for row, stage in zip(rows, wt.STAGES):
        assert row[1].split(" · ") == [c.text for c in stage.checks]
        # a skill's parenthesised note may hold `, ` itself, so the split skips parentheses
        skills = re.split(r", (?![^()]*\))", row[2])
        assert skills == list(stage.skills)
        assert [s for s in skills if s.endswith("?")] == [s for s in stage.skills if s.endswith("?")]
        assert row[3] == stage.checkpoint


def test_guard_write_twice_yields_one_section(tmp_path):
    assert run(tmp_path, "guard", "--write") == 0
    assert run(tmp_path, "guard", "--write") == 0
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert text.count("<!-- skaileup:walkthrough -->") == 1
    assert text.count("<!-- /skaileup:walkthrough -->") == 1
    assert "/scripts/walkthrough.py gate build" in text


def test_guard_write_keeps_the_rest_of_claude_md(tmp_path):
    write(tmp_path, "CLAUDE.md", "# Project\n\nOwn rules.\n")
    run(tmp_path, "guard", "--write")
    run(tmp_path, "guard", "--write")
    text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.startswith("# Project\n\nOwn rules.\n\n<!-- skaileup:walkthrough -->")
    assert text.count("## Concept walkthrough (skaileup)") == 1
    assert not (tmp_path / "AGENTS.md").exists()


@pytest.mark.parametrize("stage", ["frame", "features"])
def test_init_keeps_an_existing_file(tmp_path, capsys, stage):
    run(tmp_path, "init")
    write(tmp_path, "_concept/10_blueprint/decisions.md", "## DR-3 — x\n")
    run(tmp_path, "waive", stage, "--dr", "DR-3", "--source", "user, 2026-11-08")
    capsys.readouterr()
    assert run(tmp_path, "init") == 0
    assert capsys.readouterr().out == "walkthrough.yaml exists\n"
    assert state(tmp_path)["stages"][stage]["status"] == "waived"
