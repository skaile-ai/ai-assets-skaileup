#!/usr/bin/env python3
"""Validator for _concept/_meta/scope.yaml.

Exit codes:
    0 — file conforms to the pinned schema (schema_version 1.0).
    2 — file fails one or more validation checks (errors printed to stderr).

Usage:
    validator.py <path/to/scope.yaml>
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

# Sizing tiers — chosen by the feature-count/persistence rule (shape == "app").
ALLOWED_TIERS = {"appbuilder-mvp", "appbuilder-simple", "appbuilder-standard", "appbuilder-complex"}
# Variant flows — selected by the shape check that runs BEFORE sizing.
ALLOWED_VARIANTS = {"appbuilder-cli", "skaileup-concept-only", "skaileup-concept-reverse"}
# Every value `tier` (the routed flow id) may take.
ALLOWED_ROUTES = ALLOWED_TIERS | ALLOWED_VARIANTS
# The project shape. "app" falls through to tier sizing; the rest map 1:1 to a
# variant flow id via SHAPE_TO_ROUTE.
ALLOWED_SHAPES = {"app", "cli", "concept-only", "reverse-engineer"}
SHAPE_TO_ROUTE = {
    "cli": "appbuilder-cli",
    "concept-only": "skaileup-concept-only",
    "reverse-engineer": "skaileup-concept-reverse",
}
ALLOWED_PERSISTENCE = {"trivial", "structured", "external"}
ISO8601_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
REQUIRED_KEYS = (
    "schema_version",
    "tier",
    "flow_to_run",
    "reasoning",
    "description",
    "signals",
    "override",
    "chosen_at",
    "chosen_by",
)


def err(msg):
    print(f"INVALID: {msg}", file=sys.stderr)


def validate(path: Path) -> int:
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as e:
        err(f"YAML parse error: {e}")
        return 2
    if not isinstance(data, dict):
        err("root must be a mapping")
        return 2

    errors = []

    # Required keys
    for k in REQUIRED_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")

    # tier enum — the routed flow id: a sizing tier or a variant flow.
    if data.get("tier") not in ALLOWED_ROUTES:
        errors.append(
            f"tier must be one of {sorted(ALLOWED_ROUTES)}; got {data.get('tier')!r}"
        )

    # flow_to_run derivation: must be "flow:<tier>"
    if data.get("tier") in ALLOWED_ROUTES:
        expected_flow = f"flow:{data['tier']}"
        if data.get("flow_to_run") != expected_flow:
            errors.append(
                f"flow_to_run must be {expected_flow!r}; got {data.get('flow_to_run')!r}"
            )

    # shape (optional) — when present, must be a known shape and must agree with tier.
    if "shape" in data:
        shape = data.get("shape")
        if shape not in ALLOWED_SHAPES:
            errors.append(
                f"shape must be one of {sorted(ALLOWED_SHAPES)}; got {shape!r}"
            )
        elif shape == "app":
            if data.get("tier") not in ALLOWED_TIERS:
                errors.append(
                    f"shape 'app' requires tier in {sorted(ALLOWED_TIERS)}; got {data.get('tier')!r}"
                )
        else:  # variant shape — tier must be its 1:1 routed flow
            expected_route = SHAPE_TO_ROUTE[shape]
            if data.get("tier") != expected_route:
                errors.append(
                    f"shape {shape!r} requires tier {expected_route!r}; got {data.get('tier')!r}"
                )

    # reasoning length (30..800 after trim)
    r = (data.get("reasoning") or "")
    if not isinstance(r, str):
        errors.append("reasoning must be a string")
    else:
        rt = r.strip()
        if not (30 <= len(rt) <= 800):
            errors.append(f"reasoning length {len(rt)} not in [30, 800]")

    # description non-empty string
    desc = data.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errors.append("description must be a non-empty string")

    # signals
    s = data.get("signals")
    if not isinstance(s, dict):
        errors.append("signals must be a mapping")
        s = {}
    for k in ("features_estimate", "multi_user", "persistence", "integrations"):
        if k not in s:
            errors.append(f"signals.{k} missing")
    if "features_estimate" in s and not isinstance(s.get("features_estimate"), int):
        errors.append("signals.features_estimate must be int")
    # YAML maps booleans to bool; isinstance(bool, int) is True in Python so check bool first.
    if "multi_user" in s and not isinstance(s.get("multi_user"), bool):
        errors.append("signals.multi_user must be bool")
    if "persistence" in s and s.get("persistence") not in ALLOWED_PERSISTENCE:
        errors.append(
            f"signals.persistence must be one of {sorted(ALLOWED_PERSISTENCE)}; got {s.get('persistence')!r}"
        )
    if "integrations" in s and not isinstance(s.get("integrations"), list):
        errors.append("signals.integrations must be list")

    # override
    o = data.get("override")
    if not isinstance(o, dict):
        errors.append("override must be a mapping")
        o = {}
    if "applied" in o and not isinstance(o.get("applied"), bool):
        errors.append("override.applied must be bool")
    if o.get("applied") is True:
        if o.get("requested_tier") != data.get("tier"):
            errors.append(
                "override.requested_tier must equal tier when applied=true"
            )
        if o.get("rule_would_have_picked") not in ALLOWED_ROUTES:
            errors.append(
                "override.rule_would_have_picked must be a valid route when applied=true"
            )
    elif o.get("applied") is False:
        if o.get("requested_tier") is not None:
            errors.append(
                "override.requested_tier must be null when applied=false"
            )
        if o.get("rule_would_have_picked") is not None:
            errors.append(
                "override.rule_would_have_picked must be null when applied=false"
            )

    # chosen_at format
    chosen_at = data.get("chosen_at", "")
    if not ISO8601_Z.match(str(chosen_at)):
        errors.append(
            f"chosen_at must match ISO-8601 UTC with Z suffix; got {chosen_at!r}"
        )

    # chosen_by must be a non-empty string
    chosen_by = data.get("chosen_by")
    if not isinstance(chosen_by, str) or not chosen_by.strip():
        errors.append("chosen_by must be a non-empty string")

    if errors:
        for e in errors:
            err(e)
        return 2

    print(f"OK: {path}")
    return 0


def main(argv):
    if len(argv) != 2:
        print("usage: validator.py <path/to/scope.yaml>", file=sys.stderr)
        return 2
    return validate(Path(argv[1]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
