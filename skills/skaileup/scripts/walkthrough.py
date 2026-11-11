#!/usr/bin/env python3
"""walkthrough.py — the concept walk of a project: four stages, the user's yes on each.

    python3 walkthrough.py <command> [--root <project>]

The node is `tree/01_meta/walkthrough.md`; its `## Format` stage table is mirrored by `STAGES`
below. The state file `_concept/01_meta/walkthrough.yaml` stores only the user's stage decisions
(approved / waived / reopened) and their sources; every check is computed from the artifacts.

Commands
  init                                write all four stages `open` when the file is absent
  status                              one row per stage: stored status, each check, the next skill
  next                                the next skill and the check it fixes, or `build: all stages settled`
  approve <stage> --source "<text>"   record the user's yes; exit 2 listing every blocker
  waive <stage> --dr DR-<n> --source "<text>"
                                      record a waive backed by a decision record; exit 2 without one
  reopen <stage> --reason "<text>"    set the stage and every later one `open`
  gate build                          exit 0 iff frame, look and data are approved or waived, else 3
  gate feature <featureset>/<feature> gate build, the feature spec and its screens approved, else 3
  guard --write                       write the walkthrough section into the project's agent file

Exit codes: 0 done, 2 refused or bad input, 3 gate closed, 4 PyYAML missing.
Stdlib + PyYAML only.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

yaml = None  # PyYAML, imported in main() so a missing install prints its own message

STATE = "_concept/01_meta/walkthrough.yaml"
DECISIONS = "_concept/10_blueprint/decisions.md"
APP_DESIGN = "APP-DESIGN.md"
STORYBOOK = "_concept/09_mockup/storybook/src"
STATUSES = ("open", "approved", "waived")
OPEN_MARKERS = ("[open Q", "(proposed by")
DR_RE = re.compile(r"^DR-[0-9]+$")

OK, MISSING, UNAPPROVED, MARKERS = "ok", "missing", "unapproved", "open markers"


# --------------------------------------------------------------------------
# reading artifacts
# --------------------------------------------------------------------------

def read_text(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.is_file() else None


def frontmatter(text: str) -> dict | None:
    m = re.match(r"---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def is_approved(path: Path) -> bool:
    """`tree/README.md § Frontmatter every markdown artifact carries`: approved = the frontmatter carries an `approved:` value."""
    text = read_text(path)
    fm = frontmatter(text) if text is not None else None
    return bool(fm) and fm.get("approved") not in (None, "")


def approval(path: Path) -> str:
    if not path.is_file():
        return MISSING
    return OK if is_approved(path) else UNAPPROVED


def section(text: str, heading: str) -> str | None:
    """The body under `## <heading>` up to the next `#`/`##` heading; None when absent."""
    m = re.search(rf"^##[ \t]+{re.escape(heading)}[ \t]*$", text, re.M)
    if not m:
        return None
    end = re.search(r"^#{1,2}[ \t]", text[m.end():], re.M)
    return text[m.end():m.end() + end.start()] if end else text[m.end():]


def has_markers(text: str, markers=OPEN_MARKERS) -> bool:
    return any(mark in text for mark in markers)


# --------------------------------------------------------------------------
# the checks, one per cell entry of the stage table
# --------------------------------------------------------------------------

def exists(*rels: str) -> Callable[[Path], str]:
    return lambda root: OK if all((root / r).is_file() for r in rels) else MISSING


def approved(rel: str) -> Callable[[Path], str]:
    return lambda root: approval(root / rel)


def shell_decided(root: Path) -> str:
    path = root / "_concept/07_screens/shell.md"
    state = approval(path)
    if state != OK:
        return state
    fm = frontmatter(path.read_text(encoding="utf-8")) or {}
    return OK if fm.get("navigation") == "decided" else MARKERS


def navigation_model(root: Path) -> str:
    text = read_text(root / APP_DESIGN)
    body = section(text, "Navigation model") if text is not None else None
    if body is None:
        return MISSING
    return MARKERS if "[open Q" in body else OK


def model_settled(root: Path) -> str:
    text = read_text(root / "_concept/10_blueprint/datamodel/model.yaml")
    if text is None:
        return MISSING
    return MARKERS if "proposed:" in text else OK


def object_map(root: Path) -> str:
    text = read_text(root / APP_DESIGN)
    objects = section(text, "Objects") if text is not None else None
    if objects is None:
        return MISSING
    hierarchy = section(text, "Information hierarchy") or ""
    if has_markers(objects) or has_markers(hierarchy):
        return MARKERS
    return OK if re.search(r"^\|\s*OBJ-", objects, re.M) else MISSING


def any_dir(pattern: str) -> Callable[[Path], str]:
    return lambda root: OK if any(p.is_dir() for p in root.glob(pattern)) else MISSING


def any_file(pattern: str) -> Callable[[Path], str]:
    return lambda root: OK if any(p.is_file() for p in root.glob(pattern)) else MISSING


def any_approved(pattern: str) -> Callable[[Path], str]:
    def check(root: Path) -> str:
        files = [p for p in root.glob(pattern) if p.is_file()]
        if not files:
            return MISSING
        return OK if any(is_approved(p) for p in files) else UNAPPROVED
    return check


@dataclass(frozen=True)
class Check:
    text: str                       # the cell entry, verbatim
    skill: str                      # the producing skill that makes it pass
    run: Callable[[Path], str]      # root -> ok | missing | unapproved | open markers


@dataclass(frozen=True)
class Stage:
    name: str
    checks: tuple[Check, ...]
    skills: tuple[str, ...]         # the cell entries, verbatim; a trailing `?` marks an optional skill
    checkpoint: str


STAGES: list[Stage] = [
    Stage(
        "frame",
        (
            Check("`_concept/01_meta/expectations.md` exists", "skaileup",
                  exists("_concept/01_meta/expectations.md")),
            Check("`_concept/brief.md` approved", "concept-brief", approved("_concept/brief.md")),
            Check("`_concept/goals.md` approved", "concept-brief", approved("_concept/goals.md")),
            Check("`_concept/glossary.md` exists", "concept-glossary", exists("_concept/glossary.md")),
            Check("`_concept/04_journeys/stories.yaml` exists", "experience-journeys",
                  exists("_concept/04_journeys/stories.yaml")),
        ),
        ("skaileup (expectations)", "concept-onboard?", "concept-research?", "concept-brief",
         "concept-glossary", "experience-journeys"),
        "completion summary: pitch, roles, story-map stages",
    ),
    Stage(
        "look",
        (
            Check("`_concept/03_brand/identity.md` approved", "design-brand",
                  approved("_concept/03_brand/identity.md")),
            Check("`_concept/03_brand/brand.tokens.json` exists", "design-brand",
                  exists("_concept/03_brand/brand.tokens.json")),
            Check("`_concept/07_screens/shell.md` approved and contains `navigation: decided`",
                  "experience-shell", shell_decided),
            Check("`APP-DESIGN.md` exists with no `[open Q` in `## Navigation model`",
                  "experience-interaction", navigation_model),
            Check("`_concept/09_mockup/storybook/src/app/nav.ts` exists", "mockup-storybook",
                  exists(f"{STORYBOOK}/app/nav.ts")),
        ),
        ("design-brand", "experience-interaction (navigation-model batch)", "experience-shell",
         "mockup-storybook (App frame)"),
        "Storybook `App` story: shell + brand + one pending page per destination",
    ),
    Stage(
        "data",
        (
            Check("`_concept/10_blueprint/datamodel/model.yaml` and `seed.yaml` exist",
                  "architecture-datamodel",
                  exists("_concept/10_blueprint/datamodel/model.yaml", "_concept/10_blueprint/datamodel/seed.yaml")),
            Check("`model.yaml` contains no `proposed:`", "architecture-datamodel", model_settled),
            Check("`APP-DESIGN.md` `## Objects` has ≥1 `OBJ-` row and neither `## Objects` nor "
                  "`## Information hierarchy` contains `[open Q` or `(proposed by`",
                  "experience-interaction", object_map),
            Check("≥1 directory `_concept/09_mockup/storybook/src/entities/*/`", "mockup-storybook",
                  any_dir(f"{STORYBOOK}/entities/*/")),
        ),
        ("concept-glossary (object axes)", "architecture-datamodel", "experience-interaction (objects batch)",
         "mockup-storybook (entity stories)"),
        "Storybook `Entities/<Entity>/*` for every object-map row",
    ),
    Stage(
        "features",
        (
            Check("`_concept/05_features/featuresets.md` approved", "spec-feature",
                  approved("_concept/05_features/featuresets.md")),
            Check("≥1 `_concept/05_features/*/*.md` approved", "spec-feature",
                  any_approved("_concept/05_features/*/*.md")),
            Check("`APP-DESIGN.md` approved", "experience-interaction", approved(APP_DESIGN)),
            Check("≥1 `_concept/09_mockup/storybook/src/journeys/*.stories.ts`", "mockup-storybook",
                  any_file(f"{STORYBOOK}/journeys/*.stories.ts")),
        ),
        ("experience-behaviors?", "spec-feature (loop)", "experience-screen",
         "mockup-storybook (screens, App, journeys)", "mockup-feedback"),
        "Storybook App + Journeys; a feedback round with no open notes",
    ),
]
STAGE_NAMES = [s.name for s in STAGES]
BUILD_STAGES = ("frame", "look", "data")


def skill_id(entry: str) -> str:
    return entry.split()[0].rstrip("?")


def failing(stage: Stage, root: Path) -> list[tuple[Check, str]]:
    """The failing checks in walk order: by the position of their skill in the stage's skill list."""
    order = [skill_id(s) for s in stage.skills]
    results = [(i, c, c.run(root)) for i, c in enumerate(stage.checks)]
    bad = [(i, c, r) for i, c, r in results if r != OK]
    bad.sort(key=lambda t: (order.index(t[1].skill) if t[1].skill in order else len(order), t[0]))
    return [(c, r) for _, c, r in bad]


