#!/usr/bin/env python3
"""triage.py — mockup-feedback-triage deterministic router.

Reads the open notes of the project's annotation inbox, resolves each note's
target to a _concept/ file, groups the notes by file and writes
triage/<round-id>.json.

Usage:
  python triage.py <concept-root> <output-dir> [--inbox DIR] [--round ID]

  --inbox  the inbox directory holding items/<inboxId>.json
           (default: .data/annotations beside <concept-root>)
  --round  the round id, used as the output file stem
           (default: r-<UTC timestamp>)

Exit codes:
  0  success (even if some notes are unresolved)
  1  fatal error (bad args, unreadable inbox directory)
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SCREEN_DIR = "07_screens"
JOURNEYS_FILE = "04_journeys/stories.yaml"
DATAMODEL_FILE = "10_blueprint/datamodel/model.ts"

# A source path inside a component chain or a target ref. The ref is
# `<tag>:<path>:<line>:<col>`, so `:` ends the path; `[` `]` cover `[id].vue`.
VUE_PATH = re.compile(r"[\w@.\-\[\]/]+\.vue")
ENTITY_DIR = re.compile(r"(?:^|/)src/entities/([^/]+)/")
SCREEN_FILE = re.compile(r"(?:^|/)src/screens/(.+)\.vue$")
FLOORPLAN_FILE = re.compile(r"(?:^|/)src/floorplans/")


def slug(text: str) -> str:
    """Storybook's id sanitising: lowercase, runs of non-alphanumerics to `-`."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def vue_files(item: dict) -> list[str]:
    """Source files named by the note, innermost first: the target ref, then the chain."""
    found: list[str] = []
    ref = (item.get("target") or {}).get("ref") or ""
    chain = [s.strip() for s in (item.get("vueComponents") or "").split(">")]
    for text in [ref] + list(reversed(chain)):
        for path in VUE_PATH.findall(text):
            # A library component's own file (Nuxt UI's Form.vue) is no source of ours.
            if "node_modules/" not in path and path not in found:
                found.append(path)
    return found


def story_id(item: dict) -> str:
    url = item.get("url") or ""
    try:
        return (parse_qs(urlparse(url).query).get("id") or [""])[0]
    except ValueError:
        return ""


def entity_exists(concept_root: Path, entity: str) -> bool:
    model = concept_root / DATAMODEL_FILE
    if not model.is_file():
        return False
    pattern = re.compile(rf"^export const {re.escape(entity)}\s*=", re.MULTILINE)
    return bool(pattern.search(model.read_text(encoding="utf-8")))


def route_entity(concept_root: Path, entity: str) -> tuple[dict | None, str | None]:
    if not (concept_root / DATAMODEL_FILE).is_file():
        return None, f"file not found: _concept/{DATAMODEL_FILE}"
    if not entity_exists(concept_root, entity):
        return None, f"entity not found in _concept/{DATAMODEL_FILE}: {entity}"
    return {"file": DATAMODEL_FILE, "entity": entity}, None


def route_screen(concept_root: Path, screen: str) -> tuple[dict | None, str | None]:
    rel = f"{SCREEN_DIR}/{screen}.md"
    if (concept_root / rel).is_file():
        return {"file": rel}, None
    return None, f"file not found: _concept/{rel}"


def route_journey(concept_root: Path) -> tuple[dict | None, str | None]:
    if (concept_root / JOURNEYS_FILE).is_file():
        return {"file": JOURNEYS_FILE}, None
    return None, f"file not found: _concept/{JOURNEYS_FILE}"


def screen_from_story(concept_root: Path, sid: str) -> str | None:
    """`screens-<id>--<story>` -> the screen whose slug is <id>."""
    prefix = sid.split("--")[0]
    if not prefix.startswith("screens-"):
        return None
    want = prefix[len("screens-"):]
    root = concept_root / SCREEN_DIR
    for path in sorted(root.rglob("*.md")) if root.is_dir() else []:
        rel = path.relative_to(root).with_suffix("").as_posix()
        if slug(rel) == want:
            return rel
    return None


def entity_from_story(concept_root: Path, sid: str) -> str | None:
    """`entities-<entity>-<component>--<story>` -> the entity whose slug starts <entity>-."""
    prefix = sid.split("--")[0]
    if not prefix.startswith("entities-"):
        return None
    rest = prefix[len("entities-"):]
    model = concept_root / DATAMODEL_FILE
    if not model.is_file():
        return None
    ids = re.findall(r"^export const (\w+)\s*=\s*entity\(", model.read_text(encoding="utf-8"), re.MULTILINE)
    for entity in sorted(ids, key=lambda e: -len(slug(e))):
        if rest == slug(entity) or rest.startswith(slug(entity) + "-"):
            return entity
    return None


