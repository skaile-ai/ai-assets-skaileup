#!/usr/bin/env python3
"""Verifier for the flow manifests.

Exits 0 if all checks pass (warnings allowed); exits 2 on any error.

Each flow is **self-contained**: its top-level ``requires:`` block is the
install manifest — everything provisioned when the flow is installed. There are
no separate ``*.bundle.yaml`` files and no inheritance. ``requires:`` lists the
contracts the flow's skills read plus every skill its nodes run, as scoped asset
refs (``kind:@publisher/name``).

Checks performed:
1. Every flow file (`flows/*/<id>.flow.yaml`) validates against
   `contracts/flow.schema.json`.
2. Every flow's `id` matches its directory/filename stem.
3. Every `nodes[].data.skill` resolves to either:
   (a) an existing SKILL.md `name:` (Bucket A: existing),
   (b) a Phase-2 planned skill name (Bucket B: planned), or
   (c) a deferred Phase-3 skill in `flows/_meta/deferred_skills.yaml`
       (Bucket C: deferred — emits WARN, not ERROR).
   Anything else → ERROR (unresolved).
4. Each flow's `requires:` skill set EXACTLY equals its flow's node-skill set,
   AND its `requires:` flow set EXACTLY equals its sub-flow node targets — no
   skill/flow the flow runs is missing from the manifest, and none is listed that
   the flow does not run. (Self-contained, exact: no inheritance, no extras.)
   A tier that delegates a loop to a sub-flow node requires that `flow:` instead
   of re-listing the loop's skills; the sub-flow's own manifest provides them.
5. Every `contract:` ref in a flow's `requires:` resolves to a contract declared
   in `skaile.yaml`; every sub-flow node target resolves to a known flow id.
6. `requires:` refs use the scoped grammar `kind:@publisher/name` with the
   `skill`/`contract`/`flow` kinds (`flow:` only when a sub-flow node delegates).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
    import jsonschema
except ImportError as e:  # pragma: no cover
    print(f"ERROR: missing dep ({e}); pip install pyyaml jsonschema", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parents[3]  # repo root (skaileup/flows/_meta/ is 3 levels deep)
FLOWS = REPO / "skaileup" / "flows"
SCHEMA_PATH = REPO / "skaileup" / "contracts" / "flow.schema.json"
DEFERRED_PATH = FLOWS / "_meta" / "deferred_skills.yaml"
SKAILE_YAML = REPO / "skaile.yaml"

TIER_FLOWS = ["appbuilder-mvp", "appbuilder-simple", "appbuilder-standard", "appbuilder-complex"]
SLICE_FLOWS = ["concept-slice", "impl-slice"]
# Variant flows: not tiers — alternate shapes the scope step routes to.
# skaileup-impl / -standalone are implementation-only variants (no concept pass):
# the first reads a handed-off concept package, the second generates its own
# architecture subset.
VARIANT_FLOWS = [
    "appbuilder-cli",
    "concept-only",
    "reverse-engineer",
    "skaileup-impl",
    "skaileup-impl-standalone",
    "skaileup-implementation",
]
ALL_FLOWS = TIER_FLOWS + SLICE_FLOWS + VARIANT_FLOWS

# Skills authored by Phase-2 mini-plans 2A/2B/2C/2D/2F/2G — these are added
# to the "knowable" set for resolution checks even if SKILL.md gathering misses
# any (e.g. transient state). Mirrors the plan's "Pinned: Skill Name Registry".
PHASE_2_PLANNED = {
    "skaileup-scope-scope-project",
    "concept-slice-brainstorm",
    "concept-slice-align",
    "concept-slice-scope-feature",
    "concept-slice-design-feature",
    "impl-plan-align",
    "impl-slice-test",
    "impl-slice-recap",
    "impl-slice-refactor",
    "impl-slice-commit",
    "mockup-walkthrough-static-html",
    "component-mockup-isolated-html",
}


def bare_name(name: str) -> str:
    """Strip any publisher segment from a ref body, returning the bare asset name.

    Accepts the canonical ``@publisher/name`` shape and the legacy ``name@publisher``.
    """
    if name.startswith("@"):
        return name.split("/", 1)[1] if "/" in name else name
    return name.split("@", 1)[0]


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def load_deferred() -> set[str]:
    """Read deferred_skills.yaml. Tolerates two shapes:
    (a) plain list of names, (b) list of {name, reason} dicts.
    """
    raw = yaml.safe_load(DEFERRED_PATH.read_text())["deferred_phase_3"]
    out: set[str] = set()
    for item in raw:
        if isinstance(item, str):
            out.add(item)
        elif isinstance(item, dict) and "name" in item:
            out.add(item["name"])
        else:
            raise ValueError(f"deferred_skills.yaml: unexpected entry {item!r}")
    return out


def gather_existing_skill_names() -> set[str]:
    """Walk every SKILL.md under REPO and collect its `name:` frontmatter."""
    names: set[str] = set()
    for skill_md in REPO.glob("**/SKILL.md"):
        try:
            text = skill_md.read_text()
            if not text.startswith("---"):
                continue
            parts = text.split("---", 2)
            if len(parts) < 3:
                continue
            fm = yaml.safe_load(parts[1])
            if isinstance(fm, dict) and "name" in fm:
                names.add(str(fm["name"]))
        except Exception:
            continue
    return names


def gather_known_contracts() -> set[str]:
    """Return the set of contract names declared in skaile.yaml."""
    data = yaml.safe_load(SKAILE_YAML.read_text()) or {}
    return {
        str(a["name"])
        for a in data.get("assets", [])
        if isinstance(a, dict) and a.get("kind") == "contract" and "name" in a
    }


def collect_flow_skills(flow_data: dict) -> set[str]:
    return {n["data"]["skill"] for n in flow_data["nodes"] if n.get("type") == "skill"}


def collect_subflows(flow_data: dict) -> set[str]:
    """Flow ids referenced by sub-flow nodes (type == 'sub-flow')."""
    return {
        n["data"]["flow"]
        for n in flow_data["nodes"]
        if n.get("type") == "sub-flow"
    }


def parse_requires(flow_data: dict) -> tuple[set[str], set[str], set[str], list[str]]:
    """Return (skill names, contract names, flow names, malformed refs) from requires.

    A flow may require other flows (``flow:@pub/name``) when it delegates a loop to
    a sub-flow node instead of inlining it. The required flow's own manifest then
    transitively provides that loop's skills.
    """
    skills: set[str] = set()
    contracts: set[str] = set()
    flows: set[str] = set()
    bad: list[str] = []
    bucket = {"skill": skills, "contract": contracts, "flow": flows}
    for r in flow_data.get("requires", []) or []:
        if not isinstance(r, str) or ":" not in r:
            bad.append(str(r))
            continue
        kind, _, body = r.partition(":")
        if kind not in bucket:
            bad.append(r)
            continue
        if not body.startswith("@") or "/" not in body:
            bad.append(r)
            continue
        bucket[kind].add(bare_name(body))
    return skills, contracts, flows, bad


def main() -> int:
    schema = load_schema()
    deferred = load_deferred()
    existing = gather_existing_skill_names()
    knowable = existing | PHASE_2_PLANNED
    known_contracts = gather_known_contracts()

    errors: list[str] = []
    warnings: list[str] = []

    # ------------------------------------------------------------------
    # 0. No stray flow files: every *.flow.yaml must live under skaileup/flows/.
    #    Guards against the pre-consolidation pattern of parallel flow sets in
    #    orchestrator/ and impl-build/ drifting back in.
    # ------------------------------------------------------------------
    for fp in REPO.glob("**/*.flow.yaml"):
        try:
            fp.relative_to(FLOWS)
        except ValueError:
            errors.append(
                f"stray flow file outside skaileup/flows/: "
                f"{fp.relative_to(REPO)} (all flows must live under skaileup/flows/)"
            )

    # ------------------------------------------------------------------
    # 1+2. Validate every flow + check id matches filename stem
    # ------------------------------------------------------------------
    flow_data_by_id: dict[str, dict] = {}
    flow_skills_by_id: dict[str, set[str]] = {}
    for fid in ALL_FLOWS:
        fp = FLOWS / fid / f"{fid}.flow.yaml"
        if not fp.exists():
            errors.append(f"missing flow file: {fp}")
            continue
        try:
            data = yaml.safe_load(fp.read_text())
        except yaml.YAMLError as e:
            errors.append(f"{fp}: yaml parse failed: {e}")
            continue
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append(
                f"{fp}: schema validation failed at {list(e.absolute_path)}: {e.message}"
            )
            continue
        if data.get("id") != fid:
            errors.append(f"{fp}: id={data.get('id')!r} != filename stem {fid!r}")
        flow_data_by_id[fid] = data
        flow_skills_by_id[fid] = collect_flow_skills(data)

    # ------------------------------------------------------------------
    # 3. Resolve every skill referenced by a node
    # ------------------------------------------------------------------
    for fid, skills in flow_skills_by_id.items():
        for s in sorted(skills):
            if s in knowable:
                continue
            if s in deferred:
                warnings.append(f"{fid}: deferred skill referenced (Phase 3): {s}")
            else:
                errors.append(f"{fid}: unresolved skill name: {s}")

    # ------------------------------------------------------------------
    # 4 + 5 + 6. Per-flow requires: manifest is exact + well-formed
    # ------------------------------------------------------------------
    for fid in ALL_FLOWS:
        data = flow_data_by_id.get(fid)
        if data is None:
            continue
        if "requires" not in data:
            errors.append(f"{fid}: flow has no top-level requires: manifest")
            continue
        req_skills, req_contracts, req_flows, bad = parse_requires(data)
        node_skills = flow_skills_by_id.get(fid, set())
        node_subflows = collect_subflows(data)

        for b in bad:
            errors.append(
                f"{fid}: malformed requires ref {b!r} "
                f"(expected skill:/contract:/flow:@pub/name)"
            )

        # Exact match: requires' skill set == flow node-skill set
        missing = node_skills - req_skills
        extra = req_skills - node_skills
        if missing:
            errors.append(
                f"{fid}: requires missing skills the flow runs: {sorted(missing)}"
            )
        if extra:
            errors.append(
                f"{fid}: requires lists skills the flow does NOT run: {sorted(extra)}"
            )

        # Exact match: requires' flow set == flow's sub-flow node targets.
        # A flow that delegates a loop to a sub-flow node requires that flow;
        # a flow listed but not delegated to (or vice versa) is an error.
        missing_f = node_subflows - req_flows
        extra_f = req_flows - node_subflows
        if missing_f:
            errors.append(
                f"{fid}: requires missing sub-flows the flow delegates to: {sorted(missing_f)}"
            )
        if extra_f:
            errors.append(
                f"{fid}: requires lists flows the flow does NOT delegate to: {sorted(extra_f)}"
            )
        # Every sub-flow target must be a real flow id
        for sf in sorted(node_subflows):
            if sf not in ALL_FLOWS:
                errors.append(f"{fid}: sub-flow node targets unknown flow {sf!r}")

        # Contracts must resolve to a declared contract
        for c in sorted(req_contracts):
            if c not in known_contracts:
                errors.append(
                    f"{fid}: requires unknown contract {c!r} "
                    f"(not declared in skaile.yaml)"
                )
        if not req_contracts:
            warnings.append(f"{fid}: requires lists no contract (expected shared-contracts)")

    # ------------------------------------------------------------------
    # Print summary
    # ------------------------------------------------------------------
    for w in warnings:
        print(f"WARN: {w}", file=sys.stderr)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)

    if errors:
        print(
            f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)",
            file=sys.stderr,
        )
        return 2
    print(
        f"OK: {len(flow_data_by_id)} flows consistent — each requires: manifest "
        f"exactly covers its nodes ({len(warnings)} warning(s))"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
