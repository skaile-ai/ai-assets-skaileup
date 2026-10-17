#!/usr/bin/env python3
"""check.py — the collection's self-check.

One script, one CI job. It answers a single question: would this collection
install and run, or does it contain a reference that silently resolves to
nothing?

Every check here exists because its failure mode is *quiet*. A skill whose
directory disagrees with its `name:` installs under the directory and the flow
node that names it runs with an empty prompt, reporting `satisfied: true`. A
prerequisite path that no node documents is a gate that can never open. A cited
tree node that was deleted reads as fine. A node whose `data.phase` contradicts
its group's renders in the group's lane and never says so. None of these raise
anywhere in the toolchain, so they are raised here.

This is the collection's only real gate. forge-concept validates no flow at all — it
loads them and drops the malformed ones silently — so anything not checked here is not
checked anywhere.

The instruction layer is `tree/`, a mirror of `_concept/` with one node per part (ADR
0015). `load_tree` reads every node, `resolve` maps any `_concept/` path to the node that
documents it, and `--print-tree` renders the artifact tree from the nodes' `path:` entries —
the one copy of that tree, pasted into `tree/README.md` and checked for staleness.

About a dozen rules here are copies of facts in forge-concept and @skaile/workspaces.
Each names its fact id and nothing else: `scripts/host_facts.py` owns the path, the
signature and the date, and `scripts/verify_host.py` greps them against real checkouts.
A `file:line` in a comment is not a citation — ticket 40 measured four of fourteen
rotting in two weeks while every underlying fact still held.

The rules are only as good as the fixtures behind them, so this script runs
`test_check.py` as its last phase. That is not tidiness: ticket 34 changed these
rules without updating those fixtures, `check.py` printed a confident `0 error(s)`
because it did not run them, and `main` was red for ~13 hours. One command has to
mean green, or half of the gate is optional in practice.

Usage:
  python scripts/check.py [--repo <path>] [--no-tests]
  python scripts/check.py [--repo <path>] --print-tree

Exit codes:
  0  the collection checks out and the checker's own fixtures pass
  1  at least one error, or a failing fixture, or pytest is missing
"""
from __future__ import annotations

import argparse
import re
import subprocess
import unicodedata
import sys
from pathlib import Path

import yaml

import host_facts as hf

# The published skill body ceilings (ADR 0015). A whole SKILL.md, frontmatter included —
# that is how a reader meets it. A skill that writes no artifact keeps its procedure in
# the body (`## Steps`), so it gets the larger one.
LINE_BUDGET = 60
LINE_BUDGET_NO_ARTIFACTS = 100

# Every declared prerequisite path is joined to the *project* root, never to the concept
# (`host:prerequisite-project-root`), so the prefix is part of the declaration.
ARTIFACT_ROOT = "_concept"

# The instruction tree and the one manifest that ships it.
TREE_DIR = "tree"

# The path the host writes each step's dialog input to (`host:grounding-user-input`).
# `concept-onboard` folds it into `answers.json`, so the node that documents that file
# has to name it.
GROUNDING_USER_INPUT = "_grounding/<step>/user_input.json"
ONBOARD_NODE = "02_grounding/onboarding/answers.md"

# The named exceptions to "every prerequisite path lives under `_concept/`".
#
# `host:prerequisite-project-root` joins the declared path to the *project* root, so a project-root
# gate like `package.json` resolves correctly — the blanket ban this check used to carry
# was stricter than the reader it protects (found by ticket 23, which had to move
# `quality-test`'s source-exists gate into the step body to work around it).
#
# The ban still earns its keep for everything else, and the reason is drift, not the
# reader: the dominant defect class in this repo is a *concept* path written against a
# superseded tree (ADR 0007 renamed the whole first level; ticket 30 swept 32 files of
# it). Allowing arbitrary paths outside `_concept/` would let `experience/screens/foo.md`
# — a pre-0007 concept path — pass as "some project-root file". So the restriction stays,
# narrowed from a ban to this list: a path is legal if it is under `_concept/` (and resolves
# to a node) or if it is named here. Extend the list deliberately; a project-root path
# cannot be verified from inside this collection, because whether it exists is a fact about
# the scaffolded project, not about this repo.
PROJECT_ROOT_PREREQUISITES = {"package.json"}

# Skills this collection calls but does not ship (migration map, premise 6). Axis is
# the upstream frontmatter: "user" = disable-model-invocation: true, reachable only by
# the human; "model" = reachable through the Skill tool.
EXTERNAL_SKILLS: dict[str, str] = {
    "grilling": "model", "tdd": "model", "code-review": "model",
    "diagnosing-bugs": "model", "triage": "user",
}
# Mid-sentence calls are lower-case ("…, call the Skill tool with …"); match both.
SKILL_TOOL_CALL_RE = re.compile(r'[Cc]all the Skill tool (?:with|twice, for) "([a-z][a-z0-9-]*)"(?: and "([a-z][a-z0-9-]*)")?')
BARE_SLASH_SKILL_RE = re.compile(r'(?<=[\s`(])/([a-z][a-z0-9-]*)\b(?![/.])')

# forge-concept's lane vocabulary (`host:phase-lane-vocabulary`). An invalid value is
# silently swallowed there, which is why it is checked here.
PHASES = {"conceptualization", "implementation", "review"}

# The engine takes dependencies from `edges.filter(e => e.type === "flow")`.
# Any other type — or no type — draws an edge that orders nothing.
FLOW_EDGE = "flow"

# Ticket 10: `-mp` ships `skill` and `group` nodes only. The `sub-flow` kind died with
# the shared building blocks (every loaded flow becomes an onboarding card, so a flow
# that is not a way to start a project has no business being one), and `router` died
# with the pick-one renderers.
NODE_KINDS = {"skill", "group"}

# `host:profile-onboarding` casts `meta.onboarding.input_style` to this union without
# checking it; the wizard then branches on it and renders nothing for a value outside
# the set.
INPUT_STYLES = {"freeform", "structured", "repo"}

# `host:research-depth-options` publishes exactly these as the selectable depths.
RESEARCH_DEPTHS = {"skip", "light", "moderate", "deep"}

# Keys ticket 10 deleted as decoration. `meta.category` and the globals fell through
# every reader, which makes their bans house style — a decision this map made, owned by
# nobody else. `data.parameters` and `data.writes` are different: both still have live
# reads (`host:sub-flow-parameters-read`, `host:node-writes-legacy-read`), so those two
# bans are host-derived and carry a fact id.
DEAD_META_KEYS = ("category",)
DEAD_GLOBALS = ("approval_mode", "subagent_mode", "verbosity", "concept_depth")
DEAD_NODE_DATA = ("parameters", "writes")

# Which fact each of those two bans rests on, and the clause it contributes. Hoisted out
# of the loop so the ids stay plain literals: `test_check.py` reconciles the table by
# walking this module's AST, and a fact id built at runtime would read as an orphan.
DEAD_NODE_DATA_FACTS = {
    "parameters": (
        "host:sub-flow-parameters-read",
        "node-data-parameters",
        " — and it is not inert: {host} reads `data.parameters.flow`",
    ),
    "writes": (
        "host:node-writes-legacy-read",
        "node-data-writes",
        " — {host} still reads it for legacy flows",
    ),
}

# No `${...}` resolver runs on forge-concept's node-run path (`host:prompt-is-verbatim`)
# — the string reaches the prompt verbatim. Scoped to that path deliberately: the flow
# *connector* in @skaile/workspaces does resolve `${}`, and forge-concept never calls it.
INTERPOLATION_RE = re.compile(r"\$\{[^}]*\}")


# The three kinds of rule this script mixes, kept apart in the *output* and nowhere
# else. A red gate is a red gate — there is no second exit code, because a distinct one
# invites a CI config that ignores it.
#
#   intrinsic     depends on nothing outside this repo. `name:` == directory, links
#                 resolve, edges reference real nodes, reachability. If one fails, the
#                 collection is wrong.
#   host-derived  a copy of a fact in someone else's repo, each owned by a row in
#                 `host_facts.py`. If one fails, either the collection is wrong or the
#                 fact expired — and until someone runs `verify_host.py` that is
#                 genuinely ambiguous, so the message says both.
#   house style   decisions this map made (ADR 0015's ceilings, ticket 10's deletions,
#                 the plural rule). They stay errors: a warning nobody is forced to read
#                 is how a deleted key comes back.
INTRINSIC = "intrinsic"
HOST_DERIVED = "host-derived"
HOUSE_STYLE = "house style"

TIERS = (INTRINSIC, HOST_DERIVED, HOUSE_STYLE)


class Problem:
    """One reported failure, with the tier that decides how it reads."""

    def __init__(
        self, where: str, msg: str, tier: str, facts: tuple[str, ...] = (), rule: str | None = None
    ) -> None:
        self.where = where
        self.msg = msg
        self.tier = tier
        self.facts = facts
        self.rule = rule

    def __str__(self) -> str:
        if self.facts:
            suffix = f" [{', '.join(self.facts)}]"
        elif self.rule:
            suffix = f" [rule: {self.rule}]"
        else:
            suffix = ""
        return f"{self.where}: {self.msg}{suffix}"


class Report:
    def __init__(self) -> None:
        self.problems: list[Problem] = []

    def error(
        self,
        where: str,
        msg: str,
        *,
        fact: str | tuple[str, ...] | None = None,
        rule: str | None = None,
    ) -> None:
        """An intrinsic failure, or — with `fact=` — a host-derived one.

        `fact` names a row in `host_facts.py`, or several when one rule rests on more
        than one (an edge type governs both run ordering and readiness, in two files
        that can rot apart). An unknown id raises rather than printing: a citation that
        resolves to nothing is exactly the defect this table exists to make loud.

        `rule` names this rule, and must appear in every cited row's `rules`. It is what
        makes that column mean something: a rule id that lives only in the table is
        unfalsifiable bookkeeping — the defect the table was built to abolish, one field
        further in. `test_check.py` reconciles both directions.

        `{host}` in `msg` is replaced by the first row's host and path, so the message
        cannot drift out of step with the table.
        """
        if fact is None:
            if rule is not None:
                raise ValueError(f"rule {rule!r} given without a fact — only host-derived rules carry ids")
            self.problems.append(Problem(where, msg, INTRINSIC))
            return
        if rule is None:
            raise ValueError(f"fact {fact!r} cited with no rule id — the table's `rules` column would go unowned")
        ids = (fact,) if isinstance(fact, str) else tuple(fact)
        rows = [hf.fact(i) for i in ids]
        for row in rows:
            if rule not in row.rules:
                raise KeyError(f"rule {rule!r} is not listed in {row.id}'s `rules` — add it to scripts/host_facts.py")
        self.problems.append(
            Problem(where, msg.replace("{host}", rows[0].where), HOST_DERIVED, ids, rule)
        )

    def fail(self, where: str, rule: str, msg: str) -> None:
        """An intrinsic failure that names its rule id in the output.

        The tree rules have no host fact behind them, so the id is what a reader greps
        for. It is not reconciled against `host_facts.py` — only `error(fact=…)` is."""
        self.problems.append(Problem(where, msg, INTRINSIC, rule=rule))

    def house(self, where: str, msg: str, *, rule: str | None = None) -> None:
        """A rule this collection imposes on itself. Same severity, different reading."""
        self.problems.append(Problem(where, msg, HOUSE_STYLE, rule=rule))

    @property
    def errors(self) -> list[str]:
        return [str(p) for p in self.problems]

    def by_tier(self, tier: str) -> list[Problem]:
        return [p for p in self.problems if p.tier == tier]

    def facts_cited(self) -> set[str]:
        return {f for p in self.problems for f in p.facts}

    def ok(self) -> bool:
        return not self.problems


