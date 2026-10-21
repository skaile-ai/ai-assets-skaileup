#!/usr/bin/env python3
"""check_concept.py — the mechanical half of ops-review, run against a project's `_concept/`.

    python3 check_concept.py <project-root | _concept-dir>

One line per problem, `path: message`; exit 0 when clean, 1 when anything is reported.
Stdlib + PyYAML only. Checks:

  1. root layout     every first-level entry is in the tree; the retired paths
                     (`comparable.md`, `10_blueprint/glossary.md`, `10_blueprint/datamodel/feature-map.json`,
                     `03_brand/tokens.json`, `11_build/interaction.yaml`) are reported as unowned
  2. frontmatter     `last_updated` (and `approved`, when present) is an ISO date on every
                     artifact markdown file, plus the fields its artifact type requires
  3. cross-links     a feature's `screens:` and a screen's `implements:` resolve, in both directions
                     (a screen's `implements:` entry is a path or a `{path, status: proposed, …}`
                     mapping; either one satisfies the link)
  4. data_entities   every name is an entity `id` in `10_blueprint/datamodel/model.json` (skipped without one)
  5. criterion ids   every `AC-…` a feature spec or ledger cites follows the id grammar and is
                     defined by `04_journeys/stories.yaml` (skipped without one), scoped to the
                     feature's own slug, or scoped to another feature whose spec carries it
  6. ledger          `11_build/acceptance-criteria/<featureset>/<feature>.ac.md` rows are checkbox
                     lines with a PASS/FAIL/empty marker; evaluated rows carry
                     `<pointer> · <evaluator> · <commit> · <date>`, untested rows the id alone
  7. stale proposals every `proposed_on:` date (or `proposed by <skill>, <date>` marker) in an artifact
                     that is older than `--stale-days` (default 14) is reported with the owner skill that
                     promotes or rejects it
  8. open questions  every `## Open` row of `APP-DESIGN.md` and every `### Open` bullet of a screen spec
                     carries a recommendation; an `[open Qn]` entry has its row
  9. hard gates      `unproduced_hard_gates()` — a `hard` gate in a sibling skill's frontmatter that no
                     skill produces (run from `main` over the skills directory the script sits in)

A screen whose `floorplan:` is missing or empty is reported under 2; the floorplan is the one fact the
walkthrough and `quality-design` read it by.

The tree's legal first-level entries are parsed from the fenced tree in `tree/README.md` (a
```text fence opening `_concept/` plus a summary column) when the script sits in the
collection (`../../../tree/`), or from the installed copy
(`../../../contracts/shared-contracts/README.md`); with neither, the built-in list below,
mirrored from that fence, is used. An entry is the first token after the box-drawing prefix —
the summary column is ignored — and a directory's trailing `/` is dropped.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

import yaml

BUILTIN_ROOT = ["README.md", "brief.md", "goals.md", "glossary.md", "01_meta", "02_grounding",
                "03_brand", "04_journeys", "05_features", "06_behaviors", "07_screens",
                "08_dossiers", "09_mockup", "10_blueprint", "11_build"]
RETIRED = {
    "comparable.md": "folded into brief.md `## Comparables`",
    "10_blueprint/glossary.md": "the glossary is `glossary.md` at the root",
    "10_blueprint/datamodel/feature-map.json": "the join is each feature spec's `data_entities[]`",
    "03_brand/tokens.json": "renamed to `brand.tokens.json`, DTCG format — ADR 0016",
    "11_build/interaction.yaml": "replaced by `interaction.sarif` — ADR 0016",
}
REQUIRED = {  # artifact path (or glob-ish key) -> fields beyond last_updated
    "brief.md": ["elevator_pitch", "audience", "problem", "hero_flow"],
    "goals.md": ["success_criteria", "kpis", "constraints", "non_goals"],
    "03_brand/identity.md": ["mood", "mode"],
    "07_screens/shell.md": ["elements"],
    "10_blueprint/techstack.md": ["platform", "tech_stack_skill"],
    "10_blueprint/architecture.md": ["apps", "external_integrations"],
    "feature": ["priority", "permissions", "screens", "data_entities"],
    "screen": ["screen_id", "floorplan", "implements"],
    "ledger": ["feature", "feature_ref"],
}
# A story id never contains `-`; a feature slug may. Either way the id ends in `-<nn>`, so the
# scope is everything between `AC-` and the last `-`.
STORY_ID_RE = re.compile(r"^AC-([a-z0-9_]+)-(\d{2})$")
ID_RE = re.compile(r"^AC-([a-z0-9][a-z0-9_-]*)-(\d{2})$")
CITE_RE = re.compile(r"AC-[A-Za-z0-9_-]+")
ROW_RE = re.compile(r"^- \[(PASS|FAIL| )\] (\S+)(?: — (.*))?$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
PROPOSED_ON_RE = re.compile(r"proposed_on:\s*[\"']?(\d{4}-\d{2}-\d{2})")
PROPOSED_BY_RE = re.compile(r"proposed by [a-z][a-z0-9-]*, (\d{4}-\d{2}-\d{2})")
STALE_DAYS = 14
# Parts that quote proposals without holding one: findings carry code evidence, the decision
# records and the candidate report cite entries they already settled or reported.
PROPOSAL_SKIP = ("02_grounding/", "10_blueprint/decisions.md", "11_build/decisions.md",
                 "11_build/design-candidates.md")
PROPOSAL_OWNERS = (  # display-path prefix -> the skill that promotes or rejects a proposal there
    ("APP-DESIGN.md", "experience-interaction"),
    ("_concept/glossary.md", "concept-glossary"),
    ("_concept/07_screens/shell.md", "experience-shell"),
    ("_concept/07_screens/", "experience-screen"),
    ("_concept/05_features/", "spec-feature"),
    ("_concept/01_meta/scope.yaml", "skaileup"),
    ("_concept/10_blueprint/datamodel/", "architecture-datamodel"),
)
NO_RECOMMENDATION = {"", "-", "—", "?", "tbd", "TBD", "n/a"}


def root_entries(here: Path) -> list[str]:
    root = here.parents[3] if len(here.parents) > 3 else None
    for tree in (root / "tree" / "README.md", root / "contracts" / "shared-contracts" / "README.md") \
            if root else ():
        if tree.is_file():
            fence = re.search(r"```[a-z]*\n_concept/[^\n]*\n(.*?)```", tree.read_text(encoding="utf-8"), re.S)
            found = re.findall(r"^[├└]── (\S+)", fence.group(1), re.M) if fence else []
            if found:
                return [e.rstrip("/") for e in found]
    return BUILTIN_ROOT


def frontmatter(path: Path):
    """(dict | None, body). None when the file has no parseable frontmatter block."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return None, text
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None, m.group(2)
    return (data if isinstance(data, dict) else None), m.group(2)


