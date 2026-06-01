"""Flatten the canonical tokens.json into inline CSS custom properties.

See `references/tokens_inlining.md` for the pinned naming rules. The output
is a list of `--name: value;` strings; `render_root_block()` wraps them in
`:root { ... }` for embedding inside a `<style>` block.
"""
from __future__ import annotations

import re
import warnings
from typing import Any, Iterable

# `tailwind:` is the authoritative passthrough block — its variable names
# are already in CSS-var form (start with `--`) and must not be re-prefixed.
_TAILWIND_KEY = "tailwind"

_CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])([A-Z])")


def _to_kebab(segment: str) -> str:
    """Convert one path segment to kebab-case.

    Underscores -> hyphen. CamelCase -> hyphen + lowercase.
    """
    s = _CAMEL_BOUNDARY.sub(r"-\1", segment).lower()
    return s.replace("_", "-")


def _join_path(parts: Iterable[str]) -> str:
    return "-".join(_to_kebab(p) for p in parts)


def _flatten_recursive(
    obj: Any, path: tuple[str, ...], out: list[str]
) -> None:
    """Walk a nested dict and emit `--token-<path>: <value>;` lines.

    Non-string leaves are skipped with a warning. Empty dict leaves are
    skipped silently.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            _flatten_recursive(v, path + (str(k),), out)
        return
    if obj is None:
        return
    if not isinstance(obj, str):
        warnings.warn(
            f"skipping non-string leaf at tokens.{'.'.join(path)} "
            f"(type={type(obj).__name__})",
            stacklevel=2,
        )
        return
    name = _join_path(path)
    out.append(f"--token-{name}: {obj};")


def _flatten_tailwind_passthrough(block: Any, out: list[str]) -> None:
    """Emit tailwind: keys verbatim (they already start with `--`)."""
    if not isinstance(block, dict):
        warnings.warn(
            "tokens.tailwind is not a mapping; skipping passthrough block",
            stacklevel=2,
        )
        return
    for k, v in block.items():
        if not isinstance(k, str) or not k.startswith("--"):
            warnings.warn(
                f"skipping non-CSS-var key in tokens.tailwind: {k!r}",
                stacklevel=2,
            )
            continue
        if not isinstance(v, str):
            warnings.warn(
                f"skipping non-string tailwind value at {k}", stacklevel=2
            )
            continue
        out.append(f"{k}: {v};")


def flatten_to_css_vars(tokens: dict[str, Any]) -> list[str]:
    """Return the ordered list of `--name: value;` declarations.

    Ordering: flattened tree first (deterministic by source-key order),
    then the `tailwind:` passthrough block last so its values override
    same-named entries from the flattened tree.
    """
    out: list[str] = []
    if not isinstance(tokens, dict):
        raise TypeError("tokens must be a JSON mapping")
    for k, v in tokens.items():
        if k == _TAILWIND_KEY:
            continue
        _flatten_recursive(v, (str(k),), out)
    if _TAILWIND_KEY in tokens:
        _flatten_tailwind_passthrough(tokens[_TAILWIND_KEY], out)
    return out


def render_root_block(vars_: list[str], indent: str = "    ") -> str:
    """Wrap the variable list in a `:root { ... }` declaration."""
    body = "\n".join(f"{indent}{line}" for line in vars_)
    return f":root {{\n{body}\n}}"