# --------------------------------------------------------------------------
# frontmatter
# --------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body). Missing or unparseable frontmatter is {}."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}, text[m.end():]
    return (data if isinstance(data, dict) else {}), text[m.end():]


# --------------------------------------------------------------------------
# the instruction tree — one node per `_concept/` part (ADR 0015)
# --------------------------------------------------------------------------


def _segs(path: str) -> list[str]:
    return [s for s in path.split("/") if s]


def _is_placeholder(segment: str) -> bool:
    """A `<name>` or `*` segment stands for any one real segment."""
    return "<" in segment or segment == "*"


def _seg_eq(a: str, b: str) -> bool:
    return a == b or _is_placeholder(a) or _is_placeholder(b)


def _kind(path: str) -> str:
    """`dir` for a trailing slash, `file` for a final segment with an extension, else `any` —
    `_concept/07_screens` may name the directory, and the resolver must not guess."""
    if path.endswith("/"):
        return "dir"
    last = path.rsplit("/", 1)[-1]
    return "file" if "." in last else "any"


def _kinds_compatible(a: str, b: str) -> bool:
    return a == b or "any" in (a, b)


class Node:
    """One file of `tree/`: the instruction for the `_concept/` part named by its `path:`.

    `is_list` records the YAML form because it carries meaning: a directory entry inside a
    *list* also covers every path below it that has no node of its own, while a plain string
    covers only what it names."""

    def __init__(self, rel: str, fm: dict) -> None:
        self.rel = rel  # posix, relative to tree/
        self.file = f"{TREE_DIR}/{rel}"
        self.has_frontmatter = bool(fm)
        raw = fm.get("path")
        self.raw_path = raw
        self.is_list = isinstance(raw, list)
        items = raw if isinstance(raw, list) else ([raw] if isinstance(raw, str) else [])
        self.entries: list[str] = [e for e in items if isinstance(e, str)]
        self.summary = fm.get("summary")
        self.raw_writers = fm.get("writers")
        self.writers: list[str] = (
            [w for w in self.raw_writers if isinstance(w, str)] if isinstance(self.raw_writers, list) else []
        )

    @property
    def is_readme(self) -> bool:
        return self.rel.rsplit("/", 1)[-1] == "README.md"

    def __repr__(self) -> str:
        return f"Node({self.file})"


def load_tree(repo: Path) -> list[Node]:
    """Every node under `tree/`, sorted by path. `CONTRACT.md` is the manifest, not a node."""
    root = repo / TREE_DIR
    if not root.is_dir():
        return []
    nodes = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if rel == "CONTRACT.md" or any(part.startswith(".") for part in rel.split("/")):
            continue
        fm, _body = split_frontmatter(path.read_text(encoding="utf-8"))
        nodes.append(Node(rel, fm))
    return nodes


def _location_candidates(path: str) -> list[str]:
    """The node files (relative to `tree/`) the location rule names for a `_concept/` path:
    a directory `X` is `X/README.md`, a file `X/name.ext` is `X/name.md`, and `<x>` becomes `[x]`.
    A path that may be either (no extension, no trailing slash) offers the directory first."""
    segs = _segs(path)
    if not segs or segs[0] != ARTIFACT_ROOT:
        return []
    below = [s.replace("<", "[").replace(">", "]") for s in segs[1:]]
    kind = _kind(path)
    out = []
    if kind in ("dir", "any"):
        out.append("/".join([*below, "README.md"]))
    if kind in ("file", "any") and below:
        name = below[-1]
        stem = name.rsplit(".", 1)[0] if "." in name else name
        out.append("/".join([*below[:-1], stem + ".md"]))
    return out


def resolve(nodes: list[Node], path: str) -> Node | None:
    """The node that documents `path`, or None. The four steps are the whole rule:

    1. a literal match against any node's `path:` entries — `<x>` matches any one segment on
       either side, a trailing slash is ignored, the entry with the fewest wildcard hits wins;
    2. the location rule (`_location_candidates`) — a node that exists at that place;
    3. covering: the deepest *directory* entry of a *list-form* `path:` above the path. The
       artifact root `_concept/` is not a covering entry: its README documents the root and
       `_concept/README.md`, and a root that covered everything would resolve every typo;
    4. otherwise unresolved.
    """
    segs = _segs(path)
    if not segs:
        return None
    kind = _kind(path)

    best: tuple[int, Node] | None = None
    for node in nodes:
        for entry in node.entries:
            es = _segs(entry)
            if len(es) != len(segs) or not _kinds_compatible(_kind(entry), kind):
                continue
            if not all(_seg_eq(a, b) for a, b in zip(segs, es)):
                continue
            cost = sum(1 for a, b in zip(segs, es) if a != b)
            if best is None or cost < best[0]:
                best = (cost, node)
    if best is not None:
        return best[1]

    by_rel = {n.rel: n for n in nodes}
    for rel in _location_candidates(path):
        if rel in by_rel:
            return by_rel[rel]

    covering: tuple[int, Node] | None = None
    for node in nodes:
        if not node.is_list:
            continue
        for entry in node.entries:
            if not entry.endswith("/") or len(_segs(entry)) < 2:
                continue
            es = _segs(entry)
            if len(es) < len(segs) and all(_seg_eq(a, b) for a, b in zip(segs, es)):
                if covering is None or len(es) > covering[0]:
                    covering = (len(es), node)
    return covering[1] if covering else None


