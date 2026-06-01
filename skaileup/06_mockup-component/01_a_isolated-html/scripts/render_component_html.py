"""Render a single component as a standalone HTML page.

Stdlib-only Python string templating per Task 2G mini-plan PF-8 decision.
Same choice as Task 2F (`mockup-walkthrough-static-html`) for renderer-family
consistency. The produced HTML embeds a single `<style>` block with a
`:root { ... }` declaration containing all flattened tokens, then a CSS-Grid
`variant x state` matrix where every cell carries `data-variant` / `data-state`.

See:
- `references/tokens_inlining.md` — token flattening rules.
- `references/pattern_mocks.md` — pattern -> cell-body mock registry.
"""
from __future__ import annotations

import html as _html
from typing import Any

from .expand_grid import expand
from .inline_tokens import flatten_to_css_vars, render_root_block
from .parse_component import Component


# ---------------------------------------------------------------------------
# Pattern -> cell-body mock registry. Each function returns inner HTML for the
# cell. All styling is via inline `style="..."` referencing inlined tokens.
# ---------------------------------------------------------------------------


def _state_modifiers(state: str) -> dict[str, str]:
    s = state.lower()
    style: dict[str, str] = {}
    caption_extra = ""
    if "loading" in s:
        style["opacity"] = "0.6"
        caption_extra = " (loading)"
    elif "empty" in s:
        style["border-style"] = "dashed"
        caption_extra = " (empty)"
    elif "error" in s:
        style["border-color"] = "var(--token-colors-error)"
        style["color"] = "var(--token-colors-error)"
    elif "disabled" in s:
        style["opacity"] = "0.5"
    return {
        "style": "; ".join(f"{k}: {v}" for k, v in style.items()),
        "caption_extra": caption_extra,
    }


def _variant_modifiers(variant: str) -> dict[str, str]:
    v = variant.lower()
    style: dict[str, str] = {}
    if "compact" in v:
        style["padding"] = "6px"
    elif "outlined" in v or "secondary" in v:
        style["background"] = "var(--token-colors-background)"
        style["border-width"] = "2px"
    return {"style": "; ".join(f"{k}: {v}" for k, v in style.items())}


def _esc(value: Any) -> str:
    return _html.escape(str(value), quote=True)


def _mock_generic(component: Component, variant: str, state: str) -> str:
    s_mod = _state_modifiers(state)
    return (
        f'<div class="swatch" style="height: 32px; border-radius: var(--token-radius); '
        f'background: var(--token-colors-primary); {s_mod["style"]}"></div>'
        f'<p class="caption" style="margin: 6px 0 0 0; color: var(--token-colors-text-muted); '
        f'font-size: 11px;">{_esc(component.stem)} · {_esc(variant)} · {_esc(state)}'
        f'{_esc(s_mod["caption_extra"])}</p>'
    )


def _mock_status_badge(component: Component, variant: str, state: str) -> str:
    s_mod = _state_modifiers(state)
    return (
        f'<span style="display: inline-block; padding: 4px 10px; border-radius: 999px; '
        f'background: var(--token-colors-primary); color: var(--token-colors-background); '
        f'font-size: 11px; {s_mod["style"]}">{_esc(variant)} · {_esc(state)}</span>'
    )


def _mock_data_table(component: Component, variant: str, state: str) -> str:
    s_mod = _state_modifiers(state)
    rows = ""
    for i in range(3):
        rows += (
            f'<tr><td style="padding: 4px 6px; border-top: 1px solid var(--token-colors-border);">'
            f'row {i + 1}</td>'
            f'<td style="padding: 4px 6px; border-top: 1px solid var(--token-colors-border);">'
            f'val {i + 1}</td></tr>'
        )
    return (
        f'<table style="width: 100%; border-collapse: collapse; font-size: 11px; '
        f'color: var(--token-colors-text); {s_mod["style"]}">'
        f'<thead><tr>'
        f'<th style="text-align: left; padding: 4px 6px; color: var(--token-colors-text-muted);">'
        f'col1</th>'
        f'<th style="text-align: left; padding: 4px 6px; color: var(--token-colors-text-muted);">'
        f'col2</th>'
        f'</tr></thead>'
        f'<tbody>{rows}</tbody>'
        f'</table>'
    )