def plain(text: str) -> str:
    return text.replace("`", "")


def next_step(stage: Stage, root: Path) -> tuple[str, str]:
    """(skill, check) that moves the stage on; all checks passing leaves the user's yes."""
    bad = failing(stage, root)
    if bad:
        check, result = bad[0]
        return check.skill, f"{plain(check.text)} ({result})"
    return "skaileup", f"the user's yes on {stage.name}"


# --------------------------------------------------------------------------
# the state file
# --------------------------------------------------------------------------

class Refused(Exception):
    """Exit 2 with the message."""


def today() -> str:
    return datetime.date.today().isoformat()


def as_text(value) -> str:
    return value.isoformat() if isinstance(value, datetime.date) else str(value)


def load(root: Path) -> dict | None:
    path = root / STATE
    if not path.is_file():
        return None
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as err:
        raise Refused(f"{STATE} is not valid YAML: {err}")
    if not isinstance(doc, dict) or not isinstance(doc.get("stages") or {}, dict):
        raise Refused(f"{STATE} has no `stages:` mapping — see tree/01_meta/walkthrough.md § Format")
    stages = {}
    for name in STAGE_NAMES:
        entry = (doc.get("stages") or {}).get(name) or {"status": "open"}
        if not isinstance(entry, dict) or entry.get("status") not in STATUSES:
            raise Refused(f"{STATE}: stage {name!r} has no status out of {', '.join(STATUSES)}")
        stages[name] = {k: (v if k == "status" else as_text(v)) for k, v in entry.items()}
    history = doc.get("history") or []
    if not isinstance(history, list) or not all(isinstance(e, dict) for e in history):
        raise Refused(f"{STATE}: `history:` is not a list of events")
    # YAML 1.1 (PyYAML) reads a bare `on:` key as the boolean true; it is the event's date
    return {"stages": stages, "history": [{("on" if k is True else str(k)): as_text(v) for k, v in e.items()}
                                          for e in history]}