def is_date(v) -> bool:
    if isinstance(v, datetime.date):
        return True
    try:
        datetime.date.fromisoformat(str(v))
        return isinstance(v, str)
    except ValueError:
        return False


def model_names(model) -> set[str] | None:
    """Entity ids of a model.json: the model names `data_entities[]` cites.

    None when the file has no `entities[]` list (the old `models` / `name` shape): the caller
    reports that once rather than a finding per cited name."""
    entities = model.get("entities") if isinstance(model, dict) else None
    if not isinstance(entities, list):
        return None
    return {e["id"] for e in entities if isinstance(e, dict) and isinstance(e.get("id"), str)}


def listed_paths(value) -> list[str]:
    out = []
    for item in value if isinstance(value, list) else []:
        raw = item.get("path") if isinstance(item, dict) else item
        if isinstance(raw, str):
            out.append(raw.removeprefix("_concept/"))
    return out


def story_ids(stories: dict, report) -> tuple[set[str], set[str]]:
    """Criterion ids and story (journey) ids defined in stories.yaml; each criterion id must be
    well-formed and scoped to its journey."""
    defined: set[str] = set()

    def walk(node, journey):
        if isinstance(node, dict):
            if "id" in node and isinstance(node["id"], str) and node["id"].startswith("AC-"):
                cid = node["id"]
                m = STORY_ID_RE.match(cid)
                if not m:
                    report("04_journeys/stories.yaml", f"criterion id {cid!r} is not AC-<story-id>-<nn>")
                elif journey and m.group(1) != journey:
                    report("04_journeys/stories.yaml", f"{cid} sits under journey {journey!r}")
                if cid in defined:
                    report("04_journeys/stories.yaml", f"{cid} defined twice")
                defined.add(cid)
            for v in node.values():
                walk(v, journey)
        elif isinstance(node, list):
            for v in node:
                walk(v, journey)

    journeys = [j for j in stories.get("journeys") or [] if isinstance(j, dict)]
    for j in journeys:
        walk(j, j.get("id"))
    return defined, {j["id"] for j in journeys if isinstance(j.get("id"), str)}


