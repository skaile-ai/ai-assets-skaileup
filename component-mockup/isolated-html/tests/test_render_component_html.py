"""Tests for the orchestrating HTML renderer."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.parse_component import Component  # noqa: E402
from scripts.render_component_html import render_html  # noqa: E402

MIN_TOKENS = {
    "colors": {
        "primary": "#6366f1",
        "background": "#0f172a",
        "surface": "#1e293b",
        "text": "#f8fafc",
        "text_muted": "#94a3b8",
        "border": "#334155",
        "error": "#ef4444",
    },
    "fonts": {"heading": "Inter, sans-serif", "body": "Inter, sans-serif", "mono": "monospace"},
    "radius": "8px",
    "spacing_base": "8px",
}


def _comp() -> Component:
    return Component(
        stem="button",
        pattern="generic",
        library_component="None",
        used_in=["experience/screens/foo.md"],
        data_entities=[],
        last_updated="2026-05-07",
        purpose="Click target.",
        variants=["Default", "Outlined"],
        states=["Default", "Loading", "Disabled"],
        anatomy="[ Button ]",
    )


def test_renders_grid_and_inline_style() -> None:
    html = render_html(_comp(), MIN_TOKENS)
    assert "<!doctype html>" in html.lower()
    assert "<style>" in html
    assert "--token-colors-primary" in html
    assert 'data-variant="Default"' in html
    assert 'data-state="Default"' in html
    # zero-build invariants
    lower = html.lower()
    assert "<link" not in lower
    assert "<script" not in lower
    # all variants x states cells present (2 x 3)
    assert html.count('class="cell"') == 6


def test_anatomy_rendered_when_present() -> None:
    html = render_html(_comp(), MIN_TOKENS)
    assert "<pre" in html
    assert "[ Button ]" in html


def test_no_anatomy_section_omitted_when_absent() -> None:
    c = _comp()
    c.anatomy = None
    html = render_html(c, MIN_TOKENS)
    assert "Anatomy" not in html


def test_default_pattern_fallback_for_unknown() -> None:
    c = _comp()
    c.pattern = "completely-unknown-pattern"
    html = render_html(c, MIN_TOKENS)
    # generic fallback still produces cells
    assert html.count('class="cell"') == 6


def test_data_table_pattern_emits_table_mock() -> None:
    c = _comp()
    c.pattern = "data_table"
    html = render_html(c, MIN_TOKENS)
    assert "<table" in html


def test_used_in_footer_when_provided() -> None:
    html = render_html(_comp(), MIN_TOKENS)
    assert "Used in" in html
    assert "experience/screens/foo.md" in html


def test_grid_has_cols_var_set_to_n_variants() -> None:
    html = render_html(_comp(), MIN_TOKENS)
    # 2 variants
    assert "--cols: 2" in html


def test_every_var_reference_is_defined() -> None:
    """Hand-rolled pre-validator check: every var(--x) referenced in the
    output must also appear as a `--x:` declaration somewhere in the file.
    """
    import re

    html = render_html(_comp(), MIN_TOKENS)
    refs = set(re.findall(r"var\((--[a-z0-9-]+)\)", html))
    # A var is "defined" if it appears as `--name:` at the start of a CSS
    # declaration anywhere — either inside the :root block or inside an
    # inline style attribute (e.g. `style="--cols: 2;"`).
    defs = set(re.findall(r"(--[a-z0-9-]+)\s*:", html))
    missing = refs - defs
    assert not missing, f"undefined CSS vars: {missing}"
