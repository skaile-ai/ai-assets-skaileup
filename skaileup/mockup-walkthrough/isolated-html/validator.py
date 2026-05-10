#!/usr/bin/env python3
"""Validate produced HTML in `_concept/mockup-component/isolated-html/`.

Invariants (from the mini-plan's "Self-containment invariants"):

1. No `<link rel="stylesheet">` element anywhere.
2. No `<script>` element anywhere (inline or src-loaded).
3. No `<img src="http(s)://..."` referencing an external URL.
4. Every CSS variable referenced via `var(--name)` MUST have a `--name:`
   declaration somewhere in the document (inside `:root` or in any inline
   `style="..."` attribute).
5. (When `--components` provided) for each output `<stem>.html`, every
   variant x state declared in the source `<stem>.md` is present as exactly
   one `<div class="cell" data-variant="..." data-state="...">`.

Usage:
  python3 mockup-component/isolated-html/validator.py <out_dir> [--components <dir>]

Exits 0 on success, 1 on any violation. Violation lines are written to stderr.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Self-locate so the script can be run from anywhere.
_THIS = Path(__file__).resolve()
_SKILL_ROOT = _THIS.parent
if str(_SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILL_ROOT))

from scripts.parse_component import parse_component_md  # noqa: E402

# ---------------------------------------------------------------------------
# Regexes
# ---------------------------------------------------------------------------

_LINK_STYLESHEET_RE = re.compile(
    r"<link\b[^>]*\brel\s*=\s*['\"]?stylesheet['\"]?[^>]*>",
    re.I,
)
_SCRIPT_RE = re.compile(r"<script\b", re.I)
_IMG_EXTERNAL_RE = re.compile(
    r"<img\b[^>]*\bsrc\s*=\s*['\"](https?:|//)",
    re.I,
)
_CELL_RE = re.compile(
    r'<div\s+class="cell"\s+data-variant="([^"]+)"\s+data-state="([^"]+)"',
    re.I,
)
_VAR_REF_RE = re.compile(r"var\(\s*(--[a-z0-9-]+)\s*\)", re.I)
_VAR_DEF_RE = re.compile(r"(--[a-z0-9-]+)\s*:")


class ValidationError(RuntimeError):
    """Raised when the validator wants to surface an aggregate failure."""


def _check_no_link_stylesheet(html: str) -> list[str]:
    if _LINK_STYLESHEET_RE.search(html):
        return ["banned: <link rel='stylesheet'> element found"]
    return []


def _check_no_script(html: str) -> list[str]:
    if _SCRIPT_RE.search(html):
        return ["banned: <script> element found"]
    return []


def _check_no_external_img(html: str) -> list[str]:
    if _IMG_EXTERNAL_RE.search(html):
        return ["banned: external <img src='http(s)://...'> reference found"]
    return []


def _check_vars_defined(html: str) -> list[str]:
    refs = set(_VAR_REF_RE.findall(html))
    defs = set(_VAR_DEF_RE.findall(html))
    missing = sorted(refs - defs)
    if missing:
        return [f"undefined CSS var(s) referenced but not defined: {', '.join(missing)}"]
    return []


def _check_grid_cells(html: str, source_md: Path) -> list[str]:
    """Cross-reference: every variant x state in source MUST be a cell here."""
    component = parse_component_md(source_md)
    found = set(_CELL_RE.findall(html))
    # Apply the same default-first ordering the renderer uses.
    def _move_default(items: list[str]) -> list[str]:
        for i, x in enumerate(items):
            if x.lower() == "default" and i != 0:
                return [items[i], *items[:i], *items[i + 1 :]]
        return list(items)

    variants = _move_default(component.variants)
    states = _move_default(component.states)
    expected = {(v, s) for v in variants for s in states}
    missing = sorted(expected - found)
    extra = sorted(found - expected)
    errs: list[str] = []
    if missing:
        errs.append(
            f"missing variant x state cells: {missing} "
            f"(source: {source_md.name})"
        )
    if extra:
        errs.append(
            f"unexpected variant x state cells: {extra} "
            f"(source: {source_md.name})"
        )
    return errs


def validate_file(
    html_path: Path,
    *,
    components_dir: Path | None = None,
) -> list[str]:
    """Validate one rendered HTML file. Returns list of error strings (empty on pass)."""
    html_path = Path(html_path)
    html = html_path.read_text(encoding="utf-8")
    errors: list[str] = []
    errors.extend(_check_no_link_stylesheet(html))
    errors.extend(_check_no_script(html))
    errors.extend(_check_no_external_img(html))
    errors.extend(_check_vars_defined(html))
    if components_dir is not None:
        source_md = Path(components_dir) / f"{html_path.stem}.md"
        if source_md.is_file():
            errors.extend(_check_grid_cells(html, source_md))
        else:
            errors.append(
                f"missing source component spec for {html_path.name}: {source_md}"
            )
    # Prefix every error with the file path for actionable output.
    return [f"{html_path.name}: {e}" for e in errors]


def validate_dir(
    out_dir: Path,
    *,
    components_dir: Path | None = None,
) -> list[str]:
    """Walk `out_dir/*.html` and aggregate per-file violations."""
    out_dir = Path(out_dir)
    if not out_dir.is_dir():
        return [f"output dir does not exist: {out_dir}"]
    files = sorted(out_dir.glob("*.html"))
    if not files:
        return [f"no HTML files under {out_dir}"]
    errors: list[str] = []
    for f in files:
        errors.extend(validate_file(f, components_dir=components_dir))
    return errors


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="mockup-component-isolated-html-validator",
        description="Validate self-containment invariants for isolated-html output.",
    )
    p.add_argument("out_dir", type=Path, help="Directory containing rendered .html files")
    p.add_argument(
        "--components",
        type=Path,
        default=None,
        help="Optional: source components dir (cross-checks variant x state cells).",
    )
    args = p.parse_args(list(argv) if argv is not None else sys.argv[1:])

    errors = validate_dir(args.out_dir, components_dir=args.components)
    if errors:
        sys.stderr.write(
            f"[mockup-component-isolated-html] FAIL: {len(errors)} violation(s)\n"
        )
        for e in errors:
            sys.stderr.write(f"  - {e}\n")
        return 1
    sys.stdout.write(
        f"[mockup-component-isolated-html] OK: validated {args.out_dir}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