class _TreeEntry:
    """One line of the generated artifact tree."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.is_dir = False
        self.summary = ""
        self.kids: dict[str, _TreeEntry] = {}


def _build_entries(nodes: list[Node]) -> _TreeEntry:
    """The trie of every `path:` entry under `_concept/`. A node's summary goes on its first
    entry and on every file entry, never on a later directory entry — `<featureset>/` is not
    described by the summary of `05_features/`."""
    root = _TreeEntry(ARTIFACT_ROOT)
    root.is_dir = True
    for node in nodes:
        summary = node.summary if isinstance(node.summary, str) else ""
        for idx, entry in enumerate(node.entries):
            segs = _segs(entry)
            if not segs or segs[0] != ARTIFACT_ROOT:
                continue
            cur = root
            for i, seg in enumerate(segs[1:], start=1):
                last = i == len(segs) - 1
                cur = cur.kids.setdefault(seg, _TreeEntry(seg))
                if not last or entry.endswith("/"):
                    cur.is_dir = True
            if idx == 0 or not cur.is_dir:
                cur.summary = cur.summary or summary
    return root


def _entry_order(entry: _TreeEntry) -> tuple:
    return (entry.is_dir, entry.name != "README.md", _is_placeholder(entry.name), entry.name)


def render_tree(nodes: list[Node]) -> list[str]:
    """The artifact tree as box-drawing lines, a 4-char indent per level and the summary after
    the name. Files come before directories at each level, placeholders last."""
    root = _build_entries(nodes)
    rows: list[tuple[str, str]] = [(root.name + "/", root.summary)]

    def walk(entry: _TreeEntry, prefix: str) -> None:
        kids = sorted(entry.kids.values(), key=_entry_order)
        for i, kid in enumerate(kids):
            last = i == len(kids) - 1
            rows.append((prefix + ("└── " if last else "├── ") + kid.name + ("/" if kid.is_dir else ""), kid.summary))
            walk(kid, prefix + ("    " if last else "│   "))

    walk(root, "")
    width = max(len(label) for label, _ in rows) + 2
    return [f"{label.ljust(width)}{summary}".rstrip() for label, summary in rows]


def _normalised(lines: list[str]) -> list[str]:
    return [" ".join(line.split()) for line in lines if line.strip()]


def _first_fence(text: str) -> list[str] | None:
    """The lines of the first fenced block of `text`, or None when it has none."""
    inside = False
    lines: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("```"):
            if inside:
                return lines
            inside = True
            continue
        if inside:
            lines.append(line)
    return None


def _tree_entry_stem(raw: str) -> str:
    """The comparable name of a tree entry: no extension, no path tail, no placeholder.

    `review.yaml` -> `review`, `reviews/` -> `reviews`, `<slice_id>` -> ``.
    """
    head = raw.split("/")[0].split("<")[0].strip()
    return head.rsplit(".", 1)[0] if "." in head else head


def _is_plural_of(a: str, b: str) -> bool:
    """Whether `a` is `b` under a naive English pluralisation."""
    a, b = a.lower(), b.lower()
    return a in (b + "s", b + "es") or (b.endswith("y") and a == b[:-1] + "ies")


def check_tree_names(nodes: list[Node], rep: Report) -> None:
    """Rule `tree-sibling-singular-plural`: no two siblings in the artifact tree differ only by
    singular and plural. `tree/README.md § Naming` states the rule; this enforces it against the
    tree the nodes' `path:` entries declare, so a pair like `review.yaml` beside `reviews/`
    cannot be typed back in unnoticed."""
    root = _build_entries(nodes)

    def walk(entry: _TreeEntry, parent: str) -> None:
        stems = [s for s in (_tree_entry_stem(k.name) for k in entry.kids.values()) if s]
        for i, a in enumerate(stems):
            for b in stems[i + 1:]:
                if _is_plural_of(a, b) or _is_plural_of(b, a):
                    rep.house(
                        f"{TREE_DIR}/",
                        f"`{parent}` declares `{a}` and `{b}`, which differ only by plural",
                        rule="tree-sibling-singular-plural",
                    )
        for kid in entry.kids.values():
            walk(kid, f"{parent}{kid.name}/")

    walk(root, f"{ARTIFACT_ROOT}/")


KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Node file and directory names under `tree/`: lowercase, or a `[placeholder]` for a segment
# that stands for any one real name. `README.md` is the one capitalised name.
NODE_NAME_RE = re.compile(r"^(?:[a-z0-9][a-z0-9_.-]*|\[[a-z_]+\](?:\.md)?)$")


def _placeholder_dir(segment: str) -> str:
    return segment.replace("[", "<").replace("]", ">")


def _check_node(node: Node, skill_dirs: set[str], rep: Report) -> None:
    where = node.file
    if not node.has_frontmatter:
        rep.fail(where, "node-frontmatter", "has no parseable YAML frontmatter — a node without `path:` resolves nothing")
        return
    if not node.entries or not isinstance(node.raw_path, (str, list)) or (
        node.is_list and len(node.entries) != len(node.raw_path)
    ):
        rep.fail(where, "node-frontmatter", "`path:` must be a string or a non-empty list of strings")
        return
    parts = node.rel.split("/")
    concept_dir = f"{ARTIFACT_ROOT}/" + "".join(f"{_placeholder_dir(p)}/" for p in parts[:-1])
    dir_segs = _segs(concept_dir)
    for entry in node.entries:
        if not entry.startswith(f"{ARTIFACT_ROOT}/"):
            rep.fail(where, "node-frontmatter", f"`path:` entry {entry!r} does not start with '{ARTIFACT_ROOT}/'")
            continue
        es = _segs(entry)
        if len(es) < len(dir_segs) or not all(_seg_eq(a, b) for a, b in zip(dir_segs, es)):
            rep.fail(where, "node-frontmatter", f"`path:` entry {entry!r} is not under the node's directory {concept_dir!r}")
    first = node.entries[0]
    if node.is_readme:
        if first != concept_dir:
            rep.fail(where, "node-frontmatter", f"a README's first `path:` entry is its directory {concept_dir!r}, not {first!r}")
    elif first.startswith(f"{ARTIFACT_ROOT}/") and node.rel not in _location_candidates(first):
        wanted = " or ".join(f"{TREE_DIR}/{c}" for c in _location_candidates(first)) or "no node"
        rep.fail(
            where,
            "node-location",
            f"first `path:` entry {first!r} belongs in {wanted}, not {where} — a node sits where the "
            f"location rule puts its part",
        )
    summary = node.summary
    if not isinstance(summary, str) or not summary.strip():
        rep.fail(where, "node-frontmatter", "has no `summary:` — the tree listing renders it")
    elif len(summary) > 80:
        rep.fail(where, "node-frontmatter", f"`summary:` is {len(summary)} characters, over the 80-character limit")
    if not isinstance(node.raw_writers, list):
        rep.fail(where, "node-frontmatter", "has no `writers:` list — write `writers: []` for a part nothing generates")
    else:
        for writer in node.raw_writers:
            if not isinstance(writer, str) or writer not in skill_dirs:
                rep.fail(where, "node-frontmatter", f"`writers:` lists {writer!r}, which is no skill in this collection")


def check_tree(repo: Path, nodes: list[Node], rep: Report) -> None:
    """The tree's own rules: the manifest (T1), node frontmatter and location (T2), names (T3),
    the generated listing (T5), the host input file (T6) and the plural rule (T7)."""
    _check_manifest(repo, rep)
    tree_root = repo / TREE_DIR
    if not tree_root.is_dir():
        return

    skills_dir = repo / "skills"
    skill_dirs = {p.name for p in skills_dir.iterdir() if p.is_dir()} if skills_dir.is_dir() else set()
    for node in nodes:
        _check_node(node, skill_dirs, rep)

    for path in sorted(tree_root.rglob("*")):
        rel = path.relative_to(tree_root).as_posix()
        if any(part.startswith(".") for part in rel.split("/")):
            continue
        if path.is_dir() and not path.name.startswith("[") and not (path / "README.md").is_file():
            rep.fail(
                f"{TREE_DIR}/{rel}/",
                "dir-has-readme",
                "has no `README.md` — every directory under the tree has a node of its own "
                "(a `[placeholder]` directory is described by the README above it)",
            )
        if path.is_file() and path.name in ("README.md", "CONTRACT.md"):
            continue
        if not NODE_NAME_RE.match(path.name):
            rep.fail(
                f"{TREE_DIR}/{rel}",
                "node-name",
                f"name {path.name!r} is not lowercase or a `[placeholder]` — nodes are named after the part they document",
            )

    _check_tree_listing(repo, nodes, rep)
    _check_onboard_node(repo, skill_dirs, rep)
    check_tree_names(nodes, rep)


def _check_tree_listing(repo: Path, nodes: list[Node], rep: Report) -> None:
    """Rule `tree-readme-stale`: the first fenced block of `tree/README.md` is the generated
    artifact tree — the only hand-free copy of it — and must equal `--print-tree`."""
    where = f"{TREE_DIR}/README.md"
    readme = repo / TREE_DIR / "README.md"
    if not readme.is_file():
        rep.fail(where, "tree-readme-stale", "does not exist — the tree has no entry point and no listing")
        return
    fence = _first_fence(readme.read_text(encoding="utf-8"))
    if fence is None:
        rep.fail(where, "tree-readme-stale", "has no fenced block — paste the output of `python scripts/check.py --print-tree`")
        return
    have, want = _normalised(fence), _normalised(render_tree(nodes))
    if have != want:
        first = next((i for i, (h, w) in enumerate(zip(have, want)) if h != w), min(len(have), len(want)))
        rep.fail(
            where,
            "tree-readme-stale",
            f"its fenced tree differs from `--print-tree` (first difference at line {first + 1}: "
            f"{(have[first] if first < len(have) else '<end>')!r} vs {(want[first] if first < len(want) else '<end>')!r}) "
            f"— regenerate it",
        )


def _check_onboard_node(repo: Path, skill_dirs: set[str], rep: Report) -> None:
    """`concept-onboard` folds the host's dialog file into `answers.json`; the node that documents
    `answers.json` has to name that file's path, or the merge is dropped."""
    node = repo / TREE_DIR / ONBOARD_NODE
    where = f"{TREE_DIR}/{ONBOARD_NODE}"
    if not node.is_file():
        if "concept-onboard" in skill_dirs:
            rep.error(
                where,
                f"does not exist, so nothing names `{GROUNDING_USER_INPUT}` — {{host}} writes each "
                f"step's dialog input there, and without the merge into `answers.json` the user's "
                f"answers stay in a file no later skill reads",
                fact="host:grounding-user-input",
                rule="onboard-names-host-input",
            )
        return
    if GROUNDING_USER_INPUT not in node.read_text(encoding="utf-8"):
        rep.error(
            where,
            f"never names `{GROUNDING_USER_INPUT}` — {{host}} writes each step's dialog "
            f"input there, and the onboarding merges it into `answers.json`; without the merge the "
            f"user's answers stay in a file no later skill reads",
            fact="host:grounding-user-input",
            rule="onboard-names-host-input",
        )


# --------------------------------------------------------------------------
# skills
# --------------------------------------------------------------------------


def _artifacts_block(fm: dict) -> dict | None:
    """`metadata.artifacts`, the one place the host reads it from; None when absent or not a map."""
    meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    block = meta.get("artifacts")
    return block if isinstance(block, dict) else None


def _check_produces(fm: dict, where: str, nodes: list[Node], rep: Report) -> set[str]:
    """A skill declares what it writes: `metadata.artifacts.produces: [{ id, path }]`.

    Returns the ids it declares well-formed. The list is mandatory (`[]` for a skill that
    writes nothing under `_concept/`), each entry names a kebab-case `id` and a `path` that
    starts with `_concept/` and resolves to a node of the tree (ADR 0013, ADR 0015)."""
    block = _artifacts_block(fm)
    produces = block.get("produces") if block is not None else None
    if not isinstance(produces, list):
        rep.error(
            where,
            "has no `metadata.artifacts.produces` list — it is the declaration {host}'s node "
            "done-state read has to switch to; write `produces: []` for a skill that writes "
            "nothing under `_concept/`" if produces is None else
            f"`metadata.artifacts.produces` is a {type(produces).__name__}, not a list of "
            "`{ id, path }` entries — {host}'s node done-state read has to switch to it",
            fact="host:node-done-from-produced-by",
            rule="produces-shape",
        )
        return set()

    ids: set[str] = set()
    for i, entry in enumerate(produces):
        label = f"`produces[{i}]`"
        ident = entry.get("id") if isinstance(entry, dict) else None
        path = entry.get("path") if isinstance(entry, dict) else None
        if not isinstance(ident, str) or not isinstance(path, str) or not ident or not path:
            rep.error(
                where,
                f"{label} must be a map with a string `id` and a string `path`, got {entry!r}",
                fact="host:node-done-from-produced-by",
                rule="produces-shape",
            )
            continue
        if not KEBAB_RE.match(ident):
            rep.error(where, f"{label} id {ident!r} is not kebab-case — it is the id other skills name in `artifacts.requires`")
        else:
            ids.add(ident)
        if not path.startswith(ARTIFACT_ROOT + "/"):
            rep.error(where, f"{label} path {path!r} does not start with {ARTIFACT_ROOT + '/'!r}")
            continue
        if not _gate_segments(path):
            rep.error(where, f"{label} path {path!r} names no artifact below `{ARTIFACT_ROOT}/`")
        elif nodes and resolve(nodes, path) is None:
            rep.fail(
                where,
                "produces-path-resolves",
                f"{label} path {path!r} resolves to no node of `{TREE_DIR}/` — add the node (or a "
                f"directory entry in a list-form `path:` that covers it) before a skill writes it",
            )
    return ids


def _required_artifact_ids(fm: dict) -> list[str]:
    block = _artifacts_block(fm)
    requires = block.get("requires") if block is not None else None
    if not isinstance(requires, list):
        return []
    return [str(e["id"]) for e in requires if isinstance(e, dict) and e.get("id")]


def _produced_entries(fm: dict) -> list[tuple[str, str]]:
    """The well-formed `(id, path)` pairs of `metadata.artifacts.produces`; the shape itself is
    reported by `_check_produces`."""
    block = _artifacts_block(fm)
    produces = block.get("produces") if block is not None else None
    if not isinstance(produces, list):
        return []
    return [
        (e["id"], e["path"])
        for e in produces
        if isinstance(e, dict) and isinstance(e.get("id"), str) and isinstance(e.get("path"), str)
    ]


def _gate_segments(path: str) -> list[str]:
    """A `_concept/`-prefixed path as its segments below the root."""
    return [s for s in path.removeprefix(ARTIFACT_ROOT + "/").split("/") if s]


def _paths_overlap(a: str, b: str) -> bool:
    """True when one path equals, contains or lies under the other. A `<...>` or `*` segment
    matches any one segment, so a gate on `07_screens` meets `07_screens/<feature_slug>/<screen>.md`."""
    return all(
        x == y or _is_placeholder(x) or _is_placeholder(y)
        for x, y in zip(_gate_segments(a), _gate_segments(b))
    )


PROJECT_TYPES_NODE = "01_meta/scope.md"
PROJECT_TYPES_HEADING_RE = re.compile(r"^## Project types[ \t]*$", re.MULTILINE)
NO_ENTRIES = {"", "—", "–", "-"}


