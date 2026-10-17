#!/usr/bin/env python3
"""test_check.py — a failing fixture per rule `check.py` enforces.

Each case builds a minimal collection in a tmpdir — skills, the instruction tree, flows — breaks
exactly one thing, and asserts the break is reported. A gate with no test for its negative case is
the same silent pass the gate exists to close, so every rule in `check.py` has one here.

The fixture is clean by construction: `write_repo` writes a tree whose `writers:` are derived from
the skills' `produces` and whose listing fence is generated, so a test that breaks one thing sees
exactly one error. The four landed flows are the positive fixture for the flow rules.

  $ pytest scripts/test_check.py -q
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest
import yaml

import check
import host_facts
import verify_host


# -- the fixture collection ---------------------------------------------------

CONTRACT_MANIFEST = """\
---
name: shared-contracts
description: "The instruction tree."
version: "0.1.0"
metadata:
  do_not_invoke: true
---

# shared-contracts
"""

# `requires` sits last under `metadata:` so the tests that rewrite `metadata:\n  prerequisites:`
# or `metadata:\n` find the text they replace.
SKILL = """\
---
name: {name}
description: "A skill."
version: "0.1.0"
metadata:
  prerequisites:
    files:
      - {{ path: "_concept/07_screens", gate: soft }}
  artifacts:
    produces:
      - {{ id: brief, path: "_concept/brief.md" }}
  requires:
    - "contract:@skaile-ai/shared-contracts"
---

# {name}

Body.

## Route

Read `tree/README.md` once per session, then these nodes in order.

1. **Write it** — `tree/brief.md`.

**Done when** the brief exists.
"""

PROJECT_TYPES = """\
## Project types

| project_type | never grows |
|---|---|
| web-app | — |
"""


def write_node(root: Path, rel: str, path, writers=(), summary: str = "a part", body: str = "") -> None:
    """Write `tree/<rel>` with the frontmatter every node carries. `path` is a string or a list."""
    p = root / "tree" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    first = path[0] if isinstance(path, (list, tuple)) else path
    shown = "[" + ", ".join(f'"{e}"' for e in path) + "]" if isinstance(path, (list, tuple)) else f'"{path}"'
    p.write_text(
        f"---\npath: {shown}\nsummary: {summary}\nwriters: [{', '.join(writers)}]\n---\n\n# {first}\n\n{body}"
    )


def good_tree(root: Path) -> None:
    """The smallest tree the fixture skills need: the root, a brief, a covered directory, the scope
    node with its project-types table, and a screens directory with its placeholder children."""
    (root / "tree").mkdir(parents=True, exist_ok=True)
    (root / "tree" / "CONTRACT.md").write_text(CONTRACT_MANIFEST)
    write_node(
        root, "README.md", ["_concept/", "_concept/README.md"], summary="the artifact tree",
        body="## The rule\n\nRead the node before the part.\n\n## The tree\n\n```\nx\n```\n\n"
             "## Numbering\n\nThe first level is numbered.\n",
    )
    write_node(root, "brief.md", "_concept/brief.md", summary="the pitch", body="## Writing it\n\nWrite the pitch.\n")
    write_node(root, "01_meta/README.md", ["_concept/01_meta/"], summary="project settings")
    write_node(root, "01_meta/scope.md", "_concept/01_meta/scope.yaml", summary="flow and project type",
               body=PROJECT_TYPES)
    write_node(
        root, "07_screens/README.md", ["_concept/07_screens/"],
        summary="the app shell and one spec per screen",
        body="## Format (the elements block)\n\nA screen lists its elements.\n",
    )
    write_node(root, "07_screens/shell.md", "_concept/07_screens/shell.md", summary="the app shell")
    write_node(root, "07_screens/[feature_slug]/README.md", "_concept/07_screens/<feature_slug>/",
               summary="screens of one feature")
    write_node(root, "07_screens/[feature_slug]/[screen].md", "_concept/07_screens/<feature_slug>/<screen>.md",
               summary="one spec per screen")


def sync_writers(root: Path) -> None:
    """Rewrite every node's `writers:` from the skills' `produces`: a skill writes the node its
    `produces` path resolves to. The fixture stays clean when a test swaps a `produces` block;
    the tests of rule S11 desynchronise it on purpose, afterwards."""
    nodes = check.load_tree(root)
    writers: dict[str, list[str]] = {n.rel: [] for n in nodes}
    skills = root / "skills"
    for skill in sorted(p for p in skills.iterdir() if (p / "SKILL.md").is_file()) if skills.is_dir() else []:
        fm, _body = check.split_frontmatter((skill / "SKILL.md").read_text())
        for _ident, path in check._produced_entries(fm):
            if not path.startswith("_concept/"):
                continue
            hit = check.resolve(nodes, path)
            if hit is not None and skill.name not in writers[hit.rel]:
                writers[hit.rel].append(skill.name)
    for node in nodes:
        p = root / "tree" / node.rel
        p.write_text(re.sub(r"(?m)^writers: .*$", f"writers: [{', '.join(writers[node.rel])}]", p.read_text(), count=1))


def refresh_fence(root: Path) -> None:
    """Paste the generated tree into the first fence of `tree/README.md`, as an author would."""
    readme = root / "tree" / "README.md"
    fence = "\n".join(check.render_tree(check.load_tree(root)))
    readme.write_text(re.sub(r"(?s)```\n.*?\n```", lambda _m: f"```\n{fence}\n```", readme.read_text(), count=1))


def write_repo(root: Path, skills=("spec-feature",)) -> Path:
    good_tree(root)
    for name in skills:
        d = root / "skills" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(SKILL.format(name=name))
    (root / "flows").mkdir(exist_ok=True)
    sync_writers(root)
    refresh_fence(root)
    return root


def skill_file(root: Path, name: str = "spec-feature") -> Path:
    return root / "skills" / name / "SKILL.md"


def edit_node(root: Path, rel: str, old: str, new: str, refresh: bool = True) -> None:
    """Replace `old` in `tree/<rel>`. The listing is regenerated unless the test is about it."""
    p = root / "tree" / rel
    text = p.read_text()
    assert old in text, (rel, old)
    p.write_text(text.replace(old, new, 1))
    if refresh:
        refresh_fence(root)


def add_node(root: Path, rel: str, path, **kw) -> None:
    write_node(root, rel, path, **kw)
    refresh_fence(root)


def set_produces(root: Path, block: str, skill: str = "spec-feature") -> None:
    """Swap the fixture skill's `produces` block (the default is one `brief` entry). An empty list
    turns the route into `## Steps`, the shape a skill that writes no artifact has."""
    p = skill_file(root, skill)
    default = '    produces:\n      - { id: brief, path: "_concept/brief.md" }\n'
    assert default in p.read_text()
    text = p.read_text().replace(default, block, 1)
    if "produces: []" in block:
        text = text.replace("## Route", "## Steps")
    p.write_text(text)
    sync_writers(root)


def cite(root: Path, skill: str, node: str) -> None:
    """Make `skill` cite `tree/<node>` from its body."""
    p = skill_file(root, skill)
    p.write_text(p.read_text() + f"\nReads `tree/{node}`.\n")


def undeclare(root: Path, skill: str = "spec-feature") -> None:
    p = skill_file(root, skill)
    block = '  requires:\n    - "contract:@skaile-ai/shared-contracts"\n'
    assert block in p.read_text()
    p.write_text(p.read_text().replace(block, "", 1))


def strip_citations(root: Path, skill: str = "spec-feature") -> None:
    p = skill_file(root, skill)
    p.write_text(re.sub(r"`tree/[^`]*`", "the tree", p.read_text()))


def body(root: Path, skill: str, text: str) -> None:
    """Replace the `Body.` line of `skill`'s SKILL.md with `text`."""
    p = skill_file(root, skill)
    p.write_text(p.read_text().replace("Body.", text, 1))




def write_flow(root: Path, flow: dict, flow_id: str | None = None) -> None:
    flow_id = flow_id or flow["id"]
    d = root / "flows" / flow_id
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{flow_id}.flow.yaml").write_text(yaml.safe_dump(flow, sort_keys=False))


def good_flow() -> dict:
    """The shape the four landed flows have: three phase groups, every skill node
    parented and repeating its group's phase, `type: flow` edges only."""
    return {
        "id": "tiny",
        "version": "0.1.0",
        "name": "Tiny",
        "description": "A tiny flow.",
        "meta": {
            "icon": "i-heroicons-beaker",
            "onboarding": {"input_style": "structured", "fields": ["app_name"]},
        },
        "requires": ["skill:@skaile-ai/spec-feature", "contract:@skaile-ai/shared-contracts"],
        "globals": {"research_depth": "skip"},
        "entry": "a",
        "nodes": [
            {"id": "g-conceptualization", "type": "group", "data": {"label": "C", "phase": "conceptualization"}},
            {"id": "g-implementation", "type": "group", "data": {"label": "I", "phase": "implementation"}},
            {"id": "g-review", "type": "group", "data": {"label": "R", "phase": "review"}},
            {
                "id": "a",
                "type": "skill",
                "parentNode": "g-conceptualization",
                "data": {"skill": "spec-feature", "phase": "conceptualization"},
            },
            {
                "id": "b",
                "type": "skill",
                "parentNode": "g-implementation",
                "data": {"skill": "spec-feature", "phase": "implementation"},
            },
        ],
        "edges": [{"id": "e1", "source": "a", "target": "b", "type": "flow"}],
    }


def node(flow: dict, nid: str) -> dict:
    """Nodes are addressed by id, not index — the fixture's shape may grow."""
    return next(n for n in flow["nodes"] if n["id"] == nid)



def errors(root: Path) -> list[str]:
    return check.run(root).errors


def only(root: Path, fragment: str) -> None:
    """Assert exactly one error, mentioning `fragment`."""
    errs = errors(root)
    assert len(errs) == 1, errs
    assert fragment in errs[0], errs[0]


def among(root: Path, *fragments: str) -> None:
    """Assert every fragment is reported, and nothing beyond one error per fragment."""
    errs = errors(root)
    for fragment in fragments:
        assert any(fragment in e for e in errs), (fragment, errs)
    assert len(errs) == len(fragments), errs




# -- baseline ---------------------------------------------------------------

def test_clean_collection_has_no_errors(tmp_path):
    root = write_repo(tmp_path)
    write_flow(root, good_flow())
    assert errors(root) == []


def test_empty_flows_directory_is_fine(tmp_path):
    root = write_repo(tmp_path)
    assert errors(root) == []


# -- skills -----------------------------------------------------------------

def test_name_must_match_directory(tmp_path):
    root = write_repo(tmp_path)
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(skill.read_text().replace("name: spec-feature", "name: spec-features"))
    only(root, "must match character for character")


def test_missing_version_is_reported(tmp_path):
    root = write_repo(tmp_path)
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(skill.read_text().replace('version: "0.1.0"\n', ""))
    only(root, "no `version:`")


