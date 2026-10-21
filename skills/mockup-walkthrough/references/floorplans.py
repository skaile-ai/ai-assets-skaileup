"""floorplans.py — floorplan-frame checks shared by both renderers' validators.

`tree/09_mockup/walkthrough/README.md § Floorplan frame`: flat screen identity,
posture/density enums, floorplan and region ids against the rulebook
catalogue, and the wide + narrow frame (or the no-floorplan notice) on every
screen page. The renderers differ only in how an `href` resolves to a file, so
`check_floorplans` takes that as the `resolve(page_path, href)` callback.

Validators import this module through a `sys.path` insert of their parent
directory (`references/`), which travels with the installed skill directory.
"""
from __future__ import annotations

import re
from pathlib import Path

from html_dom import DomNode, find_all, find_first, iter_nodes, parse_dom

POSTURES = {"sovereign", "transient", "auxiliary"}
DENSITIES = {"compact", "default", "comfortable"}
SCREEN_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,47}$")
WIDE_MIN_PX = 960
NARROW_MAX_PX = 640
RULEBOOK_CONTRACT_DIRS = (".omp/contracts", ".claude/contracts", ".codex/contracts")


def default_rulebook(cwd: Path) -> Path | None:
    """The installed `app-design-rulebook` contract: the harness's contract
    directory under the working directory first, then the `rulebook/` of the
    collection checkout this module ships in."""
    candidates = [cwd / d / "app-design-rulebook" for d in RULEBOOK_CONTRACT_DIRS]
    candidates.append(Path(__file__).resolve().parents[3] / "rulebook")
    for c in candidates:
        if (c / "floorplans").is_dir():
            return c
    return None


def load_floorplans(rulebook: Path) -> dict[str, dict]:
    """`floorplans/<id>/README.md` → {id: {"kind": str, "regions": set[str]}}.

    `kind` comes from the frontmatter; the regions are the first cell of each
    row of the README's `## Regions` table (backticks stripped)."""
    catalogue: dict[str, dict] = {}
    for readme in sorted((rulebook / "floorplans").glob("*/README.md")):
        text = readme.read_text(encoding="utf-8")
        kind = re.search(r"^kind:\s*(\w+)", text, re.MULTILINE)
        regions: set[str] = set()
        in_regions = False
        rows = 0
        for line in text.splitlines():
            if line.startswith("## "):
                in_regions = line.strip() == "## Regions"
                rows = 0
                continue
            if in_regions and line.startswith("|"):
                rows += 1
                if rows > 2:  # header + separator precede the data rows
                    regions.add(line.split("|")[1].strip().strip("`"))
        catalogue[readme.parent.name] = {
            "kind": kind.group(1) if kind else "",
            "regions": regions,
        }
    return catalogue


def _classes(node: DomNode) -> list[str]:
    return node.attrs.get("class", "").split()


def _px(value: str | None) -> int | None:
    return int(value) if value and value.isdigit() else None


