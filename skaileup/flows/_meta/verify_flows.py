#!/usr/bin/env python3
"""Verifier for Phase 2 Task 2H artifacts.

Exits 0 if all checks pass (warnings allowed); exits 2 on any error.

Checks performed:
1. Every flow file (`flows/*.flow.yaml`) validates against
   `contracts/flow.schema.json`.
2. Every flow's `id` matches its filename stem.
3. Every `nodes[].data.skill` resolves to either:
   (a) an existing SKILL.md `name:` (Bucket A: existing),
   (b) a Phase-2 planned skill name (Bucket B: planned), or
   (c) a deferred Phase-3 skill in `flows/_meta/deferred_skills.yaml`
       (Bucket C: deferred — emits WARN, not ERROR).
   Anything else → ERROR (unresolved).
4. Each tier bundle inherits its predecessor: simple-app→mvp,
   standard-app→simple-app, complex-app→standard-app. mvp must NOT inherit.
5. Every flow node skill MUST be present in its tier bundle's effective
   `requires:` set (transitive via `bundle:` inheritance).
   Skills present in effective set but NOT in the tier's flow are reported
   as informational extras (WARN), not errors — this is intentional because
   inherited tiers may carry skills used by the predecessor's mockup variant
   (e.g. simple-app inherits mockup-walkthrough-text from mvp even though
   simple-app uses mockup-walkthrough-static-html).
6. Slice bundles (concept-slice, impl-slice) MUST be leaf bundles with
   `requires:` matching their flow's nodes exactly (no inheritance).
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
# Bundles are co-located with flows: skaileup/flows/<app>/<app>.bundle.yaml
SCHEMA_PATH = REPO / "skaileup" / "contracts" / "flow.schema.json"
DEFERRED_PATH = FLOWS / "_meta" / "deferred_skills.yaml"

TIER_FLOWS = ["mvp", "simple-app", "standard-app", "complex-app"]
SLICE_FLOWS = ["concept-slice", "impl-slice"]
ALL_FLOWS = TIER_FLOWS + SLICE_FLOWS

EXPECTED_PARENTS = {
    "simple-app": "mvp",
    "standard-app": "simple-app",
    "complex-app": "standard-app",
}

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


def collect_flow_skills(flow_data: dict) -> set[str]:
    return {n["data"]["skill"] for n in flow_data["nodes"] if n.get("type") == "skill"}


def parse_bundle(bundle_path: Path) -> tuple[dict, set[str], list[str]]:
    """Return (full bundle dict, set of skill names, list of parent bundle names)."""
    data = yaml.safe_load(bundle_path.read_text())
    skills: set[str] = set()
    parents: list[str] = []
    for r in data.get("requires", []):
        if not isinstance(r, str):
            continue
        kind, _, name = r.partition(":")
        name = bare_name(name)
        if kind == "skill":
            skills.add(name)
        elif kind == "bundle":
            parents.append(name)
    return data, skills, parents


def bundle_flow_refs(bundle_path: Path) -> set[str]:
    """Return the bare names of every ``flow:`` ref in a bundle's requires."""
    data = yaml.safe_load(bundle_path.read_text())
    return {
        bare_name(r.partition(":")[2])
        for r in data.get("requires", [])
        if isinstance(r, str) and r.startswith("flow:")
    }


def effective_bundle_skills(tier: str) -> set[str]:
    """Walk the bundle inheritance chain and return the union of all skills."""
    seen: set[str] = set()
    eff: set[str] = set()
    stack = [tier]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        bp = FLOWS / cur / f"{cur}.bundle.yaml"
        if not bp.exists():
            raise FileNotFoundError(bp)
        _, skills, parents = parse_bundle(bp)
        eff |= skills
        stack.extend(parents)
    return eff


def main() -> int:
    schema = load_schema()
    deferred = load_deferred()
    existing = gather_existing_skill_names()
    knowable = existing | PHASE_2_PLANNED

    errors: list[str] = []
    warnings: list[str] = []

    # ------------------------------------------------------------------
    # 1+2. Validate every flow + check id matches filename stem
    # ------------------------------------------------------------------
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
        flow_skills_by_id[fid] = collect_flow_skills(data)

    # ------------------------------------------------------------------
    # 3. Resolve every skill referenced
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
    # 4 + 5. Tier-bundle inheritance + flow ⊆ effective bundle skills
    # ------------------------------------------------------------------
    for tier in TIER_FLOWS:
        bp = FLOWS / tier / f"{tier}.bundle.yaml"
        if not bp.exists():
            errors.append(f"missing tier bundle: {bp}")
            continue
        try:
            _, _, parents = parse_bundle(bp)
        except Exception as e:
            errors.append(f"{bp}: parse failed: {e}")
            continue

        # Inheritance pin
        if tier == "mvp":
            if parents:
                errors.append(
                    f"{bp}: mvp must NOT have parent bundles, found {parents!r}"
                )
        else:
            expected = EXPECTED_PARENTS[tier]
            if expected not in parents:
                errors.append(
                    f"{bp}: missing required parent bundle:{expected} (found parents={parents!r})"
                )

        # Effective skills via transitive inheritance
        try:
            eff = effective_bundle_skills(tier)
        except FileNotFoundError as e:
            errors.append(f"{bp}: declared parent bundle missing: {e}")
            continue

        flow_set = flow_skills_by_id.get(tier, set())
        # MUST: every flow skill is bundled
        missing = flow_set - eff
        if missing:
            errors.append(
                f"{bp}: flow references skills NOT in effective bundle: {sorted(missing)}"
            )
        # INFO: extras present in inherited chain but not used by this flow
        extras = eff - flow_set
        if extras:
            warnings.append(
                f"{bp}: tier-shape extras (in inherited bundle, not in flow): {sorted(extras)}"
            )

    # ------------------------------------------------------------------
    # 6. Slice bundles must be leaves and exactly match their flow nodes
    # ------------------------------------------------------------------
    for sid in SLICE_FLOWS:
        bp = FLOWS / sid / f"{sid}.bundle.yaml"
        if not bp.exists():
            errors.append(f"missing slice bundle: {bp}")
            continue
        try:
            _, skills, parents = parse_bundle(bp)
        except Exception as e:
            errors.append(f"{bp}: parse failed: {e}")
            continue
        if parents:
            errors.append(
                f"{bp}: slice bundle must not inherit (no bundle: entries), found {parents!r}"
            )
        flow_set = flow_skills_by_id.get(sid, set())
        if skills != flow_set:
            errors.append(
                f"{bp}: requires set {sorted(skills)} != flow nodes {sorted(flow_set)}"
            )

    # ------------------------------------------------------------------
    # 7. Every bundle must provision its own flow asset, so installing the
    #    bundle yields a runnable workspace (flow + skills + contracts).
    # ------------------------------------------------------------------
    for fid in ALL_FLOWS:
        bp = FLOWS / fid / f"{fid}.bundle.yaml"
        if not bp.exists():
            continue
        if fid not in bundle_flow_refs(bp):
            errors.append(f"{bp}: bundle does not require its own flow:{fid}")

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
        f"OK: 6 flows + 6 bundles consistent ({len(warnings)} warning(s): "
        f"deferred-skill + tier-shape extras)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