def fresh() -> dict:
    return {"stages": {name: {"status": "open"} for name in STAGE_NAMES}, "history": []}


PLAIN_KEYS = {"status", "stage", "event"}  # enum tokens, written unquoted
STAGE_KEYS = ("status", "approved", "dr", "source")
EVENT_KEYS = ("on", "stage", "event", "reason", "source", "dr")


def flow_map(entry: dict, keys: tuple[str, ...]) -> str:
    """One flow mapping; `on` is quoted as a key because YAML 1.1 reads a bare `on` as true."""
    parts = [f"{json.dumps(k) if k == 'on' else k}: "
             f"{entry[k] if k in PLAIN_KEYS else json.dumps(entry[k], ensure_ascii=False)}"
             for k in keys if entry.get(k) not in (None, "")]
    return "{ " + ", ".join(parts) + " }"


def save(root: Path, state: dict) -> None:
    lines = ["# Written by walkthrough.py (skaileup) only — tree/01_meta/walkthrough.md", "stages:"]
    lines += [f"  {name}: {flow_map(state['stages'][name], STAGE_KEYS)}" for name in STAGE_NAMES]
    if state["history"]:
        lines.append("history:   # append-only")
        lines += [f"  - {flow_map(e, EVENT_KEYS)}" for e in state["history"]]
    else:
        lines.append("history: []   # append-only")
    path = root / STATE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def settled(state: dict | None, name: str) -> bool:
    return state is not None and state["stages"][name]["status"] in ("approved", "waived")