def _project_types(repo: Path, rep: Report) -> dict[str, list[str]] | None:
    """The `## Project types` table of `tree/01_meta/scope.md`: `{project_type: [never-grown entries]}`.

    None when the node does not exist (nothing to hold the gates to). A node without the table is
    an error: the rule could not see what any project type leaves out."""
    node = repo / TREE_DIR / PROJECT_TYPES_NODE
    if not node.is_file():
        return None
    where = f"{TREE_DIR}/{PROJECT_TYPES_NODE}"
    text = node.read_text(encoding="utf-8")
    m = PROJECT_TYPES_HEADING_RE.search(text)
    if not m:
        rep.fail(
            where,
            "hard-gate-on-not-grown",
            "has no `## Project types` table — the rule that keeps hard gates off artifacts a project "
            "type never grows reads its data there",
        )
        return None
    out: dict[str, list[str]] = {}
    for line in text[m.end():].splitlines():
        if line.startswith("#"):
            break
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower().replace(" ", "_") == "project_type" or set(line) <= set("|-: \t"):
            continue
        out[cells[0].strip("`")] = [
            e for e in (c.strip().strip("`") for c in cells[1].split(",")) if e not in NO_ENTRIES
        ]
    return out


def _check_not_grown_gates(repo: Path, skills: list[tuple[str, dict]], rep: Report) -> None:
    """Rule `hard-gate-on-not-grown`: a project of a type that never grows an artifact must
    not be blocked by a `hard` prerequisite on it (F35).

    A project type's never-grows entry is an artifact id from some skill's `produces`, a skill name,
    or a domain (a name prefix, `mockup` for `mockup-*`). A skill that is itself a named skill
    or lies in a named domain never runs for that type, so its gates are not held to it.
    An entry that resolves to nothing is an error — the rule could not see what it excludes."""
    types = _project_types(repo, rep)
    if not types:
        return
    where = f"{TREE_DIR}/{PROJECT_TYPES_NODE}"

    def covers(entry: str, skill: str) -> bool:
        return skill == entry or skill.startswith(entry + "-")

    def entry_paths(entry: str) -> list[str] | None:
        """The paths an entry names, or None when it names nothing at all."""
        paths = [
            path
            for skill, fm in skills
            for ident, path in _produced_entries(fm)
            if ident == entry or covers(entry, skill)
        ]
        return paths if paths or any(covers(entry, skill) for skill, _ in skills) else None

    left_out: dict[str, dict[str, list[str]]] = {}  # project type -> entry -> paths it names
    for ptype, entries in types.items():
        left_out[ptype] = {}
        for entry in entries:
            paths = entry_paths(entry)
            if paths is None:
                rep.fail(
                    where,
                    "hard-gate-on-not-grown",
                    f"project type {ptype!r} never grows {entry!r}, which is no artifact id in any "
                    f"skill's `metadata.artifacts.produces`, no skill and no domain — the gate rule "
                    f"cannot tell which paths this project type leaves out",
                )
                continue
            left_out[ptype][entry] = paths

    for skill, fm in skills:
        for item in _prerequisite_items(fm):
            if item.get("gate") != "hard":
                continue
            gate = str(item["path"]).lstrip("/")
            named: list[str] = []
            for ptype, entries in left_out.items():
                if any(covers(entry, skill) for entry in entries):
                    continue
                named += [
                    f"{entry!r} in project type {ptype}"
                    for entry, paths in entries.items()
                    if any(_paths_overlap(gate, p) for p in paths)
                ]
            if named:
                rep.fail(
                    f"skills/{skill}",
                    "hard-gate-on-not-grown",
                    f"has a `hard` prerequisite on {gate!r}, which a project type never grows "
                    f"({'; '.join(named)}) — make it `soft` and state in the step that reads it "
                    f"what the skill does without the file",
                )


# --------------------------------------------------------------------------
# citations — every asset kind cites tree nodes, and the nodes cite each other
# --------------------------------------------------------------------------

# A citation is one inline-code span: `` `tree/<path>` `` or `` `tree/<path> § <heading>` ``.
# Matched over the text with line-wrap whitespace collapsed, because citations wrap. The
# optional `../` run is for prose one directory down (`flows/README.md`). A path with `<` or `>`
# is a pattern (`tree/<p>`), not a citation — node file names use `[x]` for exactly that reason.
TREE_REF_RE = re.compile(r"`(?:\.\./)*tree/([^`\s§]*)(?: § ([^`]+))?`")
HEADING_RE = re.compile(r"^#{2,3}\s+(.+?)\s*$", re.MULTILINE)

# The whole instruction tree installs as one dir-scoped asset: `tree/CONTRACT.md` names it,
# and `contract` is a dir-scoped kind, so the directory deploys whole. A per-file `contract:`
# ref could never resolve — `_` is not a legal asset-name character.
CONTRACT_ASSET = "shared-contracts"

# ADRs 0001–0014 are carried over verbatim from `-mp` and record decisions about a layout this
# collection replaced; they name old paths on purpose. Only ADR 0015 and the ADR index are checked.
FROZEN_DOC_RE = re.compile(r"^docs/adr/00(?:0[1-9]|1[0-4])-[^/]*\.md$")


def _cited_tree_refs(text: str) -> set[str]:
    """Every `tree/<path>` this text cites in an inline-code span."""
    return {path for path, _section in TREE_REF_RE.findall(re.sub(r"\n[ \t]*", " ", text))}


def _check_tree_citations(text: str, where: str, repo: Path, rep: Report) -> None:
    """Rule `tree-citation-resolves`: a cited file exists, and a cited section resolves to a `##` or
    `###` heading equal to it or starting with `<section> (`.

    A rewrite that renames a heading leaves every `§` citation of it dangling, and the
    file-exists check cannot see that."""
    headings: dict[str, list[str]] = {}
    for path, section in sorted(set(TREE_REF_RE.findall(re.sub(r"\n[ \t]*", " ", text)))):
        if "<" in path or ">" in path:
            continue
        target = repo / TREE_DIR / path
        exists = target.is_dir() if (not path or path.endswith("/")) else target.is_file()
        if not exists:
            rep.fail(where, "tree-citation-resolves", f"cites `tree/{path}`, which does not exist")
            continue
        if not section:
            continue
        if not target.is_file():
            rep.fail(where, "tree-citation-resolves", f"cites `tree/{path} § {section}`, but {path} is a directory")
            continue
        if path not in headings:
            headings[path] = HEADING_RE.findall(target.read_text(encoding="utf-8"))
        if not any(h == section or h.startswith(f"{section} (") for h in headings[path]):
            rep.fail(where, "tree-citation-resolves", f"cites `tree/{path} § {section}`, and {path} has no such heading")


# The old cross-cutting layer is gone. A path into it is a citation of nothing, and it is the
# drift this collection was rebuilt to end: `contracts/<name>.md` anywhere a human or agent
# reads is a stale instruction waiting to be followed.
OLD_CONTRACT_PATH_RE = re.compile(r"(?<![\w./-])(?:\.\./)*contracts/[a-z_]+\.md")


def _is_frozen(rel: str) -> bool:
    return bool(FROZEN_DOC_RE.match(rel))


def _where_of(repo: Path, path: Path) -> str:
    """`skills/<dir>` for a SKILL.md — the label every skill rule uses — else the repo-relative path."""
    rel = path.relative_to(repo).as_posix()
    parts = rel.split("/")
    return f"skills/{parts[1]}" if len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md" else rel


def _files(repo: Path, folder: str, suffixes: tuple[str, ...]) -> list[Path]:
    root = repo / folder
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in suffixes and "__pycache__" not in p.parts)


def _non_frozen(repo: Path, paths: list[Path]) -> list[Path]:
    return [p for p in paths if not _is_frozen(p.relative_to(repo).as_posix())]


def check_citations(repo: Path, rep: Report) -> None:
    """Rule `tree-citation-resolves` over every file that cites the tree: skills, nodes, templates,
    flows, docs (frozen ADRs excepted) and the root markdown."""
    files = [
        *sorted(repo.glob("*.md")),
        *_non_frozen(repo, _files(repo, "docs", (".md",))),
        *_files(repo, TREE_DIR, (".md",)),
        *_files(repo, "templates", (".md",)),
        *_files(repo, "flows", (".md", ".yaml", ".yml")),
        *_files(repo, "skills", (".md",)),
    ]
    for path in files:
        _check_tree_citations(path.read_text(encoding="utf-8"), _where_of(repo, path), repo, rep)


def check_old_contract_paths(repo: Path, rep: Report) -> None:
    """Rule `no-old-contract-path`: nothing under `skills/`, `tree/`, `templates/`, `docs/`
    (frozen ADRs excepted), `README.md` or `CLAUDE.md` names `contracts/<name>.md`."""
    files = [
        *[repo / n for n in ("README.md", "CLAUDE.md") if (repo / n).is_file()],
        *_non_frozen(repo, _files(repo, "docs", (".md",))),
        *_files(repo, TREE_DIR, (".md",)),
        *_files(repo, "templates", (".md",)),
        *_files(repo, "skills", (".md", ".py", ".yaml", ".yml")),
    ]
    for path in files:
        for found in sorted(set(OLD_CONTRACT_PATH_RE.findall(path.read_text(encoding="utf-8")))):
            rep.fail(
                _where_of(repo, path),
                "no-old-contract-path",
                f"names `{found}`, a cross-cutting contract file this collection no longer ships — "
                f"cite the node under `tree/` that documents the part instead",
            )


# --------------------------------------------------------------------------
# skills
# --------------------------------------------------------------------------

def _declared_contract_assets(fm: dict) -> set[str]:
    """The contract assets this skill's `metadata.requires` names."""
    metadata = fm.get("metadata")
    if not isinstance(metadata, dict):
        return set()
    requires = metadata.get("requires")
    if not isinstance(requires, list):
        return set()
    out: set[str] = set()
    for ref in requires:
        m = REF_RE.match(str(ref))
        if m and m.group(1) == "contract":
            out.add(m.group(3))
    return out


def _check_skill_contract_dep(fm: dict, cited: set[str], where: str, rep: Report) -> None:
    """Cite a tree node and you declare the contract asset — and vice versa."""
    declared = _declared_contract_assets(fm)
    for wrong in sorted(declared - {CONTRACT_ASSET}):
        rep.error(
            where,
            f"declares contract {wrong!r}, but the only contract asset is {CONTRACT_ASSET!r} — "
            f"{{host}} indexes an asset under its slugified `name:`, so a per-file ref names nothing",
            fact="host:asset-name-slug",
            rule="contract-asset-is-one",
        )
    if cited and CONTRACT_ASSET not in declared:
        rep.error(
            where,
            f"cites {len(cited)} `tree/` path(s) but does not declare "
            f"`contract:@skaile-ai/{CONTRACT_ASSET}` in `metadata.requires` — "
            f"nothing would install what it reads, and {{host}} is what reports the gap",
            fact="host:doctor-walks-requires",
            rule="skill-declares-contract",
        )
    if not cited and CONTRACT_ASSET in declared:
        rep.error(
            where,
            f"declares {CONTRACT_ASSET!r} but cites no `tree/` path — {{host}} would "
            f"report a dependency that reached no reader",
            fact="host:doctor-walks-requires",
            rule="skill-declares-contract",
        )


