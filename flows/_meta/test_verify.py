#!/usr/bin/env python3
"""Test harness for flows/_meta/verify_flows.py.

Invokes the verifier as a subprocess against:
  (a) the live repo (happy path → exit 0, with warnings),
  (b) a temp scratch repo with a synthesized flow that fails one specific
      check (exit 2 in each case).

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

REPO = Path(__file__).resolve().parents[2]
VERIFIER = REPO / "flows" / "_meta" / "verify_flows.py"
SCHEMA = REPO / "contracts" / "flow.schema.json"


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

    Layout:
      <root>/contracts/flow.schema.json     (copied)
      <root>/flows/_meta/deferred_skills.yaml (copied)
      <root>/flows/_meta/verify_flows.py    (copied)
      <root>/flows/<all 6 flow yamls>       (copied)
      <root>/bundles/<all 6 bundle yamls>   (copied)
      <root>/<each existing SKILL.md as a stub so name-resolution works>
    """
    (tmp_path / "contracts").mkdir(parents=True)
    shutil.copy2(SCHEMA, tmp_path / "contracts/flow.schema.json")
    (tmp_path / "flows" / "_meta").mkdir(parents=True)
    shutil.copy2(REPO / "flows/_meta/verify_flows.py",
                 tmp_path / "flows/_meta/verify_flows.py")
    shutil.copy2(REPO / "flows/_meta/deferred_skills.yaml",
                 tmp_path / "flows/_meta/deferred_skills.yaml")
    for f in (REPO / "flows").glob("*.flow.yaml"):
        shutil.copy2(f, tmp_path / "flows" / f.name)
    (tmp_path / "bundles").mkdir(parents=True)
    for f in (REPO / "bundles").glob("*.bundle.yaml"):
        shutil.copy2(f, tmp_path / "bundles" / f.name)
    # Mirror real SKILL.md files so the verifier's name-resolution finds the
    # full set. We only copy frontmatter (a stub body is fine).
    for skill_md in REPO.glob("**/SKILL.md"):
        rel = skill_md.relative_to(REPO)
        # Skip anything we already populated under flows/ or bundles/
        if rel.parts[0] in ("flows", "bundles", "node_modules", "_concept",
                             ".git", "docs"):
            continue
        text = skill_md.read_text()
        # Keep only the frontmatter block to keep the scratch repo small
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                text = "---" + parts[1] + "---\n"
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
    return tmp_path / "flows" / "_meta" / "verify_flows.py"


# ---------------------------------------------------------------------------
# Case 2: unresolved skill name → exit 2
# ---------------------------------------------------------------------------
def test_unresolved_skill_fails(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    flow_path = tmp_path / "flows" / "mvp.flow.yaml"
    data = yaml.safe_load(flow_path.read_text())
    # Inject an unresolvable skill name
    data["nodes"][1]["data"]["skill"] = "this-does-not-exist-anywhere"
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
    proc = _run(verifier)
    # mvp already references impl-architecture-templates-select (deferred), so we
    # expect a WARN line for it and overall exit 0.
    assert proc.returncode == 0
    assert "deferred skill referenced" in proc.stderr
    assert "impl-architecture-templates-select" in proc.stderr


# ---------------------------------------------------------------------------
# Case 4: bundle missing a flow's skill → exit 2
# ---------------------------------------------------------------------------
def test_bundle_missing_flow_skill_fails(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    bundle_path = tmp_path / "bundles" / "mvp.bundle.yaml"
    data = yaml.safe_load(bundle_path.read_text())
    # Drop concept-brief from the requires (mvp.flow.yaml still uses it)
    data["requires"] = [
        r for r in data["requires"]
        if r != "skill:concept-brief"
    ]
    bundle_path.write_text(yaml.safe_dump(data, sort_keys=False))
    proc = _run(verifier)
    assert proc.returncode == 2
    assert "flow references skills NOT in effective bundle" in proc.stderr
    assert "concept-brief" in proc.stderr


# ---------------------------------------------------------------------------
# Case 5: jsonschema validation failure → exit 2
# ---------------------------------------------------------------------------
def test_schema_violation_fails(tmp_path):
    verifier = _build_scratch_repo(tmp_path)
    flow_path = tmp_path / "flows" / "mvp.flow.yaml"
    data = yaml.safe_load(flow_path.read_text())
    # Break: add a top-level key the schema rejects
    # (top-level additionalProperties is False)
    data["this_is_not_a_known_key"] = "bad"
    flow_path.write_text(yaml.safe_dump(data, sort_keys=False))
    proc = _run(verifier)
    assert proc.returncode == 2
    assert "schema validation failed" in proc.stderr
