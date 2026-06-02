"""_bundle_lib.py — shared data loading and ancestry resolution for compile-bundle.

Internal module — imported by compile_bundle.py and validator.py.
Not a standalone script.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

import yaml


def bare_name(ref: str) -> str:
    """Strip the `kind:` prefix and any publisher segment, returning the bare asset name.

    Canonical ref form is ``kind:@publisher/name`` (e.g. ``skill:@skaile-ai/concept-brief``).
    Also tolerates legacy ``kind:name`` and ``kind:name@publisher`` shapes.
    """
    body = ref.split(":", 1)[1] if ":" in ref else ref
    if body.startswith("@"):
        return body.split("/", 1)[1] if "/" in body else body
    return body.split("@", 1)[0]


class BundleData(TypedDict):
    bundle_refs: list[str]   # bare parent stems, e.g. ["mvp"]
    skill_refs: list[str]    # bare skill names, e.g. ["concept-brief"]
    other_refs: list[str]    # any other requires: entries (preserved verbatim)
    raw_text: str            # original file text for in-place patching
    path: Path               # file path for writing back


def load_flows(flows_dir: Path) -> dict[str, list[str]]:
    """Return {stem: [skill_name, ...]} in node document order.

    Stem is the filename without the .flow.yaml suffix.
    Flows are co-located with their bundles under flows_dir/<app>/<app>.flow.yaml.
    Includes nodes with optional: true — they are still required by the bundle.
    """
    result: dict[str, list[str]] = {}
    for path in sorted(flows_dir.glob("*/*.flow.yaml")):
        stem = path.name.removesuffix(".flow.yaml")
        try:
            flow = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            print(f"ERROR: malformed YAML in {path}: {exc}", file=sys.stderr)
            sys.exit(1)
        result[stem] = list(dict.fromkeys(
            node["data"]["skill"]
            for node in flow.get("nodes", [])
            if node.get("type") == "skill"
            and isinstance(node.get("data"), dict)
            and "skill" in node["data"]
        ))
    return result


def load_bundles(flows_dir: Path) -> dict[str, BundleData]:
    """Return {stem: BundleData} for each *.bundle.yaml file.

    Bundles are co-located with their flows under flows_dir/<app>/<app>.bundle.yaml.
    Stem is the filename without the .bundle.yaml suffix.
    Missing requires: key is treated as an empty list.
    All skill:/bundle: prefixes are stripped; bare names are stored.
    """
    result: dict[str, BundleData] = {}
    for path in sorted(flows_dir.glob("*/*.bundle.yaml")):
        stem = path.name.removesuffix(".bundle.yaml")
        raw_text = path.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(raw_text) or {}
        except yaml.YAMLError as exc:
            print(f"ERROR: malformed YAML in {path}: {exc}", file=sys.stderr)
            sys.exit(1)
        requires = [str(r) for r in (data.get("requires") or [])]
        result[stem] = BundleData(
            bundle_refs=[bare_name(r) for r in requires if r.startswith("bundle:")],
            skill_refs=[bare_name(r) for r in requires if r.startswith("skill:")],
            other_refs=[r for r in requires if not r.startswith(("bundle:", "skill:"))],
            raw_text=raw_text,
            path=path,
        )
    return result


def resolve_ancestors(
    stem: str,
    bundles: dict[str, BundleData],
    _path: tuple[str, ...] | None = None,
) -> set[str]:
    """Return the union of all bare skill names from all ancestor bundles.

    Resolution rule: bundle:foo → bundles[foo].
    Traversal order does not matter (result is a set union).
    Raises ValueError on circular inheritance with the full cycle path.
    """
    if _path is None:
        _path = ()
    if stem in _path:
        idx = _path.index(stem)
        cycle = " → ".join(_path[idx:]) + f" → {stem}"
        raise ValueError(f"Circular bundle inheritance detected: {cycle}")
    _path = _path + (stem,)

    bundle = bundles.get(stem)
    if bundle is None:
        return set()

    ancestor_skills: set[str] = set()
    for parent_stem in bundle["bundle_refs"]:
        parent = bundles.get(parent_stem)
        if parent is None:
            print(
                f"WARNING: bundle '{stem}' references unknown bundle '{parent_stem}' — skipping",
                file=sys.stderr,
            )
            continue
        ancestor_skills.update(parent["skill_refs"])
        ancestor_skills.update(resolve_ancestors(parent_stem, bundles, _path))
    return ancestor_skills