def check(concept: Path, here: Path, today: datetime.date | None = None,
          stale_days: int = STALE_DAYS) -> list[str]:
    problems: list[str] = []

    def report(path, msg):
        problems.append(f"_concept/{path}: {msg}")

    def rel(p: Path) -> str:
        return p.relative_to(concept).as_posix()

    # 1. layout
    legal = root_entries(here)
    for entry in sorted(concept.iterdir()):
        if entry.name not in legal and entry.name not in RETIRED:
            report(entry.name, "unowned — not an entry of the _concept/ tree")
    for path, why in RETIRED.items():
        if (concept / path).exists():
            report(path, f"unowned — retired path ({why})")

    # models, stories
    model = None
    mj = concept / "10_blueprint/datamodel/model.json"
    if mj.is_file():
        try:
            model = model_names(json.loads(mj.read_text()))
            if model is None:
                report(rel(mj), "no `entities[]` list (format: tree/10_blueprint/datamodel/model.md)")
        except json.JSONDecodeError as e:
            report(rel(mj), f"not valid JSON ({e.msg})")
    defined = stories = None
    sy = concept / "04_journeys/stories.yaml"
    if sy.is_file():
        try:
            defined, stories = story_ids(yaml.safe_load(sy.read_text()) or {}, report)
        except yaml.YAMLError:
            report(rel(sy), "not valid YAML")

    # artifact classification
    features = sorted(p for p in (concept / "05_features").glob("*/*.md")) if (concept / "05_features").is_dir() else []
    screens = sorted(p for p in (concept / "07_screens").glob("*.md") if p.name != "shell.md") \
        if (concept / "07_screens").is_dir() else []
    ledgers = sorted((concept / "11_build/acceptance-criteria").glob("*/*.ac.md")) \
        if (concept / "11_build/acceptance-criteria").is_dir() else []
    dossiers = sorted((concept / "08_dossiers").glob("*/index.md")) if (concept / "08_dossiers").is_dir() else []
    plain = [concept / k for k in REQUIRED if "/" in k or k.endswith(".md") if (concept / k).is_file()]
    other = [p for d in ("05_features", "06_behaviors") for p in (concept / d).glob("*.md")] + \
        [p for p in (concept / "02_grounding/research").glob("*.md")] + [concept / "glossary.md"]
    kind = {**{p: "feature" for p in features}, **{p: "screen" for p in screens},
            **{p: "ledger" for p in ledgers}, **{p: "dossier" for p in dossiers}}

    # 2. frontmatter
    fm: dict[Path, dict] = {}
    for p in dict.fromkeys(plain + other + list(kind)):
        if not p.is_file():
            continue
        data, _ = frontmatter(p)
        if data is None:
            report(rel(p), "no YAML frontmatter")
            continue
        fm[p] = data
        need = ["last_updated"] + REQUIRED.get(kind.get(p) or rel(p), [])
        for field in need:
            if field not in data:
                report(rel(p), f"frontmatter lacks `{field}`")
        for field in ("last_updated", "approved"):
            if field in data and not is_date(data[field]):
                report(rel(p), f"`{field}` is not an ISO date: {data[field]!r}")
        if kind.get(p) == "dossier" and data.get("status") not in ("open", "frozen"):
            report(rel(p), "`status` must be open or frozen")
        if p not in dossiers and "status" in data:
            report(rel(p), "`status:` belongs to dossiers only — a stale template wrote it")
        if kind.get(p) == "screen" and "screen_id" in data and data["screen_id"] != p.stem:
            report(rel(p), f"`screen_id` {data['screen_id']!r} does not match the file name {p.stem!r}")
        if kind.get(p) == "screen" and "floorplan" in data and not (
                isinstance(data["floorplan"], str) and data["floorplan"].strip()):
            report(rel(p), "`floorplan` is empty — name one floorplan id of `rulebook/floorplans/`")

    # 3. cross-links
    for f in features:
        for target in listed_paths(fm.get(f, {}).get("screens")):
            s = concept / target
            if not s.is_file():
                report(rel(f), f"screens: {target} does not exist")
            elif rel(f) not in listed_paths(fm.get(s, {}).get("implements")):
                report(rel(s), f"implements: does not name {rel(f)}, which lists it in screens:")
    for s in screens:
        for target in listed_paths(fm.get(s, {}).get("implements")):
            f = concept / target
            if not f.is_file():
                report(rel(s), f"implements: {target} does not exist")
            elif rel(s) not in listed_paths(fm.get(f, {}).get("screens")):
                report(rel(f), f"screens: does not list {rel(s)}, which implements it")

    # 4. data_entities
    if model is not None:
        for p in features + screens:
            names = fm.get(p, {}).get("data_entities") or []
            for name in names if isinstance(names, list) else [names]:
                if name not in model:
                    report(rel(p), f"data_entities: {name} is not a model in model.json")

    # 5. criterion ids cited by feature specs
    cited: dict[Path, set[str]] = {}
    for f in features:
        cited[f] = set(CITE_RE.findall(frontmatter(f)[1]))
    # A feature-scoped id belongs to the spec named by its scope; another spec may cite it.
    owned = {f.stem: cited[f] for f in features}
    for f in features:
        for cid in sorted(cited[f]):
            report_id(cid, f.stem, defined, stories, owned, rel(f), report)

    # 6. ledger
    for ac in ledgers:
        data, body = frontmatter(ac)
        feature = (data or {}).get("feature")
        if feature is not None and feature != ac.name.removesuffix(".ac.md"):
            report(rel(ac), f"feature: {feature!r} does not match the file name")
        ref = str((data or {}).get("feature_ref", "")).removeprefix("_concept/")
        spec = concept / ref if ref else None
        if ref and not spec.is_file():
            report(rel(ac), f"feature_ref: {ref} does not exist")
        slug = ac.name.removesuffix(".ac.md")
        offset = ac.read_text(encoding="utf-8").count("\n") - body.count("\n")
        for n, line in enumerate(body.splitlines(), offset + 1):
            if not line.startswith(("- ", "|")):
                continue
            m = ROW_RE.match(line)
            where = f"{rel(ac)}:{n}"
            if not m:
                report(where, "not a ledger row — rows are `- [ ] <id>` or `- [PASS|FAIL] <id> — <evidence>`")
                continue
            marker, cid, evidence = m.groups()
            report_id(cid, slug, defined, stories, owned, where, report)
            if spec and spec in cited and cid not in cited[spec]:
                report(where, f"{cid} is not cited in {ref}")
            if marker == " " and evidence:
                report(where, "an untested row carries the id alone")
            if marker != " ":
                parts = [x.strip() for x in (evidence or "").split(" · ")]
                if len(parts) != 4 or not all(parts) or not COMMIT_RE.match(parts[2]) or not is_date(parts[3]):
                    report(where, "evidence must be `<pointer> · <evaluator> · <commit> · <date>`")

    # 7-8. proposals and open questions
    root = concept.parent
    problems += stale_proposals(concept, root, today or datetime.date.today(), stale_days)
    problems += open_question_problems(concept, root, screens + [concept / "07_screens/shell.md"])
    return problems