def stage_of(name: str) -> Stage:
    return STAGES[STAGE_NAMES.index(name)]


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def cmd_init(root: Path, _args) -> int:
    if (root / STATE).is_file():
        print("walkthrough.yaml exists")
        return 0
    save(root, fresh())
    print(f"wrote {STATE}: all four stages open")
    return 0


def cmd_status(root: Path, _args) -> int:
    state = load(root)
    if state is None:
        print(f"no {STATE} — run the skaileup skill")
    labels = max(len(label) for label in (OK, MISSING, UNAPPROVED, MARKERS))
    for stage in STAGES:
        status = state["stages"][stage.name]["status"] if state else "open"
        entry = state["stages"][stage.name] if state else {}
        detail = entry.get("approved") or entry.get("dr") or ""
        if settled(state, stage.name):
            nxt = "-"
        else:
            skill, check = next_step(stage, root)
            nxt = f"{skill} → {check}"
        print(f"{stage.name:<9} {status:<9}{' ' + detail if detail else ''}   next: {nxt}")
        for check in stage.checks:
            print(f"  {check.run(root):<{labels}}  {plain(check.text)}")
    return 0


def cmd_next(root: Path, _args) -> int:
    state = load(root)
    for stage in STAGES:
        if not settled(state, stage.name):
            skill, check = next_step(stage, root)
            print(f"{stage.name}: {skill} → {check}")
            return 0
    print("build: all stages settled")
    return 0


def require_state(root: Path) -> dict:
    state = load(root)
    if state is None:
        raise Refused(f"no {STATE} — run `walkthrough.py init` from the skaileup skill first")
    return state


def cmd_approve(root: Path, args) -> int:
    state = require_state(root)
    stage = stage_of(args.stage)
    if state["stages"][stage.name]["status"] == "approved":
        print(f"{stage.name} is already approved")
        return 0
    blockers = [f"stage '{s}' is open" for s in STAGE_NAMES[:STAGE_NAMES.index(stage.name)]
                if not settled(state, s)]
    blockers += [f"{plain(c.text)}: {r}" for c, r in failing(stage, root)]
    if blockers:
        raise Refused(f"cannot approve '{stage.name}':\n" + "\n".join(f"  - {b}" for b in blockers))
    on = today()
    state["stages"][stage.name] = {"status": "approved", "approved": on, "source": args.source}
    state["history"].append({"on": on, "stage": stage.name, "event": "approved", "source": args.source})
    save(root, state)
    print(f"approved {stage.name} ({args.source})")
    return 0


