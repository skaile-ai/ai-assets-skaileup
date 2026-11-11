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
                     (a pending proposal entry with anchor `implements` or `screens` whose payload names
                     the other side satisfies the link until its owner settles it)
  4. data_entities   every name is an entity `id` of `10_blueprint/datamodel/model.yaml` (skipped without one),
                     read through `bunx @skaile/model@1 json` (or `npx`); a model the tool rejects, or a
                     machine with neither runner, is one line on `model.yaml`
  5. criterion ids   every `AC-…` a feature spec or ledger cites follows the id grammar and is
                     defined by `04_journeys/stories.yaml` (skipped without one), scoped to the
                     feature's own slug, or scoped to another feature whose spec carries it
  6. ledger          `11_build/acceptance-criteria/<featureset>/<feature>.ac.md` rows are checkbox
                     lines with a PASS/FAIL/empty marker; evaluated rows carry
                     `<pointer> · <evaluator> · <commit> · <date>`, untested rows the id alone
  7. proposals       every `_concept/proposals/*.yaml` file parses; an entry whose `target` resolves
                     to no node of the tree is reported; a `proposed` entry older than `--stale-days`
                     (default 14, counted from the file's `proposed_on`) is reported with the owner skill
                     that promotes or rejects it; an inline proposal marker left in an owner artifact
                     (`status: proposed`, `proposed_by`/`proposed_on`, `(proposed by …)`, or a `proposed:`
                     key of a YAML file) is reported as one to move into a proposal file
  8. open questions  every `## Open` row of `APP-DESIGN.md` and every `### Open` bullet of a screen spec
                     carries a recommendation; an `[open Qn]` entry has its row
  9. glossary split  when the project keeps its own glossary (`01_meta/scope.yaml` key `glossary` names a
                     path, else the latest pending proposal entry targeting `scope.yaml` at anchor
                     `key:glossary` names one, else the root holds a `CONTEXT.md`; `tree/glossary.md
                     § Where the words live`): every `_concept/glossary.md` entry id is the slug of a
                     term there, the entries carry no definition or `_Avoid_` line, every term there
                     has an entry, and no two terms there share an id (two meanings of
                     one word get distinct bold terms); a named path that does not exist is one
                     line. Mode `concept` (and an undecided `CONTEXT-MAP.md` root) checks none of this

A screen whose `floorplan:` is missing or empty is reported under 2; the floorplan is the one fact the
screen story and `quality-design` read it by.

The tree's legal first-level entries are parsed from the fenced tree in `tree/README.md` (a
```text fence opening `_concept/` plus a summary column) when the script sits in the
collection (`../../../tree/`), or from the installed copy
(`../../../contracts/shared-contracts/README.md`); with neither, the built-in list below,
mirrored from that fence, is used. An entry is the first token after the box-drawing prefix —
the summary column is ignored — and a directory's trailing `/` is dropped. A proposal's `target` is
resolved against the `path:` of the nodes in that same tree (a `<placeholder>` matches one path
segment; `CONTEXT.md` and the project glossary resolve to `_concept/glossary.md`); with neither tree,
against the prefixes of `PROPOSAL_OWNERS`.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

BUILTIN_ROOT = ["README.md", "brief.md", "goals.md", "glossary.md", "01_meta", "02_grounding",
                "03_brand", "04_journeys", "05_features", "06_behaviors", "07_screens",
                "08_dossiers", "09_mockup", "10_blueprint", "11_build", "proposals"]
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
DATAMODEL_DIR = "10_blueprint/datamodel/"
PROPOSALS_DIR = "proposals"
STALE_DAYS = 14
# A proposal lives in its own file under `_concept/proposals/` (`tree/proposals/README.md`); an owner
# artifact never holds one. These are the inline markers the earlier mechanism left in owner artifacts.
INLINE_MARKER_RE = re.compile(r"\bstatus:[ \t]*[\"']?proposed\b|\bproposed_(?:by|on)\b|\(proposed by\b")
INLINE_YAML_KEY_RE = re.compile(r"(?:^|[\s{,])proposed:")  # a `proposed:` key, block or flow style
# Parts that quote proposals without holding one: findings carry code evidence, the decision
# records and the candidate report cite entries they already settled or reported; the Storybook
# package is code, the proposal files are the proposals themselves.
QUOTING_PARTS = ("02_grounding/", "10_blueprint/decisions.md", "11_build/decisions.md",
                 "11_build/design-candidates.md", "09_mockup/storybook/", f"{PROPOSALS_DIR}/")
PROPOSAL_OWNERS = (  # target path (or path prefix) -> the skill that promotes or rejects a proposal there
    ("APP-DESIGN.md", "experience-interaction"),
    ("CONTEXT.md", "concept-glossary"),
    ("_concept/glossary.md", "concept-glossary"),
    ("_concept/07_screens/shell.md", "experience-shell"),
    ("_concept/07_screens/", "experience-screen"),
    ("_concept/05_features/featuresets.md", "concept-brief"),
    ("_concept/05_features/", "spec-feature"),
    ("_concept/01_meta/scope.yaml", "skaileup"),
    ("_concept/10_blueprint/datamodel/", "architecture-datamodel"),
)
GLOSSARY_NODE = "_concept/glossary.md"
SCOPE = "_concept/01_meta/scope.yaml"
NO_RECOMMENDATION = {"", "-", "—", "?", "tbd", "TBD", "n/a"}


SLUG_ALNUM_RE = re.compile(r"[^a-z0-9]+")
TERM_RE = re.compile(r"^\*\*(.+?)\*\*:")
ENTRY_RE = re.compile(r"^\*\*(.+?)\*\* \(`([^`]+)`\):\s*$")
TRANSLITERATE = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


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


MODEL_TOOL = "@skaile/model@1"
MODEL_TOOL_TIMEOUT = 180


class ModelToolError(Exception):
    """`@skaile/model` could not be run or rejected the model; the message says which."""


def run_model_tool(command: str, datamodel: Path) -> subprocess.CompletedProcess:
    """`bunx @skaile/model@1 <command> <dir>` (`npx --yes` without Bun), run to the end; raises
    `ModelToolError` when neither runner is on PATH or the run outlasts `MODEL_TOOL_TIMEOUT` seconds."""
    if shutil.which("bunx"):
        runner = ["bunx"]
    elif shutil.which("npx"):
        runner = ["npx", "--yes"]
    else:
        raise ModelToolError(f"neither `bunx` (Bun) nor `npx` (Node) is on PATH to run `{MODEL_TOOL} {command}`")
    try:
        return subprocess.run([*runner, MODEL_TOOL, command, str(datamodel)],
                              capture_output=True, text=True, timeout=MODEL_TOOL_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise ModelToolError(f"`{MODEL_TOOL} {command}` did not finish within {MODEL_TOOL_TIMEOUT} s") from None


def datamodel_json(datamodel: Path) -> dict:
    """`{model, seed}` of a datamodel directory, from `@skaile/model@1 json <dir>`."""
    r = run_model_tool("json", datamodel)
    if r.returncode != 0:
        raise ModelToolError(f"`{MODEL_TOOL} json` failed: {(r.stderr or r.stdout).strip()}")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as e:
        raise ModelToolError(f"`{MODEL_TOOL} json` printed no JSON ({e.msg})") from e


def model_names(model) -> set[str] | None:
    """Entity ids of a normalized `DataModel`: the model names `data_entities[]` cites.

    None when it has no `entities[]` list: the caller reports that once rather than a finding
    per cited name."""
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
    my = concept / DATAMODEL_DIR / "model.yaml"
    if my.is_file():
        try:
            model = model_names(datamodel_json(my.parent).get("model"))
            if model is None:
                report(rel(my), "no `entities` (format: tree/10_blueprint/datamodel/model.md)")
        except ModelToolError as e:
            report(rel(my), str(e))
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

    # 3. cross-links; a pending proposal entry for the missing side holds the link until it is settled
    entries, proposal_errors = read_proposals(concept)
    links = pending_links(entries)
    for f in features:
        for target in listed_paths(fm.get(f, {}).get("screens")):
            s = concept / target
            if not s.is_file():
                report(rel(f), f"screens: {target} does not exist")
            elif rel(f) not in listed_paths(fm.get(s, {}).get("implements")) and (rel(s), rel(f)) not in links:
                report(rel(s), f"implements: does not name {rel(f)}, which lists it in screens:")
    for s in screens:
        for target in listed_paths(fm.get(s, {}).get("implements")):
            f = concept / target
            if not f.is_file():
                report(rel(s), f"implements: {target} does not exist")
            elif rel(s) not in listed_paths(fm.get(f, {}).get("screens")) and (rel(f), rel(s)) not in links:
                report(rel(f), f"screens: does not list {rel(s)}, which implements it")

    # 4. data_entities
    if model is not None:
        for p in features + screens:
            names = fm.get(p, {}).get("data_entities") or []
            for name in names if isinstance(names, list) else [names]:
                if name not in model:
                    report(rel(p), f"data_entities: {name} is not a model in model.yaml")

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
    pg, _ = glossary_target(concept)
    pg = pg if pg and is_project_path(pg) else None
    problems += proposal_errors
    problems += proposal_problems(entries, here, today or datetime.date.today(), stale_days, pg)
    problems += inline_proposals(concept, root, pg)
    problems += open_question_problems(concept, root, screens + [concept / "07_screens/shell.md"])
    problems += glossary_split_problems(concept, root)
    return problems


def as_date(value) -> datetime.date | None:
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value))
    except ValueError:
        return None


def read_proposals(concept: Path) -> tuple[list[dict], list[str]]:
    """Every entry of `_concept/proposals/*.yaml` (`tree/proposals/README.md`) as
    `{file, line, proposed_by, proposed_on, entry}`, plus one line per file that cannot be read."""
    folder = concept / PROPOSALS_DIR
    records: list[dict] = []
    problems: list[str] = []
    for path in sorted(folder.glob("*.yaml")) if folder.is_dir() else []:
        shown = f"_concept/{PROPOSALS_DIR}/{path.name}"
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            problems.append(f"{shown}: not valid YAML")
            continue
        items = data.get("entries") if isinstance(data, dict) else None
        if not isinstance(items, list):
            problems.append(f"{shown}: no `entries` list (format: tree/proposals/README.md)")
            continue
        for entry in items:
            if not isinstance(entry, dict):
                problems.append(f"{shown}: an entry is not a mapping")
                continue
            m = re.search(rf"^[ \t]*(?:-[ \t]+)?id:[ \t]*[\"']?{re.escape(str(entry.get('id', '')))}[\"']?[ \t]*(?:#.*)?$",
                          text, re.M)
            records.append({"file": shown, "line": text.count("\n", 0, m.start()) + 1 if m else 1,
                            "proposed_by": data.get("proposed_by"), "proposed_on": data.get("proposed_on"),
                            "entry": entry})
    return records, problems


def is_pending(record: dict) -> bool:
    return record["entry"].get("status") == "proposed"


def pending_links(records: list[dict]) -> set[tuple[str, str]]:
    """(artifact, linked path), both relative to `_concept/`, of every pending entry with anchor
    `implements` (a screen naming a feature) or `screens` (a feature naming a screen)."""
    out = set()
    for r in records:
        e = r["entry"]
        if not is_pending(r) or e.get("anchor") not in ("implements", "screens") or not isinstance(e.get("target"), str):
            continue
        for path in listed_paths([e.get("payload")]):
            out.add((e["target"].strip().removeprefix("_concept/"), path))
    return out


def tree_nodes(here: Path) -> list[tuple[str, list[str]]] | None:
    """(`path:` entry, owners) of every node of the tree beside the script, or of its installed copy;
    None when neither is there."""
    root = here.parents[3] if len(here.parents) > 3 else None
    for tree in (root / "tree", root / "contracts" / "shared-contracts") if root else ():
        if not (tree / "README.md").is_file():
            continue
        nodes = []
        for p in sorted(tree.rglob("*.md")):
            data, _ = frontmatter(p)
            if not data:
                continue
            paths = data.get("path")
            owners = [o for o in data.get("owner") or [] if isinstance(o, str)] \
                if isinstance(data.get("owner"), list) else []
            for path in paths if isinstance(paths, list) else [paths]:
                if isinstance(path, str):
                    nodes.append((path, owners))
        return nodes
    return None


def path_pattern(path: str) -> str:
    """A node `path:` as a regex; a `<placeholder>` matches one path segment."""
    return "".join("[^/]+" if part.startswith("<") else re.escape(part)
                   for part in re.split(r"(<[^>/]+>)", path) if part)


def target_owners(target: str, nodes, project_glossary: str | None) -> list[str] | None:
    """The owners of the node `target` resolves to, None when it resolves to none. `CONTEXT.md` and the
    project glossary resolve to the glossary node."""
    if target in ("CONTEXT.md", project_glossary):
        target = GLOSSARY_NODE
    if nodes is None:
        owner = next((o for prefix, o in PROPOSAL_OWNERS if target.startswith(prefix)), None)
        return [owner] if owner else None
    return next((owners for path, owners in nodes if re.fullmatch(path_pattern(path), target)), None)


def owner_of(target: str, owners: list[str], project_glossary: str | None) -> str:
    if target in ("CONTEXT.md", project_glossary):
        return "concept-glossary"
    return next((o for prefix, o in PROPOSAL_OWNERS if target.startswith(prefix)), None) \
        or " or ".join(owners) or "its owner skill"


def proposal_problems(records: list[dict], here: Path, today: datetime.date, days: int,
                      project_glossary: str | None = None) -> list[str]:
    """An entry with no target, an entry whose target resolves to no node, and a `proposed` entry more
    than `days` days old, the last named with the owner skill that promotes or rejects it."""
    out: list[str] = []
    nodes = tree_nodes(here)
    for r in records:
        e = r["entry"]
        where, eid, target = f"{r['file']}:{r['line']}", e.get("id", "?"), e.get("target")
        if not isinstance(target, str) or not target.strip():
            out.append(f"{where}: entry `{eid}` has no `target`")
            continue
        target = target.strip()
        owners = target_owners(target, nodes, project_glossary)
        if owners is None:
            out.append(f"{where}: entry `{eid}` targets {target}, which resolves to no node of the tree")
            continue
        date = as_date(r["proposed_on"])
        if not is_pending(r) or date is None:
            continue
        age = (today - date).days
        if age > days:
            out.append(f"{where}: entry `{eid}` for {target} is proposed since {date.isoformat()}, {age} days "
                       f"(limit {days}) — promote or reject it with {owner_of(target, owners, project_glossary)}")
    return out


def inline_proposals(concept: Path, root: Path, project_glossary: str | None = None) -> list[str]:
    """One line per line of an owner artifact that still carries an inline proposal marker; a proposal
    belongs in its own file under `_concept/proposals/`. In split mode the project glossary is read too."""
    files = [(p.relative_to(concept).as_posix(), p) for p in sorted(concept.rglob("*"))
             if p.is_file() and p.suffix in (".md", ".yaml", ".yml")]
    files = [(f"_concept/{rel}", p) for rel, p in files if not rel.startswith(QUOTING_PARTS)]
    for extra in ("APP-DESIGN.md", project_glossary):
        if extra and (root / extra).is_file():
            files.append((extra, root / extra))
    out: list[str] = []
    for shown, p in files:
        is_yaml = p.suffix in (".yaml", ".yml")
        lines = enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1) if is_yaml \
            else glossary_lines(p)
        for n, line in lines:
            if INLINE_MARKER_RE.search(line) or (is_yaml and not line.lstrip().startswith("#")
                                                 and INLINE_YAML_KEY_RE.search(line)):
                out.append(f"{shown}:{n}: inline proposal; move it to a proposal file under _concept/proposals/")
    return out