def stale_proposals(concept: Path, root: Path, today: datetime.date, days: int) -> list[str]:
    """One line per `proposed` entry whose proposal date is more than `days` days old."""
    out: list[str] = []
    files = [(p.relative_to(concept).as_posix(), p) for p in sorted(concept.rglob("*"))
             if p.is_file() and p.suffix in (".md", ".yaml", ".yml", ".json")]
    files = [(f"_concept/{rel}", p) for rel, p in files if not rel.startswith(PROPOSAL_SKIP)]
    if (root / "APP-DESIGN.md").is_file():
        files.append(("APP-DESIGN.md", root / "APP-DESIGN.md"))
    for shown, p in files:
        owner = next((o for prefix, o in PROPOSAL_OWNERS if shown.startswith(prefix)), "its owner skill")
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for pattern in (PROPOSED_ON_RE, PROPOSED_BY_RE):
                for m in pattern.finditer(line):
                    try:
                        age = (today - datetime.date.fromisoformat(m.group(1))).days
                    except ValueError:
                        continue
                    if age > days:
                        out.append(f"{shown}:{n}: proposed entry from {m.group(1)} is {age} days old "
                                   f"(limit {days}) — promote or reject it with {owner}")
    return out


def open_question_problems(concept: Path, root: Path, screens: list[Path]) -> list[str]:
    """Open questions without a recommendation: `APP-DESIGN.md` `## Open` rows (and `[open Qn]`
    entries with no row) and the `### Open` bullets of screen specs. A bullet has one when it
    contains the word "recommend"."""
    out: list[str] = []
    app = root / "APP-DESIGN.md"
    if app.is_file():
        lines = app.read_text(encoding="utf-8", errors="replace").splitlines()
        rows: set[str] = set()
        in_open = False
        for n, line in enumerate(lines, 1):
            if line.startswith("## "):
                in_open = line[3:].strip().lower() == "open"
            elif in_open and line.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if re.fullmatch(r"Q\d+", cells[0]):
                    rows.add(cells[0])
                    if len(cells) < 4 or cells[3] in NO_RECOMMENDATION:
                        out.append(f"APP-DESIGN.md:{n}: open question {cells[0]} has no recommendation "
                                   "— experience-interaction writes one beside every question")
        for n, line in enumerate(lines, 1):
            for qid in re.findall(r"\[open (Q\d+)\]", line):
                if qid not in rows:
                    out.append(f"APP-DESIGN.md:{n}: [open {qid}] has no row in `## Open` "
                               "— experience-interaction writes the question and its recommendation")
    for s in screens:
        if not s.is_file():
            continue
        shown = f"_concept/{s.relative_to(concept).as_posix()}"
        bullets: list[tuple[int, str]] = []
        in_open = False
        for n, line in enumerate(s.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.startswith("#"):
                in_open = line.lstrip("#").strip().lower() == "open"
            elif in_open and line.startswith("- "):
                bullets.append((n, line))
            elif in_open and bullets and line.strip():
                bullets[-1] = (bullets[-1][0], bullets[-1][1] + " " + line.strip())
        for n, text in bullets:
            if not re.search("recommend", text, re.I):
                out.append(f"{shown}:{n}: open question without a recommendation "
                           "— experience-screen states one beside every question")
    return out


def _paths_overlap(a: str, b: str) -> bool:
    """Equal, or one a directory prefix of the other; a `<placeholder>` segment matches any one."""
    pa, pb = a.strip("/").split("/"), b.strip("/").split("/")
    return all(x == y or ("<" in x and ">" in x) or ("<" in y and ">" in y) for x, y in zip(pa, pb))


def unproduced_hard_gates(skills_dir: Path) -> list[str]:
    """A `hard` gate in one skill's frontmatter that no *other* skill produces: a skill that can
    never open, reported as `skills/<name>/SKILL.md: …`. A gate outside `_concept/` other than
    `APP-DESIGN.md` (`package.json`) belongs to the project, not to a skill."""
    produced: dict[str, list[str]] = {}
    gates: dict[str, list[str]] = {}
    for skill in sorted(skills_dir.glob("*/SKILL.md")):
        data, _ = frontmatter(skill)
        meta = (data or {}).get("metadata") or {}
        arts = meta.get("artifacts") or {}
        produced[skill.parent.name] = listed_paths_raw(arts.get("produces"))
        gates[skill.parent.name] = [
            str(g["path"]) for g in (meta.get("prerequisites") or {}).get("files") or []
            if isinstance(g, dict) and g.get("gate") == "hard" and isinstance(g.get("path"), str)
        ]
    if len(produced) < 2:
        return []
    out = []
    for name, paths in gates.items():
        for gate in paths:
            if not gate.startswith("_concept/") and gate != "APP-DESIGN.md":
                continue
            if not any(_paths_overlap(gate, p) for other, ps in produced.items() if other != name for p in ps):
                out.append(f"skills/{name}/SKILL.md: hard gate on {gate} — no skill produces it; "
                           "make the gate soft or add the skill that writes it")
    return out


def listed_paths_raw(value) -> list[str]:
    """`path` of each `{ id, path }` entry, `_concept/` prefix kept."""
    return [i["path"] for i in value if isinstance(i, dict) and isinstance(i.get("path"), str)] \
        if isinstance(value, list) else []


def report_id(cid, slug, defined, stories, owned, where, report):
    m = ID_RE.match(cid)
    if not m:
        report(where, f"{cid} is not a criterion id (AC-<story-id>-<nn>)")
    elif defined is None or cid in defined:
        return
    elif m.group(1) != slug:
        scope = m.group(1)
        if scope not in owned:
            report(where, f"{cid} is neither in stories.yaml nor scoped to a feature")
        elif cid not in owned[scope]:
            report(where, f"{cid} is scoped to feature {scope!r}, whose spec does not carry it")
    elif slug in stories:
        report(where, f"{cid} is scoped to feature {slug!r}, which is also a story id")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check_concept.py", add_help=False)
    parser.add_argument("project", nargs="?")
    parser.add_argument("--stale-days", type=int, default=STALE_DAYS)
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        args = None
    if args is None or args.project is None:
        print("usage: check_concept.py <project-root | _concept-dir> [--stale-days N]", file=sys.stderr)
        return 2
    root = Path(args.project)
    concept = root / "_concept" if (root / "_concept").is_dir() else root
    if not concept.is_dir():
        print(f"{root}: no _concept/ directory", file=sys.stderr)
        return 2
    here = Path(__file__).resolve()
    problems = check(concept, here, stale_days=args.stale_days)
    problems += unproduced_hard_gates(here.parents[2])
    print("\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