def test_line_budget(tmp_path):
    root = write_repo(tmp_path)
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(skill.read_text() + "\nfiller\n" * check.LINE_BUDGET)
    only(root, f"over the {check.LINE_BUDGET}-line ceiling")



def test_prerequisite_path_outside_the_tree(tmp_path):
    root = write_repo(tmp_path)
    skill = skill_file(root)
    skill.write_text(
        skill.read_text().replace('path: "_concept/07_screens"', 'path: "_concept/experience/screens"')
    )
    only(root, "resolves to no node of `tree/`")


def test_prerequisite_path_covered_by_a_directory_entry_resolves(tmp_path):
    root = write_repo(tmp_path)
    skill = skill_file(root)
    skill.write_text(skill.read_text().replace('path: "_concept/07_screens"', 'path: "_concept/01_meta/anything.yaml"'))
    assert errors(root) == []


def test_prerequisite_path_without_the_concept_prefix(tmp_path):
    """The path the validator joins is the project root's, so the prefix is load-bearing."""
    root = write_repo(tmp_path)
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(skill.read_text().replace('path: "_concept/07_screens"', 'path: "07_screens"'))
    only(root, "does not start with '_concept/'")


def test_named_project_root_prerequisite_is_allowed(tmp_path):
    """`host:prerequisite-project-root` joins to the project root, so `package.json` genuinely resolves —
    the restriction is a named list now, not a blanket ban."""
    root = write_repo(tmp_path)
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(skill.read_text().replace('path: "_concept/07_screens"', 'path: "package.json"'))
    assert errors(root) == []


def test_unnamed_project_root_prerequisite_is_still_rejected(tmp_path):
    """The list is the whole exception. A path outside `_concept/` that is not on it is
    still the pre-0007 concept path this check exists to catch."""
    root = write_repo(tmp_path)
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(skill.read_text().replace('path: "_concept/07_screens"', 'path: "experience/screens"'))
    only(root, "named project-root gates")


def test_prerequisites_at_the_frontmatter_root(tmp_path):
    """The failure this catches is silent: the block parses and the gate never fires."""
    root = write_repo(tmp_path)
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(
        skill.read_text().replace(
            'metadata:\n  prerequisites:\n    files:\n      - { path: "_concept/07_screens", gate: soft }\n',
            "prerequisites:\n  files:\n    - { path: \"_concept/07_screens\", gate: soft }\nmetadata:\n",
        )
    )
    only(root, "must sit under `metadata:`")


def test_artifacts_at_the_frontmatter_root(tmp_path):
    root = write_repo(tmp_path)
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(
        skill.read_text().replace("metadata:\n", "artifacts:\n  requires:\n    - { id: screens }\nmetadata:\n")
    )
    only(root, "must sit under `metadata:`")


def test_skill_without_produces(tmp_path):
    root = write_repo(tmp_path)
    set_produces(root, "    requires: []\n")
    only(root, "has no `metadata.artifacts.produces` list")



def test_skill_without_an_artifacts_block(tmp_path):
    root = write_repo(tmp_path)
    skill = skill_file(root)
    skill.write_text(skill.read_text().replace("  artifacts:\n    produces:\n", "").replace(
        '      - { id: brief, path: "_concept/brief.md" }\n', ""
    ))
    sync_writers(root)
    only(root, "has no `metadata.artifacts.produces` list")


def test_produces_that_is_not_a_list(tmp_path):
    root = write_repo(tmp_path)
    set_produces(root, "    produces: brief\n")
    only(root, "`metadata.artifacts.produces` is a str, not a list")


def test_empty_produces_is_legal(tmp_path):
    """A skill that writes only code or git state declares `[]`; the key is what is mandatory."""
    root = write_repo(tmp_path)
    set_produces(root, "    produces: []\n")
    assert errors(root) == []


def test_produces_entry_without_a_path(tmp_path):
    root = write_repo(tmp_path)
    set_produces(root, "    produces:\n      - { id: brief }\n")
    only(root, "must be a map with a string `id` and a string `path`")


def test_produces_id_must_be_kebab_case(tmp_path):
    root = write_repo(tmp_path)
    set_produces(root, '    produces:\n      - { id: Brief_Doc, path: "_concept/brief.md" }\n')
    only(root, "is not kebab-case")


def test_produces_path_without_the_concept_prefix(tmp_path):
    root = write_repo(tmp_path)
    set_produces(root, '    produces:\n      - { id: brief, path: "brief.md" }\n')
    only(root, "does not start with '_concept/'")



def test_produces_path_outside_the_tree(tmp_path):
    root = write_repo(tmp_path)
    set_produces(root, '    produces:\n      - { id: brief, path: "_concept/pitch.md" }\n')
    only(root, "produces-path-resolves")
    assert "resolves to no node of `tree/`" in errors(root)[0]


@pytest.mark.parametrize(
    "path",
    [
        "_concept/brief.md",
        "_concept/README.md",  # the root README documents itself
        "_concept/07_screens/",
        "_concept/07_screens",  # a directory named without its slash
        "_concept/07_screens/<feature_slug>/<screen>.md",
        "_concept/07_screens/checkout/payment.md",  # a placeholder entry matches any one segment
        "_concept/07_screens/shell.md",
        "_concept/01_meta/extra.yaml",  # lies under a list-form directory entry
    ],
)
def test_produces_paths_that_resolve(tmp_path, path):
    root = write_repo(tmp_path)
    set_produces(root, f'    produces:\n      - {{ id: brief, path: "{path}" }}\n')
    assert errors(root) == []


@pytest.mark.parametrize(
    "path",
    [
        "_concept/brief.md/extra",  # below a file entry
        "_concept/09_nothing/",  # not a root entry
        "_concept/pitch.md",  # the root README does not cover what no node names
        "_concept/brief",  # a file named without its extension is not the directory `brief/` either
        "_concept/brief.json",  # `tree/brief.md` sits where the location rule puts `brief.*`; that is not a match
    ],
)
def test_produces_paths_that_do_not_resolve(tmp_path, path):
    root = write_repo(tmp_path)
    set_produces(root, f'    produces:\n      - {{ id: brief, path: "{path}" }}\n')
    only(root, "produces-path-resolves")
    assert "resolves to no node of `tree/`" in errors(root)[0]


def test_produces_the_bare_artifact_root(tmp_path):
    """`_concept/` names no part, so the resolver is never asked: the shape check reports it."""
    root = write_repo(tmp_path)
    set_produces(root, '    produces:\n      - { id: brief, path: "_concept/" }\n')
    only(root, "names no artifact below `_concept/`")
    assert "produces-path-resolves" not in errors(root)[0]


def test_required_artifact_nobody_produces(tmp_path):
    root = write_repo(tmp_path)
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(
        skill.read_text().replace(
            "  artifacts:\n", "  artifacts:\n    requires:\n      - { id: screens }\n", 1
        )
    )
    only(root, "requires artifact 'screens'")
    assert "skills/spec-feature" in errors(root)[0]


def test_required_artifact_produced_by_another_skill(tmp_path):
    """The producer may sit later in the directory order than the reader."""
    root = write_repo(tmp_path, skills=("spec-feature", "zeta-producer"))
    set_produces(root, '    produces:\n      - { id: screens, path: "_concept/07_screens/" }\n', "zeta-producer")
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(
        skill.read_text().replace(
            "  artifacts:\n", "  artifacts:\n    requires:\n      - { id: screens }\n", 1
        )
    )
    assert errors(root) == []


SCREENS = '    produces:\n      - { id: screens, path: "_concept/07_screens/<feature_slug>/<screen>.md" }\n'


def set_gate(root: Path, skill: str, gate: str) -> None:
    """Swap the fixture skill's one prerequisite gate (the default is `soft` on `07_screens`)."""
    p = root / "skills" / skill / "SKILL.md"
    text = p.read_text()
    assert re.search(r"gate: (hard|soft)", text)
    p.write_text(re.sub(r"gate: (hard|soft)", f"gate: {gate}", text, count=1))



def write_project_types(root: Path, types: dict[str, list[str]]) -> None:
    """Rewrite the `## Project types` table of the scope node: `{project_type: [never-grown entries]}`."""
    node_file = root / "tree" / "01_meta" / "scope.md"
    text = node_file.read_text()
    rows = "".join(f"| {t} | {', '.join(entries) or '—'} |\n" for t, entries in types.items())
    node_file.write_text(
        text[: text.index("## Project types")]
        + "## Project types\n\n| project_type | never grows |\n|---|---|\n" + rows
    )


def not_grown_repo(root: Path, skills=("spec-feature", "zeta-producer")) -> Path:
    """`zeta-producer` writes the screens, so the project type's `screens` id resolves; it has a
    `soft` gate of its own, and `spec-feature` gets a `hard` gate on `07_screens`."""
    write_repo(root, skills=skills)
    set_produces(root, SCREENS, "zeta-producer")
    set_gate(root, "spec-feature", "hard")
    return root


def test_hard_gate_on_a_path_a_project_type_never_grows(tmp_path):
    root = not_grown_repo(tmp_path)
    write_project_types(root, {"api-service": ["screens"]})
    only(root, "has a `hard` prerequisite on '_concept/07_screens'")
    assert "skills/spec-feature" in errors(root)[0]
    assert "api-service" in errors(root)[0]
    assert "hard-gate-on-not-grown" in errors(root)[0]


def test_soft_gate_on_a_path_a_project_type_never_grows_is_clean(tmp_path):
    root = not_grown_repo(tmp_path)
    set_gate(root, "spec-feature", "soft")
    write_project_types(root, {"api-service": ["screens"]})
    assert errors(root) == []


def test_hard_gate_on_a_path_no_project_type_leaves_out_is_clean(tmp_path):
    root = not_grown_repo(tmp_path)
    write_project_types(root, {"web-app": []})
    assert errors(root) == []


def test_not_grown_entry_that_resolves_to_nothing(tmp_path):
    root = not_grown_repo(tmp_path)
    set_gate(root, "spec-feature", "soft")
    write_project_types(root, {"api-service": ["nonesuch"]})
    only(root, "never grows 'nonesuch'")


def test_skill_in_a_not_grown_domain_is_not_held_to_its_own_gates(tmp_path):
    """`mockup-view` never runs where `mockup` is not grown, so its hard gate on screens is moot."""
    root = not_grown_repo(tmp_path, skills=("spec-feature", "zeta-producer", "mockup-view"))
    set_gate(root, "mockup-view", "hard")
    set_gate(root, "spec-feature", "soft")
    write_project_types(root, {"api-service": ["screens", "mockup"]})
    assert errors(root) == []


