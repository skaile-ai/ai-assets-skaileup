#!/usr/bin/env python3
"""validator.py — mockup-walkthrough-static-html validator.

Two modes:

1. **Site-root mode** (default): structural checks only.
   $ python validator.py <site-root> [--source-root <path>]

2. **Fixture mode**: in addition to structural checks, byte-compare every
   generated file (after deterministic normalisation of `generated_at`)
   against the expected snapshot under
   `mockup-walkthrough/static-html/tests/expected/<fixture>/`.
   $ python validator.py <site-root> --fixture <name>

Exit codes:
  0  PASS — every check OK
  2  FAIL — at least one violation; report printed line-by-line
  1  internal error (e.g. unparseable JSON, missing site root)

Site-root layout expected:

  <site-root>/
    index.html
    manifest.json
    screen/<group>/<name>.html
    journey/<id>.html

Stdlib + PyYAML only (PyYAML is used elsewhere in this repo for
frontmatter; install via `python -m pip install PyYAML` if missing).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# ── Pinned constants ─────────────────────────────────────────────────

SCHEMA_VERSION = "1.2"
RENDERER = "mockup-walkthrough-static-html"
TOP_LEVEL_KEYS = {
    "schema_version",
    "renderer",
    "renderer_version",
    "generated_at",
    "source_root",
    "app_nav",
    "screens",
    "journeys",
    "features",
    "warnings",
}
ALLOWED_DATA_SPEC_ATTRS = {
    "data-spec-screen",
    "data-spec-element",
    "data-spec-provisional",
    "data-spec-journey",
    "data-spec-index",
}

# Canonical spec-template headings (contracts/walkthrough_renderer.md §
# Auto-slug fallback exclusion list / § Spec reference panel) — these become
# the spec panel's own `<h2>`/`<h3>` skeleton and MUST NEVER be rendered as
# an annotatable `el-region` widget, i.e. their slug MUST NEVER appear as a
# `data-spec-element` value anywhere on the site.
CANONICAL_HEADING_SLUGS = {
    "purpose",
    "route",
    "what-the-user-sees",
    "wireframe",
    "information-displayed",
    "actions",
    "situations",
    "ui-elements",
    "template-data",
    "navigation",
    "layout-areas",
    "responsive-behaviour",
}

JS_FRAMEWORK_PATTERNS = [
    re.compile(r'<script\s+[^>]*src\s*=\s*"https?://', re.IGNORECASE),
    re.compile(r'<script\s+[^>]*src\s*=\s*"//', re.IGNORECASE),
    re.compile(
        r'<link\s+[^>]*rel\s*=\s*"stylesheet"[^>]*href\s*=\s*"https?://',
        re.IGNORECASE,
    ),
]


# ── Violation accumulator ────────────────────────────────────────────


class Report:
    def __init__(self) -> None:
        self.violations: list[str] = []

    def add(self, where: str, message: str) -> None:
        self.violations.append(f"{where}: {message}")

    def ok(self) -> bool:
        return not self.violations

    def print_and_exit(self) -> None:
        if self.ok():
            print("PASS — mockup-walkthrough-static-html validator")
            sys.exit(0)
        print(
            f"FAIL — mockup-walkthrough-static-html: "
            f"{len(self.violations)} violation(s)"
        )
        for v in self.violations:
            print(f"  {v}")
        sys.exit(2)


# ── Tiny attribute extractor ─────────────────────────────────────────


class AttrCollector(HTMLParser):
    """Collects (tag, attrs_dict) tuples for every start/startend tag."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        self.tags.append((tag, dict(attrs)))

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self.tags.append((tag, dict(attrs)))


def parse_html(path: Path) -> list[tuple[str, dict[str, str]]]:
    parser = AttrCollector()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.tags


def find_body_attrs(
    tags: list[tuple[str, dict[str, str]]]
) -> dict[str, str]:
    for tag, attrs in tags:
        if tag == "body":
            return attrs
    return {}