ROUTE_HEADING_RE = re.compile(r"^## Route[ \t]*$", re.MULTILINE)
STEPS_HEADING_RE = re.compile(r"^## Steps[ \t]*$", re.MULTILINE)
NUMBERED_RE = re.compile(r"^\d+\.\s")


def _section_lines(body: str, heading: re.Pattern[str]) -> list[str] | None:
    """The lines under a `## ` heading, up to the next one; None when the heading is absent."""
    m = heading.search(body)
    if not m:
        return None
    out: list[str] = []
    for line in body[m.end():].splitlines():
        if line.startswith("## "):
            break
        out.append(line)
    return out


def _route_items(lines: list[str]) -> list[str]:
    """The numbered items of a section, each joined with its wrapped continuation lines."""
    items: list[str] = []
    open_item = False
    for line in lines:
        if NUMBERED_RE.match(line):
            items.append(line)
            open_item = True
        elif not line.strip():
            open_item = False
        elif open_item:
            items[-1] += " " + line.strip()
    return items


def _check_route_shape(produces_empty: bool, body: str, where: str, rep: Report) -> None:
    """Rule `route-shape`: a skill that writes artifacts is a route — a `## Route` heading whose
    numbered items each cite a `tree/` node. A skill that writes none keeps a `## Steps` list."""
    if produces_empty:
        if _section_lines(body, STEPS_HEADING_RE) is None:
            rep.fail(where, "route-shape", "writes no artifact (`produces: []`) and has no `## Steps` heading")
        return
    lines = _section_lines(body, ROUTE_HEADING_RE)
    if lines is None:
        rep.fail(where, "route-shape", "writes artifacts and has no `## Route` heading")
        return
    items = _route_items(lines)
    if not items:
        rep.fail(where, "route-shape", "`## Route` has no numbered items")
    for i, item in enumerate(items, start=1):
        if not TREE_REF_RE.search(item):
            rep.fail(where, "route-shape", f"route item {i} cites no `tree/…` node — a route is a list of nodes to read")


def _check_writers(nodes: list[Node], skill_fms: list[tuple[str, dict]], rep: Report) -> None:
    """Rule `produces-writer-listed` / `writer-without-produces`: a node's `writers:` and the skills'
    `produces` say the same thing from both ends.

    A produces path resolving to a node must find the skill in its `writers:`. A node's writer
    must have a produces path that resolves to the node, or a directory above one of the node's
    entries, or a path below one of the node's directory entries."""
    fms = dict(skill_fms)
    for skill, fm in skill_fms:
        for _ident, path in _produced_entries(fm):
            if not path.startswith(ARTIFACT_ROOT + "/"):
                continue
            node = resolve(nodes, path)
            if node is not None and skill not in node.writers:
                rep.fail(
                    f"skills/{skill}",
                    "produces-writer-listed",
                    f"produces {path!r}, which resolves to `{node.file}`, whose `writers:` does not list {skill!r}",
                )

    def prefix(a: list[str], b: list[str]) -> bool:
        return len(a) <= len(b) and all(_seg_eq(x, y) for x, y in zip(a, b))

    for node in nodes:
        for writer in node.writers:
            if writer not in fms:
                continue  # an unknown skill is `node-frontmatter`'s report
            ok = False
            for _ident, p in _produced_entries(fms[writer]):
                if not p.startswith(ARTIFACT_ROOT + "/"):
                    continue
                ps = _segs(p)
                if (
                    resolve(nodes, p) is node
                    or any(prefix(ps, _segs(e)) for e in node.entries)
                    or any(e.endswith("/") and prefix(_segs(e), ps) for e in node.entries)
                ):
                    ok = True
                    break
            if not ok:
                rep.fail(
                    node.file,
                    "writer-without-produces",
                    f"lists writer {writer!r}, but no `produces` path of that skill resolves to this node "
                    f"or lies above or below its `path:` entries",
                )


def check_skills(
    repo: Path, nodes: list[Node], rep: Report
) -> tuple[set[str], dict[str, set[str]], dict[str, dict]]:
    """Check every skill.

    Returns `(installable skill names, `tree/` paths cited per skill directory, parsed frontmatter
    per skill directory)`. The second is what makes a flow's `contract:` manifest checkable for
    exactness rather than only for existence; the third is what a flow's hard gates are held
    against the writers upstream of them.
    """
    skills_dir = repo / "skills"
    names: set[str] = set()
    contracts: dict[str, set[str]] = {}
    if not skills_dir.is_dir():
        return names, contracts, {}

    produced: set[str] = set()
    required: list[tuple[str, str]] = []
    skill_fms: list[tuple[str, dict]] = []
    bodies: list[tuple[str, str]] = []

    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        directory = skill_md.parent.name
        where = f"skills/{directory}"
        text = skill_md.read_text()
        fm, body = split_frontmatter(text)

        # Keyed by directory, because that is what a flow node resolves against —
        # `name:` may be wrong, and the mismatch is reported separately below.
        contracts[directory] = _cited_tree_refs(text)

        if not fm:
            rep.error(where, "SKILL.md has no parseable YAML frontmatter")
            continue

        # The reader declares its own dependency. A skill's `metadata.requires` is the
        # one list with a live reader in the shipped installer (`host:doctor-walks-requires`,
        # which reports a dependency that reached no workspace), while a flow's dependency
        # edges are built from its nodes' `run.assets`, never from its top-level `requires:`
        # (`extractFlowRequires`, @skaile/workspaces discovery/src/requires-graph.ts).
        _check_skill_contract_dep(fm, contracts[directory], where, rep)

        # 1. identity. Three of the four roles a skill name plays resolve through the
        #    directory, and forge-concept never reads `name:` for identity at all
        #    (`host:skill-identity-is-the-directory`) — so a mismatch is invisible until
        #    a node runs with no skill body.
        name = fm.get("name")
        if not name:
            rep.error(where, "frontmatter has no `name:`")
        elif name != directory:
            rep.error(
                where,
                f"`name:` is {name!r} but the directory is {directory!r} — they must match "
                f"character for character; {{host}} resolves a node's skill through the directory",
                fact="host:skill-identity-is-the-directory",
                rule="skill-name-matches-directory",
            )
        else:
            names.add(name)

        # 2. the one frontmatter field with a live reader.
        if "version" not in fm:
            rep.error(where, "frontmatter has no `version:`")

        # 3. the body ceiling: a route is short; a skill that writes no artifact carries its steps.
        block = _artifacts_block(fm)
        declared = block.get("produces") if block is not None else None
        produces_empty = isinstance(declared, list) and not declared
        ceiling = LINE_BUDGET_NO_ARTIFACTS if produces_empty else LINE_BUDGET
        line_count = len(text.splitlines())
        if line_count > ceiling:
            rep.house(
                where,
                f"SKILL.md is {line_count} lines, over the {ceiling}-line ceiling",
                rule="skill-line-budget",
            )

        # 4. the machine layer has to be where its readers look — neither reader falls
        #    back to the frontmatter root, and neither raises. A block at the root parses
        #    clean and reports `satisfied: true` on an unmet gate.
        for key in ("artifacts", "prerequisites"):
            if key in fm:
                rep.error(
                    where,
                    f"`{key}:` is at the frontmatter root — it must sit under `metadata:`, "
                    f"which is the only place its reader looks ({{host}})",
                    fact="host:skill-metadata-nesting",
                    rule="machine-layer-nesting",
                )

        # 5. declared prerequisites are joined to the *project* root, not to `_concept/`
        #    (`host:prerequisite-project-root`). A concept path without the prefix resolves
        #    one level too high, and the path has to resolve to a node of the tree. Paths
        #    outside the concept are legal only when named in PROJECT_ROOT_PREREQUISITES —
        #    see that constant for why the restriction survives ticket 23's finding.
        for entry in _prerequisite_paths(fm):
            if not entry.startswith(ARTIFACT_ROOT + "/"):
                if entry in PROJECT_ROOT_PREREQUISITES:
                    continue
                rep.error(
                    where,
                    f"prerequisite path {entry!r} does not start with {ARTIFACT_ROOT + '/'!r} and is not "
                    f"one of the named project-root gates ({', '.join(sorted(PROJECT_ROOT_PREREQUISITES))}) — "
                    f"{{host}} joins it to the project root, so a concept path without the prefix "
                    f"resolves outside the concept",
                    fact="host:prerequisite-project-root",
                    rule="prerequisite-prefix",
                )
                continue
            if nodes and resolve(nodes, entry) is None:
                rep.error(
                    where,
                    f"prerequisite path {entry!r} resolves to no node of `{TREE_DIR}/` — {{host}} "
                    f"would resolve it against the project root and find nothing",
                    fact="host:prerequisite-project-root",
                    rule="prerequisite-path-resolves",
                )

        # 5b. what the skill writes, and which artifacts it reads by id (ADR 0013).
        produced |= _check_produces(fm, where, nodes, rep)
        required += [(where, ident) for ident in _required_artifact_ids(fm)]
        skill_fms.append((directory, fm))

        # 6. the body is a route, or a list of steps for a skill that writes no artifact.
        if isinstance(declared, list):
            _check_route_shape(produces_empty, body, where, rep)

        bodies.append((where, body))

    # 7a. every artifact id a skill requires is produced by some skill — a second pass, as
    #     the producer may come later in the directory order.
    for where, ident in required:
        if ident not in produced:
            rep.error(
                where,
                f"requires artifact {ident!r} in `metadata.artifacts.requires`, which no skill "
                f"declares in `metadata.artifacts.produces` — add it to the skill that writes it",
            )

    # 7b. a hard gate on an artifact a project type never grows — needs every skill's declarations,
    #     so it is a second pass too.
    _check_not_grown_gates(repo, skill_fms, rep)

    # 7c. a node's writers and the skills' produces agree from both ends.
    _check_writers(nodes, skill_fms, rep)

    # 7. a skill is called one way, and only if it exists here or in EXTERNAL_SKILLS —
    #    a second pass, so a call to a skill later in the directory order resolves.
    for where, body in bodies:
        _check_skill_calls(body, where, names, rep)

    return names, contracts, dict(skill_fms)


