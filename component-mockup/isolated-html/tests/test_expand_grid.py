"""Tests for the variant x state expander."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.expand_grid import expand  # noqa: E402


def test_cartesian_with_default_first() -> None:
    cells = expand(
        variants=["Default", "Compact"],
        states=["Loading", "Default", "Populated"],
    )
    # default state moved to position 0
    assert cells[0] == ("Default", "Default")
    assert cells[1] == ("Compact", "Default")
    assert len(cells) == 6


def test_row_major_order() -> None:
    cells = expand(variants=["A", "B"], states=["s1", "s2"])
    # row-major: state s1 across all variants first, then s2
    assert cells == [("A", "s1"), ("B", "s1"), ("A", "s2"), ("B", "s2")]


def test_default_only() -> None:
    cells = expand(variants=["default"], states=["default"])
    assert cells == [("default", "default")]


def test_default_in_variants_moved_first() -> None:
    cells = expand(variants=["Compact", "Default"], states=["Loading"])
    # default variant moves to position 0 too (column-wise default-first)
    assert cells[0] == ("Default", "Loading")