def collect_attr_values(
    tags: list[tuple[str, dict[str, str]]], attr: str
) -> list[str]:
    return [a[attr] for _, a in tags if attr in a]


# ── Minimal DOM tree (for checks that need containment/wrapping) ─────
#
# The flat AttrCollector above is enough for attribute-presence checks, but
# `check_targets` / `check_content_fidelity` need parent/child relationships
# (e.g. "is this node wrapped by an <a>", "how many <tr> inside this
# <table>'s <tbody>"). Stdlib-only, same spirit as AttrCollector above.

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class DomNode:
    __slots__ = ("tag", "attrs", "parent", "children")

    def __init__(
        self,
        tag: str,
        attrs: dict[str, str],
        parent: "DomNode | None",
    ) -> None:
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children: list["DomNode"] = []


class DomTreeParser(HTMLParser):
    """Builds a minimal parent/child tree of tag/attrs nodes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = DomNode("#root", {}, None)
        self._stack: list[DomNode] = [self.root]

    def _open(self, tag: str, attrs: list, self_closing: bool) -> None:
        node = DomNode(tag, dict(attrs), self._stack[-1])
        self._stack[-1].children.append(node)
        if not self_closing and tag not in VOID_TAGS:
            self._stack.append(node)

    def handle_starttag(self, tag: str, attrs: list) -> None:
        self._open(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        self._open(tag, attrs, self_closing=True)

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self._stack) - 1, 0, -1):
            if self._stack[i].tag == tag:
                del self._stack[i:]
                return


def parse_dom(path: Path) -> DomNode:
    parser = DomTreeParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.root


def iter_nodes(node: DomNode):
    yield node
    for child in node.children:
        yield from iter_nodes(child)


def find_all(node: DomNode, predicate) -> list[DomNode]:
    return [n for n in iter_nodes(node) if predicate(n)]


def find_first(node: DomNode, predicate) -> DomNode | None:
    for n in iter_nodes(node):
        if predicate(n):
            return n
    return None


def nearest_anchor(node: DomNode) -> DomNode | None:
    """`node` itself if it's an `<a>`, else the nearest `<a>` ancestor."""
    cur: DomNode | None = node
    while cur is not None:
        if cur.tag == "a":
            return cur
        cur = cur.parent
    return None


def find_descendant_or_self_anchor(node: DomNode) -> DomNode | None:
    """`node` itself if it's an `<a>`, else the first `<a>` among its
    descendants (self-inclusive top-down search via `find_first`).

    Mirror-image of `nearest_anchor` (which walks *up* to find a wrapping
    `<a>`). `items[]` entries need the opposite direction: per
    `contracts/walkthrough_renderer.md` § kind → DOM tag mapping, a list
    `<li>` (or nav/tabs entry) carries its own `data-spec-element`, and
    `items[].target` "wraps that `<li>`'s content in `<a>`" — i.e. the link
    is a *child* of the entry node, not an ancestor of it.
    """
    return find_first(node, lambda n: n.tag == "a")


def has_ancestor(node: DomNode, stop_at: DomNode, predicate) -> bool:
    """True if any ancestor strictly between `node` and `stop_at` matches."""
    cur = node.parent
    while cur is not None and cur is not stop_at:
        if predicate(cur):
            return True
        cur = cur.parent
    return False


def resolve_href(page_path: Path, href: str) -> Path:
    """Resolve `href` (as rendered on `page_path`) to a filesystem path."""
    href = href.split("#", 1)[0]
    return (page_path.parent / href).resolve()


def has_relative_anchor(nav: DomNode) -> bool:
    for a in find_all(nav, lambda n: n.tag == "a" and "href" in n.attrs):
        href = a.attrs["href"]
        if not href or href == "#":
            continue
        if re.match(r"^([a-zA-Z][a-zA-Z0-9+.-]*:)?//", href) or href.startswith("/"):
            continue
        return True
    return False