def cmd_waive(root: Path, args) -> int:
    state = require_state(root)
    if not DR_RE.match(args.dr):
        raise Refused(f"--dr {args.dr!r} is not a decision record id (DR-<n>)")
    decisions = read_text(root / DECISIONS) or ""
    if not re.search(rf"\b{re.escape(args.dr)}(?![0-9])", decisions):
        raise Refused(f"{args.dr} does not occur in {DECISIONS} — record the user's decision there first")
    on = today()
    state["stages"][args.stage] = {"status": "waived", "dr": args.dr, "source": args.source}
    state["history"].append({"on": on, "stage": args.stage, "event": "waived",
                             "source": args.source, "dr": args.dr})
    save(root, state)
    print(f"waived {args.stage} ({args.dr}, {args.source})")
    return 0


def cmd_reopen(root: Path, args) -> int:
    state = require_state(root)
    on = today()
    changed = []
    for name in STAGE_NAMES[STAGE_NAMES.index(args.stage):]:
        if state["stages"][name]["status"] != "open":
            state["stages"][name] = {"status": "open"}
            state["history"].append({"on": on, "stage": name, "event": "reopened", "reason": args.reason})
            changed.append(name)
    if not changed:
        print(f"{args.stage} and every later stage are already open")
        return 0
    save(root, state)
    print(f"reopened {', '.join(changed)}")
    return 0


def gate_build(root: Path, state: dict | None) -> str | None:
    """The gate message for the first open build stage, None when frame, look and data are settled."""
    for name in BUILD_STAGES:
        if not settled(state, name):
            skill, check = next_step(stage_of(name), root)
            return (f"Concept stage '{name}' is open — run the skaileup skill to continue the walk "
                    f"(next: {skill} → {check}).")
    return None


def screen_paths(screens) -> list[str]:
    """`screens:` entries (`- path: 07_screens/<screen>.md`, a proposed mapping, or a bare id) as paths."""
    paths = []
    for entry in screens if isinstance(screens, list) else []:
        ref = (entry.get("path") or entry.get("screen_id") or entry.get("id")) if isinstance(entry, dict) else entry
        if not ref:
            continue
        ref = str(ref)
        if "/" in ref or ref.endswith(".md"):
            paths.append("_concept/" + ref.removeprefix("_concept/"))
        else:
            paths.append(f"_concept/07_screens/{ref}.md")
    return paths


def gate_feature(root: Path, target: str) -> str | None:
    feature = root / "_concept/05_features" / f"{target}.md"
    rel = f"_concept/05_features/{target}.md"
    if not feature.is_file():
        return f"Feature spec {rel} is missing — run spec-feature for it."
    if not is_approved(feature):
        return f"Feature spec {rel} is not approved — run spec-feature and ask the user for the yes."
    fm = frontmatter(feature.read_text(encoding="utf-8")) or {}
    for screen in screen_paths(fm.get("screens")):
        state = approval(root / screen)
        if state == MISSING:
            return f"Screen {screen} of {target} is missing — run experience-screen for it."
        if state == UNAPPROVED:
            return f"Screen {screen} of {target} is not approved — run experience-screen and ask the user for the yes."
    return None


def cmd_gate(root: Path, args) -> int:
    target = (args.target or "").removesuffix(".md")
    if args.what == "build" and target:
        raise Refused("gate build takes no argument")
    if args.what == "feature" and not re.fullmatch(r"[^/\s.][^/\s]*/[^/\s.][^/\s]*", target):
        raise Refused("gate feature needs <featureset>/<feature>, e.g. `gate feature polls/create-poll`")
    message = gate_build(root, load(root))
    if message is None and args.what == "feature":
        message = gate_feature(root, target)
    if message:
        print(message)
        return 3
    print("gate open: frame, look and data are settled" + (f"; {target} is approved" if args.what == "feature" else ""))
    return 0


