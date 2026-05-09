#!/usr/bin/env python3
"""validator.py — mockup-feedback-annotate injection validator.

Checks that a walkthrough site root has the annotation overlay correctly
injected by the mockup-feedback-annotate skill.

Usage:
  python validator.py <site-root>

Exit codes:
  0   PASS
  2   FAIL (violations found)
  1   Internal error (bad args, missing site root)
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

OVERLAY_FILENAME = "annotation-overlay.js"
EXPECTED_SCRIPT_TAG = f'<script type="module" src="{OVERLAY_FILENAME}"></script>'

CDN_PATTERNS = [
    re.compile(r'<script\s[^>]*src\s*=\s*"https?://', re.IGNORECASE),
    re.compile(r'<script\s[^>]*src\s*=\s*"//', re.IGNORECASE),
]


class _ScriptChecker(HTMLParser):
    """Walks one HTML file and records overlay script presence and position."""

    def __init__(self) -> None:
        super().__init__()
        self.in_head = False
        self.overlay_found = False
        self.overlay_in_head = False
        self.cdns: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "head":
            self.in_head = True
        if tag == "script":
            src = dict(attrs).get("src", "")
            if src == OVERLAY_FILENAME:
                self.overlay_found = True
                if self.in_head:
                    self.overlay_in_head = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self.in_head = False


class Report:
    def __init__(self) -> None:
        self.violations: list[str] = []

    def add(self, where: str, msg: str) -> None:
        self.violations.append(f"{where}: {msg}")

    def ok(self) -> bool:
        return len(self.violations) == 0

    def dump(self) -> None:
        for v in self.violations:
            print("FAIL", v)


def collect_html_files(site_root: Path) -> list[Path]:
    return sorted(site_root.rglob("*.html"))


def check_site(site_root: Path) -> Report:
    r = Report()

    if not site_root.is_dir():
        r.add(str(site_root), "site root directory does not exist")
        return r

    # 1. Overlay bundle must be present
    overlay_path = site_root / OVERLAY_FILENAME
    if not overlay_path.is_file():
        r.add(OVERLAY_FILENAME, "overlay bundle not found in site root")

    html_files = collect_html_files(site_root)
    if not html_files:
        r.add(str(site_root), "no .html files found — nothing to check")
        return r

    for html in html_files:
        rel = html.relative_to(site_root)
        raw = html.read_text(encoding="utf-8")

        # 2. CDN check (must not introduce external scripts)
        for pat in CDN_PATTERNS:
            if pat.search(raw):
                r.add(str(rel), "unexpected CDN script/link reference introduced by injection")

        # 3. Parse HTML for overlay script position
        checker = _ScriptChecker()
        checker.feed(raw)

        if not checker.overlay_found:
            r.add(str(rel), f"missing overlay script tag ({EXPECTED_SCRIPT_TAG!r})")
            continue

        if checker.overlay_in_head:
            r.add(str(rel), "overlay script tag is in <head> — must be last child of <body>")

        # 4. Must be just before </body> (last script in file)
        body_close = raw.rfind("</body>")
        tag_pos = raw.rfind(f'src="{OVERLAY_FILENAME}"')
        if body_close < 0:
            r.add(str(rel), "no </body> tag found")
        elif tag_pos < 0:
            pass  # already caught by overlay_found check above
        elif tag_pos > body_close:
            r.add(str(rel), "overlay script tag appears after </body>")
        else:
            # Verify no <script> tag appears between overlay tag and </body>
            between = raw[tag_pos + len(f'src="{OVERLAY_FILENAME}"'):body_close]
            if re.search(r'<script', between, re.IGNORECASE):
                r.add(str(rel), "overlay script tag is not the last <script> before </body>")

    return r


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python validator.py <site-root>", file=sys.stderr)
        return 1

    site_root = Path(sys.argv[1])
    r = check_site(site_root)

    if r.ok():
        print(f"PASS  {site_root}")
        return 0

    r.dump()
    return 2


if __name__ == "__main__":
    sys.exit(main())