def term_id(term: str) -> str:
    """The id of a glossary term: its kebab-case slug, umlauts transliterated (`Überweisung` → `ueberweisung`)."""
    return SLUG_ALNUM_RE.sub("-", term.lower().translate(TRANSLITERATE)).strip("-")


def is_project_path(value: str) -> bool:
    """A project-relative path: no leading `/`, no `..`."""
    return not value.startswith("/") and ".." not in Path(value).parts


def glossary_target(concept: Path) -> tuple[str | None, bool]:
    """(project glossary path, explicit) per `tree/glossary.md § Where the words live`; the path is
    None in concept mode and in the undecided mode. A confirmed `glossary` key in `scope.yaml` wins,
    else the latest pending proposal entry for it (target `scope.yaml`, anchor `key:glossary`), else
    `CONTEXT.md` when the project root has one."""
    root = concept.parent
    scope = concept / "01_meta/scope.yaml"
    data = None
    if scope.is_file():
        try:
            data = yaml.safe_load(scope.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            data = None
    value = None
    if isinstance(data, dict) and isinstance(data.get("glossary"), str) and data["glossary"].strip():
        value = data["glossary"].strip()
    else:
        records, _ = read_proposals(concept)
        pending = [((as_date(r["proposed_on"]) or datetime.date.min), i, r["entry"]["payload"].strip())
                   for i, r in enumerate(records)
                   if is_pending(r) and r["entry"].get("target") == SCOPE
                   and r["entry"].get("anchor") == "key:glossary"
                   and isinstance(r["entry"].get("payload"), str) and r["entry"]["payload"].strip()]
        if pending:
            value = max(pending)[2]
    if value is not None:
        return (None, False) if value == "concept" else (value, True)
    return ("CONTEXT.md", False) if (root / "CONTEXT.md").is_file() else (None, False)


def glossary_lines(path: Path):
    """(line number, text) of every line outside a fenced code block. A fence closes on a line of
    the opening character, at least as long as the opening, with nothing else on it (CommonMark), so a
    three-backtick block inside a four-backtick fence stays fenced."""
    fence = None  # (char, length) of the open fence
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.strip()
        run = re.match(r"(`{3,}|~{3,})", stripped)
        if fence is None:
            if run:
                fence = (run.group(1)[0], len(run.group(1)))
            else:
                yield n, line
        elif run and run.group(1)[0] == fence[0] and len(run.group(1)) >= fence[1] \
                and not stripped[len(run.group(1)):].strip():
            fence = None


def glossary_split_problems(concept: Path, root: Path) -> list[str]:
    """The split-mode rules (docstring rule 9): `_concept/glossary.md` holds ontology entries, the
    project glossary holds the words with one id per term, and the two name the same terms."""
    pg, explicit = glossary_target(concept)
    if pg is None:
        return []
    pg_path = root / pg
    if not is_project_path(pg) or not pg_path.is_file():
        if explicit:
            return [f"_concept/01_meta/scope.yaml: glossary names {pg}, which does not exist"]
        return []
    ontology = concept / "glossary.md"
    if not ontology.is_file():
        return []
    out: list[str] = []

    terms: dict[str, int] = {}  # id -> first line
    for n, line in glossary_lines(pg_path):
        m = TERM_RE.match(line)
        if m:
            tid = term_id(m.group(1))
            if tid in terms:
                out.append(f"{pg}:{n}: term `{tid}` repeats the id of line {terms[tid]} — "
                           f"concept-glossary qualifies one")
            else:
                terms[tid] = n

    entries: dict[str, int] = {}  # id -> line
    block = None  # (id, reported)
    for n, line in glossary_lines(ontology):
        m = ENTRY_RE.match(line)
        if m:
            block = [m.group(2), False]
            entries.setdefault(block[0], n)
            if block[0] not in terms:
                out.append(f"_concept/glossary.md:{n}: entry `{block[0]}` has no term in {pg} — "
                           f"renamed or removed; concept-glossary settles it")
        elif line.startswith("#"):
            block = None
        elif block and not block[1] and line.strip() and not line.startswith("- "):
            block[1] = True
            out.append(f"_concept/glossary.md:{n}: entry `{block[0]}` carries a definition or _Avoid_ line — "
                       f"in split mode the words live in {pg}")
    for tid, n in terms.items():
        if tid not in entries:
            out.append(f"{pg}:{n}: term `{tid}` has no entry in _concept/glossary.md — concept-glossary adds its kind")
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
    print("\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