def _check_skill_calls(body: str, where: str, names: set[str], rep: Report) -> None:
    """An operative call reads `Call the Skill tool with "<name>"`, and a user-invoked
    skill is an instruction to the human, never a Skill-tool call."""
    # A call wraps like any sentence; read it with the line breaks folded to spaces.
    called = {n for pair in SKILL_TOOL_CALL_RE.findall(re.sub(r"\n[ \t]*", " ", body)) for n in pair if n}
    for name in sorted(called):
        if name in names or EXTERNAL_SKILLS.get(name) == "model":
            continue
        if EXTERNAL_SKILLS.get(name) == "user":
            rep.house(
                where,
                f"calls the Skill tool with {name!r}, which is user-invoked upstream — phrase it "
                f"as an instruction to the human: tell the user to run `/{name}`",
                rule="skill-call-target",
            )
        else:
            rep.house(
                where,
                f"calls the Skill tool with {name!r}, which is neither a skill in this collection "
                f"nor an external skill in EXTERNAL_SKILLS",
                rule="skill-call-target",
            )
    for name in sorted(set(BARE_SLASH_SKILL_RE.findall(body))):
        if name in names or EXTERNAL_SKILLS.get(name) == "model":
            rep.house(
                where,
                f"mentions `/{name}` as a slash command — an operative call reads: "
                f"Call the Skill tool with \"{name}\"",
                rule="bare-slash-skill",
            )


def _prerequisite_items(fm: dict) -> list[dict]:
    """The `metadata.prerequisites.files` entries that name a path, read the way the resolver
    reads them — and also from the root, so a misplaced block is checked for its paths rather
    than silently skipped."""
    meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    prereq = meta.get("prerequisites") or fm.get("prerequisites") or {}
    if not isinstance(prereq, dict):
        return []
    files = prereq.get("files") or []
    return [item for item in files if isinstance(item, dict) and item.get("path")]


def _prerequisite_paths(fm: dict) -> list[str]:
    """Declared file gates' paths, as the resolver joins them."""
    return [str(item["path"]).lstrip("/") for item in _prerequisite_items(fm)]


# --------------------------------------------------------------------------
# the contract manifest
# --------------------------------------------------------------------------

def _check_manifest(repo: Path, rep: Report) -> None:
    """Without `tree/CONTRACT.md`, discovery finds no contract at all — and a second manifest
    anywhere would ship a second, competing instruction layer.

    Same failure ticket 29 gated for flows, from the other side: the installer indexes
    the asset under its slugified `name:`, so a name that does not slugify to what every
    `contract:` ref says leaves those refs naming nothing.
    """
    where = f"{TREE_DIR}/CONTRACT.md"
    manifest = repo / TREE_DIR / "CONTRACT.md"
    if not manifest.is_file():
        rep.error(f"{TREE_DIR}/", "has no `CONTRACT.md` — discovery finds no contract asset and every `contract:` ref names nothing")
    else:
        fm, _body = split_frontmatter(manifest.read_text())
        if not fm:
            rep.error(where, "has no parseable YAML frontmatter — the manifest is the frontmatter")
        else:
            name = fm.get("name")
            if not name:
                rep.error(where, "frontmatter has no `name:`")
            elif _slugify_asset_name(str(name)) != CONTRACT_ASSET:
                rep.error(
                    where,
                    f"`name:` {name!r} installs as {_slugify_asset_name(str(name))!r}, but every "
                    f"`contract:` ref names {CONTRACT_ASSET!r} — {{host}} takes the asset's identity "
                    f"from the slugified name",
                    fact="host:asset-name-slug",
                    rule="contract-manifest-slug",
                )

    for other in sorted(repo.rglob("CONTRACT.md")):
        rel = other.relative_to(repo)
        if other == manifest or any(part.startswith(".") for part in rel.parts):
            continue
        rep.fail(
            rel.as_posix(),
            "only-one-contract-manifest",
            f"is a second `CONTRACT.md` — `{TREE_DIR}/CONTRACT.md` is the only one, and the installer "
            f"ships the whole directory of every manifest it discovers",
        )


# --------------------------------------------------------------------------
# flows
# --------------------------------------------------------------------------

def check_flows(
    repo: Path,
    skill_names: set[str],
    skill_contracts: dict[str, set[str]],
    skill_fms: dict[str, dict],
    rep: Report,
) -> None:
    flows_dir = repo / "flows"
    if not flows_dir.is_dir():
        return

    for flow_file in sorted(flows_dir.glob("*/*.flow.yaml")):
        where = f"flows/{flow_file.parent.name}/{flow_file.name}"
        text = flow_file.read_text()
        try:
            flow = yaml.safe_load(text) or {}
        except yaml.YAMLError as exc:
            rep.error(where, f"is not parseable YAML: {exc}")
            continue
        if not isinstance(flow, dict):
            rep.error(where, "does not contain a mapping")
            continue
        _check_one_flow(repo, flow, text, flow_file, where, skill_names, skill_contracts, skill_fms, rep)


def _slugify_asset_name(raw: str) -> str:
    """The installer's canonical asset name for `raw`.

    Mirrors `slugifyAssetName` (`host:asset-name-slug`): NFKD, drop
    combining accents, lowercase, every other run of non-alphanumerics to `-`, trim.
    """
    decomposed = unicodedata.normalize("NFKD", raw)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", stripped.lower()))


def _check_one_flow(
    repo: Path,
    flow: dict,
    text: str,
    flow_file: Path,
    where: str,
    skill_names: set[str],
    skill_contracts: dict[str, set[str]],
    skill_fms: dict[str, dict],
    rep: Report,
) -> None:
    stem = flow_file.name[: -len(".flow.yaml")]
    directory = flow_file.parent.name
    flow_id = flow.get("id")

    # identity — the loader finds a flow by directory, the manifest names it by id.
    if not flow_id:
        rep.error(where, "has no `id:`")
    elif flow_id != stem or flow_id != directory:
        rep.error(where, f"`id:` {flow_id!r} must equal both the filename stem {stem!r} and the directory {directory!r}")

    # `validateFlow` requires `name`; forge-concept's loader does not. Carrying it
    # satisfies both, at the cost of one line. (The claim used to read "platform's
    # validateFlow" — the schema lives in @skaile/workspaces, which platform calls.)
    flow_name = flow.get("name")
    if not flow_name:
        rep.error(
            where,
            "has no top-level `name:` — {host} requires a non-empty one",
            fact="host:flow-manifest-requires-name",
            rule="flow-name-present",
        )
    elif flow_id and _slugify_asset_name(flow_name) != flow_id:
        # `name:` is not decoration: the installer takes a flow's asset identity from it,
        # not from `id:` (`host:flow-asset-named-from-name`). A title that does not slugify
        # to the id makes the flow unresolvable as `flow:@<publisher>/<id>` and it silently
        # never installs, while the deployed directory the loader matches on is named from
        # the same slug.
        rep.error(
            where,
            f"`name:` {flow_name!r} slugifies to {_slugify_asset_name(flow_name)!r}, not to `id:` "
            f"{flow_id!r} — {{host}} names the asset from `name:`, so this flow cannot be "
            f"installed as `flow:@skaile-ai/{flow_id}`",
            fact="host:flow-asset-named-from-name",
            rule="flow-name-slugifies-to-id",
        )

    _check_presentation(flow, text, where, rep)

    nodes = flow.get("nodes") or []
    edges = flow.get("edges") or []
    if not isinstance(nodes, list) or not nodes:
        rep.error(
            where,
            "has no `nodes:` — {host} discards a flow missing id/nodes/edges, without an error",
            fact="host:loader-discards-incomplete-flow",
            rule="flow-has-nodes",
        )
        return
    if not isinstance(edges, list):
        rep.error(where, "`edges:` is not a list")
        return

    # node ids
    ids: list[str] = []
    for node in nodes:
        if not isinstance(node, dict) or not node.get("id"):
            rep.error(where, "a node has no `id`")
            continue
        ids.append(node["id"])
    seen: set[str] = set()
    for nid in ids:
        if nid in seen:
            rep.error(where, f"duplicate node id {nid!r}")
        seen.add(nid)

    by_id = {n["id"]: n for n in nodes if isinstance(n, dict) and n.get("id")}

    node_skills = _check_nodes(nodes, by_id, where, skill_names, rep)

    # edges. The host orders nodes along `type: flow` and nothing else
    # (`host:flow-edge-orders-run`, `host:flow-edge-gates-state`), so a differently-typed
    # edge draws on the canvas and orders nothing. Reachability below catches it when it is
    # the only path to a node; this catches it when it runs *parallel* to a flow edge,
    # where reachability stays green and the edge is pure decoration.
    for edge in edges:
        if not isinstance(edge, dict):
            rep.error(where, "an edge is not a mapping")
            continue
        src, tgt = edge.get("source"), edge.get("target")
        eid = edge.get("id", f"{src}->{tgt}")
        if src not in by_id:
            rep.error(where, f"edge {eid!r} has source {src!r}, which is not a node id")
        if tgt not in by_id:
            rep.error(where, f"edge {eid!r} has target {tgt!r}, which is not a node id")
        if src is not None and src == tgt:
            rep.error(where, f"edge {eid!r} is a self-loop on {src!r}")
        etype = edge.get("type")
        if etype != FLOW_EDGE:
            rep.error(
                where,
                f"edge {eid!r} has `type: {etype!r}`, but {{host}} reads only `type: {FLOW_EDGE}` — "
                f"it would draw an edge that orders nothing, and gates no node's readiness either",
                fact=("host:flow-edge-orders-run", "host:flow-edge-gates-state"),
                rule="edge-type-flow",
            )

    # reachability under flow-typed edges — a disconnected subgraph is still possible
    # with every edge correctly typed.
    _check_reachability(flow, by_id, edges, where, rep)

    # a hard gate needs a writer upstream of its node — the order half of F04.
    _check_gate_writers(flow, by_id, edges, skill_fms, where, rep)

    # requires: exactness. A missing entry is not a house-rule violation — the
    # skill is then never installed, and the node runs with an empty prompt.
    _check_requires(flow, node_skills, skill_contracts, repo, where, rep)


