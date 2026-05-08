"""Tests for the component-md parser."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the skill root is on sys.path so `scripts.parse_component` resolves
# regardless of the cwd pytest is invoked from.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.parse_component import parse_component_md  # noqa: E402

FIXTURE = """---
pattern: data_table
library_component: PrimeVue DataTable
used_in: [experience/screens/02_dashboard/overview.md]
data_entities: [task]
last_updated: 2026-05-07
---

# Component: Data Table

## Purpose
Sortable, filterable, paginated table.

## Variants
- **Default:** full table
- **Compact:** reduced padding

## States
- **Loading:** skeleton rows
- **Empty:** empty state
- **Populated:** normal data

## Anatomy
~~~text
+------+------+
| col1 | col2 |
+------+------+
~~~
"""


def test_parses_frontmatter_and_sections(tmp_path: Path) -> None:
    f = tmp_path / "data_table.md"
    f.write_text(FIXTURE)
    result = parse_component_md(f)
    assert result.pattern == "data_table"
    assert result.library_component == "PrimeVue DataTable"
    assert result.variants == ["Default", "Compact"]
    assert result.states == ["Loading", "Empty", "Populated"]
    assert "Sortable" in result.purpose
    assert result.stem == "data_table"
    assert result.anatomy is not None
    assert "col1" in result.anatomy


def test_missing_variants_defaults_to_default(tmp_path: Path) -> None:
    src = """---
pattern: status_badge
last_updated: 2026-05-07
---

# Component: Status Badge

## Purpose
Tiny status indicator.

## States
- **Active:** green
- **Inactive:** gray
"""
    f = tmp_path / "status_badge.md"
    f.write_text(src)
    result = parse_component_md(f)
    assert result.variants == ["default"]
    assert result.states == ["Active", "Inactive"]
    assert result.anatomy is None


def test_missing_states_defaults_to_default(tmp_path: Path) -> None:
    src = """---
pattern: card
---

# Component: Card

## Purpose
Container.

## Variants
- **Default:** rounded
- **Outlined:** border only
"""
    f = tmp_path / "card.md"
    f.write_text(src)
    result = parse_component_md(f)
    assert result.variants == ["Default", "Outlined"]
    assert result.states == ["default"]


def test_default_state_moved_to_position_zero(tmp_path: Path) -> None:
    src = """---
pattern: button
---

# Component: Button

## Purpose
Click target.

## Variants
- **Primary:** filled
- **Secondary:** outlined

## States
- **Hover:** highlighted
- **Default:** rest state
- **Disabled:** muted
"""
    f = tmp_path / "button.md"
    f.write_text(src)
    result = parse_component_md(f)
    # default should be moved to position 0 (case-insensitive match)
    assert result.states[0].lower() == "default"
    assert "Hover" in result.states
    assert "Disabled" in result.states


def test_no_frontmatter_raises(tmp_path: Path) -> None:
    f = tmp_path / "broken.md"
    f.write_text("# No Frontmatter Here\n")
    import pytest

    with pytest.raises(ValueError):
        parse_component_md(f)
