"""Parse a component markdown file (frontmatter + selected H2 sections).

Used by the `component-mockup-isolated-html` skill. Produces a `Component`
dataclass with everything the renderer needs from the source spec.

The expected source shape is documented in
`experience/components/SKILL.md` Step 5 and pinned in the skill's plan.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# H2 section header (case-sensitive — matches the canonical capitalization
# in `experience/components/SKILL.md` Step 5).
_H2_RE = re.compile(r"^##\s+(Purpose|Variants|States|Anatomy)\s*$", re.M)
# Bullet of the form `- **Name:** description` (description is ignored here;
# we only extract the bold name).
_BULLET_NAME_RE = re.compile(r"^\s*-\s*\*\*([^*:]+?):\*\*", re.M)
# First fenced ~~~text block under ## Anatomy.
_ANATOMY_FENCE_RE = re.compile(r"~~~text\s*\n(.*?)\n~~~", re.S)


@dataclass
class Component:
    """Parsed component spec.

    Field order matches the source markdown's declared sections.
    """

    stem: str
    pattern: str | None
    library_component: str | None
    used_in: list[str] = field(default_factory=list)
    data_entities: list[str] = field(default_factory=list)
    last_updated: str | None = None
    purpose: str = ""
    variants: list[str] = field(default_factory=list)
    states: list[str] = field(default_factory=list)
    anatomy: str | None = None


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body_markdown). Raises ValueError if missing."""
    if not text.startswith("---"):
        raise ValueError("component markdown must begin with YAML frontmatter (---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("component markdown frontmatter not terminated by ---")
    fm_text = parts[1]
    body = parts[2].lstrip("\n")
    fm = yaml.safe_load(fm_text) or {}
    if not isinstance(fm, dict):
        raise ValueError("frontmatter must parse to a YAML mapping")
    return fm, body


def _section_bodies(body: str) -> dict[str, str]:
    """Split a markdown body on `## <H2>` headers; return {header: section_text}.

    Only headers in the H2 allowlist (Purpose|Variants|States|Anatomy) are
    captured. The body of each section spans up to the next H2 (any H2,
    not just allow-listed ones) or end-of-document.
    """
    matches = list(_H2_RE.finditer(body))
    sections: dict[str, str] = {}
    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.end()
        # End at the next H2 (any), or end of body.
        next_h2 = re.search(r"^##\s+\S+", body[start:], re.M)
        end = start + (next_h2.start() if next_h2 else len(body) - start)
        sections[name] = body[start:end].strip("\n")
    return sections


def _extract_bullet_names(section_text: str) -> list[str]:
    """Extract `**Name:**` from each `- **Name:** description` bullet."""
    return [m.group(1).strip() for m in _BULLET_NAME_RE.finditer(section_text)]


def _move_default_first(items: list[str]) -> list[str]:
    """If any entry case-insensitively equals 'default', move it to position 0."""
    for i, val in enumerate(items):
        if val.lower() == "default" and i != 0:
            return [items[i], *items[:i], *items[i + 1 :]]
    return items


def _coerce_str_list(val: Any) -> list[str]:
    if val is None:
        return []
    if isinstance(val, str):
        return [val]
    if isinstance(val, list):
        return [str(x) for x in val]
    return [str(val)]


def parse_component_md(path: Path) -> Component:
    """Parse a single component markdown file. See module docstring."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)
    sections = _section_bodies(body)

    purpose = sections.get("Purpose", "").strip()
    variants = _extract_bullet_names(sections.get("Variants", ""))
    states = _extract_bullet_names(sections.get("States", ""))
    if not variants:
        variants = ["default"]
    if not states:
        states = ["default"]
    states = _move_default_first(states)
    variants = _move_default_first(variants)

    anatomy: str | None = None
    anatomy_section = sections.get("Anatomy")
    if anatomy_section:
        m = _ANATOMY_FENCE_RE.search(anatomy_section)
        if m:
            anatomy = m.group(1).rstrip("\n")

    last_updated = fm.get("last_updated")
    if last_updated is not None and not isinstance(last_updated, str):
        last_updated = str(last_updated)

    return Component(
        stem=path.stem,
        pattern=fm.get("pattern"),
        library_component=fm.get("library_component"),
        used_in=_coerce_str_list(fm.get("used_in")),
        data_entities=_coerce_str_list(fm.get("data_entities")),
        last_updated=last_updated,
        purpose=purpose,
        variants=variants,
        states=states,
        anatomy=anatomy,
    )
