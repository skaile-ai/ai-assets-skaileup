#!/usr/bin/env python3
"""Orchestrator: glob components -> parse -> render -> write per-component HTML.

Usage:
  python3 mockup-component/isolated-html/scripts/run.py \\
    --components _concept/experience/screens/components \\
    --tokens _concept/discovery/brand/tokens.json \\
    --out _concept/mockup-component/isolated-html
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make the script runnable both as a module (`python3 -m scripts.run`) and as
# a file (`python3 scripts/run.py`). When run as a file, __package__ is empty,
# so we need to put the skill root on sys.path before the relative imports.
_THIS = Path(__file__).resolve()
_SKILL_ROOT = _THIS.parents[1]
if __package__ in (None, ""):
    if str(_SKILL_ROOT) not in sys.path:
        sys.path.insert(0, str(_SKILL_ROOT))
    from scripts.parse_component import parse_component_md  # type: ignore
    from scripts.render_component_html import render_html  # type: ignore
else:
    from .parse_component import parse_component_md
    from .render_component_html import render_html


def _err(msg: str) -> None:
    sys.stderr.write(f"[mockup-component-isolated-html] ERROR: {msg}\n")


def _info(msg: str) -> None:
    sys.stdout.write(f"[mockup-component-isolated-html] {msg}\n")


def run(components_dir: Path, tokens_path: Path, out_dir: Path) -> int:
    """Render one HTML per component spec. Returns process exit code."""
    components_dir = Path(components_dir)
    tokens_path = Path(tokens_path)
    out_dir = Path(out_dir)

    if not components_dir.is_dir():
        _err(
            f"components dir not found: {components_dir}. "
            "Run `experience-components` first to produce component specs."
        )
        return 2
    if not tokens_path.is_file():
        _err(
            f"tokens file not found: {tokens_path}. "
            "Run `design-brand-visual` (or equivalent) first to produce tokens.json."
        )
        return 2

    try:
        tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        _err(f"invalid JSON in {tokens_path}: {e}")
        return 2
    if not isinstance(tokens, dict):
        _err(f"tokens.json must be a JSON object at top level, got {type(tokens).__name__}")
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)

    # Glob *.md, exclude underscore-prefixed (e.g., _SKILL.md, _README.md).
    sources = sorted(
        p for p in components_dir.glob("*.md") if not p.name.startswith("_")
    )
    if not sources:
        _err(f"no component .md files found under {components_dir}")
        return 2

    rendered = 0
    for src in sources:
        try:
            comp = parse_component_md(src)
        except ValueError as e:
            _err(f"skipping {src.name}: {e}")
            continue
        html = render_html(comp, tokens)
        out_path = out_dir / f"{comp.stem}.html"
        out_path.write_text(html, encoding="utf-8")
        _info(f"rendered {src.name} -> {out_path}")
        rendered += 1

    _info(f"done — {rendered} file(s) written to {out_dir}")
    return 0 if rendered > 0 else 2


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="mockup-component-isolated-html",
        description="Render one standalone HTML per component spec.",
    )
    p.add_argument("--components", type=Path, required=True)
    p.add_argument("--tokens", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(list(argv) if argv is not None else sys.argv[1:])
    return run(args.components, args.tokens, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