# ── Structural checks ────────────────────────────────────────────────


def check_manifest_shape(site: Path, report: Report) -> dict | None:
    manifest_path = site / "manifest.json"
    if not manifest_path.exists():
        report.add(str(manifest_path), "manifest.json missing")
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.add(str(manifest_path), f"manifest.json invalid JSON: {exc}")
        return None
    if not isinstance(manifest, dict):
        report.add(str(manifest_path), "manifest.json root must be an object")
        return None
    missing = TOP_LEVEL_KEYS - manifest.keys()
    if missing:
        report.add(
            str(manifest_path),
            f"manifest.json missing top-level keys: {sorted(missing)}",
        )
    if manifest.get("schema_version") != SCHEMA_VERSION:
        report.add(
            str(manifest_path),
            f"schema_version != {SCHEMA_VERSION!r} "
            f"(got {manifest.get('schema_version')!r})",
        )
    if manifest.get("renderer") != RENDERER:
        report.add(
            str(manifest_path),
            f"renderer != {RENDERER!r} (got {manifest.get('renderer')!r})",
        )
    return manifest


def check_index(site: Path, report: Report) -> None:
    index_path = site / "index.html"
    if not index_path.exists():
        report.add(str(index_path), "index.html missing")
        return
    tags = parse_html(index_path)
    body_attrs = find_body_attrs(tags)
    if body_attrs.get("data-spec-index") != "true":
        report.add(
            str(index_path),
            'index.html <body> missing data-spec-index="true"',
        )


def check_screens(
    site: Path,
    manifest: dict,
    project_root: Path,
    source_root: Path,
    report: Report,
) -> None:
    for screen in manifest.get("screens", []):
        rendered = site / screen.get("rendered_html", "")
        screen_id = screen.get("screen_id", "")
        screen_path = screen.get("screen_path", "")
        elements = screen.get("elements", [])

        if not rendered.exists():
            report.add(
                str(rendered),
                f"rendered_html does not exist (screen_id={screen_id!r})",
            )
            continue

        # Source resolution: screen_path is repo-relative; we resolve
        # it under the project root (e.g. tests/fixtures/<name>/).
        if screen_path:
            src = (project_root / screen_path).resolve()
            if not src.exists():
                report.add(
                    str(src),
                    f"data-spec-screen source missing for "
                    f"screen_id={screen_id!r}",
                )
            else:
                try:
                    src.relative_to(source_root)
                except ValueError:
                    report.add(
                        str(src),
                        f"source not under --source-root={source_root}",
                    )

        tags = parse_html(rendered)
        body_attrs = find_body_attrs(tags)
        if body_attrs.get("data-spec-screen") != screen_id:
            report.add(
                str(rendered),
                f"<body> data-spec-screen={body_attrs.get('data-spec-screen')!r} "
                f"!= manifest screen_id={screen_id!r}",
            )

        rendered_element_ids = set(
            collect_attr_values(tags, "data-spec-element")
        )
        for elem in elements:
            elem_id = elem.get("element_id", "")
            if elem_id not in rendered_element_ids:
                report.add(
                    str(rendered),
                    f'data-spec-element="{elem_id}" missing from rendered HTML',
                )

        # Disallowed data-spec-* attribute names.
        for _, attrs in tags:
            for k in attrs:
                if k.startswith("data-spec-") and k not in ALLOWED_DATA_SPEC_ATTRS:
                    report.add(
                        str(rendered),
                        f"unknown attribute {k!r} (not in renderer contract)",
                    )

        # Zero-build invariant.
        check_zero_build(rendered, report)


