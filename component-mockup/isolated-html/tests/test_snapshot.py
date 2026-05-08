"""Byte-for-byte snapshot test of the fixture's rendered HTML."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.parse_component import parse_component_md  # noqa: E402
from scripts.render_component_html import render_html  # noqa: E402

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "minimal"


def test_fixture_button_matches_snapshot() -> None:
    component = parse_component_md(FIXTURE_DIR / "button.md")
    tokens = json.loads((FIXTURE_DIR / "tokens.json").read_text(encoding="utf-8"))
    actual = render_html(component, tokens)
    expected = (FIXTURE_DIR / "expected.html").read_text(encoding="utf-8")
    if actual != expected:
        # Helpful diff snippet on failure: write actual to /tmp for inspection.
        Path("/tmp/_isolated_html_actual.html").write_text(actual, encoding="utf-8")
        # Find first diverging line for a quick locator.
        a_lines = actual.splitlines()
        e_lines = expected.splitlines()
        for i, (a, e) in enumerate(zip(a_lines, e_lines)):
            if a != e:
                raise AssertionError(
                    f"snapshot drift at line {i + 1}:\n"
                    f"  expected: {e!r}\n"
                    f"  actual:   {a!r}\n"
                    f"(full actual written to /tmp/_isolated_html_actual.html)"
                )
        # length mismatch fallthrough
        raise AssertionError(
            f"snapshot length differs: actual={len(a_lines)} lines vs expected={len(e_lines)} lines"
        )
