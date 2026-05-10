#!/usr/bin/env python3
"""validator.py — check that every flow skill is covered by its bundle.

Read-only. Does not modify any files.

Run from repo root:
  python lab/compile-bundle/validator.py

Exit codes:
  0  All bundles cover their flows (or no gaps found)
  2  At least one coverage gap found
  1  Internal error (parse failure, circular inheritance)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _bundle_lib import load_bundles, load_flows, resolve_ancestors

FLOWS_DIR = Path("flows")
BUNDLES_DIR = Path("bundles")


def main(
    flows_dir: Path = FLOWS_DIR,
    bundles_dir: Path = BUNDLES_DIR,
) -> None:
    flows = load_flows(flows_dir)
    bundles = load_bundles(bundles_dir)

    gaps_found = False

    for stem, flow_skills in sorted(flows.items()):
        if stem not in bundles:
            print(f"WARNING: no bundle for flow '{stem}' — skipping")
            continue

        try:
            ancestor_skills = resolve_ancestors(stem, bundles)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

        covered = set(bundles[stem]["skill_refs"]) | ancestor_skills
        missing = [s for s in flow_skills if s not in covered]

        if missing:
            print(f"FAIL: {stem}.bundle.yaml is missing {len(missing)} skill(s): {missing}")
            gaps_found = True

    if not gaps_found:
        print("PASS — all bundles cover their flows")
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