def check_journeys(
    site: Path, manifest: dict, screen_id_set: set[str], report: Report
) -> None:
    for journey in manifest.get("journeys", []):
        rendered = site / journey.get("rendered_html", "")
        journey_id = journey.get("journey_id", "")

        if not rendered.exists():
            report.add(
                str(rendered),
                f"rendered_html missing (journey_id={journey_id!r})",
            )
            continue

        tags = parse_html(rendered)
        body_attrs = find_body_attrs(tags)
        if body_attrs.get("data-spec-journey") != journey_id:
            report.add(
                str(rendered),
                f"<body> data-spec-journey="
                f"{body_attrs.get('data-spec-journey')!r} "
                f"!= manifest journey_id={journey_id!r}",
            )

        # Every step link's data-spec-screen must resolve.
        for tag, attrs in tags:
            if tag == "a" and "data-spec-screen" in attrs:
                step_id = attrs["data-spec-screen"]
                if step_id not in screen_id_set:
                    report.add(
                        str(rendered),
                        f'data-spec-screen="{step_id}" not in rendered '
                        "screens set",
                    )

        check_zero_build(rendered, report)


def check_zero_build(html_path: Path, report: Report) -> None:
    text = html_path.read_text(encoding="utf-8")
    for pat in JS_FRAMEWORK_PATTERNS:
        if pat.search(text):
            report.add(
                str(html_path),
                f"zero-build invariant violated: "
                f"non-relative script/stylesheet URL ({pat.pattern!r})",
            )
            return


# ── Target resolution (contracts/walkthrough_renderer.md § Target
# resolution, § App-shell navigation) ─────────────────────────────────


def _check_single_target(
    *,
    where: str,
    target: str,
    screen_path: str,
    elem_id: str,
    screen_id_set: set[str],
    unresolved_warnings: set[tuple[str | None, str | None]],
    node: DomNode | None,
    rendered_path: Path,
    report: Report,
    anchor_finder=nearest_anchor,
) -> None:
    target_stem = target.split("#", 1)[0]
    resolves = target_stem in screen_id_set

    if node is None:
        report.add(
            where,
            f'data-spec-element="{elem_id}" not found in rendered HTML '
            f"(target={target!r})",
        )
        return

    anchor = anchor_finder(node)

    if resolves:
        if anchor is None:
            report.add(
                where,
                f"target {target!r} resolves but no <a> found on/wrapping "
                f'data-spec-element="{elem_id}"',
            )
            return
        href = anchor.attrs.get("href", "")
        if href == "#":
            report.add(
                where,
                f'target {target!r} resolves but rendered href="#"',
            )
            return
        resolved_path = resolve_href(rendered_path, href)
        if not resolved_path.exists():
            report.add(
                where,
                f"resolved href {href!r} does not point to an existing "
                f"file ({resolved_path})",
            )
    else:
        if (screen_path, elem_id) not in unresolved_warnings:
            report.add(
                where,
                f"target {target!r} does not resolve against the rendered "
                "screen_id set, and no matching unresolved_target warning "
                "was found",
            )
        if anchor is not None and anchor.attrs.get("href", "") != "#":
            report.add(
                where,
                f"target {target!r} is unresolved but rendered "
                f"href={anchor.attrs.get('href')!r} (expected \"#\")",
            )


