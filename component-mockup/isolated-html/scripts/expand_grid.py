"""Cartesian expansion of variants x states into row-major cell order.

Returns a flat list of (variant, state) tuples in row-major order
(states are rows, variants are columns), with any case-insensitive
"default" entry moved to position 0 in both axes for deterministic output.
"""
from __future__ import annotations


def _move_default_first(items: list[str]) -> list[str]:
    for i, val in enumerate(items):
        if val.lower() == "default" and i != 0:
            return [items[i], *items[:i], *items[i + 1 :]]
    return items


def expand(variants: list[str], states: list[str]) -> list[tuple[str, str]]:
    """Return [(variant, state)] in row-major order with default-first ordering."""
    v = _move_default_first(list(variants))
    s = _move_default_first(list(states))
    cells: list[tuple[str, str]] = []
    for state in s:
        for variant in v:
            cells.append((variant, state))
    return cells
