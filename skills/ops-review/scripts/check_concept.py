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
  4. data_entities   every name is an entity `id` in `10_blueprint/datamodel/model.json` (skipped without one)
  5. criterion ids   every `AC-…` a feature spec or ledger cites follows the id grammar and is
                     defined by `04_journeys/stories.yaml` (skipped without one) or scoped to the
                     feature's own slug
  6. ledger          `11_build/acceptance-criteria/<featureset>/<feature>.ac.md` rows are checkbox
                     lines with a PASS/FAIL/empty marker; evaluated rows carry
                     `<pointer> · <evaluator> · <commit> · <date>`, untested rows the id alone

The tree's legal first-level entries are parsed from the fenced tree in `tree/README.md` (a
```text fence opening `_concept/` plus a summary column) when the script sits in the
collection (`../../../tree/`), or from the installed copy
(`../../../contracts/shared-contracts/README.md`); with neither, the built-in list below,
mirrored from that fence, is used. An entry is the first token after the box-drawing prefix —
the summary column is ignored — and a directory's trailing `/` is dropped.
"""
from __future__ import annotations

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
    "screen": ["implements"],
    "ledger": ["feature", "feature_ref"],
}
ID_RE = re.compile(r"^AC-([a-z0-9_]+)-(\d{2})$")
CITE_RE = re.compile(r"AC-[A-Za-z0-9_-]+")
ROW_RE = re.compile(r"^- \[(PASS|FAIL| )\] (\S+)(?: — (.*))?$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")


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


def model_names(model) -> set[str]:
    """Entity ids of a model.json: the model names `data_entities[]` cites."""
    entities = model.get("entities") if isinstance(model, dict) else None
    return {e["id"] for e in entities or [] if isinstance(e, dict) and isinstance(e.get("id"), str)}


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
                m = ID_RE.match(cid)
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


def check(concept: Path, here: Path) -> list[str]:
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
    screens = sorted((concept / "07_screens").glob("*/*.md")) if (concept / "07_screens").is_dir() else []
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
        for cid in sorted(cited[f]):
            report_id(cid, f.stem, defined, stories, rel(f), report)

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
            report_id(cid, slug, defined, stories, where, report)
            if spec and spec in cited and cid not in cited[spec]:
                report(where, f"{cid} is not cited in {ref}")
            if marker == " " and evidence:
                report(where, "an untested row carries the id alone")
            if marker != " ":
                parts = [x.strip() for x in (evidence or "").split(" · ")]
                if len(parts) != 4 or not all(parts) or not COMMIT_RE.match(parts[2]) or not is_date(parts[3]):
                    report(where, "evidence must be `<pointer> · <evaluator> · <commit> · <date>`")
    return problems


def report_id(cid, slug, defined, stories, where, report):
    m = ID_RE.match(cid)
    if not m:
        report(where, f"{cid} is not a criterion id (AC-<story-id>-<nn>)")
    elif defined is None or cid in defined:
        return
    elif m.group(1) != slug:
        report(where, f"{cid} is neither in stories.yaml nor scoped to feature {slug!r}")
    elif slug in stories:
        report(where, f"{cid} is scoped to feature {slug!r}, which is also a story id")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_concept.py <project-root | _concept-dir>", file=sys.stderr)
        return 2
    root = Path(argv[1])
    concept = root / "_concept" if (root / "_concept").is_dir() else root
    if not concept.is_dir():
        print(f"{root}: no _concept/ directory", file=sys.stderr)
        return 2
    problems = check(concept, Path(__file__).resolve())
    print("\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