def _check_row_target(
    *,
    rendered_path: Path,
    dom: DomNode,
    elem_id: str,
    row_target: str,
    screen_path: str,
    screen_id_set: set[str],
    unresolved_warnings: set[tuple[str | None, str | None]],
    report: Report,
) -> None:
    where = f"{rendered_path} element={elem_id!r}"
    target_stem = row_target.split("#", 1)[0]
    resolves = target_stem in screen_id_set

    table = find_first(
        dom,
        lambda n, eid=elem_id: n.tag == "table"
        and n.attrs.get("data-spec-element") == eid,
    )
    if table is None:
        report.add(
            where, f'row_target check: <table data-spec-element="{elem_id}"> not found'
        )
        return

    rows = find_all(table, lambda n: n.tag == "tr")
    body_rows = [
        r for r in rows if not has_ancestor(r, table, lambda n: n.tag == "thead")
    ]
    if not body_rows:
        return  # no data rows to check (e.g. skeleton-row edge case)

    for row in body_rows:
        first_cell = next((c for c in row.children if c.tag == "td"), None)
        if first_cell is None:
            continue
        anchor = find_first(first_cell, lambda n: n.tag == "a")

        if resolves:
            if anchor is None:
                report.add(
                    where,
                    f"row_target {row_target!r} resolves but no <a> in "
                    "row's first cell",
                )
                continue
            href = anchor.attrs.get("href", "")
            if href == "#":
                report.add(
                    where,
                    f'row_target {row_target!r} resolves but rendered href="#"',
                )
                continue
            resolved_path = resolve_href(rendered_path, href)
            if not resolved_path.exists():
                report.add(
                    where,
                    f"row_target resolved href {href!r} does not point to "
                    f"an existing file ({resolved_path})",
                )
        else:
            if (screen_path, elem_id) not in unresolved_warnings:
                report.add(
                    where,
                    f"row_target {row_target!r} does not resolve, and no "
                    "matching unresolved_target warning was found",
                )
            if anchor is not None and anchor.attrs.get("href", "") != "#":
                report.add(
                    where,
                    f"row_target unresolved but rendered "
                    f"href={anchor.attrs.get('href')!r} (expected \"#\")",
                )


def _item_entries(container: DomNode, kind: str) -> list[DomNode]:
    """Per-`items[]`-entry DOM nodes for a `nav`/`tabs`/`list` container, in
    `items[]` order — shared by `check_content_fidelity` (entry-count check)
    and `_check_item_targets` (per-entry `items[].target` resolution).
    """
    if kind == "list":
        return [c for c in container.children if c.tag == "li"]
    if kind == "tabs":
        return [
            c
            for c in container.children
            if c.tag in ("a", "span") and "tab" in c.attrs.get("class", "").split()
        ]
    # `nav` (shell-authoritative or explicit) — one <li>/<a> per item, same
    # shape as the generated default app nav.
    return [c for c in container.children if c.tag in ("li", "a")]


def _check_item_targets(
    *,
    rendered_path: Path,
    dom: DomNode,
    elem: dict,
    screen_path: str,
    screen_id_set: set[str],
    unresolved_warnings: set[tuple[str | None, str | None]],
    report: Report,
) -> None:
    """Validate `items[].target` on a `nav`/`tabs`/`list` element — the
    per-entry destination distinct from the element's own `target`/
    `row_target` (contracts/elements_block.md § Navigation targets;
    contracts/walkthrough_renderer.md § Target resolution names `items[]`
    entries alongside `target`/`row_target` as needing the identical
    resolution treatment).
    """
    items = elem.get("items")
    if not items:
        return

    elem_id = elem.get("element_id", "")
    kind = elem.get("kind", "")
    container = find_first(
        dom,
        lambda n, eid=elem_id: n.attrs.get("data-spec-element") == eid
        and n.tag in ("ul", "nav"),
    )
    if container is None:
        return  # missing container already reported by check_content_fidelity

    entries = _item_entries(container, kind)

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue  # bare-string list item — no target field possible
        target = item.get("target")
        if target is None:
            continue  # legal + inert, same as an untargeted button

        entry = entries[i] if i < len(entries) else None
        if entry is None:
            report.add(
                f"{rendered_path} element={elem_id!r}",
                f"items[{i}] target={target!r} declared but no matching "
                f"rendered entry (kind={kind!r})",
            )
            continue

        # The entry's own `data-spec-element` IS the item's resolved
        # element id (explicit `id` or auto-slugged-from-label) — read it
        # off the DOM rather than re-deriving the auto-slug algorithm.
        item_elem_id = entry.attrs.get("data-spec-element", "")
        _check_single_target(
            where=f"{rendered_path} element={elem_id!r} items[{i}]={item_elem_id!r}",
            target=target,
            screen_path=screen_path,
            elem_id=item_elem_id,
            screen_id_set=screen_id_set,
            unresolved_warnings=unresolved_warnings,
            node=entry,
            rendered_path=rendered_path,
            report=report,
            anchor_finder=find_descendant_or_self_anchor,
        )


