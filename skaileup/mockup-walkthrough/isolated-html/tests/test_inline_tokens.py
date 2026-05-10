"""Tests for token flattening into CSS custom properties."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.inline_tokens import flatten_to_css_vars, render_root_block  # noqa: E402


def test_flatten_basic() -> None:
    tokens = {
        "colors": {"primary": "#6366f1", "text_muted": "#94a3b8"},
        "radius": "8px",
        "tailwind": {"--color-primary": "#6366f1", "--radius": "0.5rem"},
    }
    vars_ = flatten_to_css_vars(tokens)
    assert "--token-colors-primary: #6366f1;" in vars_
    assert "--token-colors-text-muted: #94a3b8;" in vars_
    assert "--token-radius: 8px;" in vars_
    # tailwind block passes through and is emitted last (so it overrides)
    passthrough_idx = vars_.index("--color-primary: #6366f1;")
    flattened_idx = vars_.index("--token-colors-primary: #6366f1;")
    assert passthrough_idx > flattened_idx
    assert "--radius: 0.5rem;" in vars_


def test_skips_non_string_leaf() -> None:
    tokens = {"radius": 8, "colors": {"primary": "#fff"}}
    vars_ = flatten_to_css_vars(tokens)
    # int leaf skipped
    assert all(not v.startswith("--token-radius:") for v in vars_)
    assert "--token-colors-primary: #fff;" in vars_


def test_render_root_block_wraps_vars() -> None:
    out = render_root_block(["--a: 1;", "--b: 2;"])
    assert ":root {" in out
    assert "--a: 1;" in out
    assert "--b: 2;" in out
    assert out.strip().endswith("}")


def test_camel_case_segment_kebabbed() -> None:
    tokens = {"colorScheme": {"primaryFg": "#abc"}}
    vars_ = flatten_to_css_vars(tokens)
    assert "--token-color-scheme-primary-fg: #abc;" in vars_