def resolve_item(item: dict, concept_root: Path) -> tuple[dict | None, str | None]:
    """Returns ({file[, entity]}, None) or (None, reason)."""
    sid = story_id(item)

    files = vue_files(item)
    for path in files:
        m = ENTITY_DIR.search(path)
        if m:
            return route_entity(concept_root, m.group(1))
        m = SCREEN_FILE.search(path)
        if m:
            return route_screen(concept_root, m.group(1))

    entity = entity_from_story(concept_root, sid)
    if entity:
        return route_entity(concept_root, entity)
    screen = screen_from_story(concept_root, sid)
    if screen:
        return route_screen(concept_root, screen)
    if sid.startswith("journeys-"):
        return route_journey(concept_root)

    for path in files:
        if FLOORPLAN_FILE.search(path):
            return None, f"rulebook asset: {path} ships with mockup-storybook and has no concept file"
    if files:
        return None, f"no concept file for {files[0]}"
    target = item.get("target") or {}
    if target.get("kind") == "route":
        return None, f"no component: note targets route {target.get('ref', '/')}"
    return None, "no component: note carries no source position"


def load_open_items(inbox: Path) -> tuple[list[dict], list[dict]]:
    """Returns (open items sorted by arrival, unreadable files as unresolved entries)."""
    items: list[dict] = []
    broken: list[dict] = []
    items_dir = inbox / "items"
    for path in sorted(items_dir.glob("*.json")) if items_dir.is_dir() else []:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("not a JSON object")
        except Exception as exc:
            broken.append({"inboxId": path.stem, "reason": f"unreadable item file: {exc}"})
            continue
        if data.get("status", "open") != "open":
            continue
        data.setdefault("inboxId", path.stem)
        items.append(data)
    items.sort(key=lambda d: (d.get("receivedAt", ""), d["inboxId"]))
    return items, broken


def triage_inbox(inbox: Path, concept_root: Path, round_id: str) -> dict:
    items, broken = load_open_items(inbox)
    groups: dict[tuple[str, str | None], list[str]] = {}
    unresolved: list[dict] = list(broken)

    for item in items:
        route, reason = resolve_item(item, concept_root)
        if route:
            groups.setdefault((route["file"], route.get("entity")), []).append(item["inboxId"])
        else:
            unresolved.append({"inboxId": item["inboxId"], "reason": reason})

    out_groups = []
    for (file_rel, entity), ids in groups.items():
        group = {"file": file_rel}
        if entity:
            group["entity"] = entity
        group["items"] = ids
        out_groups.append(group)

    return {
        "roundId": round_id,
        "triagedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "groups": out_groups,
        "unresolved": unresolved,
    }


def main() -> int:
    raw = sys.argv[1:]
    opts: dict[str, str] = {}
    args: list[str] = []
    i = 0
    while i < len(raw):
        if raw[i] in ("--inbox", "--round") and i + 1 < len(raw):
            opts[raw[i][2:]] = raw[i + 1]
            i += 2
        elif raw[i].startswith("--"):
            print(f"ERROR: unknown or incomplete option {raw[i]!r}", file=sys.stderr)
            return 1
        else:
            args.append(raw[i])
            i += 1

    if len(args) < 2:
        print(
            "Usage: python triage.py <concept-root> <output-dir> [--inbox DIR] [--round ID]",
            file=sys.stderr,
        )
        return 1

    concept_root = Path(args[0])
    output_dir = Path(args[1])
    inbox = Path(opts["inbox"]) if "inbox" in opts else concept_root.resolve().parent / ".data" / "annotations"
    round_id = opts.get("round") or "r-" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", round_id):
        print(f"ERROR: round id {round_id!r} is not usable as a file name", file=sys.stderr)
        return 1
    if not inbox.is_dir():
        print(f"ERROR: inbox directory not found: {inbox}", file=sys.stderr)
        return 1

    result = triage_inbox(inbox, concept_root, round_id)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{round_id}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    n_items = sum(len(g["items"]) for g in result["groups"]) + len(result["unresolved"])
    print(
        f"{n_items} open note(s) triaged across {len(result['groups'])} group(s); "
        f"{len(result['unresolved'])} unresolved; round {round_id}"
    )
    for u in result["unresolved"]:
        print(f"  UNRESOLVED {u['inboxId']}: {u['reason']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