def _mock_card(component: Component, variant: str, state: str) -> str:
    s_mod = _state_modifiers(state)
    return (
        f'<div style="display: flex; flex-direction: column; gap: 4px; {s_mod["style"]}">'
        f'<strong style="font-size: 12px;">{_esc(component.stem)}</strong>'
        f'<span style="color: var(--token-colors-text-muted); font-size: 11px;">'
        f'{_esc(variant)} · {_esc(state)}</span>'
        f'<div style="height: 2px; background: var(--token-colors-border); border-radius: '
        f'var(--token-radius);"></div>'
        f'<div style="height: 2px; background: var(--token-colors-border); border-radius: '
        f'var(--token-radius); width: 60%;"></div>'
        f'</div>'
    )


def _mock_form(component: Component, variant: str, state: str) -> str:
    s_mod = _state_modifiers(state)
    return (
        f'<div style="display: flex; flex-direction: column; gap: 4px; {s_mod["style"]}">'
        f'<label style="font-size: 11px; color: var(--token-colors-text-muted);">Field</label>'
        f'<div style="height: 24px; border: 1px solid var(--token-colors-border); '
        f'border-radius: var(--token-radius); background: var(--token-colors-background);"></div>'
        f'<span style="display: inline-block; align-self: flex-start; padding: 3px 8px; '
        f'border-radius: var(--token-radius); background: var(--token-colors-primary); '
        f'color: var(--token-colors-background); font-size: 11px;">Submit</span>'
        f'</div>'
    )


def _mock_empty_state(component: Component, variant: str, state: str) -> str:
    return (
        f'<div style="display: flex; flex-direction: column; align-items: center; gap: 4px; '
        f'padding: 8px;">'
        f'<div style="width: 24px; height: 24px; border: 1px dashed '
        f'var(--token-colors-border); border-radius: 50%;"></div>'
        f'<span style="color: var(--token-colors-text-muted); font-size: 11px; '
        f'font-style: italic;">{_esc(variant)} · {_esc(state)}</span>'
        f'</div>'
    )


def _mock_confirm_dialog(component: Component, variant: str, state: str) -> str:
    s_mod = _state_modifiers(state)
    return (
        f'<div style="display: flex; flex-direction: column; gap: 6px; {s_mod["style"]}">'
        f'<strong style="font-size: 12px;">Confirm?</strong>'
        f'<span style="color: var(--token-colors-text-muted); font-size: 11px;">'
        f'{_esc(variant)} · {_esc(state)}</span>'
        f'<div style="display: flex; gap: 6px;">'
        f'<span style="padding: 3px 8px; border-radius: var(--token-radius); '
        f'background: var(--token-colors-primary); color: var(--token-colors-background); '
        f'font-size: 11px;">Yes</span>'
        f'<span style="padding: 3px 8px; border-radius: var(--token-radius); '
        f'border: 1px solid var(--token-colors-border); font-size: 11px;">No</span>'
        f'</div></div>'
    )


PATTERN_MOCKS = {
    "generic": _mock_generic,
    "data_table": _mock_data_table,
    "status_badge": _mock_status_badge,
    "card": _mock_card,
    "form": _mock_form,
    "empty_state": _mock_empty_state,
    "confirm_dialog": _mock_confirm_dialog,
}


# ---------------------------------------------------------------------------
# Page rendering
# ---------------------------------------------------------------------------


_BASE_CSS = """\
*, *::before, *::after { box-sizing: border-box; }
body {
  font-family: var(--token-fonts-body), system-ui, sans-serif;
  color: var(--token-colors-text);
  background: var(--token-colors-background);
  margin: 0;
  padding: 24px;
  line-height: 1.4;
}
header h1 {
  font-family: var(--token-fonts-heading), system-ui, sans-serif;
  margin: 0 0 4px 0;
}
.subtitle { margin: 0 0 4px 0; color: var(--token-colors-text); }
.meta { margin: 0 0 24px 0; color: var(--token-colors-text-muted); font-size: 12px; }
section.variant-state-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: 120px repeat(var(--cols), minmax(120px, 1fr));
  align-items: start;
  margin-bottom: 24px;
}
.grid-header, .grid-row-label {
  color: var(--token-colors-text-muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.cell {
  border: 1px solid var(--token-colors-border);
  border-radius: var(--token-radius);
  padding: 12px;
  background: var(--token-colors-surface);
  min-height: 64px;
}
section.anatomy pre {
  background: var(--token-colors-surface);
  border: 1px solid var(--token-colors-border);
  border-radius: var(--token-radius);
  padding: 12px;
  overflow-x: auto;
  color: var(--token-colors-text);
  font-family: var(--token-fonts-mono), ui-monospace, monospace;
  font-size: 12px;
}
footer { margin-top: 24px; color: var(--token-colors-text-muted); font-size: 12px; }
footer a { color: var(--token-colors-text-muted); }
"""