GUARD_START = "<!-- skaileup:walkthrough -->"
GUARD_END = "<!-- /skaileup:walkthrough -->"
GUARD = """<!-- skaileup:walkthrough -->
## Concept walkthrough (skaileup)
This app is specified top-down before it is built: frame → look → data → features (`_concept/01_meta/walkthrough.yaml`).
- Before planning, ticketing or orchestrating any implementation, run `python3 <skills-dir>/scripts/walkthrough.py gate build` from the project root. A non-zero exit means a stage is open: run the `skaileup` skill and continue the walk instead of planning code.
- A request that changes the look, the data model or a feature first reopens its stage (`walkthrough.py reopen <stage> --reason "<the user's words>"`) and updates the concept; code follows the re-approved concept.
- Subagents never answer a question the user owns; they return it as a decision batch and the session agent asks the user.
- A stage is approved only with the user's explicit yes in the conversation (`walkthrough.py approve <stage> --source "user, <date>"`).
<!-- /skaileup:walkthrough -->"""


def skills_dir(root: Path) -> str:
    """This script's skill directory, relative to the project root when it sits inside it."""
    skill = Path(__file__).resolve().parent.parent
    try:
        return skill.relative_to(root.resolve()).as_posix()
    except ValueError:
        return skill.as_posix()


def cmd_guard(root: Path, _args) -> int:
    block = GUARD.replace("<skills-dir>", skills_dir(root))
    target = next((root / n for n in ("AGENTS.md", "CLAUDE.md") if (root / n).is_file()), root / "AGENTS.md")
    text = read_text(target)
    if text is None:
        text = block + "\n"
    else:
        start, end = text.find(GUARD_START), text.find(GUARD_END)
        if start != -1 and end > start:
            text = text[:start] + block + text[end + len(GUARD_END):]
        else:
            text = (text.rstrip("\n") + "\n\n" if text.strip() else "") + block + "\n"
    target.write_text(text, encoding="utf-8")
    print(f"wrote the walkthrough section to {target.name}")
    return 0


# --------------------------------------------------------------------------
# entry
# --------------------------------------------------------------------------

def parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=".", help="the project root (default: .)")
    p = argparse.ArgumentParser(prog="walkthrough.py", description="The concept walk of a project.")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init", parents=[common]).set_defaults(run=cmd_init)
    sub.add_parser("status", parents=[common]).set_defaults(run=cmd_status)
    sub.add_parser("next", parents=[common]).set_defaults(run=cmd_next)
    a = sub.add_parser("approve", parents=[common])
    a.add_argument("stage", choices=STAGE_NAMES)
    a.add_argument("--source", required=True, help='e.g. "user, 2026-11-08"')
    a.set_defaults(run=cmd_approve)
    w = sub.add_parser("waive", parents=[common])
    w.add_argument("stage", choices=STAGE_NAMES)
    w.add_argument("--dr", required=True, help="the decision record, DR-<n>")
    w.add_argument("--source", required=True)
    w.set_defaults(run=cmd_waive)
    r = sub.add_parser("reopen", parents=[common])
    r.add_argument("stage", choices=STAGE_NAMES)
    r.add_argument("--reason", required=True, help="the user's words")
    r.set_defaults(run=cmd_reopen)
    g = sub.add_parser("gate", parents=[common])
    g.add_argument("what", choices=("build", "feature"))
    g.add_argument("target", nargs="?", help="<featureset>/<feature> for `gate feature`")
    g.set_defaults(run=cmd_gate)
    gd = sub.add_parser("guard", parents=[common])
    gd.add_argument("--write", action="store_true", required=True)
    gd.set_defaults(run=cmd_guard)
    return p


def main(argv: list[str]) -> int:
    global yaml
    args = parser().parse_args(argv[1:])
    try:
        import yaml as _yaml
    except ImportError:
        print("walkthrough.py needs PyYAML: python3 -m pip install pyyaml")
        return 4
    yaml = _yaml
    root = Path(args.root)
    if not root.is_dir():
        print(f"{root}: not a directory")
        return 2
    try:
        return args.run(root, args)
    except Refused as err:
        print(err)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