def test_scope_node_without_a_project_types_table(tmp_path):
    """The rule reads its data from the table; a node without it leaves the rule blind."""
    root = write_repo(tmp_path)
    edit_node(root, "01_meta/scope.md", "## Project types", "## Types")
    only(root, "has no `## Project types` table")
    assert "hard-gate-on-not-grown" in errors(root)[0]


# -- hard gates need a writer upstream ---------------------------------------

def gate_flow(first: str, second: str) -> dict:
    """`a` runs `first`, `b` runs `second`, in that order — the two nodes of `good_flow`."""
    flow = good_flow()
    node(flow, "a")["data"]["skill"] = first
    node(flow, "b")["data"]["skill"] = second
    flow["requires"] = [f"skill:@skaile-ai/{s}" for s in sorted({first, second})] + [
        "contract:@skaile-ai/shared-contracts"
    ]
    return flow


def gate_repo(root: Path, *, gate="_concept/07_screens", writes=SCREENS) -> Path:
    """`spec-feature` holds a `hard` gate on `gate`; `zeta-producer` writes `writes`."""
    write_repo(root, skills=("spec-feature", "zeta-producer"))
    set_produces(root, writes, "zeta-producer")
    set_gate(root, "spec-feature", "hard")
    skill = root / "skills" / "spec-feature" / "SKILL.md"
    skill.write_text(skill.read_text().replace('path: "_concept/07_screens"', f'path: "{gate}"'))
    return root


def test_hard_gate_with_no_upstream_writer(tmp_path):
    """The writer is in the flow and writes something else: the gate has nothing to open it."""
    root = gate_repo(tmp_path, writes='    produces:\n      - { id: brief, path: "_concept/brief.md" }\n')
    write_flow(root, gate_flow("zeta-producer", "spec-feature"))
    only(root, "no upstream node produces it")
    assert "node 'b' runs skill 'spec-feature'" in errors(root)[0]
    assert "'_concept/07_screens'" in errors(root)[0]
    assert "flow 'tiny'" in errors(root)[0]


def test_hard_gate_with_the_writer_upstream_is_clean(tmp_path):
    root = gate_repo(tmp_path)
    write_flow(root, gate_flow("zeta-producer", "spec-feature"))
    assert errors(root) == []


def test_hard_gate_whose_writer_only_runs_downstream(tmp_path):
    """Order matters: the writer exists in the flow, but after the node that needs it."""
    root = gate_repo(tmp_path)
    write_flow(root, gate_flow("spec-feature", "zeta-producer"))
    only(root, "no upstream node produces it")
    assert "node 'a' runs skill 'spec-feature'" in errors(root)[0]
    assert "upstream: none" in errors(root)[0]


def test_hard_gate_on_the_entry_node_has_no_upstream(tmp_path):
    root = gate_repo(tmp_path)
    flow = good_flow()
    node(flow, "b")["data"]["skill"] = "spec-feature"
    write_flow(root, flow)
    errs = errors(root)
    assert len(errs) == 2 and all("no upstream node produces it" in e for e in errs), errs


@pytest.mark.parametrize(
    "gate, written",
    [
        ("_concept/07_screens", "_concept/07_screens/<feature_slug>/<screen>.md"),  # file under the gated directory
        ("_concept/07_screens/shell.md", "_concept/07_screens/"),  # the directory holding the gated file
        ("_concept/07_screens/checkout/pay.md", "_concept/07_screens/<feature_slug>/<screen>.md"),  # placeholders
        ("_concept/07_screens/*", "_concept/07_screens/shell.md"),  # `*` matches one segment
        ("_concept/07_screens", "_concept/07_screens"),  # equal
    ],
)
def test_hard_gate_met_by_a_directory_prefix_match(tmp_path, gate, written):
    root = gate_repo(tmp_path, gate=gate, writes=f'    produces:\n      - {{ id: screens, path: "{written}" }}\n')
    write_flow(root, gate_flow("zeta-producer", "spec-feature"))
    assert errors(root) == []


def test_hard_gate_on_a_sibling_path_is_not_met(tmp_path):
    """Prefix matching is by whole segment: `shell.md` does not open a gate on `07_screens/checkout`."""
    root = gate_repo(
        tmp_path,
        gate="_concept/07_screens/checkout",
        writes='    produces:\n      - { id: shell, path: "_concept/07_screens/shell.md" }\n',
    )
    write_flow(root, gate_flow("zeta-producer", "spec-feature"))
    only(root, "no upstream node produces it")


def test_soft_gate_needs_no_upstream_writer(tmp_path):
    root = gate_repo(tmp_path, writes='    produces:\n      - { id: brief, path: "_concept/brief.md" }\n')
    set_gate(root, "spec-feature", "soft")
    write_flow(root, gate_flow("spec-feature", "zeta-producer"))
    assert errors(root) == []


def test_project_root_gate_is_not_held_to_an_upstream_writer(tmp_path):
    """`package.json` is the project's, not a node's — the rule is about `_concept/` artifacts."""
    root = gate_repo(tmp_path, gate="package.json")
    write_flow(root, gate_flow("spec-feature", "zeta-producer"))
    assert errors(root) == []



# -- citations: skills, nodes, templates, docs and flows cite the tree ---------

def test_missing_cited_node(tmp_path):
    root = write_repo(tmp_path)
    cite(root, "spec-feature", "gone.md")
    only(root, "cites `tree/gone.md`, which does not exist")


def test_citing_without_declaring_the_contract_asset(tmp_path):
    """Cite a node and you declare the one contract asset, or nothing installs what the skill reads."""
    root = write_repo(tmp_path)
    undeclare(root)
    only(root, "does not declare")


def test_declaring_the_contract_asset_without_citing(tmp_path):
    root = write_repo(tmp_path)
    set_produces(root, "    produces: []\n")
    strip_citations(root)
    only(root, "cites no `tree/` path")


def test_a_skill_declaring_a_per_file_contract(tmp_path):
    root = write_repo(tmp_path)
    p = skill_file(root)
    p.write_text(p.read_text().replace(
        '    - "contract:@skaile-ai/shared-contracts"\n',
        '    - "contract:@skaile-ai/shared-contracts"\n    - "contract:@skaile-ai/seed_data"\n',
    ))
    only(root, "the only contract asset is 'shared-contracts'")


def test_node_citing_a_missing_node(tmp_path):
    root = write_repo(tmp_path)
    edit_node(root, "brief.md", "Write the pitch.", "See `tree/nothing.md`.")
    only(root, "cites `tree/nothing.md`")
    assert "tree/brief.md" in errors(root)[0]


def test_flow_docs_are_scanned_for_citations(tmp_path):
    """`flows/README.md` cites the tree like everything else, and a deleted node must not read as fine."""
    root = write_repo(tmp_path)
    write_flow(root, good_flow())
    (root / "flows" / "README.md").write_text("Validated against `../tree/nothing.md`.\n")
    only(root, "cites `tree/nothing.md`")


def test_template_citing_a_missing_node(tmp_path):
    root = write_repo(tmp_path)
    doc(root, "templates/web/TEMPLATE.md", "Seeds follow `tree/10_blueprint/datamodel/seed.md`.\n")
    only(root, "cites `tree/10_blueprint/datamodel/seed.md`, which does not exist")


def test_root_markdown_citing_a_missing_node(tmp_path):
    root = write_repo(tmp_path)
    doc(root, "README.md", "Read `tree/nothing.md` first.\n")
    only(root, "cites `tree/nothing.md`")


def test_cited_section_with_no_such_heading(tmp_path):
    """A rewrite that renames a heading leaves every `§` citation of it dangling, and
    the file still exists — the file-exists check alone stays green."""
    root = write_repo(tmp_path)
    body(root, "spec-feature", "Per `tree/README.md § Nowhere`.")
    only(root, "cites `tree/README.md § Nowhere`, and README.md has no such heading")
    assert "tree-citation-resolves" in errors(root)[0]


def test_cited_section_resolves_across_a_wrap_and_a_parenthetical(tmp_path):
    root = write_repo(tmp_path)
    body(
        root,
        "spec-feature",
        "Per `tree/README.md §\n   Numbering`; the shape is\n`tree/07_screens/README.md § Format`.",
    )
    assert errors(root) == []


def test_a_cited_section_of_a_directory(tmp_path):
    root = write_repo(tmp_path)
    body(root, "spec-feature", "Per `tree/07_screens/ § Format`.")
    only(root, "is a directory")


def test_a_tree_pattern_is_not_a_citation(tmp_path):
    root = write_repo(tmp_path)
    body(root, "spec-feature", "A node sits at `tree/<p>` for the part `_concept/<p>`.")
    assert errors(root) == []


# -- skills: the host's dialog input ----------------------------------------

def onboard_repo(root: Path, node_body: str) -> Path:
    """`concept-onboard` with the node that documents `answers.json`, whose body is `node_body`."""
    write_repo(root, skills=("spec-feature", "concept-onboard"))
    set_produces(
        root,
        '    produces:\n      - { id: onboarding-answers, path: "_concept/02_grounding/onboarding/answers.json" }\n',
        "concept-onboard",
    )
    write_node(root, "02_grounding/README.md", ["_concept/02_grounding/"], summary="what the skills read")
    write_node(root, "02_grounding/onboarding/README.md", ["_concept/02_grounding/onboarding/"],
               summary="the wizard answers")
    write_node(root, "02_grounding/onboarding/answers.md", "_concept/02_grounding/onboarding/answers.json",
               summary="the answers", body=node_body)
    sync_writers(root)
    refresh_fence(root)
    return root


def test_onboard_that_never_names_the_host_input_file(tmp_path):
    """The host writes each step's dialog input to `_grounding/<step>/user_input.json`; an
    onboarding node that does not name it has dropped the merge into `answers.json`."""
    root = onboard_repo(tmp_path, "Merge the dialog answers.\n")
    only(root, "never names `_grounding/<step>/user_input.json`")


def test_onboard_that_names_the_host_input_file_is_clean(tmp_path):
    root = onboard_repo(tmp_path, "Merge `_grounding/<step>/user_input.json` into `answers.json`.\n")
    assert errors(root) == []


def test_onboard_without_its_node(tmp_path):
    root = write_repo(tmp_path, skills=("spec-feature", "concept-onboard"))
    only(root, "does not exist, so nothing names `_grounding/<step>/user_input.json`")


# -- skills: calling a skill ------------------------------------------------

def test_skill_tool_call_naming_an_unknown_skill(tmp_path):
    root = write_repo(tmp_path)
    body(root, "spec-feature", 'Call the Skill tool with "nonesuch".')
    only(root, "calls the Skill tool with 'nonesuch'")


def test_skill_tool_call_naming_a_user_invoked_skill(tmp_path):
    """`triage` is reachable only by the human, so the call is an instruction to them."""
    root = write_repo(tmp_path)
    body(root, "spec-feature", 'First, call the Skill tool with "triage".')
    only(root, "user-invoked upstream")


