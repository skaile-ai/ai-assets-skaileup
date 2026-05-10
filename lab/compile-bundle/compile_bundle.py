#!/usr/bin/env python3
"""compile_bundle.py — sync bundles/*.bundle.yaml from flows/*.flow.yaml.

Additive only: adds missing skill: entries, never removes anything.
Inheritance-aware: skips skills already covered by ancestor bundles.

Run from repo root:
  python lab/compile-bundle/compile_bundle.py

Exit codes:
  0  Completed (bundles updated or already up to date)
  1  Internal error (parse failure, circular inheritance)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _bundle_lib import load_bundles, load_flows, resolve_ancestors

FLOWS_DIR = Path("flows")
BUNDLES_DIR = Path("bundles")


def insert_skills(raw_text: str, missing: list[str]) -> str:
    """Insert missing skill lines at the correct position in bundle YAML text.

    Priority:
      1. After the last '  - skill:' line.
      2. Before the first '  - bundle:' line (if no skill lines exist).
      3. After the 'requires:' key line (if neither skill nor bundle lines exist).
    """
    lines = raw_text.splitlines(keepends=True)

    last_skill_idx: int | None = None
    first_bundle_idx: int | None = None
    requires_idx: int | None = None

    for i, line in enumerate(lines):
        if line.startswith("  - skill:"):
            last_skill_idx = i
        if first_bundle_idx is None and line.startswith("  - bundle:"):
            first_bundle_idx = i
        if requires_idx is None and line.strip() == "requires:":
            requires_idx = i

    if last_skill_idx is not None:
        insert_at = last_skill_idx + 1
    elif first_bundle_idx is not None:
        insert_at = first_bundle_idx
    elif requires_idx is not None:
        insert_at = requires_idx + 1
    else:
        insert_at = len(lines)

    new_lines = [f"  - skill:{name}\n" for name in missing]
    lines[insert_at:insert_at] = new_lines
    return "".join(lines)


def main(
    flows_dir: Path = FLOWS_DIR,
    bundles_dir: Path = BUNDLES_DIR,
) -> None:
    flows = load_flows(flows_dir)
    bundles = load_bundles(bundles_dir)

    any_updated = False

    for stem, flow_skills in sorted(flows.items()):
        if stem not in bundles:
            print(f"WARNING: no bundle for flow '{stem}' — skipping", file=sys.stderr)
            continue

        try:
            ancestor_skills = resolve_ancestors(stem, bundles)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

        covered = set(bundles[stem]["skill_refs"]) | ancestor_skills
        missing = [s for s in flow_skills if s not in covered]

        if not missing:
            continue

        bundle = bundles[stem]
        new_text = insert_skills(bundle["raw_text"], missing)
        bundle["path"].write_text(new_text, encoding="utf-8")
        names = ", ".join(missing)
        print(f"Added {len(missing)} skill(s) to {stem}.bundle.yaml: [{names}]")
        any_updated = True

    if not any_updated:
        print("All bundles up to date.")


if __name__ == "__main__":
    main()
