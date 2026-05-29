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

SCHEMA_VERSION = "1.0"
RENDERER = "mockup-walkthrough-static-html"
TOP_LEVEL_KEYS = {
    "schema_version",
    "renderer",
    "renderer_version",
    "generated_at",
    "source_root",
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

    if args.fixture:
        # Expected snapshot lives at
        # mockup-walkthrough/static-html/tests/expected/<fixture>/
        skill_root = Path(__file__).resolve().parent
        expected = skill_root / "tests" / "expected" / args.fixture
        fixture_diff(site, expected, report)

    report.print_and_exit()


if __name__ == "__main__":
    main()
