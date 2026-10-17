# The skill template — a skill is a route

A skill holds frontmatter and the ordered list of nodes it visits. Format, procedure and
checks for each `_concept/` part live in that part's node (see
[`node-template.md`](./node-template.md)); the skill holds only the order and what is
specific to this skill's use of the node. [ADR 0017](./adr/0017-the-instruction-tree-mirrors-the-artifact-tree.md)
has the reasoning.

```markdown
---
name: <kebab-case; this is the skill's whole identity — install path, flow data.skill,
       produced_by, grounding path>
description: "Use when <trigger>, or when the user says '<phrase>'."
version: "0.1.0"
metadata:                            # everything a machine reads sits under this key —
  requires:                          # `parseSkillRequirements` and `extractSkillRequires`
    - contract:@skaile-ai/shared-contracts   # both read `metadata.` and never fall back to the root
  artifacts:
    requires:
      - { id: <artifact> }           # id only; no code has ever read a `gate:` here
    produces:                        # what this skill writes, mandatory; `[]` writes nothing
      - { id: <artifact>, path: "_concept/<part>/..." }   # resolves to a node
  prerequisites:
    files:                           # the live gate: `_concept/`-prefixed, `hard` or `soft`
      - { path: "_concept/<part>/...", gate: hard, min_entries: 1 }
    inputs_optional:                 # the input dialog forge-concept renders
      - { id: <field>, label: "...", type: text }
---

# <name>

<≤ 3 lines: the job, and where it stops. The description carries the triggers, so state
the job and the boundary instead of restating them.>

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format
and procedure for its part; this file holds only the order.

1. **<Verb phrase>** — `tree/03_brand/identity.md`. <≤ 1 line of skill-specific constraint,
   only if the node cannot carry it.>
2. **<Verb phrase>** — `tree/10_blueprint/datamodel/README.md § Naming` (add `§ <heading>`
   when the node serves several skills).

**Done when** <a condition the agent can check, ideally one a command checks for it>.
```

**Ceiling 60 lines including frontmatter.** A skill that does not fit is a missing node or a
procedure that belongs in one.

**`produces: []` skills** (`skaileup`, `build-branch`, `build-scaffold`, `build-database`,
`quality-test`, `ops-review`) write nothing under `_concept/`, so no node holds their
procedure. They carry `## Steps` in place of `## Route` — the compressed procedure, stated
positively at the step each constraint binds — with a **ceiling of 100 lines**. They still
cite a node for every `_concept/` format they read.

## The rules behind it

- **`metadata:` is where the readers look.** `resolver/src/parser.ts:45-46` reads
  `fm.metadata.prerequisites` with no root-level fallback, and
  `discovery/src/requires-graph.ts:236-238` returns early on a missing `metadata`. A block at
  the root parses, renders no error, and reports `satisfied: true` on an unmet gate.
  `name`, `description` and `version` stay at the root: those readers normalise both.
- **A declared path is joined to the *project* root** (`resolver/src/validator.ts:81`), not to
  `_concept/`, so every concept path carries the prefix. `scripts/check.py` enforces both
  halves: a path either starts with `_concept/` and resolves to a node, or is one of the named
  project-root gates in `PROJECT_ROOT_PREREQUISITES`.
- **A skill declares what it writes** (ADR 0013). `metadata.artifacts.produces` is a list of
  `{ id, path }`, mandatory on every skill: `id` is the kebab-case artifact id other skills
  name in `artifacts.requires` (every required id must be produced by some skill), and
  `path` starts with `_concept/` and resolves to a node that lists the skill under `writers`.
  A skill that writes nothing under `_concept/` says `produces: []`. The only path allowed
  outside `_concept/` is the named project-root artifact `APP-DESIGN.md`
  ([ADR 0015](./adr/0015-interaction-decisions-live-in-app-design.md), the
  `PROJECT_ROOT_ARTIFACTS` set in `scripts/check.py`), whose node is `tree/APP-DESIGN.md`.
  `scripts/check.py` enforces it in both directions; the host's node done-state read is
  `host:node-done-from-produces`: a node is done when every non-templated path in the list
  exists.
- **A skill that cites the tree declares the contract** (`contract:@skaile-ai/shared-contracts`
  under `metadata.requires`), and a skill that declares it cites the tree.
- **Frontmatter differs from `-mp` only where the tree requires it.** A skill whose body
  cites `tree/` declares `contract:@skaile-ai/shared-contracts` under `metadata.requires`
  (`scripts/check.py` rule `skill-declares-contract`, host fact `host:doctor-walks-requires`);
  that is the one permitted change, and it is why `build-branch`, `build-scaffold` and
  `quality-standards` gained it. `concept-scope` also gains `_concept/README.md` in
  `produces`.
- **Every route item cites a node** by its repo-relative path under `tree/`, optionally
  followed by ` § ` and a `##`/`###` heading of that node — one citation per line, as in the
  example above; `scripts/check.py` resolves both the file and the heading.
- **A `soft` gate renders nowhere** — it is excluded from `satisfied` and never warned on. If
  its absence changes what the skill does, the step says so; the frontmatter alone tells the
  human nothing.
- **The environment and the tree are sources of truth; the body is not a cache of them.** No
  READS/WRITES path list (the frontmatter and the nodes have it), no CHECKLIST (the node's
  `## Checks` has it), no Context Budget table.
- **Constraints are stated positively, at the step they bind.** No `MUST`/`NEVER` block.
- **Calling a skill the collection does not ship.** An operative call reads
  `Call the Skill tool with "<name>"`; two skills are
  `call the Skill tool twice, for "<a>" and "<b>"` (one skill per call, never "with a and
  b"); a user-invoked skill is an instruction to the human (`tell the user to run
  `/<name>``) and never a Skill-tool call; the allowed names are `EXTERNAL_SKILLS` in
  `scripts/check.py`; a hard dependency says in the same step what happens when the skill
  is absent.
- **`## Depth Behavior`, `## Standalone Mode`, `## Context Budget`** describe how the
  collection works, not what the skill does. They belong in one place, once —
  `tree/README.md § How a skill runs` — not in thirty skills each.