def test_bare_slash_command_for_a_model_invoked_skill(tmp_path):
    root = write_repo(tmp_path)
    body(root, "spec-feature", "Run `/tdd` for each row.")
    only(root, "mentions `/tdd` as a slash command")


def test_the_three_call_shapes_are_legal(tmp_path):
    root = write_repo(tmp_path)
    body(
        root,
        "spec-feature",
        'Call the Skill tool with "tdd". Then, call the Skill tool twice, for "tdd" and '
        '"code-review". Before that, tell the user to run `/triage`.',
    )
    assert errors(root) == []


# -- flows: identity and presentation ---------------------------------------

def test_flow_id_must_match_directory_and_stem(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["id"] = "other"
    write_flow(root, flow, flow_id="tiny")
    # Two rules fire, and both are true of this file: the id matches neither the stem
    # nor the directory, and `name:` no longer slugifies to it either.
    among(root, "must equal both the filename stem", "names the asset from `name:`")


def test_flow_name_must_slugify_to_its_id(tmp_path):
    """Ticket 29: the installer takes a flow's asset name from `name:`, not `id:`, so a
    title that does not slugify to the id is unresolvable and silently never installs."""
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["name"] = "Reverse Engineer a Codebase"
    write_flow(root, flow)
    only(root, "slugifies to 'reverse-engineer-a-codebase', not to `id:` 'tiny'")


def test_a_title_cased_name_slugifies_to_its_id(tmp_path):
    """The rule is the slug, not string equality — `Appbuilder MVP` is a legal title for
    `appbuilder-mvp`, and every landed flow is named that way."""
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["id"] = "appbuilder-mvp"
    flow["name"] = "Appbuilder MVP"
    write_flow(root, flow)
    assert errors(root) == []


def test_flow_needs_a_top_level_name(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    del flow["name"]
    write_flow(root, flow)
    only(root, "no top-level `name:`")


def test_flow_needs_a_version(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    del flow["version"]
    write_flow(root, flow)
    only(root, "no non-empty string `version:`")


def test_flow_needs_a_description(tmp_path):
    """`host:profile-description` publishes it verbatim onto the onboarding card."""
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["description"] = "  "
    write_flow(root, flow)
    only(root, "no non-empty string `description:`")


def test_flow_icon_must_be_an_iconify_name(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["meta"]["icon"] = "rocket"
    write_flow(root, flow)
    only(root, "must be an `i-` prefixed Iconify name")


def test_flow_needs_meta(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    del flow["meta"]
    write_flow(root, flow)
    among(root, "has no `meta:`", "must be an `i-` prefixed", "no `meta.onboarding:` mapping")


def test_input_style_outside_the_union(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["meta"]["onboarding"]["input_style"] = "wizard"
    write_flow(root, flow)
    only(root, "`meta.onboarding.input_style: 'wizard'`")


def test_structured_onboarding_needs_fields(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["meta"]["onboarding"]["fields"] = []
    write_flow(root, flow)
    only(root, "no non-empty `meta.onboarding.fields:` list")


def test_placeholder_outside_freeform_has_no_reader(tmp_path):
    """`host:onboarding-placeholder-freeform` binds it to the freeform textarea only."""
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["meta"]["onboarding"]["placeholder"] = "Describe your app"
    write_flow(root, flow)
    only(root, "binds it to the freeform textarea only")


def test_research_depth_outside_the_options(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["globals"]["research_depth"] = "exhaustive"
    write_flow(root, flow)
    only(root, "`globals.research_depth: 'exhaustive'`")


def test_flow_needs_globals(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    del flow["globals"]
    write_flow(root, flow)
    only(root, "has no `globals:` mapping")


# -- flows: keys ticket 10 deleted ------------------------------------------

def test_meta_category_is_dead(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["meta"]["category"] = "appbuilder"
    write_flow(root, flow)
    only(root, "carries `meta.category:`")


@pytest.mark.parametrize("key", ["approval_mode", "subagent_mode", "verbosity", "concept_depth"])
def test_dead_globals(tmp_path, key):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["globals"][key] = "whatever"
    write_flow(root, flow)
    only(root, f"carries `globals.{key}:`")


def test_interpolation_has_no_resolver(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["description"] = "Builds ${app_name}."
    write_flow(root, flow)
    only(root, "contains the interpolation '${app_name}'")


def test_node_parameters_are_not_inert(tmp_path):
    """`data.parameters` is the one deleted key with a live host read
    (`host:sub-flow-parameters-read` takes `data.parameters.flow` as a child flow id)."""
    root = write_repo(tmp_path)
    flow = good_flow()
    node(flow, "b")["data"]["parameters"] = {"flow": "skaileup-slice"}
    write_flow(root, flow)
    only(root, "carries `data.parameters:`")


def test_node_writes_is_dead(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    node(flow, "b")["data"]["writes"] = "05_features"
    write_flow(root, flow)
    only(root, "carries `data.writes:`")


# -- flows: node kinds ------------------------------------------------------

def test_sub_flow_node_is_rejected(tmp_path):
    """Ticket 10 inlined the shared building blocks and deleted the kind."""
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["nodes"].append(
        {"id": "s", "type": "sub-flow", "data": {"flow": "skaileup-slice", "phase": "implementation"}}
    )
    flow["edges"].append({"id": "e2", "source": "b", "target": "s", "type": "flow"})
    write_flow(root, flow)
    only(root, "`type: 'sub-flow'`")


def test_router_node_is_rejected(tmp_path):
    """The pick-one renderers died with the mockup merge, and the kind with them."""
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["nodes"].append(
        {"id": "r", "type": "router", "data": {"phase": "review", "routes": [{"target": "b"}]}}
    )
    flow["edges"].append({"id": "e2", "source": "b", "target": "r", "type": "flow"})
    write_flow(root, flow)
    only(root, "`type: 'router'`")


def test_requires_may_not_name_a_flow(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["requires"].append("flow:@skaile-ai/skaileup-slice")
    write_flow(root, flow)
    only(root, "ships no `sub-flow` nodes")


# -- flows: groups and phases -----------------------------------------------

def test_three_group_nodes_per_flow(tmp_path):
    """Two concept flows carry an empty `implementation` group for exactly this rule."""
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["nodes"] = [n for n in flow["nodes"] if n["id"] != "g-review"]
    write_flow(root, flow)
    only(root, "has 2 group node(s)")


def test_two_groups_may_not_share_a_phase(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    node(flow, "g-review")["data"]["phase"] = "implementation"
    write_flow(root, flow)
    only(root, "has 3 group node(s)")


def test_node_without_phase(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    del node(flow, "b")["data"]["phase"]
    write_flow(root, flow)
    only(root, "declares no `data.phase`")


def test_node_with_invalid_phase(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    node(flow, "b")["data"]["phase"] = "banana"
    write_flow(root, flow)
    only(root, "not one of")


def test_node_phase_must_agree_with_its_group(tmp_path):
    """The rule ticket 28 wrote as "one table so they cannot disagree" — and the one
    nothing checked. Both values are enum-valid; the group silently wins at render time."""
    root = write_repo(tmp_path)
    flow = good_flow()
    node(flow, "b")["data"]["phase"] = "review"
    write_flow(root, flow)
    only(root, "silently overridden and the two must be written from one table")


def test_skill_node_must_sit_in_a_group(tmp_path):
    """Without a parent there is no group phase to agree with, so the rule above is
    unenforceable on that node by construction."""
    root = write_repo(tmp_path)
    flow = good_flow()
    del node(flow, "b")["parentNode"]
    write_flow(root, flow)
    only(root, "has no `parentNode`")


def test_parent_node_must_be_a_group(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    node(flow, "b")["parentNode"] = "a"
    write_flow(root, flow)
    only(root, "which is not a group node")


def test_group_node_may_not_be_parented(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    node(flow, "g-review")["parentNode"] = "g-conceptualization"
    write_flow(root, flow)
    only(root, "is not a skill node but declares `parentNode`")


def test_skill_node_geometry_disables_the_swimlanes(tmp_path):
    """`host:positioned-nodes-lose-lanes` drops positioned nodes from the lane computation and returns
    `lanes: []` once none remain — authoring geometry deletes the group-phase override."""
    root = write_repo(tmp_path)
    flow = good_flow()
    node(flow, "b")["position"] = {"x": 10, "y": 10}
    write_flow(root, flow)
    only(root, "carries `position:`")


# -- flows: graph -----------------------------------------------------------

def test_duplicate_node_ids(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    node(flow, "b")["id"] = "a"
    flow["edges"] = [{"id": "e1", "source": "a", "target": "a", "type": "flow"}]
    write_flow(root, flow)
    errs = errors(root)
    assert any("duplicate node id" in e for e in errs), errs
    assert any("self-loop" in e for e in errs), errs


def test_dangling_edge_endpoint(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["edges"][0]["target"] = "nope"
    write_flow(root, flow)
    errs = errors(root)
    assert any("is not a node id" in e for e in errs), errs
    assert any("unreachable from `entry`" in e for e in errs), errs


def test_unresolvable_skill(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    node(flow, "b")["data"]["skill"] = "ghost"
    flow["requires"].append("skill:@skaile-ai/ghost")
    write_flow(root, flow)
    only(root, "has no `skills/ghost/` directory")


def test_untyped_edge_orders_nothing(tmp_path):
    """The check the whole flow half exists for: an untyped edge validates
    green everywhere else and creates zero dependency."""
    root = write_repo(tmp_path)
    flow = good_flow()
    del flow["edges"][0]["type"]
    write_flow(root, flow)
    among(root, "reads only `type: flow`", "unreachable from `entry` along `type: flow` edges")


def test_review_loop_edge_is_a_no_op(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["edges"][0]["type"] = "review-loop"
    write_flow(root, flow)
    among(root, "reads only `type: flow`", "unreachable from `entry`")


def test_optional_edge_does_not_confer_reachability(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["edges"][0]["type"] = "optional"
    write_flow(root, flow)
    among(root, "reads only `type: flow`", "unreachable from `entry`")


def test_non_flow_edge_parallel_to_a_flow_edge(tmp_path):
    """Reachability alone cannot see this one: every node still runs, and the extra edge
    draws on the canvas while ordering nothing."""
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["edges"].append({"id": "e2", "source": "a", "target": "b", "type": "parallel"})
    write_flow(root, flow)
    only(root, "reads only `type: flow`")




# -- skills: the body ceiling (S7) ---------------------------------------------

def pad_to(root: Path, skill: str, total: int) -> None:
    """Append filler lines until SKILL.md is exactly `total` lines long."""
    p = skill_file(root, skill)
    have = len(p.read_text().splitlines())
    assert have <= total, (have, total)
    p.write_text(p.read_text() + "x\n" * (total - have))
    assert len(p.read_text().splitlines()) == total


def test_route_skill_at_the_ceiling_is_clean(tmp_path):
    root = write_repo(tmp_path)
    pad_to(root, "spec-feature", check.LINE_BUDGET)
    assert errors(root) == []


def test_route_skill_one_line_over_the_ceiling(tmp_path):
    root = write_repo(tmp_path)
    pad_to(root, "spec-feature", check.LINE_BUDGET + 1)
    only(root, "SKILL.md is 61 lines, over the 60-line ceiling")
    assert "skill-line-budget" in errors(root)[0]


def test_steps_skill_gets_the_larger_ceiling(tmp_path):
    """A skill that writes no artifact keeps its procedure in the body, so 100 lines are legal."""
    root = write_repo(tmp_path)
    set_produces(root, "    produces: []\n")
    pad_to(root, "spec-feature", check.LINE_BUDGET_NO_ARTIFACTS)
    assert errors(root) == []


def test_steps_skill_one_line_over_the_larger_ceiling(tmp_path):
    root = write_repo(tmp_path)
    set_produces(root, "    produces: []\n")
    pad_to(root, "spec-feature", check.LINE_BUDGET_NO_ARTIFACTS + 1)
    only(root, "SKILL.md is 101 lines, over the 100-line ceiling")


# -- skills: the body is a route (S12) ----------------------------------------

def test_artifact_skill_without_a_route_heading(tmp_path):
    root = write_repo(tmp_path)
    p = skill_file(root)
    p.write_text(p.read_text().replace("## Route", "## Notes"))
    only(root, "writes artifacts and has no `## Route` heading")
    assert "route-shape" in errors(root)[0]


def test_route_without_numbered_items(tmp_path):
    root = write_repo(tmp_path)
    p = skill_file(root)
    p.write_text(p.read_text().replace("1. **Write it** — `tree/brief.md`.\n", ""))
    only(root, "`## Route` has no numbered items")


def test_route_item_that_cites_no_node(tmp_path):
    root = write_repo(tmp_path)
    p = skill_file(root)
    p.write_text(p.read_text().replace("1. **Write it** — `tree/brief.md`.", "1. **Write it** — the brief."))
    only(root, "route item 1 cites no `tree/…` node")


def test_route_item_citation_may_wrap_onto_the_next_line(tmp_path):
    root = write_repo(tmp_path)
    p = skill_file(root)
    p.write_text(p.read_text().replace("1. **Write it** — `tree/brief.md`.", "1. **Write it** —\n   `tree/brief.md`."))
    assert errors(root) == []


def test_skill_that_writes_nothing_has_no_steps_heading(tmp_path):
    root = write_repo(tmp_path)
    set_produces(root, "    produces: []\n")
    p = skill_file(root)
    p.write_text(p.read_text().replace("## Steps", "## Notes"))
    only(root, "writes no artifact (`produces: []`) and has no `## Steps` heading")


# -- skills <-> nodes: writers say the same thing from both ends (S3, S11) ---------

def test_produces_path_below_a_string_form_directory_entry_does_not_resolve(tmp_path):
    """Verification 4: a skill producing a path no node documents. The directory has a node, but
    its `path:` is a plain string, which covers only the directory itself."""
    root = write_repo(tmp_path)
    add_node(root, "03_brand/README.md", "_concept/03_brand/", summary="colours and fonts")
    set_produces(root, '    produces:\n      - { id: brief, path: "_concept/03_brand/nothing.md" }\n')
    only(root, "produces-path-resolves")
    assert "resolves to no node of `tree/`" in errors(root)[0]


def test_produces_path_below_a_list_form_directory_entry_resolves(tmp_path):
    """A list-form `path:` is how a README says it also documents everything below it."""
    root = write_repo(tmp_path)
    add_node(root, "03_brand/README.md", ["_concept/03_brand/"], summary="colours and fonts")
    set_produces(root, '    produces:\n      - { id: brief, path: "_concept/03_brand/nothing.md" }\n')
    assert errors(root) == []


def test_node_that_does_not_list_the_skill_producing_it(tmp_path):
    root = write_repo(tmp_path)
    edit_node(root, "brief.md", "writers: [spec-feature]", "writers: []")
    only(root, "whose `writers:` does not list 'spec-feature'")
    assert "produces-writer-listed" in errors(root)[0]


def test_node_listing_a_writer_that_produces_nothing_there(tmp_path):
    """Verification 4: `writers: [design-brand]` with no matching `produces`."""
    root = write_repo(tmp_path, skills=("spec-feature", "design-brand"))
    set_produces(root, "    produces: []\n", "design-brand")
    edit_node(root, "brief.md", "writers: [spec-feature]", "writers: [spec-feature, design-brand]")
    only(root, "lists writer 'design-brand', but no `produces` path of that skill resolves to this node")
    assert "writer-without-produces" in errors(root)[0]


def test_the_root_readme_is_not_the_writer_of_what_it_does_not_name(tmp_path):
    """`_concept/` is a directory entry, but a root that covered every path would make any skill
    its writer; only the root README itself is documented there."""
    root = write_repo(tmp_path, skills=("spec-feature", "concept-scope", "design-brand"))
    set_produces(root, '    produces:\n      - { id: concept-readme, path: "_concept/README.md" }\n', "concept-scope")
    edit_node(root, "README.md", "writers: [concept-scope]", "writers: [concept-scope, design-brand]")
    only(root, "lists writer 'design-brand', but no `produces` path of that skill resolves to this node")
    assert "writer-without-produces" in errors(root)[0]
    assert "tree/README.md" in errors(root)[0]


def test_a_directory_produces_path_above_a_node_satisfies_its_writer(tmp_path):
    """A skill that writes `07_screens/` as a whole is the writer of what lies inside it."""
    root = write_repo(tmp_path, skills=("spec-feature", "zeta-producer"))
    set_produces(root, '    produces:\n      - { id: screens, path: "_concept/07_screens/" }\n', "zeta-producer")
    edit_node(root, "07_screens/[feature_slug]/[screen].md", "writers: []", "writers: [zeta-producer]")
    assert errors(root) == []


def test_a_produces_path_below_a_directory_entry_satisfies_the_readme_writer(tmp_path):
    root = write_repo(tmp_path, skills=("spec-feature", "zeta-producer"))
    set_produces(root, SCREENS, "zeta-producer")
    edit_node(root, "07_screens/README.md", "writers: []", "writers: [zeta-producer]")
    assert errors(root) == []


def test_node_listing_a_writer_that_is_no_skill(tmp_path):
    root = write_repo(tmp_path)
    edit_node(root, "brief.md", "writers: [spec-feature]", "writers: [spec-feature, ghost]")
    only(root, "`writers:` lists 'ghost', which is no skill in this collection")


# -- the tree: manifest (T1) ---------------------------------------------------

def test_tree_without_a_manifest(tmp_path):
    root = write_repo(tmp_path)
    (root / "tree" / "CONTRACT.md").unlink()
    only(root, "has no `CONTRACT.md`")


def test_manifest_name_must_slugify_to_the_contract_asset(tmp_path):
    root = write_repo(tmp_path)
    (root / "tree" / "CONTRACT.md").write_text(CONTRACT_MANIFEST.replace("shared-contracts", "Shared Things"))
    only(root, "installs as 'shared-things', but every `contract:` ref names 'shared-contracts'")


def test_a_title_cased_manifest_name_slugifies_to_the_contract_asset(tmp_path):
    root = write_repo(tmp_path)
    (root / "tree" / "CONTRACT.md").write_text(CONTRACT_MANIFEST.replace("shared-contracts", "Shared Contracts"))
    assert errors(root) == []


def test_a_second_manifest_anywhere(tmp_path):
    """Verification 4: the installer ships the whole directory of every `CONTRACT.md` it finds,
    so a second one would ship a competing instruction layer."""
    root = write_repo(tmp_path)
    (root / "skills" / "spec-feature" / "CONTRACT.md").write_text(CONTRACT_MANIFEST)
    only(root, "is a second `CONTRACT.md`")
    assert "only-one-contract-manifest" in errors(root)[0]


def test_the_manifest_is_not_a_node(tmp_path):
    root = write_repo(tmp_path)
    assert "CONTRACT.md" not in {n.rel for n in check.load_tree(root)}


# -- the tree: node frontmatter and location (T2) ---------------------------------

def raw_node(root: Path, rel: str, text: str) -> None:
    p = root / "tree" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    refresh_fence(root)


def test_node_without_frontmatter(tmp_path):
    root = write_repo(tmp_path)
    raw_node(root, "extra.md", "# a plain markdown file\n")
    only(root, "has no parseable YAML frontmatter")
    assert "node-frontmatter" in errors(root)[0]


def test_node_path_that_is_neither_a_string_nor_a_list(tmp_path):
    root = write_repo(tmp_path)
    raw_node(root, "extra.md", "---\npath: 3\nsummary: x\nwriters: []\n---\n")
    only(root, "`path:` must be a string or a non-empty list of strings")


def test_node_path_entry_outside_the_concept(tmp_path):
    root = write_repo(tmp_path)
    write_node(root, "extra.md", "other/extra.yaml")
    only(root, "does not start with '_concept/'")


def test_node_path_entry_outside_the_nodes_directory(tmp_path):
    root = write_repo(tmp_path)
    add_node(root, "01_meta/extra.md", ["_concept/01_meta/extra.yaml", "_concept/03_brand/extra.yaml"])
    only(root, "is not under the node's directory '_concept/01_meta/'")


def test_readme_whose_first_entry_is_not_its_directory(tmp_path):
    root = write_repo(tmp_path)
    edit_node(root, "01_meta/README.md", 'path: ["_concept/01_meta/"]', 'path: ["_concept/01_meta/other/"]')
    only(root, "a README's first `path:` entry is its directory '_concept/01_meta/'")


def test_the_root_readme_documents_the_artifact_root(tmp_path):
    root = write_repo(tmp_path)
    edit_node(root, "README.md", 'path: ["_concept/", "_concept/README.md"]', 'path: ["_concept/README.md"]')
    only(root, "a README's first `path:` entry is its directory '_concept/'")


def test_node_in_the_wrong_place(tmp_path):
    """The location rule is the fallback of resolution, so a node must sit where it says."""
    root = write_repo(tmp_path)
    add_node(root, "misplaced.md", "_concept/extra.yaml")
    only(root, "belongs in tree/extra.md, not tree/misplaced.md")
    assert "node-location" in errors(root)[0]


def test_node_without_a_summary(tmp_path):
    root = write_repo(tmp_path)
    raw_node(root, "extra.md", '---\npath: "_concept/extra.yaml"\nwriters: []\n---\n')
    only(root, "has no `summary:`")


def test_node_summary_over_80_characters(tmp_path):
    root = write_repo(tmp_path)
    edit_node(root, "brief.md", "summary: the pitch", "summary: " + "x" * 81)
    only(root, "`summary:` is 81 characters, over the 80-character limit")


def test_node_summary_of_exactly_80_characters_is_legal(tmp_path):
    root = write_repo(tmp_path)
    edit_node(root, "brief.md", "summary: the pitch", "summary: " + "x" * 80)
    assert errors(root) == []


def test_node_without_a_writers_list(tmp_path):
    root = write_repo(tmp_path)
    raw_node(root, "extra.md", '---\npath: "_concept/extra.yaml"\nsummary: x\n---\n')
    only(root, "has no `writers:` list")


# -- the tree: names (T3) --------------------------------------------------------

def test_node_name_must_be_lowercase(tmp_path):
    root = write_repo(tmp_path)
    add_node(root, "Bad_Name.md", "_concept/Bad_Name.yaml")
    only(root, "'Bad_Name.md' is not lowercase or a `[placeholder]`")
    assert "node-name" in errors(root)[0]


def test_directory_without_a_readme(tmp_path):
    root = write_repo(tmp_path)
    add_node(root, "04_journeys/stories.md", "_concept/04_journeys/stories.yaml")
    only(root, "has no `README.md`")
    assert "dir-has-readme" in errors(root)[0]


def test_placeholder_directory_without_a_readme(tmp_path):
    """`[feature_slug]/` is a directory like any other: it needs a node of its own."""
    root = write_repo(tmp_path)
    (root / "tree" / "07_screens" / "[feature_slug]" / "README.md").unlink()
    refresh_fence(root)
    only(root, "has no `README.md`")
    assert "dir-has-readme" in errors(root)[0]
    assert "tree/07_screens/[feature_slug]/" in errors(root)[0]


# -- the tree: the generated listing (T5) ------------------------------------------

def normalised(lines) -> list[str]:
    return [" ".join(line.split()) for line in lines if line.strip()]


def test_render_tree_of_the_fixture(tmp_path):
    """Files before directories, placeholders last, a summary after each name, a directory
    described by the summary of its own README."""
    root = write_repo(tmp_path)
    assert normalised(check.render_tree(check.load_tree(root))) == [
        "_concept/ the artifact tree",
        "├── README.md the artifact tree",
        "├── brief.md the pitch",
        "├── 01_meta/ project settings",
        "│ └── scope.yaml flow and project type",
        "└── 07_screens/ the app shell and one spec per screen",
        "├── shell.md the app shell",
        "└── <feature_slug>/ screens of one feature",
        "└── <screen>.md one spec per screen",
    ]


def test_stale_listing(tmp_path):
    """Verification 4: a node changes and the pasted fence does not follow."""
    root = write_repo(tmp_path)
    edit_node(root, "brief.md", "summary: the pitch", "summary: the elevator pitch", refresh=False)
    only(root, "its fenced tree differs from `--print-tree`")
    assert "tree-readme-stale" in errors(root)[0]


def test_listing_that_misses_a_new_node(tmp_path):
    root = write_repo(tmp_path)
    write_node(root, "extra.md", "_concept/extra.yaml")
    only(root, "its fenced tree differs from `--print-tree`")


def test_listing_that_is_only_re_spaced_is_current(tmp_path):
    root = write_repo(tmp_path)
    readme = root / "tree" / "README.md"
    fence = check._first_fence(readme.read_text())
    respaced = "\n".join(line.replace("  ", "     ") + "   " for line in fence) + "\n\n"
    readme.write_text(readme.read_text().replace("\n".join(fence), respaced.rstrip("\n"), 1))
    assert errors(root) == []


def test_readme_without_a_fence(tmp_path):
    root = write_repo(tmp_path)
    readme = root / "tree" / "README.md"
    readme.write_text(re.sub(r"(?s)```\n.*?\n```\n", "", readme.read_text(), count=1))
    only(root, "has no fenced block")


def test_tree_without_a_readme(tmp_path):
    """No entry point: the listing is gone, and every skill's first route line cites a file that is not."""
    root = write_repo(tmp_path)
    (root / "tree" / "README.md").unlink()
    among(
        root,
        "does not exist — the tree has no entry point and no listing",
        "cites `tree/README.md`, which does not exist",
    )


def test_print_tree_prints_the_generated_listing(tmp_path, monkeypatch, capsys):
    root = write_repo(tmp_path)
    monkeypatch.setattr(sys, "argv", ["check.py", "--repo", str(root), "--print-tree"])
    assert check.main() == 0
    out = capsys.readouterr().out
    assert out.splitlines() == check.render_tree(check.load_tree(root))
    assert out.startswith("_concept/")


def test_main_exit_code_follows_the_report(tmp_path, monkeypatch, capsys):
    root = write_repo(tmp_path)
    monkeypatch.setattr(sys, "argv", ["check.py", "--repo", str(root), "--no-tests"])
    assert check.main() == 0
    assert "0 error(s)" in capsys.readouterr().out
    (root / "tree" / "CONTRACT.md").unlink()
    assert check.main() == 1


# -- the tree: siblings (T7) ---------------------------------------------------------

def test_siblings_that_differ_only_by_plural(tmp_path):
    root = write_repo(tmp_path)
    add_node(root, "review.md", "_concept/review.yaml")
    add_node(root, "reviews/README.md", ["_concept/reviews/"])
    only(root, "`_concept/` declares `review` and `reviews`, which differ only by plural")
    assert "tree-sibling-singular-plural" in errors(root)[0]


def test_a_nested_plural_pair_is_found_too(tmp_path):
    root = write_repo(tmp_path)
    add_node(root, "01_meta/flow.md", "_concept/01_meta/flow.yaml")
    add_node(root, "01_meta/flows/README.md", ["_concept/01_meta/flows/"])
    only(root, "`_concept/01_meta/` declares `flow` and `flows`")


# -- resolution (R1), without the filesystem -----------------------------------------

def nodes_of(*specs) -> list:
    return [check.Node(rel, {"path": path, "summary": "s", "writers": []}) for rel, path in specs]


def test_node_remembers_whether_its_path_was_a_list():
    string_form, list_form = nodes_of(("a/README.md", "_concept/a/"), ("b/README.md", ["_concept/b/"]))
    assert (string_form.is_list, string_form.entries) == (False, ["_concept/a/"])
    assert (list_form.is_list, list_form.entries) == (True, ["_concept/b/"])


def test_resolve_literal_match():
    nodes = nodes_of(("brief.md", "_concept/brief.md"))
    assert check.resolve(nodes, "_concept/brief.md") is nodes[0]
    assert check.resolve(nodes, "_concept/pitch.md") is None


def test_resolve_placeholder_on_either_side():
    nodes = nodes_of(("07_screens/[feature_slug]/[screen].md", "_concept/07_screens/<feature_slug>/<screen>.md"))
    assert check.resolve(nodes, "_concept/07_screens/checkout/pay.md") is nodes[0]
    assert check.resolve(nodes, "_concept/07_screens/<a>/<b>.md") is nodes[0]
    assert check.resolve(nodes, "_concept/07_screens/checkout/pay.md/extra") is None


def test_resolve_prefers_the_literal_entry_over_the_placeholder_one():
    nodes = nodes_of(("05/[a].md", "_concept/05/<a>.md"), ("05/index.md", "_concept/05/index.md"))
    assert check.resolve(nodes, "_concept/05/index.md") is nodes[1]
    assert check.resolve(nodes, "_concept/05/other.md") is nodes[0]


def test_resolve_ignores_a_trailing_slash():
    nodes = nodes_of(("07_screens/README.md", ["_concept/07_screens/"]))
    assert check.resolve(nodes, "_concept/07_screens") is nodes[0]
    assert check.resolve(nodes, "_concept/07_screens/") is nodes[0]


def test_resolve_by_location_rule_is_for_directories():
    """A directory resolves to the README that sits where the rule puts it, whatever its `path:`
    says; `X` and `X/` alike, and a placeholder segment becomes `[x]`."""
    nodes = nodes_of(
        ("a/b.md", "_concept/a/c.yaml"),
        ("a/README.md", "_concept/a/other.yaml"),
        ("a/[x]/README.md", "_concept/a/<x>/d.yaml"),
    )
    assert check.resolve(nodes, "_concept/a") is nodes[1]  # a directory named without its slash
    assert check.resolve(nodes, "_concept/a/") is nodes[1]
    assert check.resolve(nodes, "_concept/a/<x>/") is nodes[2]
    assert check.resolve(nodes, "_concept/a/zzz") is None  # no `a/zzz/README.md`
    assert check.resolve(nodes, "_concept/a/c.yaml") is nodes[0]  # a file resolves through its `path:`


def test_resolve_does_not_match_a_file_by_location():
    """The location rule is extension-blind (`scope.yaml` and `scope.json` are both `scope.md`),
    so a file path resolves only through a `path:` entry that names it."""
    nodes = nodes_of(
        ("01_meta/scope.md", "_concept/01_meta/scope.yaml"),
        ("11_build/trace.md", "_concept/11_build/trace.yaml"),
        ("brief.md", "_concept/brief.md"),
    )
    assert check.resolve(nodes, "_concept/01_meta/scope.yaml") is nodes[0]
    assert check.resolve(nodes, "_concept/11_build/trace.yaml") is nodes[1]
    assert check.resolve(nodes, "_concept/brief.md") is nodes[2]
    for wrong in ("_concept/01_meta/scope.json", "_concept/11_build/trace.json", "_concept/brief"):
        assert check.resolve(nodes, wrong) is None, wrong


def test_only_a_list_form_directory_entry_covers_what_lies_below():
    covering = nodes_of(("09/README.md", ["_concept/09/"]))
    plain = nodes_of(("09/README.md", "_concept/09/"))
    assert check.resolve(covering, "_concept/09/deep/x.json") is covering[0]
    assert check.resolve(plain, "_concept/09/deep/x.json") is None


def test_the_deepest_covering_entry_wins():
    nodes = nodes_of(("09/README.md", ["_concept/09/"]), ("09/w/README.md", ["_concept/09/w/"]))
    assert check.resolve(nodes, "_concept/09/w/deep/x.json") is nodes[1]
    assert check.resolve(nodes, "_concept/09/other.json") is nodes[0]


def test_the_artifact_root_covers_nothing_but_itself():
    nodes = nodes_of(("README.md", ["_concept/", "_concept/README.md"]))
    assert check.resolve(nodes, "_concept/") is nodes[0]
    assert check.resolve(nodes, "_concept/README.md") is nodes[0]
    assert check.resolve(nodes, "_concept/typo.md") is None


# -- no path into the retired contracts folder (T8) -----------------------------

def append(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(text)


OLD_PATH = "See `contracts/elements_block.md` for the schema.\n"


def test_a_skill_body_naming_a_retired_contract_file(tmp_path):
    """Verification 4: `contracts/<name>.md` anywhere a reader looks is a stale instruction."""
    root = write_repo(tmp_path)
    body(root, "spec-feature", "See `contracts/elements_block.md`.")
    only(root, "names `contracts/elements_block.md`")
    assert "skills/spec-feature" in errors(root)[0]
    assert "no-old-contract-path" in errors(root)[0]


@pytest.mark.parametrize(
    "rel", ["tree/brief.md", "templates/web/TEMPLATE.md", "docs/guide.md", "README.md", "CLAUDE.md"]
)
def test_a_retired_contract_path_is_found_in_every_asset_kind(tmp_path, rel):
    root = write_repo(tmp_path)
    append(root, rel, OLD_PATH)
    only(root, "names `contracts/elements_block.md`")
    assert rel in errors(root)[0]


def test_a_relative_retired_contract_path_is_found_too(tmp_path):
    root = write_repo(tmp_path)
    append(root, "docs/guide.md", "Read `../contracts/seed_data.md`.\n")
    only(root, "names `../contracts/seed_data.md`")


def test_the_installed_path_of_the_tree_is_not_a_retired_contract_path(tmp_path):
    """`.claude/contracts/shared-contracts/<p>` is where the tree installs; it is not `contracts/<name>.md`."""
    root = write_repo(tmp_path)
    append(root, "docs/guide.md", "Installed at `.claude/contracts/shared-contracts/brief.md`.\n")
    assert errors(root) == []


def test_a_retired_contract_path_in_a_skill_script(tmp_path):
    root = write_repo(tmp_path)
    append(root, "skills/spec-feature/scripts/x.py", "# see contracts/elements_block.md\n")
    only(root, "names `contracts/elements_block.md`")


# -- flows: requires --------------------------------------------------------

def test_requires_missing_a_skill_a_node_runs(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["requires"] = ["contract:@skaile-ai/shared-contracts"]
    write_flow(root, flow)
    only(root, "does not list it in `requires:`")


def test_requires_listing_a_skill_no_node_runs(tmp_path):
    root = write_repo(tmp_path, skills=("spec-feature", "build-plan"))
    flow = good_flow()
    flow["requires"].append("skill:@skaile-ai/build-plan")
    write_flow(root, flow)
    only(root, "which no node in this flow runs")


def test_requires_names_a_per_file_contract(tmp_path):
    """The instruction tree is one asset, so a per-file ref names nothing —
    `_` is not a legal asset-name character, so it could never have resolved."""
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["requires"].append("contract:@skaile-ai/seed_data")
    write_flow(root, flow)
    only(root, "the only contract asset is 'shared-contracts'")


def test_requires_omits_the_contract_its_skills_read(tmp_path):
    """What a flow owes is the one asset, present iff any of its own node skills cites the tree."""
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["requires"] = ["skill:@skaile-ai/spec-feature"]
    write_flow(root, flow)
    only(root, "does not list `contract:@skaile-ai/shared-contracts`")


def test_requires_lists_the_contract_no_skill_reads(tmp_path):
    root = write_repo(tmp_path)
    set_produces(root, "    produces: []\n")
    strip_citations(root)
    undeclare(root)
    write_flow(root, good_flow())
    only(root, "which none of this flow's skills read")


def test_requires_ref_grammar(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["requires"] = ["spec-feature"]
    write_flow(root, flow)
    errs = errors(root)
    assert any("is not a `kind:@publisher/name` ref" in e for e in errs), errs


# -- prose: docs/ and the root ----------------------------------------------

def doc(root, rel: str, text: str) -> None:
    """Write a prose file at `rel`, creating its directory."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_dead_relative_link_in_docs(tmp_path):
    root = write_repo(tmp_path)
    doc(root, "docs/guide.md", "See [the template](skill-template.md).\n")
    only(root, "links to `skill-template.md`")


def test_dead_relative_link_at_the_root(tmp_path):
    root = write_repo(tmp_path)
    doc(root, "README.md", "Start from [the examples](docs/examples/WHY.md).\n")
    only(root, "links to `docs/examples/WHY.md`")


def test_live_relative_link_resolves(tmp_path):
    root = write_repo(tmp_path)
    doc(root, "docs/skill-template.md", "# template\n")
    doc(root, "docs/guide.md", "See [the template](skill-template.md).\n")
    assert errors(root) == []


def test_external_and_anchor_links_are_not_paths(tmp_path):
    root = write_repo(tmp_path)
    doc(root, "README.md", "[repo](https://example.com/x) · [above](#layout) · [self](README.md#layout)\n")
    assert errors(root) == []


def test_dead_skill_path_in_docs(tmp_path):
    root = write_repo(tmp_path)
    doc(root, "docs/examples/WHY.md", "The port landed at `skills/concept-brief/`.\n")
    only(root, "names the path `skills/concept-brief`")


def test_live_skill_path_resolves(tmp_path):
    root = write_repo(tmp_path)
    doc(root, "docs/examples/WHY.md", "The port landed at `skills/spec-feature/`.\n")
    assert errors(root) == []


def test_readme_skill_index_missing_a_skill(tmp_path):
    root = write_repo(tmp_path, skills=("spec-feature", "build-plan"))
    doc(root, "README.md", "## Skills\n\n| skill | does |\n|---|---|\n| [spec-feature](skills/spec-feature/) | specs |\n")
    only(root, "does not list `skills/build-plan` under `## Skills`")


def test_readme_without_a_skills_heading_is_not_an_index(tmp_path):
    root = write_repo(tmp_path, skills=("spec-feature", "build-plan"))
    doc(root, "README.md", "Start with [spec-feature](skills/spec-feature/).\n")
    assert errors(root) == []


FROZEN_ADR = (
    "Deletes `contracts/iron_laws.md`, see [it](gone.md) and `skills/ghost`; cites `tree/nothing.md`.\n"
)


def test_frozen_adrs_may_name_what_they_replaced(tmp_path):
    """ADRs 0001–0014 are carried over verbatim and record a layout that no longer exists; the gate
    reads the live documents, not the records."""
    root = write_repo(tmp_path)
    doc(root, "docs/adr/0004-contracts-earn-their-place.md", FROZEN_ADR)
    doc(root, "docs/adr/0014-the-glossary-is-a-root-file.md", FROZEN_ADR)
    assert errors(root) == []


def test_adr_0015_is_not_frozen(tmp_path):
    root = write_repo(tmp_path)
    doc(root, "docs/adr/0015-the-instruction-tree-mirrors-the-artifact-tree.md", FROZEN_ADR)
    errs = errors(root)
    assert len(errs) == 4, errs
    for fragment in ("links to `gone.md`", "names the path `skills/ghost`", "cites `tree/nothing.md`",
                     "no-old-contract-path"):
        assert any(fragment in e for e in errs), (fragment, errs)


def test_the_adr_index_is_not_frozen(tmp_path):
    root = write_repo(tmp_path)
    doc(root, "docs/adr/README.md", "See [the first](0001-gone.md).\n")
    only(root, "links to `0001-gone.md`")


# -- the host-facts table ---------------------------------------------------
#
# Ticket 41. The table only decouples anything if it is kept honest, and the thing that
# actually went wrong is ticket 34: five rules landed depending on host behaviour with
# **no owner**, and nothing forced them to declare it. So these gate the two directions
# that catch that — a citation resolving to nothing, and a fact nobody rests on — rather
# than only checking that the rows are well shaped.

FACT_ID_RE = re.compile(r"^host:[a-z][a-z0-9-]*$")


def check_py_ast() -> ast.Module:
    return ast.parse(Path(check.__file__).read_text())


def _docstring_nodes(tree: ast.Module) -> set[int]:
    """The id() of every docstring Constant, which does not count as a citation.

    Comments are invisible to the AST, which is most of why this is an AST scan — but
    docstrings are not comments, they are `ast.Constant` strings. Without this a fact id
    named only in a docstring would satisfy the orphan gate while no rule cited it,
    which is the hole in prose form rather than in code.
    """
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            first = node.body[0] if node.body else None
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                out.add(id(first.value))
    return out


def cited_fact_ids() -> set[str]:
    """Every fact id `check.py` cites in code, read from its AST."""
    tree = check_py_ast()
    docstrings = _docstring_nodes(tree)
    return {
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, str)
        and FACT_ID_RE.match(n.value)
        and id(n) not in docstrings
    }


def cited_pairs() -> set[tuple[str, str]]:
    """Every `(fact id, rule id)` pair `check.py` reports with.

    The dynamic site — `DEAD_NODE_DATA_FACTS`, whose two entries are chosen at runtime —
    is read from the constant itself rather than from the call, so the loop that hands
    `check.py` its ids is covered by the same reconciliation as the literal sites.
    """
    pairs: set[tuple[str, str]] = set()
    for node in ast.walk(check_py_ast()):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr != "error":
            continue
        fact_kw = next((k for k in node.keywords if k.arg == "fact"), None)
        rule_kw = next((k for k in node.keywords if k.arg == "rule"), None)
        if fact_kw is None:
            continue
        assert rule_kw is not None, "a fact cited with no rule id"
        if isinstance(fact_kw.value, ast.Constant):
            facts = [fact_kw.value.value]
        elif isinstance(fact_kw.value, ast.Tuple):
            facts = [e.value for e in fact_kw.value.elts]
        else:
            continue  # the dynamic site, covered below
        rule = rule_kw.value.value if isinstance(rule_kw.value, ast.Constant) else None
        if rule is None:
            continue
        pairs.update((f, rule) for f in facts)
    for fact_id, rule_id, _extra in check.DEAD_NODE_DATA_FACTS.values():
        pairs.add((fact_id, rule_id))
    return pairs


def test_every_cited_fact_resolves_to_a_row():
    dangling = sorted(cited_fact_ids() - set(host_facts.BY_ID))
    assert not dangling, f"cited in check.py, absent from host_facts.py: {dangling}"


def test_every_row_is_cited_by_a_rule():
    orphans = sorted(set(host_facts.BY_ID) - cited_fact_ids())
    assert not orphans, f"in host_facts.py, cited by no rule: {orphans}"


def test_every_declared_rule_is_used_by_a_site_citing_that_fact():
    """The `rules` column is reconciled, not just non-empty.

    Ticket 41's own failure mode, one field in: a rule id that lives only in the table
    is unfalsifiable bookkeeping, and `verify_host.py` prints those ids on every expiry.
    """
    pairs = cited_pairs()
    unused = sorted(
        f"{f.id} -> {rule}" for f in host_facts.FACTS for rule in f.rules if (f.id, rule) not in pairs
    )
    assert not unused, f"declared in host_facts.py, cited by no site: {unused}"


def test_every_cited_rule_is_declared_by_its_fact():
    undeclared = sorted(
        f"{fact_id} -> {rule}"
        for fact_id, rule in cited_pairs()
        if rule not in host_facts.fact(fact_id).rules
    )
    assert not undeclared, f"cited in check.py, absent from that row's `rules`: {undeclared}"


def test_a_fact_cited_without_a_rule_id_raises():
    rep = check.Report()
    with pytest.raises(ValueError):
        rep.error("somewhere", "broken", fact="host:profile-icon")


def test_a_rule_id_the_row_does_not_list_raises():
    rep = check.Report()
    with pytest.raises(KeyError):
        rep.error("somewhere", "broken", fact="host:profile-icon", rule="not-a-rule-of-that-fact")


def test_an_intrinsic_error_may_not_carry_a_rule_id():
    rep = check.Report()
    with pytest.raises(ValueError):
        rep.error("somewhere", "broken", rule="flow-icon")


def test_a_fact_id_named_only_in_a_docstring_does_not_count_as_a_citation():
    """The orphan gate must not be satisfiable by prose — see `_docstring_nodes`."""
    tree = ast.parse('def f():\n    """See host:profile-icon."""\n    return 1\n')
    docstrings = _docstring_nodes(tree)
    constants = [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert any(id(n) in docstrings for n in constants)


def test_an_unknown_fact_id_raises_rather_than_printing():
    rep = check.Report()
    with pytest.raises(KeyError):
        rep.error("somewhere", "broken", fact="host:no-such-fact", rule="whatever")


@pytest.mark.parametrize("f", host_facts.FACTS, ids=lambda f: f.id)
def test_fact_rows_are_well_formed(f):
    assert FACT_ID_RE.match(f.id), f.id
    assert f.host in host_facts.HOSTS, f.host
    assert f.expect in (host_facts.PRESENT, host_facts.ABSENT), f.expect
    assert f.signature.strip(), "a fact with no signature cannot be verified"
    assert f.claim.strip().endswith((".", ".)")), "the claim is prose, ending in a full stop"
    assert f.rules, "a fact resting under no rule is an orphan by construction"
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", f.verified), f.verified
    assert not f.path.startswith("/"), "paths are relative to the host checkout"


def test_fact_ids_are_unique():
    ids = [f.id for f in host_facts.FACTS]
    assert len(ids) == len(set(ids))


# -- the tiers --------------------------------------------------------------

def tiers(root: Path) -> dict[str, list[str]]:
    rep = check.run(root)
    return {t: [str(p) for p in rep.by_tier(t)] for t in check.TIERS}


def test_a_host_derived_failure_names_its_fact_and_interpolates_the_path(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["meta"]["icon"] = "mdi-rocket"
    write_flow(root, flow)
    grouped = tiers(root)
    assert grouped[check.INTRINSIC] == []
    assert len(grouped[check.HOST_DERIVED]) == 1
    msg = grouped[check.HOST_DERIVED][0]
    row = host_facts.fact("host:profile-icon")
    assert f"[{row.id}]" in msg
    assert row.path in msg, "the path comes from the table, never from the message"


def test_a_rule_resting_on_two_facts_names_both(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["edges"][0]["type"] = "parallel"
    write_flow(root, flow)
    msg = next(m for m in tiers(root)[check.HOST_DERIVED] if "orders nothing" in m)
    assert "[host:flow-edge-orders-run, host:flow-edge-gates-state]" in msg


def test_house_style_lands_in_its_own_tier(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["globals"]["verbosity"] = "loud"
    write_flow(root, flow)
    grouped = tiers(root)
    assert len(grouped[check.HOUSE_STYLE]) == 1
    assert "host:" not in grouped[check.HOUSE_STYLE][0], "a house rule owes nothing to a host"
    assert grouped[check.HOST_DERIVED] == []


def test_an_intrinsic_failure_carries_no_fact(tmp_path):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["nodes"].append({"id": "orphan", "type": "skill", "parentNode": "g_concept",
                          "data": {"skill": "spec-feature", "phase": "conceptualization"}})
    write_flow(root, flow)
    grouped = tiers(root)
    assert any("unreachable" in m for m in grouped[check.INTRINSIC])
    assert not any("unreachable" in m for m in grouped[check.HOST_DERIVED])


def test_the_summary_groups_by_tier_and_names_the_verifier(tmp_path, capsys):
    root = write_repo(tmp_path)
    flow = good_flow()
    flow["meta"]["icon"] = "mdi-rocket"
    flow["globals"]["verbosity"] = "loud"
    write_flow(root, flow)
    check.print_report(check.run(root))
    out = capsys.readouterr().out
    assert "host-derived" in out and "house style" in out
    assert "verify_host.py --fact host:profile-icon" in out
    assert "two readings" in out, "a host-derived failure is ambiguous until the verifier runs"


def test_a_clean_run_says_nothing_about_facts(tmp_path, capsys):
    root = write_repo(tmp_path)
    write_flow(root, good_flow())
    check.print_report(check.run(root))
    assert capsys.readouterr().out == ""


# -- verify_host ------------------------------------------------------------
#
# The verifier's own logic, without the real checkouts: `expect` is the half that is
# easy to get backwards, and an absent fact that silently starts passing is how a ban
# would go on being enforced after the host made it wrong.

def host_tree(root: Path, rel: str, text: str) -> Path:
    p = root / host_facts.HOSTS["forge-concept"] / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return root


def a_fact(**kw) -> host_facts.Fact:
    base = dict(
        id="host:probe", host="forge-concept", path="probe.ts", signature="const x = 1;",
        expect=host_facts.PRESENT, claim="A probe.", rules=("probe",), verified="2026-09-09",
    )
    return host_facts.Fact(**{**base, **kw})


def test_verifier_holds_when_a_present_signature_is_found(tmp_path):
    host_tree(tmp_path, "probe.ts", "const x = 1;\n")
    verdict, _detail, hits = verify_host.check_fact(a_fact(), tmp_path)
    assert verdict == verify_host.HOLDS
    assert hits == [1]


def test_verifier_expires_when_a_present_signature_moved(tmp_path):
    host_tree(tmp_path, "probe.ts", "const y = 2;\n")
    verdict, detail, _ = verify_host.check_fact(a_fact(), tmp_path)
    assert verdict == verify_host.EXPIRED
    assert "moved or died" in detail


def test_verifier_expires_when_an_absent_signature_appears(tmp_path):
    host_tree(tmp_path, "probe.ts", "const x = 1;\n")
    verdict, detail, _ = verify_host.check_fact(a_fact(expect=host_facts.ABSENT), tmp_path)
    assert verdict == verify_host.EXPIRED
    assert "now wrong" in detail, "a ban whose fact reappeared is the dangerous direction"


def test_verifier_holds_when_an_absent_signature_stays_absent(tmp_path):
    host_tree(tmp_path, "probe.ts", "const y = 2;\n")
    verdict, _detail, _ = verify_host.check_fact(a_fact(expect=host_facts.ABSENT), tmp_path)
    assert verdict == verify_host.HOLDS


def test_verifier_expires_when_the_host_file_is_gone(tmp_path):
    host_tree(tmp_path, "other.ts", "const x = 1;\n")
    verdict, detail, _ = verify_host.check_fact(a_fact(), tmp_path)
    assert verdict == verify_host.EXPIRED
    assert "no such file" in detail


# --- skills/ops-review/scripts/check_concept.py: the mechanical half of ops-review ---------

def load_check_concept():
    import importlib.util

    script = Path(__file__).resolve().parent.parent / "skills/ops-review/scripts/check_concept.py"
    spec = importlib.util.spec_from_file_location("check_concept", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, script


def concept_tree(root: Path) -> Path:
    """A minimal valid `_concept/`: one journey, one model, one feature, one screen, one ledger."""
    files = {
        "brief.md": "---\nelevator_pitch: p\naudience: a\nproblem: q\nhero_flow: h\nlast_updated: 2026-09-05\n---\n",
        "goals.md": "---\nsuccess_criteria: []\nkpis: []\nconstraints: []\nnon_goals: []\nlast_updated: 2026-09-05\n---\n",
        "glossary.md": "---\nlast_updated: 2026-09-05\napproved: 2026-09-05\n---\n",
        "04_journeys/stories.yaml": (
            "version: '1.0'\nlast_updated: 2026-09-05\njourneys:\n  - id: login\n    steps:\n"
            "      - action: sign in\n        acceptance:\n          - { id: AC-login-01, ears: 'WHEN x, THE SYSTEM SHALL y' }\n"
        ),
        "10_blueprint/datamodel/model.json": '{"models": [{"name": "User"}]}',
        "05_features/auth/login.md": (
            "---\npriority: must-have\npermissions: {member: [view]}\nscreens:\n  - path: 07_screens/login/login.md\n"
            "data_entities: [User]\nlast_updated: 2026-09-05\n---\n\n## Criteria\n\n- AC-login-01\n"
        ),
        "07_screens/login/login.md": (
            "---\nimplements:\n  - 05_features/auth/login.md\nlast_updated: 2026-09-05\n---\n"
        ),
        "11_build/acceptance-criteria/auth/login.ac.md": (
            "---\nfeature: login\nfeature_ref: _concept/05_features/auth/login.md\nlast_updated: 2026-09-05\n---\n\n"
            "# Criteria — Login\n\n"
            "- [PASS] AC-login-01 — tests/login.test.ts · build-implement · 4f2a9c1 · 2026-09-05\n"
        ),
    }
    concept = root / "_concept"
    for rel, text in files.items():
        path = concept / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return concept


def test_check_concept_passes_a_minimal_valid_tree(tmp_path):
    module, script = load_check_concept()
    assert module.check(concept_tree(tmp_path), script) == []


def test_check_concept_reports_one_broken_screens_link(tmp_path):
    module, script = load_check_concept()
    concept = concept_tree(tmp_path)
    feature = concept / "05_features/auth/login.md"
    feature.write_text(
        feature.read_text().replace(
            "  - path: 07_screens/login/login.md\n",
            "  - path: 07_screens/login/login.md\n  - path: 07_screens/login/missing.md\n",
        )
    )
    problems = module.check(concept, script)
    assert len(problems) == 1, problems
    assert "05_features/auth/login.md" in problems[0] and "07_screens/login/missing.md" in problems[0]


def test_check_concept_reports_the_retired_comparable_file_as_unowned(tmp_path):
    module, script = load_check_concept()
    concept = concept_tree(tmp_path)
    (concept / "comparable.md").write_text("---\nlast_updated: 2026-09-05\n---\n")
    problems = module.check(concept, script)
    assert len(problems) == 1, problems
    assert "comparable.md" in problems[0] and "unowned" in problems[0]


def test_check_concept_reads_the_real_trees_first_level_entries():
    """The fence in `tree/README.md` opens with ```text and carries a summary column; the parser
    must find it and take names only, or the script silently falls back to its built-in list."""
    module, script = load_check_concept()
    entries = module.root_entries(script)
    assert entries is not module.BUILTIN_ROOT
    assert {"README.md", "brief.md", "01_meta", "11_build"} <= set(entries)
    assert all(" " not in e and not e.endswith("/") for e in entries), entries


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