def check_targets(site: Path, manifest: dict, report: Report) -> None:
    screens = manifest.get("screens", [])
    screen_id_set = {s.get("screen_id", "") for s in screens}

    unresolved_warnings = {
        (w.get("screen_path"), w.get("element_id"))
        for w in manifest.get("warnings", [])
        if w.get("kind") == "unresolved_target"
    }

    dom_cache: dict[str, DomNode | None] = {}

    def get_dom(rendered_rel: str) -> DomNode | None:
        if rendered_rel not in dom_cache:
            p = site / rendered_rel
            dom_cache[rendered_rel] = parse_dom(p) if p.exists() else None
        return dom_cache[rendered_rel]

    for screen in screens:
        screen_path = screen.get("screen_path", "")
        rendered_rel = screen.get("rendered_html", "")
        rendered_path = site / rendered_rel
        dom = get_dom(rendered_rel)
        if dom is None:
            continue  # already reported missing by check_screens

        for elem in screen.get("elements", []):
            elem_id = elem.get("element_id", "")

            target = elem.get("target")
            if target is not None:
                node = find_first(
                    dom,
                    lambda n, eid=elem_id: n.attrs.get("data-spec-element") == eid,
                )
                _check_single_target(
                    where=f"{rendered_path} element={elem_id!r}",
                    target=target,
                    screen_path=screen_path,
                    elem_id=elem_id,
                    screen_id_set=screen_id_set,
                    unresolved_warnings=unresolved_warnings,
                    node=node,
                    rendered_path=rendered_path,
                    report=report,
                )

            row_target = elem.get("row_target")
            if row_target is not None:
                _check_row_target(
                    rendered_path=rendered_path,
                    dom=dom,
                    elem_id=elem_id,
                    row_target=row_target,
                    screen_path=screen_path,
                    screen_id_set=screen_id_set,
                    unresolved_warnings=unresolved_warnings,
                    report=report,
                )

            _check_item_targets(
                rendered_path=rendered_path,
                dom=dom,
                elem=elem,
                screen_path=screen_path,
                screen_id_set=screen_id_set,
                unresolved_warnings=unresolved_warnings,
                report=report,
            )

        # Every screen page MUST carry the app-shell nav: a <nav
        # class="app-nav"> with at least one relative-href <a>.
        app_navs = find_all(
            dom,
            lambda n: n.tag == "nav" and "app-nav" in n.attrs.get("class", "").split(),
        )
        if not app_navs or not any(has_relative_anchor(n) for n in app_navs):
            report.add(
                str(rendered_path),
                'expected >= 1 <nav class="app-nav"> containing a '
                "relative-href <a> (§ App-shell navigation)",
            )

    # app_nav[] entries must each resolve to an existing rendered file.
    # (§ App-shell navigation: the resolved href is identical from any
    # screen/<group>/<name>.html page, since they all sit at the same depth
    # — use the first rendered screen as the reference page.)
    if screens:
        ref_rendered = site / screens[0].get("rendered_html", "")
        for i, entry in enumerate(manifest.get("app_nav", [])):
            target = entry.get("target", "")
            label = entry.get("label", "")
            resolved_path = resolve_href(ref_rendered, target)
            if not resolved_path.exists():
                report.add(
                    "manifest.json app_nav",
                    f"app_nav[{i}] label={label!r} target={target!r} does "
                    f"not resolve to an existing file ({resolved_path})",
                )