def _check_presentation(flow: dict, text: str, where: str, rep: Report) -> None:
    """The keys the onboarding endpoint turns into a card, and the keys ticket 10
    deleted. Every field here is read without validation on the far side: a missing
    `description` renders an empty card, an `input_style` outside the union is cast to
    it and branches to nothing, and a `research_depth` outside the published options is
    offered as a selected value the picker cannot show."""
    for key in ("version", "description"):
        value = flow.get(key)
        if not isinstance(value, str) or not value.strip():
            rep.error(
                where,
                f"has no non-empty string `{key}:` — {{host}} publishes `description` verbatim",
                fact="host:profile-description",
                rule="flow-description",
            )

    meta = flow.get("meta")
    if meta is None:
        rep.error(
            where,
            "has no `meta:` — {host} reads `meta.icon` and `meta.onboarding` from it",
            fact="host:profile-onboarding",
            rule="flow-meta",
        )
        meta = {}
    elif not isinstance(meta, dict):
        rep.error(where, "`meta:` is not a mapping")
        meta = {}

    for dead in DEAD_META_KEYS:
        if dead in meta:
            rep.house(where, f"carries `meta.{dead}:`, deleted by ticket 10 — every value fell through every reader")

    icon = meta.get("icon")
    if not isinstance(icon, str) or not icon.startswith("i-"):
        rep.error(
            where,
            f"has `meta.icon: {icon!r}` — it must be an `i-` prefixed Iconify name; "
            f"{{host}} passes it straight to the icon component, which renders nothing for anything else",
            fact="host:profile-icon",
            rule="flow-icon",
        )

    onboarding = meta.get("onboarding")
    if not isinstance(onboarding, dict):
        rep.error(
            where,
            "has no `meta.onboarding:` mapping — {host} then falls back to a structured "
            "form with no fields",
            fact="host:profile-onboarding",
            rule="onboarding-present",
        )
    else:
        style = onboarding.get("input_style")
        if style not in INPUT_STYLES:
            rep.error(
                where,
                f"has `meta.onboarding.input_style: {style!r}`, not one of {sorted(INPUT_STYLES)} "
                f"— {{host}} casts it to the union without checking it",
                fact="host:profile-onboarding",
                rule="onboarding-input-style",
            )
        fields = onboarding.get("fields")
        if style in ("structured", "repo"):
            if not isinstance(fields, list) or not fields or not all(isinstance(f, str) and f.strip() for f in fields):
                rep.error(
                    where,
                    f"has `input_style: {style!r}` but no non-empty `meta.onboarding.fields:` "
                    f"list — {{host}} would render a form with no questions",
                    fact="host:profile-onboarding",
                    rule="onboarding-fields",
                )
        if "placeholder" in onboarding and style != "freeform":
            rep.error(
                where,
                f"carries `meta.onboarding.placeholder:` with `input_style: {style!r}` — "
                f"{{host}} binds it to the freeform textarea only, so it has no reader here",
                fact="host:onboarding-placeholder-freeform",
                rule="onboarding-placeholder",
            )

    globals_ = flow.get("globals")
    if not isinstance(globals_, dict):
        rep.error(
            where,
            "has no `globals:` mapping — {host} seeds the onboarding depth picker from "
            "`globals.research_depth`",
            fact="host:research-depth-seed",
            rule="flow-globals",
        )
    else:
        for dead in DEAD_GLOBALS:
            if dead in globals_:
                rep.house(where, f"carries `globals.{dead}:`, deleted by ticket 10 — it has no reader in either host")
        depth = globals_.get("research_depth")
        if depth not in RESEARCH_DEPTHS:
            rep.error(
                where,
                f"has `globals.research_depth: {depth!r}`, not one of {sorted(RESEARCH_DEPTHS)} "
                f"— {{host}} publishes exactly those as selectable",
                fact="host:research-depth-options",
                rule="research-depth",
            )

    for found in sorted(set(INTERPOLATION_RE.findall(text))):
        rep.error(
            where,
            f"contains the interpolation {found!r} — {{host}} resolves nothing, so the "
            f"literal string reaches the prompt",
            fact="host:prompt-is-verbatim",
            rule="no-interpolation",
        )


def _check_nodes(nodes: list, by_id: dict, where: str, skill_names: set[str], rep: Report) -> set[str]:
    """Node kinds, phases, group containment. Returns the set of skills the flow runs."""
    node_skills: set[str] = set()
    group_phases: dict[str, str] = {}

    for node in nodes:
        if not isinstance(node, dict) or not node.get("id"):
            continue
        nid = node["id"]
        data = node.get("data") if isinstance(node.get("data"), dict) else {}
        kind = node.get("type")

        if kind not in NODE_KINDS:
            rep.house(
                where,
                f"node {nid!r} has `type: {kind!r}` — `-mp` ships `skill` and `group` nodes only "
                f"(ticket 10 deleted the `sub-flow` and `router` kinds)",
            )

        # Both bans are host-derived rather than house style: each key still has a live
        # reader, so the ban would change meaning if the host stopped reading it.
        for dead in DEAD_NODE_DATA:
            if dead in data:
                fact_id, rule_id, extra = DEAD_NODE_DATA_FACTS[dead]
                rep.error(
                    where,
                    f"node {nid!r} carries `data.{dead}:`, deleted by ticket 10{extra}",
                    fact=fact_id,
                    rule=rule_id,
                )

        phase = data.get("phase")
        if phase is None:
            rep.error(
                where,
                f"node {nid!r} declares no `data.phase` — {{host}} then guesses one from the skill name",
                fact="host:phase-guessed-from-skill",
                rule="node-phase-present",
            )
        elif phase not in PHASES:
            rep.error(
                where,
                f"node {nid!r} has `data.phase: {phase!r}`, not one of {sorted(PHASES)} — "
                f"{{host}} is the whole lane vocabulary, and swallows anything else",
                fact="host:phase-lane-vocabulary",
                rule="node-phase-enum",
            )

        if kind == "group":
            if isinstance(phase, str):
                group_phases[nid] = phase
            continue

        if kind == "skill":
            skill = data.get("skill")
            if not skill:
                rep.error(where, f"skill node {nid!r} has no `data.skill`")
            else:
                node_skills.add(skill)
                if skill_names and skill not in skill_names:
                    rep.error(where, f"node {nid!r} names skill {skill!r}, which has no `skills/{skill}/` directory")

            # Authored geometry on a skill node is not cosmetic
            # (`host:positioned-nodes-lose-lanes`): every positioned node drops out of the
            # lane computation and the layout returns early with `lanes: []` once none are
            # left, so a fully-positioned flow loses the swimlanes *and* the group-phase
            # override that makes group nodes worth carrying. The collection has to
            # withhold geometry to get the feature.
            if node.get("position") is not None:
                rep.error(
                    where,
                    f"skill node {nid!r} carries `position:` — {{host}} removes positioned "
                    f"nodes from the lane computation, so authoring geometry here disables the phase swimlanes",
                    fact="host:positioned-nodes-lose-lanes",
                    rule="node-position",
                )

    # Three group nodes per flow, one per phase. Ticket 10 kept group nodes for one
    # reason — `host:group-phase-wins` — so a flow missing a lane loses the mechanism for
    # the nodes that would have sat in it.
    if len(group_phases) != 3 or set(group_phases.values()) != PHASES:
        rep.error(
            where,
            f"has {len(group_phases)} group node(s) with phases {sorted(group_phases.values())} — "
            f"every flow carries exactly three, one per phase {sorted(PHASES)}, because {{host}} "
            f"lets a group override its children's",
            fact="host:group-phase-wins",
            rule="group-nodes-per-phase",
        )

    # parentNode, and the agreement that makes the two phase declarations one table.
    for node in nodes:
        if not isinstance(node, dict) or not node.get("id"):
            continue
        nid = node["id"]
        if node.get("type") != "skill":
            if node.get("parentNode") is not None:
                rep.error(where, f"node {nid!r} is not a skill node but declares `parentNode` — only skill nodes sit in a group")
            continue
        parent = node.get("parentNode")
        if parent is None:
            rep.error(
                where,
                f"skill node {nid!r} has no `parentNode` — it sits in no phase group, so nothing can "
                f"hold its `data.phase` to the lane it renders in ({{host}})",
                fact="host:group-phase-wins",
                rule="skill-node-parent",
            )
            continue
        if parent not in by_id:
            rep.error(where, f"node {nid!r} has parentNode {parent!r}, which is not a node id")
            continue
        if by_id[parent].get("type") != "group":
            rep.error(where, f"node {nid!r} has parentNode {parent!r}, which is not a group node")
            continue
        data = node.get("data") if isinstance(node.get("data"), dict) else {}
        own = data.get("phase")
        group = group_phases.get(parent)
        # Only compare enum-valid values: a phase outside the enum is already reported
        # above, and reporting it twice hides that it is one defect.
        if own in PHASES and group is not None and own != group:
            rep.error(
                where,
                f"node {nid!r} declares `data.phase: {own!r}` but sits in group {parent!r}, whose phase is "
                f"{group!r} — {{host}} takes the group's, so the node's declaration is "
                f"silently overridden and the two must be written from one table",
                fact="host:group-phase-wins",
                rule="node-phase-agrees-with-group",
            )

    return node_skills


def _check_reachability(flow: dict, by_id: dict, edges: list, where: str, rep: Report) -> None:
    entry = flow.get("entry")
    if not entry:
        rep.error(where, "has no `entry:`")
        return
    if entry not in by_id:
        rep.error(where, f"`entry: {entry!r}` is not a node id")
        return

    adjacency: dict[str, list[str]] = {}
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        if edge.get("type") == FLOW_EDGE:
            adjacency.setdefault(edge.get("source"), []).append(edge.get("target"))

    reached = {entry}
    stack = [entry]
    while stack:
        cur = stack.pop()
        for nxt in adjacency.get(cur, []):
            if nxt and nxt not in reached:
                reached.add(nxt)
                stack.append(nxt)

    # group nodes are containers, not steps — they carry no flow edges.
    for nid, node in sorted(by_id.items()):
        if node.get("type") == "group":
            continue
        if nid not in reached:
            rep.error(
                where,
                f"node {nid!r} is unreachable from `entry` along `type: flow` edges — "
                f"it will never run, whatever else connects it",
            )


