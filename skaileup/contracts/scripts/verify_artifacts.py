#!/usr/bin/env python3
"""Verify the artifact registry against every skill's `metadata.artifacts:` block.

Single source of truth for artifact id ↔ path is contracts/artifacts.yaml. Each
skill declares the artifacts it touches by ID only (produces / consumes / requires).
This script enforces that the declarations and the registry stay consistent.

Checks
------
1. registry-well-formed : every entry has path, kind, side, produced_by, description;
                          kind ∈ {durable, scratch, code}; side ∈ {concept, impl}.
2. producer-exists       : every produced_by names a real skill.
3. id-in-registry        : every id used in any skill's artifacts block exists in
                          the registry. (ERROR)
4. no-dangling           : every consumed/required id is produced by some skill. (ERROR)
5. producer-bidirectional: if a skill `produces` id X, the registry's produced_by
                          for X lists that skill. (ERROR)
6. registry-has-producer : every registry id is produced by at least one skill that
                          actually declares `produces` for it. (WARN — backfill in progress)
7. path-match            : if a skill body still has a `WRITES` line whose path maps
                          to a produced id, it must equal the registry path. (WARN)

Exit code 1 on any ERROR. WARN never fails the build.

Requires PyYAML (same dependency as flows/_meta/verify_flows.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    sys.stderr.write("verify_artifacts.py requires PyYAML — `pip install pyyaml`\n")
    sys.exit(2)

VALID_KIND = {"durable", "scratch", "code"}
VALID_SIDE = {"concept", "impl"}

REPO = Path(__file__).resolve().parents[3]          # …/ai-assets-skaileup
REGISTRY = REPO / "skaileup" / "contracts" / "artifacts.yaml"
SKILLS_ROOT = REPO / "skaileup"


def load_registry() -> dict:
    data = yaml.safe_load(REGISTRY.read_text())
    return data.get("artifacts", {})


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text()
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return None


def ids_from(block, key) -> list[str]:
    """Pull the list of `id:` values under artifacts.<key>."""
    entries = (block or {}).get(key) or []
    out = []
    for e in entries:
        if isinstance(e, dict) and "id" in e:
            out.append(e["id"])
        elif isinstance(e, str):
            out.append(e)
    return out


def _stem(p: str) -> str:
    """Path prefix up to the first placeholder (<id> or {id}), trailing / stripped.
    Lets `_slice/impl/{slice_id}/x` and `_slice/impl/<slice_id>/x` compare equal."""
    cut = len(p)
    for ch in ("<", "{", "*"):
        i = p.find(ch)
        if i != -1:
            cut = min(cut, i)
    return p[:cut].rstrip("/")


def writes_paths(path: Path) -> list[str]:
    """Best-effort: literal paths under a `WRITES` DSL block in the body."""
    text = path.read_text()
    out, in_writes = [], False
    for line in text.splitlines():
        if line.strip() == "WRITES":
            in_writes = True
            continue
        if in_writes:
            stripped = line.strip().replace("\\", "")
            if not stripped or stripped[0].isupper() and stripped.split(" ")[0].isalpha() \
                    and stripped.split(" ")[0].isupper():
                # next DSL keyword line — stop
                in_writes = False
                continue
            token = stripped.split(" ")[0].split("—")[0].strip()
            if token.startswith("_concept") or token.startswith("_implementation") \
                    or token.startswith("_slice"):
                out.append(token)
    return out


def main() -> int:
    registry = load_registry()
    errors: list[str] = []
    warns: list[str] = []

    # known skill names
    skill_files = sorted(SKILLS_ROOT.rglob("SKILL.md"))
    name_of: dict[Path, str] = {}
    skills: dict[str, dict] = {}
    for sf in skill_files:
        fm = parse_frontmatter(sf) or {}
        name = fm.get("name")
        if name:
            name_of[sf] = name
            skills[name] = fm
    known_names = set(skills)

    # 1. registry well-formed
    for aid, entry in registry.items():
        for field in ("path", "kind", "side", "produced_by", "description"):
            if field not in entry:
                errors.append(f"[registry] {aid}: missing field '{field}'")
        if entry.get("kind") not in VALID_KIND:
            errors.append(f"[registry] {aid}: bad kind {entry.get('kind')!r}")
        if entry.get("side") not in VALID_SIDE:
            errors.append(f"[registry] {aid}: bad side {entry.get('side')!r}")

    # 2. producer-exists
    reg_producers: dict[str, set[str]] = {}
    for aid, entry in registry.items():
        pb = entry.get("produced_by", [])
        pb = [pb] if isinstance(pb, str) else list(pb or [])
        reg_producers[aid] = set(pb)
        for p in pb:
            if p not in known_names:
                errors.append(f"[registry] {aid}: produced_by '{p}' is not a known skill")

    # collect declarations
    declared_producers: dict[str, set[str]] = {}    # id -> skills that `produces`
    all_consumed: set[str] = set()
    for sf, name in name_of.items():
        fm = skills[name]
        arts = (fm.get("metadata") or {}).get("artifacts")
        if not arts:
            continue
        prod = ids_from(arts, "produces")
        cons = ids_from(arts, "consumes")
        req = ids_from(arts, "requires")

        for aid in prod + cons + req:
            if aid not in registry:
                errors.append(f"[{name}] uses unknown artifact id '{aid}' (not in registry)")

        for aid in prod:
            declared_producers.setdefault(aid, set()).add(name)
            # 5. bidirectional
            if aid in registry and name not in reg_producers.get(aid, set()):
                errors.append(
                    f"[{name}] produces '{aid}' but registry produced_by does not list it")

        all_consumed.update(cons)
        all_consumed.update(req)

        # 7. path match (best effort). Compare on the prefix up to the first
        #    placeholder (<id> / {id}) so templated paths match regardless of syntax.
        reg_paths = {_stem(registry[a]["path"]) for a in prod if a in registry}
        for wp in writes_paths(sf):
            wp_norm = _stem(wp)
            if reg_paths and not any(wp_norm.startswith(rp) or rp.startswith(wp_norm)
                                     for rp in reg_paths):
                warns.append(f"[{name}] WRITES '{wp}' matches no registry path for its produced ids")

    # 4. no-dangling: a consumed/required id must be produced by some skill OR have a
    #    registry producer (covers not-yet-backfilled producers).
    for aid in sorted(all_consumed):
        if aid not in registry:
            continue  # already reported in id-in-registry
        has_decl = aid in declared_producers
        has_reg = bool(reg_producers.get(aid))
        if not has_decl and not has_reg:
            errors.append(f"[graph] artifact '{aid}' is consumed/required but produced by no skill")

    # 6. registry-has-producer (warn until backfill complete)
    for aid in sorted(registry):
        if aid not in declared_producers:
            warns.append(f"[registry] '{aid}' has no skill declaring `produces` (backfill pending)")

    # report
    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(registry)} registry ids · {len(declared_producers)} with declared producers · "
          f"{len(errors)} errors · {len(warns)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