# ── Content fidelity (contracts/walkthrough_renderer.md § kind → DOM tag
# mapping, § Spec reference panel, § Auto-slug fallback exclusion list) ──


def check_content_fidelity(site: Path, manifest: dict, report: Report) -> None:
    all_data_spec_element_values: set[str] = set()

    for screen in manifest.get("screens", []):
        screen_path = screen.get("screen_path", "")
        rendered_rel = screen.get("rendered_html", "")
        rendered_path = site / rendered_rel
        if not rendered_path.exists():
            continue  # already reported missing by check_screens

        dom = parse_dom(rendered_path)
        tags = parse_html(rendered_path)
        elements = screen.get("elements", [])
        non_provisional = [e for e in elements if not e.get("provisional")]

        for elem in elements:
            elem_id = elem.get("element_id", "")
            where = f"{rendered_path} element={elem_id!r}"

            sample_rows = elem.get("sample_rows")
            if sample_rows is not None:
                table = find_first(
                    dom,
                    lambda n, eid=elem_id: n.tag == "table"
                    and n.attrs.get("data-spec-element") == eid,
                )
                if table is None:
                    report.add(where, "sample_rows declared but <table> not found")
                else:
                    tbody = find_first(table, lambda n: n.tag == "tbody")
                    if tbody is None:
                        report.add(where, "sample_rows declared but <tbody> not found")
                    else:
                        tr_count = len(find_all(tbody, lambda n: n.tag == "tr"))
                        if tr_count != len(sample_rows):
                            report.add(
                                where,
                                f"<tbody> has {tr_count} <tr> but manifest "
                                f"declares {len(sample_rows)} sample_rows",
                            )

            items = elem.get("items")
            if items is not None:
                kind = elem.get("kind", "")
                container = find_first(
                    dom,
                    lambda n, eid=elem_id: n.attrs.get("data-spec-element") == eid
                    and n.tag in ("ul", "nav"),
                )
                if container is None:
                    report.add(
                        where,
                        f"items declared (kind={kind!r}) but container node not found",
                    )
                else:
                    entries = _item_entries(container, kind)
                    if len(entries) != len(items):
                        report.add(
                            where,
                            f"rendered {len(entries)} item entries but "
                            f"manifest declares {len(items)} items "
                            f"(kind={kind!r})",
                        )

            options = elem.get("options")
            if options is not None:
                select = find_first(
                    dom,
                    lambda n, eid=elem_id: n.tag == "select"
                    and n.attrs.get("data-spec-element") == eid,
                )
                if select is None:
                    report.add(where, "options declared but <select> not found")
                else:
                    opt_count = len(find_all(select, lambda n: n.tag == "option"))
                    if opt_count != len(options):
                        report.add(
                            where,
                            f"<select> has {opt_count} <option> but manifest "
                            f"declares {len(options)} options",
                        )

        all_data_spec_element_values.update(
            collect_attr_values(tags, "data-spec-element")
        )

        spec_panels = [
            (t, a) for t, a in tags if t == "details" and a.get("class") == "spec-panel"
        ]
        if len(spec_panels) != 1:
            report.add(
                str(rendered_path),
                f'expected exactly one <details class="spec-panel">, '
                f"found {len(spec_panels)}",
            )

        prose_sections = [
            (t, a)
            for t, a in tags
            if t == "section"
            and "screen-body-prose" in a.get("class", "").split()
        ]
        if prose_sections:
            report.add(
                str(rendered_path),
                'found disallowed <section class="screen-body-prose"> '
                "(spec body MUST render only inside the spec panel)",
            )

        if not non_provisional:
            has_warning = any(
                w.get("kind") == "no_explicit_elements"
                and w.get("screen_path") == screen_path
                for w in manifest.get("warnings", [])
            )
            if not has_warning:
                report.add(
                    str(rendered_path),
                    f"screen {screen_path!r} has zero non-provisional "
                    "elements but no matching no_explicit_elements warning",
                )

    leaked = all_data_spec_element_values & CANONICAL_HEADING_SLUGS
    if leaked:
        report.add(
            str(site),
            "canonical spec-template heading slug(s) rendered as "
            f"data-spec-element somewhere in the site: {sorted(leaked)}",
        )


