"""Tests for the isolated-html output validator."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.parse_component import parse_component_md  # noqa: E402
from scripts.render_component_html import render_html  # noqa: E402
from validator import (  # noqa: E402
    ValidationError,
    validate_dir,
    validate_file,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "minimal"


def _render_fixture(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    component = parse_component_md(FIXTURE_DIR / "button.md")
    tokens = json.loads((FIXTURE_DIR / "tokens.json").read_text(encoding="utf-8"))
    html = render_html(component, tokens)
    out = out_dir / f"{component.stem}.html"
    out.write_text(html, encoding="utf-8")
    return out


def test_passes_clean_snapshot(tmp_path: Path) -> None:
    out_path = _render_fixture(tmp_path)
    errors = validate_file(out_path, components_dir=FIXTURE_DIR)
    assert errors == [], errors


def test_passes_dir_walk(tmp_path: Path) -> None:
    _render_fixture(tmp_path)
    errors = validate_dir(tmp_path, components_dir=FIXTURE_DIR)
    assert errors == [], errors


def test_undefined_var_fails(tmp_path: Path) -> None:
    out_path = _render_fixture(tmp_path)
    text = out_path.read_text(encoding="utf-8")
    # Reference an undefined variable in body.
    text = text.replace(
        '<body>',
        '<body><div style="color: var(--token-does-not-exist);">x</div>',
    )
    out_path.write_text(text, encoding="utf-8")
    errors = validate_file(out_path, components_dir=FIXTURE_DIR)
    assert any("undefined" in e.lower() for e in errors), errors


def test_link_stylesheet_banned(tmp_path: Path) -> None:
    out_path = _render_fixture(tmp_path)
    text = out_path.read_text(encoding="utf-8")
    text = text.replace(
        "</head>",
        '<link rel="stylesheet" href="external.css"></head>',
    )
    out_path.write_text(text, encoding="utf-8")
    errors = validate_file(out_path, components_dir=FIXTURE_DIR)
    assert any("link" in e.lower() and "stylesheet" in e.lower() for e in errors), errors


def test_script_banned(tmp_path: Path) -> None:
    out_path = _render_fixture(tmp_path)
    text = out_path.read_text(encoding="utf-8")
    text = text.replace("</head>", "<script>alert('x')</script></head>")
    out_path.write_text(text, encoding="utf-8")
    errors = validate_file(out_path, components_dir=FIXTURE_DIR)
    assert any("script" in e.lower() for e in errors), errors


def test_external_img_warns_or_fails(tmp_path: Path) -> None:
    out_path = _render_fixture(tmp_path)
    text = out_path.read_text(encoding="utf-8")
    text = text.replace(
        "<body>",
        '<body><img src="https://example.com/x.png">',
    )
    out_path.write_text(text, encoding="utf-8")
    errors = validate_file(out_path, components_dir=FIXTURE_DIR)
    assert any("external" in e.lower() and "img" in e.lower() for e in errors), errors


def test_missing_cell_fails(tmp_path: Path) -> None:
    out_path = _render_fixture(tmp_path)
    text = out_path.read_text(encoding="utf-8")
    # Drop the very first cell entirely (Default x Default).
    import re

    text2, n = re.subn(
        r'<div class="cell" data-variant="Default" data-state="Default"[^>]*>.*?</div>',
        "",
        text,
        count=1,
        flags=re.S,
    )
    assert n == 1, "expected to find a Default x Default cell to delete"
    out_path.write_text(text2, encoding="utf-8")
    errors = validate_file(out_path, components_dir=FIXTURE_DIR)
    assert any("variant" in e.lower() and "state" in e.lower() for e in errors), errors


def test_validator_main_exit_zero_on_clean(tmp_path: Path) -> None:
    _render_fixture(tmp_path)
    from validator import main as validator_main

    rc = validator_main([str(tmp_path), "--components", str(FIXTURE_DIR)])
    assert rc == 0


def test_validator_main_exit_nonzero_on_bad(tmp_path: Path) -> None:
    out_path = _render_fixture(tmp_path)
    text = out_path.read_text(encoding="utf-8")
    text = text.replace("</head>", "<script>x</script></head>")
    out_path.write_text(text, encoding="utf-8")
    from validator import main as validator_main

    rc = validator_main([str(tmp_path), "--components", str(FIXTURE_DIR)])
    assert rc != 0