def _humanize(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").title()


def _render_grid(component: Component) -> str:
    variants = component.variants
    states = component.states
    cells = expand(variants=variants, states=states)
    # Re-order variants/states with default-first for header rendering too,
    # mirroring `expand`.
    def _default_first(items: list[str]) -> list[str]:
        for i, x in enumerate(items):
            if x.lower() == "default" and i != 0:
                return [items[i], *items[:i], *items[i + 1 :]]
        return list(items)

    variants_o = _default_first(variants)
    states_o = _default_first(states)

    pattern_fn = PATTERN_MOCKS.get(component.pattern or "generic", _mock_generic)

    lines: list[str] = []
    lines.append(
        f'  <section class="variant-state-grid" style="--cols: {len(variants_o)};">'
    )
    # Top-left empty cell
    lines.append('    <div></div>')
    # Column headers (variants)
    for v in variants_o:
        lines.append(f'    <div class="grid-header">{_esc(v)}</div>')
    # Rows
    cell_iter = iter(cells)
    for s in states_o:
        lines.append(f'    <div class="grid-row-label">{_esc(s)}</div>')
        for v in variants_o:
            cv, cs = next(cell_iter)
            assert cv == v and cs == s, "expand() ordering drift vs grid render"
            v_mod = _variant_modifiers(v)
            cell_inner = pattern_fn(component, v, s)
            cell_style = v_mod["style"]
            style_attr = f' style="{cell_style}"' if cell_style else ""
            lines.append(
                f'    <div class="cell" data-variant="{_esc(v)}" '
                f'data-state="{_esc(s)}"{style_attr}>{cell_inner}</div>'
            )
    lines.append('  </section>')
    return "\n".join(lines)


def _render_used_in(component: Component) -> str:
    if not component.used_in:
        return ""
    items = "\n".join(
        f'    <li><a href="../../{_esc(u)}">{_esc(u)}</a></li>'
        for u in component.used_in
    )
    return (
        '  <footer>\n'
        '    <h2>Used in</h2>\n'
        '    <ul>\n'
        f'{items}\n'
        '    </ul>\n'
        '  </footer>'
    )


def render_html(component: Component, tokens: dict[str, Any]) -> str:
    """Render the component as a complete standalone HTML page (string)."""
    pattern_human = _humanize(component.pattern or "generic")
    title = f"Component: {pattern_human} — {component.stem}"

    css_vars = flatten_to_css_vars(tokens)
    root_block = render_root_block(css_vars)

    grid = _render_grid(component)

    anatomy_section = ""
    if component.anatomy:
        anatomy_section = (
            '  <section class="anatomy">\n'
            '    <h2>Anatomy</h2>\n'
            f'    <pre>{_esc(component.anatomy)}</pre>\n'
            '  </section>'
        )

    used_in = _render_used_in(component)

    library_line = (
        f"Library mapping: {_esc(component.library_component)}"
        if component.library_component
        else ""
    )
    if component.last_updated:
        sep = " · " if library_line else ""
        library_line = f"{library_line}{sep}Last updated: {_esc(component.last_updated)}"

    purpose_html = (
        f'<p class="subtitle">{_esc(component.purpose)}</p>'
        if component.purpose
        else ""
    )
    meta_html = f'<p class="meta">{library_line}</p>' if library_line else ""

    parts: list[str] = []
    parts.append("<!doctype html>")
    parts.append('<html lang="en">')
    parts.append("<head>")
    parts.append('  <meta charset="utf-8">')
    parts.append(f"  <title>{_esc(title)}</title>")
    parts.append("  <style>")
    # Indent the root block so it sits inside <style>
    parts.append("    " + root_block.replace("\n", "\n    "))
    parts.append("    " + _BASE_CSS.replace("\n", "\n    ").rstrip())
    parts.append("  </style>")
    parts.append("</head>")
    parts.append("<body>")
    parts.append("  <header>")
    parts.append(f"    <h1>Component: {_esc(pattern_human)}</h1>")
    if purpose_html:
        parts.append(f"    {purpose_html}")
    if meta_html:
        parts.append(f"    {meta_html}")
    parts.append("  </header>")
    parts.append(grid)
    if anatomy_section:
        parts.append(anatomy_section)
    if used_in:
        parts.append(used_in)
    parts.append("</body>")
    parts.append("</html>")
    parts.append("")  # trailing newline
    return "\n".join(parts)