# ── Fixture mode (snapshot diff) ─────────────────────────────────────


def normalise_manifest_for_compare(text: str) -> str:
    """Replace runtime `generated_at` value with literal ``<pinned>``.

    The expected snapshot stores `"generated_at": "<pinned>"` so the
    snapshot is stable across renders. Replacing only the value (not the
    key) keeps the field's presence asserted.
    """
    return re.sub(
        r'"generated_at"\s*:\s*"[^"]*"',
        '"generated_at": "<pinned>"',
        text,
    )


def fixture_diff(site: Path, expected: Path, report: Report) -> None:
    if not expected.is_dir():
        report.add(str(expected), "expected snapshot directory missing")
        return
    expected_files = sorted(
        p.relative_to(expected) for p in expected.rglob("*") if p.is_file()
    )
    for rel in expected_files:
        exp_path = expected / rel
        got_path = site / rel
        if not got_path.exists():
            report.add(str(got_path), f"expected fixture file missing: {rel}")
            continue
        exp_text = exp_path.read_text(encoding="utf-8")
        got_text = got_path.read_text(encoding="utf-8")
        if rel.name == "manifest.json":
            got_text = normalise_manifest_for_compare(got_text)
            exp_text = normalise_manifest_for_compare(exp_text)
        if got_text != exp_text:
            # Locate first differing line.
            for i, (a, b) in enumerate(
                zip(exp_text.splitlines(), got_text.splitlines()), 1
            ):
                if a != b:
                    report.add(
                        f"{got_path}:{i}",
                        f"snapshot mismatch — expected "
                        f"{a[:80]!r}, got {b[:80]!r}",
                    )
                    break
            else:
                report.add(
                    str(got_path),
                    "snapshot mismatch (length differs)",
                )


# ── Entry ────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="validator.py",
        description="mockup-walkthrough-static-html validator",
    )
    parser.add_argument("site_root", help="site root directory")
    parser.add_argument(
        "--fixture",
        default=None,
        help="fixture name under tests/expected/",
    )
    parser.add_argument(
        "--source-root",
        default="experience/screens",
        help="path the manifest source_root resolves to (must contain screen sources)",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="root that screen_path values are anchored to "
        "(default: parent of --source-root's parent)",
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="optional working dir for path-agnostic test runs",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd) if args.cwd else Path.cwd()
    site = (cwd / args.site_root).resolve()
    source_root = (cwd / args.source_root).resolve()
    if args.project_root is not None:
        project_root = (cwd / args.project_root).resolve()
    else:
        # Default: project_root = source_root.parent.parent
        # (since source_root is typically `<project>/experience/screens`
        # — strip both segments to land on the project root).
        project_root = source_root.parent.parent

    if not site.is_dir():
        print(f"FAIL — site root does not exist: {site}", file=sys.stderr)
        sys.exit(1)

    report = Report()
    manifest = check_manifest_shape(site, report)
    check_index(site, report)
    if manifest is not None:
        check_screens(site, manifest, project_root, source_root, report)
        screen_id_set = {
            s.get("screen_id", "")
            for s in manifest.get("screens", [])
        }
        check_journeys(site, manifest, screen_id_set, report)
        check_targets(site, manifest, report)
        check_content_fidelity(site, manifest, report)

    if args.fixture:
        # Expected snapshot lives at
        # mockup-walkthrough/static-html/tests/expected/<fixture>/
        skill_root = Path(__file__).resolve().parent
        expected = skill_root / "tests" / "expected" / args.fixture
        fixture_diff(site, expected, report)

    report.print_and_exit()


if __name__ == "__main__":
    main()