def check_floorplans(
    site: Path,
    manifest: dict,
    rulebook: Path | None,
    resolve,
    report,
) -> None:
    """Flat screen identity, enums, floorplan/region ids, and the wide + narrow
    frame (or the no-floorplan notice) on every screen page.

    `resolve(page_path, href)` maps an `href` rendered on `page_path` to the
    filesystem path it names; `report` takes `.add(where, message)`."""
    catalogue = load_floorplans(rulebook) if rulebook else {}
    declared = any(s.get("floorplan") for s in manifest.get("screens", []))
    if declared and rulebook is None:
        report.add(
            "--rulebook",
            "app-design-rulebook not found (pass --rulebook <dir holding floorplans/>)",
        )
    warned = {
        w.get("screen_path")
        for w in manifest.get("warnings", [])
        if w.get("kind") == "no_floorplan"
    }

    for screen in manifest.get("screens", []):
        sid = screen.get("screen_id", "")
        spath = screen.get("screen_path", "")
        rendered = site / screen.get("rendered_html", "")
        where = str(rendered)

        if not SCREEN_ID_RE.match(sid) or sid == "shell" or spath != f"07_screens/{sid}.md":
            report.add(
                where,
                f"screen_id={sid!r} / screen_path={spath!r}: screens are flat "
                "(07_screens/<screen>.md, id ^[a-z][a-z0-9-]{1,47}$, `shell` reserved)",
            )
        posture = screen.get("posture")
        if posture not in POSTURES:
            report.add(where, f"posture={posture!r} not in {sorted(POSTURES)}")
        density = screen.get("density")
        if density not in DENSITIES:
            report.add(where, f"density={density!r} not in {sorted(DENSITIES)}")

        fid = screen.get("floorplan")
        fp = catalogue.get(fid) if fid else None
        usable = fp is not None and fp["kind"] == "screen"
        if not fid:
            report.add(where, "screen declares no floorplan")
        elif rulebook is not None and not usable:
            report.add(
                where,
                f"floorplan={fid!r} is not a screen floorplan of the rulebook "
                f"(known: {sorted(k for k, v in catalogue.items() if v['kind'] == 'screen')})",
            )
        if usable:
            regions = screen.get("regions") or {}
            for key in regions:
                if key not in fp["regions"]:
                    report.add(
                        where,
                        f"regions key {key!r} is not a region of floorplan {fid!r} "
                        f"({sorted(fp['regions'])})",
                    )
            for el in screen.get("elements", []):
                r = el.get("region")
                if r is not None and r not in fp["regions"]:
                    report.add(
                        where,
                        f"element {el.get('element_id')!r} region {r!r} is not a "
                        f"region of floorplan {fid!r}",
                    )

        if not rendered.exists():
            continue  # check_screens reports it
        dom = parse_dom(rendered)
        notice = find_first(dom, lambda n: "floorplan-notice" in _classes(n))
        section = find_first(
            dom, lambda n: n.tag == "section" and "floorplan" in _classes(n)
        )
        if not usable:
            if notice is None:
                report.add(where, "no floorplan: page lacks the visible .floorplan-notice")
            if spath not in warned:
                report.add(where, "no floorplan: manifest lacks a no_floorplan warning")
            if section is not None:
                report.add(where, "no floorplan: page must not render a .floorplan frame")
            continue

        if notice is not None:
            report.add(where, ".floorplan-notice rendered although the floorplan resolves")
        frame_rel = screen.get("floorplan_html", "")
        frame_path = site / frame_rel
        if section is None:
            report.add(where, "page lacks the <section class=\"floorplan\"> frames")
        else:
            widths = []
            for ifr in find_all(section, lambda n: n.tag == "iframe"):
                src = ifr.attrs.get("src", "")
                if resolve(rendered, src) != frame_path.resolve():
                    report.add(where, f"iframe src={src!r} does not resolve to {frame_rel!r}")
                widths.append(_px(ifr.attrs.get("width")))
            if not any(w is not None and w >= WIDE_MIN_PX for w in widths):
                report.add(where, f"no wide iframe (width >= {WIDE_MIN_PX})")
            if not any(w is not None and w <= NARROW_MAX_PX for w in widths):
                report.add(where, f"no narrow iframe (width <= {NARROW_MAX_PX})")
        if not frame_path.exists():
            report.add(str(frame_path), f"floorplan_html does not exist (screen_id={sid!r})")
            continue
        frame = parse_dom(frame_path)
        if find_first(frame, lambda n: n.tag == "script") is not None:
            report.add(str(frame_path), "floorplan frame carries a <script>; it must be inert")
        for n in iter_nodes(frame):
            for k in n.attrs:
                if k.startswith("data-spec-"):
                    report.add(str(frame_path), f"frame carries {k!r}; it is not annotatable")
        wanted = set(screen.get("regions") or {}) | {
            el["region"] for el in screen.get("elements", []) if el.get("region")
        }
        wanted.add("shell")
        for key in sorted(wanted):
            node = find_first(frame, lambda n, k=key: n.attrs.get("data-region") == k)
            if node is None:
                report.add(str(frame_path), f"region {key!r} missing from the frame")
            elif find_first(node, lambda n: "fp-fill" in _classes(n)) is None:
                report.add(str(frame_path), f"region {key!r} has no .fp-fill content")
