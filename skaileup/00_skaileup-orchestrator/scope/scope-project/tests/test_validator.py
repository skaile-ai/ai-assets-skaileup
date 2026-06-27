# tests/test_validator.py
"""Tests for skaileup-scope-scope-project's validator.py.

Coverage:
- All four example fixtures pass the validator (positive case).
- Missing tier rejected (negative).
- flow_to_run / tier mismatch rejected (negative).
- Snapshot of the deterministic decision rule against all four fixtures.
"""
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_DIR / "validator.py"
EXAMPLES = SKILL_DIR / "examples"
FIXTURES = json.loads((EXAMPLES / "fixtures.json").read_text())


def run_validator(yaml_path):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(yaml_path)],
        capture_output=True,
        text=True,
    )


VARIANT_EXAMPLES = ["cli-app", "concept-only", "reverse-engineer"]


def test_all_four_examples_pass():
    for f in FIXTURES:
        path = EXAMPLES / f"{f['expected_tier']}.scope.yaml"
        r = run_validator(path)
        assert r.returncode == 0, f"{path} failed: stderr={r.stderr} stdout={r.stdout}"


def test_variant_examples_pass():
    for v in VARIANT_EXAMPLES:
        path = EXAMPLES / f"{v}.scope.yaml"
        r = run_validator(path)
        assert r.returncode == 0, f"{path} failed: stderr={r.stderr} stdout={r.stdout}"


def _variant_yaml(shape, tier, flow_to_run):
    return (
        'schema_version: "1.0"\n'
        f'shape: {shape}\n'
        f'tier: {tier}\n'
        f'flow_to_run: "{flow_to_run}"\n'
        'reasoning: "this reasoning is exactly long enough to satisfy the validator length floor."\n'
        'description: "x"\n'
        'signals:\n'
        '  features_estimate: 3\n'
        '  multi_user: false\n'
        '  persistence: structured\n'
        '  integrations: []\n'
        'override:\n'
        '  applied: false\n'
        '  requested_tier: null\n'
        '  rule_would_have_picked: null\n'
        'chosen_at: "2026-05-07T00:00:00Z"\n'
        'chosen_by: "skaileup-scope-scope-project@1.2.0"\n'
    )


def test_variant_route_passes(tmp_path):
    p = tmp_path / "ok.yaml"
    p.write_text(_variant_yaml("cli", "cli-app", "flow:cli-app"))
    r = run_validator(p)
    assert r.returncode == 0, f"stderr={r.stderr} stdout={r.stdout}"


def test_variant_flow_must_match_tier(tmp_path):
    # tier is a variant but flow_to_run points elsewhere → reject
    p = tmp_path / "bad.yaml"
    p.write_text(_variant_yaml("cli", "cli-app", "flow:mvp"))
    r = run_validator(p)
    assert r.returncode != 0


def test_shape_must_agree_with_tier(tmp_path):
    # shape says cli but tier is a sizing tier → reject
    p = tmp_path / "bad.yaml"
    p.write_text(_variant_yaml("cli", "mvp", "flow:mvp"))
    r = run_validator(p)
    assert r.returncode != 0
    combined = (r.stderr + r.stdout).lower()
    assert "shape" in combined


def test_unknown_shape_rejected(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text(_variant_yaml("desktop", "mvp", "flow:mvp"))
    r = run_validator(p)
    assert r.returncode != 0


def test_missing_tier_fails(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text('schema_version: "1.0"\nflow_to_run: "flow:mvp"\n')
    r = run_validator(p)
    assert r.returncode != 0
    combined = (r.stderr + r.stdout).lower()
    assert "tier" in combined


def test_flow_must_match_tier(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text(
        'schema_version: "1.0"\n'
        'tier: mvp\n'
        'flow_to_run: "flow:standard-app"\n'
        'reasoning: "this reasoning is exactly long enough to satisfy the validator length floor."\n'
        'description: "x"\n'
        'signals:\n'
        '  features_estimate: 1\n'
        '  multi_user: false\n'
        '  persistence: trivial\n'
        '  integrations: []\n'
        'override:\n'
        '  applied: false\n'
        '  requested_tier: null\n'
        '  rule_would_have_picked: null\n'
        'chosen_at: "2026-05-07T00:00:00Z"\n'
        'chosen_by: "skaileup-scope-scope-project@1.0.0"\n'
    )
    r = run_validator(p)
    assert r.returncode != 0


def test_snapshot_rule_for_each_fixture():
    """Determinism guard: rule(signals) == expected_tier for all 4 fixtures."""

    def rule(s):
        if s["features_estimate"] <= 1 and s["persistence"] == "trivial":
            return "mvp"
        if s["features_estimate"] <= 5 and not s["multi_user"]:
            return "simple-app"
        if s["persistence"] == "external" or len(s["integrations"]) >= 2:
            return "complex-app"
        if s["features_estimate"] <= 20 or s["multi_user"]:
            return "standard-app"
        return "complex-app"

    for f in FIXTURES:
        assert rule(f["signals"]) == f["expected_tier"], f


def test_shape_routing_snapshot():
    """Stage-0 determinism guard: a non-app shape short-circuits to its flow."""

    def route(shape, sizing_tier):
        if shape == "reverse-engineer":
            return "reverse-engineer"
        if shape == "concept-only":
            return "concept-only"
        if shape == "cli":
            return "cli-app"
        return sizing_tier  # shape == "app"

    assert route("cli", "mvp") == "cli-app"
    assert route("concept-only", "standard-app") == "concept-only"
    assert route("reverse-engineer", "complex-app") == "reverse-engineer"
    assert route("app", "simple-app") == "simple-app"