def _check_gate_writers(
    flow: dict, by_id: dict, edges: list, skill_fms: dict[str, dict], where: str, rep: Report
) -> None:
    """Rule: every `hard` prerequisite of a node's skill has a writer upstream of that node.

    A hard gate on an artifact no earlier node writes is a node that can never open (F04): the
    host reports `satisfied: true` or blocks forever, and neither raises. "Upstream" is every node
    that lies on a path from `entry` to the node along `type: flow` edges, the node itself
    excluded — a node later in the run, or on a branch that never reaches it, writes too late.
    A writer's `produces[].path` meets the gate when the two are equal or one is a directory
    prefix of the other, a placeholder segment matching any one. Paths outside `_concept/`
    (the named project-root gates) are the project's, not a node's, and are not held to this.
    A node unreachable from `entry` is reported by `_check_reachability` and skipped here."""
    entry = flow.get("entry")
    if entry not in by_id:
        return

    forward: dict[str, list[str]] = {}
    for edge in edges:
        if isinstance(edge, dict) and edge.get("type") == FLOW_EDGE:
            forward.setdefault(edge.get("source"), []).append(edge.get("target"))

    def reach(start: str, blocked: str | None = None) -> set[str]:
        seen, stack = {start}, [start]
        while stack:
            for nxt in forward.get(stack.pop(), []):
                if nxt in by_id and nxt != blocked and nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return seen

    reached = reach(entry)
    ahead = {nid: reach(nid) for nid in reached}

    def upstream(nid: str) -> set[str]:
        if nid == entry:
            return set()
        return {x for x in reach(entry, nid) - {nid} if nid in ahead[x]}

    skill_of = {
        nid: node["data"]["skill"]
        for nid, node in by_id.items()
        if node.get("type") == "skill"
        and isinstance(node.get("data"), dict)
        and isinstance(node["data"].get("skill"), str)
    }
    writes = {
        nid: [path for _, path in _produced_entries(skill_fms[skill])]
        for nid, skill in skill_of.items()
        if skill in skill_fms
    }

    flow_id = flow.get("id")
    for nid in sorted(reached):
        skill = skill_of.get(nid)
        if skill not in skill_fms:
            continue
        before = sorted(upstream(nid))
        written = [path for u in before for path in writes.get(u, [])]
        for item in _prerequisite_items(skill_fms[skill]):
            if item.get("gate") != "hard":
                continue
            gate = str(item["path"]).lstrip("/")
            if not gate.startswith(ARTIFACT_ROOT + "/"):
                continue
            if any(_paths_overlap(gate, path) for path in written):
                continue
            rep.error(
                where,
                f"flow {flow_id!r}: node {nid!r} runs skill {skill!r}, which has a `hard` "
                f"prerequisite on {gate!r}, but no upstream node produces it "
                f"(upstream: {', '.join(before) or 'none'}) — the node can never open; add a node "
                f"that writes it before this one, or make the gate `soft` and state in the skill "
                f"what it does without the file",
            )


REF_RE = re.compile(r"^(skill|flow|contract):@([A-Za-z0-9_-]+)/([A-Za-z0-9_.-]+)(?:#(.+))?$")


def _check_requires(
    flow: dict,
    node_skills: set[str],
    skill_contracts: dict[str, set[str]],
    repo: Path,
    where: str,
    rep: Report,
) -> None:
    requires = flow.get("requires")
    if requires is None:
        rep.error(where, "has no `requires:` manifest — installing the flow would install none of its skills")
        return

    declared_skills: set[str] = set()
    declared_contracts: set[str] = set()
    unresolvable_contracts: set[str] = set()
    for ref in requires:
        m = REF_RE.match(str(ref))
        if not m:
            rep.error(where, f"`requires:` entry {ref!r} is not a `kind:@publisher/name` ref")
            continue
        kind, _publisher, name, _version = m.groups()
        if kind == "skill":
            declared_skills.add(name)
        elif kind == "flow":
            # A `flow:` ref only makes sense for a sub-flow node, a kind `-mp` no
            # longer ships — so it can only install a flow nothing here delegates to.
            rep.error(where, f"`requires:` lists flow {name!r}, but `-mp` ships no `sub-flow` nodes — nothing can delegate to it")
        elif kind == "contract":
            declared_contracts.add(name)
            if name != CONTRACT_ASSET:
                unresolvable_contracts.add(name)
                rep.error(
                    where,
                    f"`requires:` names contract {name!r}, but the only contract asset is "
                    f"{CONTRACT_ASSET!r} — {{host}} indexes by slugified name, so a per-file "
                    f"ref resolves to nothing",
                    fact="host:asset-name-slug",
                    rule="requires-contract-per-file",
                )

    for missing in sorted(node_skills - declared_skills):
        rep.error(where, f"runs skill {missing!r} but does not list it in `requires:` — it would not be installed")
    for extra in sorted(declared_skills - node_skills):
        rep.error(where, f"`requires:` lists skill {extra!r}, which no node in this flow runs")

    # The reference layer is one asset, so a flow's contract manifest is one ref or none:
    # present when any of its own node skills reads a contract file, absent when none
    # does. Per-file exactness is not expressible here and is gated on the skills, which
    # is where the reading happens — `skill:` refs keep the "no inheritance, no extras"
    # rule because a skill really is per-node.
    if node_skills and all(s in skill_contracts for s in node_skills):
        needed = any(skill_contracts[skill] for skill in node_skills)
        if needed and CONTRACT_ASSET not in declared_contracts:
            rep.error(where, f"its skills read contract files, but `requires:` does not list `contract:@skaile-ai/{CONTRACT_ASSET}` — the reference layer would not be installed")
        if not needed and CONTRACT_ASSET in declared_contracts:
            rep.error(where, f"`requires:` lists {CONTRACT_ASSET!r}, which none of this flow's skills read")


# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# prose
# --------------------------------------------------------------------------

# `docs/` and the root markdown are the one part of the collection no gate looked at:
# `check.py` globs `skills/`, `contracts/` and `flows/` and stopped there. That is how two
# worked examples drifted onto the tree ADR 0007 replaced and three deleted skill names sat
# unread until ticket 33 found them by hand — the same quiet failure every other check here
# exists to raise, in the files a *human* reads first.
#
# The bar is ticket 33's: a reader must not be able to copy a path that resolves to nothing.
# It is deliberately a check on **paths**, not on prose. Two artifacts in this repo are
# supposed to name things that no longer exist — an ADR recording a deletion cites the
# contract it deleted (`0004` → `iron_laws.md`, `0010` → `plans.md`), and `examples/WHY.md`
# quotes pre-port skill bodies verbatim. A dead-*name* check would fire on exactly the two
# places where naming a dead thing is correct, so mentions are free and only links and
# `skills/<name>` paths are gated.
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
SKILL_PATH_RE = re.compile(r"(?<![A-Za-z0-9_./-])`?skills/([a-z0-9][a-z0-9-]*)")
SKILLS_HEADING_RE = re.compile(r"^## Skills[ \t]*$", re.MULTILINE)


def _prose_files(repo: Path) -> list[Path]:
    """Every markdown file no other check reads: `docs/` and the repo root.

    `skills/` and `tree/` are gated by their own checks, which know far more about what those
    files are; `flows/` holds YAML. What is left is prose — minus ADRs 0001–0014, frozen
    records that name the layout this collection replaced (`FROZEN_DOC_RE`).
    """
    docs = sorted((repo / "docs").rglob("*.md")) if (repo / "docs").is_dir() else []
    return _non_frozen(repo, docs) + sorted(repo.glob("*.md"))


def check_docs(repo: Path, skill_names: set[str], rep: Report) -> None:
    for path in _prose_files(repo):
        where = path.relative_to(repo).as_posix()
        text = path.read_text(encoding="utf-8")

        for target in MD_LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            rel = target.split("#", 1)[0]
            if not rel:
                continue
            if not (path.parent / rel).exists():
                rep.error(where, f"links to `{target}`, which does not exist")

        listed = set(SKILL_PATH_RE.findall(text))
        for name in sorted(listed):
            if name not in skill_names:
                rep.error(where, f"names the path `skills/{name}`, which is not a skill in this collection")

        # The README's `## Skills` table is the human's index of the collection, read with
        # the same token reader as the phantom check above, so both directions agree.
        if where == "README.md" and SKILLS_HEADING_RE.search(text):
            for name in sorted(skill_names - listed):
                rep.house(
                    "README.md",
                    f"does not list `skills/{name}` under `## Skills` — every skill is in the README index",
                )


def run(repo: Path) -> Report:
    rep = Report()
    nodes = load_tree(repo)
    skill_names, skill_contracts, skill_fms = check_skills(repo, nodes, rep)
    check_tree(repo, nodes, rep)
    check_citations(repo, rep)
    check_old_contract_paths(repo, rep)
    check_flows(repo, skill_names, skill_contracts, skill_fms, rep)
    check_docs(repo, skill_names, rep)
    return rep


def run_own_tests() -> int:
    """Run `test_check.py`, the failing fixture behind every rule above.

    A missing pytest is an error, not a skip: a skipped test phase reports the same
    confident green as the defect this phase exists to catch.
    """
    tests = Path(__file__).resolve().parent / "test_check.py"
    if not tests.is_file():
        print(f"ERROR {tests.name} is missing — the rules above have no fixtures behind them")
        return 1

    sys.stdout.flush()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(tests), "-q"],
        cwd=tests.parent,
    )
    sys.stdout.flush()
    if proc.returncode == 4:  # pytest's usage error, which includes "no module named pytest"
        print("ERROR pytest could not run — install it (`pip install pytest`); a skipped test phase is not a pass")
    return proc.returncode


TIER_HEADINGS = {
    INTRINSIC: "intrinsic — this collection is wrong",
    HOST_DERIVED: "host-derived — this collection is wrong, or the fact expired",
    HOUSE_STYLE: "house style — a rule this collection imposes on itself",
}


def print_report(rep: Report) -> None:
    """Print failures grouped by tier.

    The tiering is output only: every tier is an error and the exit code stays one bit,
    because a distinct code invites a CI config that ignores it. It exists because the
    three read differently. An intrinsic failure has one meaning. A host-derived one has
    two, and which it is cannot be settled from inside this repo — so it names its fact
    and the tool that can.
    """
    for tier in TIERS:
        problems = rep.by_tier(tier)
        if not problems:
            continue
        print(f"-- {TIER_HEADINGS[tier]} ({len(problems)})")
        for problem in problems:
            print(f"ERROR {problem}")
        print()

    cited = sorted(rep.facts_cited())
    if cited:
        print(
            "Each host-derived failure above has two readings: this collection is wrong,\n"
            "or the fact it rests on expired. Only the verifier can tell them apart:\n"
            f"    python scripts/verify_host.py --fact {cited[0]}\n"
            f"    python scripts/verify_host.py            # all {len(hf.FACTS)} facts\n"
            f"facts cited by this run: {', '.join(cited)}\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the collection for references that resolve to nothing.")
    parser.add_argument("--repo", default=None, help="repo root (default: the parent of this script's directory)")
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="skip `test_check.py`. For CI, which runs it as its own step, and for iterating on one rule.",
    )
    parser.add_argument(
        "--print-tree",
        action="store_true",
        help="print the artifact tree generated from the nodes' `path:` entries (the lines that go in "
        "the fenced block of `tree/README.md`) and exit; runs no checks.",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve() if args.repo else Path(__file__).resolve().parent.parent

    if args.print_tree:
        print("\n".join(render_tree(load_tree(repo))))
        return 0

    rep = run(repo)

    skills = len(list((repo / "skills").glob("*/SKILL.md"))) if (repo / "skills").is_dir() else 0
    flows = len(list((repo / "flows").glob("*/*.flow.yaml"))) if (repo / "flows").is_dir() else 0

    print_report(rep)

    print(f"\n{skills} skill(s) · {flows} flow(s) · {len(rep.errors)} error(s)")

    if args.no_tests:
        print("fixtures: skipped (--no-tests) — this run does not mean green")
        return 0 if rep.ok() else 1

    print("\nrunning the checker's own fixtures…", flush=True)
    tests_rc = run_own_tests()
    return 0 if (rep.ok() and tests_rc == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
