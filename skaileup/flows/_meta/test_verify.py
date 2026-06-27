#!/usr/bin/env python3
"""Test harness for flows/_meta/verify_flows.py.

Invokes the verifier as a subprocess against:
  (a) the live repo (happy path → exit 0),
  (b) a temp scratch repo with a synthesized flow that fails one specific
      check (exit 2 in each case).

Flows are self-contained: each carries a top-level ``requires:`` manifest.
There are no ``*.bundle.yaml`` files.

Run:  python3 -m pytest flows/_meta/test_verify.py -v
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]  # repo root (skaileup/flows/_meta/ is 3 levels deep)
FLOWS = REPO / "skaileup" / "flows"
VERIFIER = FLOWS / "_meta" / "verify_flows.py"
SCHEMA = REPO / "skaileup" / "contracts" / "flow.schema.json"
SKAILE_YAML = REPO / "skaile.yaml"


def _run(verifier_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(verifier_path)],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Case 1: happy path — verifier exits 0 against the real repo
# ---------------------------------------------------------------------------
def test_happy_path_exits_zero():
    proc = _run(VERIFIER)
    assert proc.returncode == 0, (
        f"verifier failed:\nstdout={proc.stdout}\nstderr={proc.stderr}"
    )
    assert "OK:" in proc.stdout


# ---------------------------------------------------------------------------
# Helpers for synthetic-repo cases
# ---------------------------------------------------------------------------
def _build_scratch_repo(tmp_path: Path) -> Path:
    """Mirror the minimum repo structure the verifier touches.

    Layout (self-contained flows; new contracts location):
      <root>/skaile.yaml                                 (copied)
      <root>/skaileup/contracts/flow.schema.json         (copied)
      <root>/skaileup/flows/_meta/deferred_skills.yaml   (copied)
      <root>/skaileup/flows/_meta/verify_flows.py        (copied)
      <root>/skaileup/flows/<app>/<app>.flow.yaml        (copied)
      <root>/<each existing SKILL.md as a stub so name-resolution works>
    """
    shutil.copy2(SKAILE_YAML, tmp_path / "skaile.yaml")
    (tmp_path / "skaileup" / "contracts").mkdir(parents=True)
    shutil.copy2(SCHEMA, tmp_path / "skaileup" / "contracts" / "flow.schema.json")
    (tmp_path / "skaileup" / "flows" / "_meta").mkdir(parents=True)
    shutil.copy2(FLOWS / "_meta" / "verify_flows.py",
                 tmp_path / "skaileup" / "flows" / "_meta" / "verify_flows.py")
    shutil.copy2(FLOWS / "_meta" / "deferred_skills.yaml",
                 tmp_path / "skaileup" / "flows" / "_meta" / "deferred_skills.yaml")
    # Copy flow files
    for flow_file in FLOWS.glob("*/*.flow.yaml"):
        app = flow_file.parent.name
        dest_dir = tmp_path / "skaileup" / "flows" / app
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(flow_file, dest_dir / flow_file.name)
    # Mirror real SKILL.md files so the verifier's name-resolution finds the
    # full set. We only copy frontmatter (a stub body is fine).
    for skill_md in REPO.glob("**/SKILL.md"):
        rel = skill_md.relative_to(REPO)
        if rel.parts[0] in ("node_modules", "_concept", ".git", "docs"):
            continue
        if rel.parts[:2] == ("skaileup", "flows"):
            continue
        text = skill_md.read_text()
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                text = "---" + parts[1] + "---\n"
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
    return tmp_path / "skaileup" / "flows" / "_meta" / "verify_flows.py"


# ---------------------------------------------------------------------------
# Case 2: unresolved skill name → exit 2
# ---------------------------------------------------------------------------
def test_unresolved_skill_fails(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    flow_path = tmp_path / "skaileup" / "flows" / "appbuilder-mvp" / "appbuilder-mvp.flow.yaml"
    data = yaml.safe_load(flow_path.read_text())
    # Repoint a node + its requires entry at an unresolvable skill so the only
    # failing signal is name-resolution (not a requires-coverage mismatch).
    data["nodes"][1]["data"]["skill"] = "this-does-not-exist-anywhere"
    data["requires"] = [
        "skill:@skaile-ai/this-does-not-exist-anywhere" if r == "skill:@skaile-ai/concept-brief" else r
        for r in data["requires"]
    ]
    flow_path.write_text(yaml.safe_dump(data, sort_keys=False))
    proc = _run(verifier)
    assert proc.returncode == 2, (
        f"expected exit 2, got {proc.returncode}\n"
        f"stdout={proc.stdout}\nstderr={proc.stderr}"
    )
    assert "unresolved skill name: this-does-not-exist-anywhere" in proc.stderr


# ---------------------------------------------------------------------------
# Case 3: deferred skill → WARN + exit 0
# ---------------------------------------------------------------------------
def test_deferred_skill_warns_only(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    deferred_path = (
        tmp_path / "skaileup" / "flows" / "_meta" / "deferred_skills.yaml"
    )
    deferred_path.write_text(
        yaml.safe_dump({"deferred_phase_3": ["zz-deferred-demo"]}, sort_keys=False)
    )
    flow_path = tmp_path / "skaileup" / "flows" / "appbuilder-mvp" / "appbuilder-mvp.flow.yaml"
    data = yaml.safe_load(flow_path.read_text())
    data["nodes"][1]["data"]["skill"] = "zz-deferred-demo"
    # Keep requires in sync so the only signal is the deferred WARN, not a
    # requires-coverage ERROR.
    data["requires"] = [
        "skill:@skaile-ai/zz-deferred-demo" if r == "skill:@skaile-ai/concept-brief" else r
        for r in data["requires"]
    ]
    flow_path.write_text(yaml.safe_dump(data, sort_keys=False))
    proc = _run(verifier)
    assert proc.returncode == 0, (
        f"expected exit 0, got {proc.returncode}\nstderr={proc.stderr}"
    )
    assert "deferred skill referenced" in proc.stderr
    assert "zz-deferred-demo" in proc.stderr


# ---------------------------------------------------------------------------
# Case 4: requires missing a flow's skill → exit 2
# ---------------------------------------------------------------------------
def test_requires_missing_flow_skill_fails(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    flow_path = tmp_path / "skaileup" / "flows" / "appbuilder-mvp" / "appbuilder-mvp.flow.yaml"
    data = yaml.safe_load(flow_path.read_text())
    # Drop concept-brief from requires (appbuilder-mvp.flow.yaml still runs it as a node)
    data["requires"] = [
        r for r in data["requires"] if r != "skill:@skaile-ai/concept-brief"
    ]
    flow_path.write_text(yaml.safe_dump(data, sort_keys=False))
    proc = _run(verifier)
    assert proc.returncode == 2
    assert "requires missing skills the flow runs" in proc.stderr
    assert "concept-brief" in proc.stderr


# ---------------------------------------------------------------------------
# Case 5: requires lists a skill the flow does NOT run → exit 2
# ---------------------------------------------------------------------------
def test_requires_extra_skill_fails(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    flow_path = tmp_path / "skaileup" / "flows" / "appbuilder-mvp" / "appbuilder-mvp.flow.yaml"
    data = yaml.safe_load(flow_path.read_text())
    data.setdefault("requires", []).append("skill:@skaile-ai/ops-review")
    flow_path.write_text(yaml.safe_dump(data, sort_keys=False))
    proc = _run(verifier)
    assert proc.returncode == 2
    assert "requires lists skills the flow does NOT run" in proc.stderr
    assert "ops-review" in proc.stderr


# ---------------------------------------------------------------------------
# Case 6: unknown contract in requires → exit 2
# ---------------------------------------------------------------------------
def test_requires_unknown_contract_fails(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    flow_path = tmp_path / "skaileup" / "flows" / "appbuilder-mvp" / "appbuilder-mvp.flow.yaml"
    data = yaml.safe_load(flow_path.read_text())
    data["requires"].append("contract:@skaile-ai/not-a-real-contract")
    flow_path.write_text(yaml.safe_dump(data, sort_keys=False))
    proc = _run(verifier)
    assert proc.returncode == 2
    assert "unknown contract" in proc.stderr


# ---------------------------------------------------------------------------
# Case 7: jsonschema validation failure → exit 2
# ---------------------------------------------------------------------------
def test_schema_violation_fails(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    flow_path = tmp_path / "skaileup" / "flows" / "appbuilder-mvp" / "appbuilder-mvp.flow.yaml"
    data = yaml.safe_load(flow_path.read_text())
    # Break: add a top-level key the schema rejects
    data["this_is_not_a_known_key"] = "bad"
    flow_path.write_text(yaml.safe_dump(data, sort_keys=False))
    proc = _run(verifier)
    assert proc.returncode == 2
    assert "schema validation failed" in proc.stderr


# ---------------------------------------------------------------------------
# Case 8: schema accepts router/gate/sub-flow node types + review-loop edge
# ---------------------------------------------------------------------------
def test_schema_accepts_new_node_and_edge_types():
    """Regression guard for the v1.1 schema bump (router, gate, sub-flow, review-loop)."""
    import jsonschema

    schema = json.loads(SCHEMA.read_text())
    flow = {
        "id": "smoke",
        "name": "Smoke",
        "description": "exercises router + gate + sub-flow + review-loop",
        "requires": ["contract:@skaile-ai/shared-contracts"],
        "nodes": [
            {
                "id": "r1",
                "type": "router",
                "position": {"x": 0, "y": 0},
                "data": {
                    "label": "Tier Router",
                    "routes": [
                        {"condition": "tier == 'appbuilder-mvp'", "target": "g1"},
                        {"condition": "default", "target": None},
                    ],
                },
            },
            {
                "id": "g1",
                "type": "gate",
                "position": {"x": 100, "y": 0},
                "data": {
                    "label": "Features Gate",
                    "check": "artifact.features.status in ['draft', 'approved']",
                    "on_fail": "pause-for-human",
                    "message": "Features required.",
                },
            },
            {
                "id": "sf1",
                "type": "sub-flow",
                "position": {"x": 200, "y": 0},
                "data": {"flow": "concept-slice", "pass_context": True},
            },
            {
                "id": "s1",
                "type": "skill",
                "position": {"x": 300, "y": 0},
                "data": {"skill": "impl-slice-implement"},
            },
        ],
        "edges": [
            {"id": "e1", "source": "r1", "target": "g1"},
            {"id": "e2", "source": "g1", "target": "sf1"},
            {"id": "e3", "source": "sf1", "target": "s1"},
            {
                "id": "e-loop",
                "source": "s1",
                "target": "g1",
                "type": "review-loop",
                "max_iterations": 3,
                "exit_condition": "tests.passing",
            },
        ],
        "entry": "r1",
    }
    jsonschema.validate(flow, schema)


# ---------------------------------------------------------------------------
# Case 9: schema rejects a malformed requires ref
# ---------------------------------------------------------------------------
def test_schema_rejects_bad_requires_ref():
    import jsonschema

    schema = json.loads(SCHEMA.read_text())
    flow = {
        "id": "smoke",
        "name": "Smoke",
        "requires": ["not-a-scoped-ref"],
        "nodes": [
            {"id": "s1", "type": "skill", "position": {"x": 0, "y": 0},
             "data": {"skill": "impl-slice-implement"}},
        ],
        "edges": [],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(flow, schema)


@pytest.mark.parametrize(
    "mutation,reason",
    [
        # invalid on_fail enum
        (lambda f: f["nodes"][1]["data"].update({"on_fail": "invalid-mode"}), "gate on_fail enum"),
        # empty routes
        (lambda f: f["nodes"][0]["data"].update({"routes": []}), "router routes minItems"),
        # bad flow id pattern (uppercase + space)
        (lambda f: f["nodes"][2]["data"].update({"flow": "BAD ID"}), "sub-flow id pattern"),
        # bogus edge type
        (lambda f: f["edges"][0].update({"type": "not-a-real-edge-type"}), "edge type enum"),
    ],
)
def test_schema_rejects_bad_new_types(mutation, reason):
    """Each mutation must trip a validation error — proves the schema is constraining."""
    import jsonschema

    schema = json.loads(SCHEMA.read_text())
    flow = {
        "id": "smoke",
        "name": "Smoke",
        "nodes": [
            {
                "id": "r1",
                "type": "router",
                "position": {"x": 0, "y": 0},
                "data": {"routes": [{"condition": "default", "target": None}]},
            },
            {
                "id": "g1",
                "type": "gate",
                "position": {"x": 100, "y": 0},
                "data": {
                    "check": "artifact.features.status in ['draft', 'approved']",
                    "on_fail": "pause-for-human",
                },
            },
            {
                "id": "sf1",
                "type": "sub-flow",
                "position": {"x": 200, "y": 0},
                "data": {"flow": "concept-slice"},
            },
        ],
        "edges": [{"id": "e1", "source": "r1", "target": "g1"}],
    }
    mutation(flow)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(flow, schema)
