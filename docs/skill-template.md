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
    files:                           # `_concept/`-prefixed; `soft` unless the skill parses the file's format
      - { path: "_concept/<part>/...", gate: soft }
    inputs_optional:                 # the input dialog forge-concept renders
      - { id: <field>, label: "...", type: text }
---

# <name>

<≤ 3 lines: the job, and where it stops. The description carries the triggers, so state
the job and the boundary instead of restating them.>

## Route

Read `tree/protocol/running.md` once per session, then these nodes in order — each holds the format
and procedure for its part; this file holds only the order.

1. **<Verb phrase>** — `tree/03_brand/identity.md`. <≤ 1 line of skill-specific constraint,
   only if the node cannot carry it.>
2. **<Verb phrase>** — `tree/10_blueprint/datamodel/README.md § Naming` (add `§ <heading>`
   when the node serves several skills).

**Done when** <a condition the agent can check, ideally one a command checks for it>.
```

**Ceiling 60 lines including frontmatter.** A skill that does not fit is a missing node or a
procedure that belongs in one.

**`produces: []` skills** (`build-branch`, `build-scaffold`, `build-database`,
`quality-test`, `ops-review`) write nothing under `_concept/` but, at most, their own proposal
file (`quality-test` declares that one entry), so no node holds their procedure. They carry
`## Steps` in place of `## Route` — the compressed procedure, stated positively at the step each
constraint binds — with a **ceiling of 100 lines**. They still cite a node for every `_concept/`
format they read.

**The opener cites only the protocol files the route uses** (`tree/README.md § Protocol`):
`tree/protocol/running.md` always, narrowed to the rules it binds where the skill does not
interview (`(the todo list, rules 1 and 8)`); `tree/protocol/ownership.md` when it writes a
proposal file (`tree/proposals/README.md`) or settles proposals targeting its own artifacts; `tree/protocol/delegation.md`
when it hands passes to another agent context. `tree/README.md` itself is read only to find a
part's node.

## The rules behind it

- **`metadata:` is where the readers look.** `resolver/src/parser.ts:45-46` reads
  `fm.metadata.prerequisites` with no root-level fallback, and
  `discovery/src/requires-graph.ts:236-238` returns early on a missing `metadata`. A block at
  the root parses, renders no error, and reports `satisfied: true` on an unmet gate.
  `name`, `description` and `version` stay at the root: those readers normalise both.
- **A declared path is joined to the *project* root** (`resolver/src/validator.ts:81`), not to
  `_concept/`, so every concept path carries the prefix. `scripts/check.py` enforces both
  halves: a path either starts with `_concept/` and resolves to a node, or is a named
  project-root artifact in `PROJECT_ROOT_ARTIFACTS`.
- **A skill declares what it writes** (ADR 0013). `metadata.artifacts.produces` is a list of
  `{ id, path }`, mandatory on every skill: `id` is the kebab-case artifact id other skills
  name in `artifacts.requires` (every required id must be produced by some skill), and
  `path` starts with `_concept/` and resolves to a node that lists the skill under `owner`.
  A skill that writes nothing under `_concept/` says `produces: []`. The only paths allowed
  outside `_concept/` are the named project-root artifacts `APP-DESIGN.md`
  ([ADR 0015](./adr/0015-interaction-decisions-live-in-app-design.md)),
  `docs/adr/<NNNN>-<slug>.md` ([ADR 0032](./adr/0032-one-decision-log-under-docs-adr.md)) and
  `docs/agents/domain.md` ([ADR 0035](./adr/0035-skaileup-writes-a-guidance-section-for-upstream-skills.md)),
  the `PROJECT_ROOT_ARTIFACTS` set in `scripts/check.py`, whose nodes are `tree/APP-DESIGN.md`,
  `tree/docs/adr/README.md` and `tree/docs/agents/domain.md`.
  `scripts/check.py` enforces it in both directions; the host's node done-state read is
  `host:node-done-from-produces`: a node is done when every non-templated path in the list
  exists.
- **A proposer produces its proposal file.** Every skill listed in some node's `may_propose`
  declares `{ id: proposals, path: "_concept/proposals/<date>-<skill>-<scope>.yaml" }`, and only
  those skills produce under `_concept/proposals/` (`scripts/check.py` rule
  `proposer-produces-proposals`).
- **A skill that cites the tree declares the contract** (`contract:@skaile-ai/shared-contracts`
  under `metadata.requires`), and a skill that declares it cites the tree.
- **Frontmatter differs from `-mp` only where the tree requires it.** A skill whose body
  cites `tree/` declares `contract:@skaile-ai/shared-contracts` under `metadata.requires`
  (`scripts/check.py` rule `skill-declares-contract`, host fact `host:doctor-walks-requires`);
  that is the one permitted change, and it is why `build-branch`, `build-scaffold` and
  `quality-standards` gained it. `skaileup` also lists `_concept/README.md` in
  `produces`.
- **Every route item cites a node** by its repo-relative path under `tree/`, optionally
  followed by ` § ` and a `##`/`###` heading of that node — one citation per line, as in the
  example above; `scripts/check.py` resolves both the file and the heading.
- **`hard` is for a machine-read format the skill can neither derive nor ask for** — the
  data model `model.yaml` for `build-database`, `APP-DESIGN.md` for `quality-interaction`
  ([ADR 0019](./adr/0019-scoped-fact-resolution.md)). Every other input is `soft`, and the
  route step that reads it is a derive-or-ask step, so a missing input is never a stop.
  `scripts/check.py` rule `hard-gate-has-producer` fails a hard gate that no skill produces
  and that is not a project-root prerequisite.
- **An input is declared once per field.** `metadata.prerequisites.files` holds the paths and
  `metadata.artifacts.requires` the ids, and hosts read both; each names an input once, and
  `requires` lists only artifacts the route reads. No id there contradicts a `soft` gate.
- **A `soft` gate renders nowhere** — it is excluded from `satisfied` and never warned on. If
  its absence changes what the skill does, the step says so; the frontmatter alone tells the
  human nothing.
- **No flow-order prose.** A skill does not say "runs after X" or "hands over to Y": order
  lives in the flow graph, and next steps are named by demand — the skills that own what is
  still missing (`tree/protocol/running.md § How a skill runs`, rule 8).
- **An interviewing route item is a derive-or-ask step**: read what exists → derive the rest
  from `_concept/02_grounding/findings/` (scoped `concept-reverse` when the code holds it) →
  batch-ask what neither settles; it cites `tree/protocol/running.md § How a skill runs` and does not
  restate the rules.
- **The environment and the tree are sources of truth; the body is not a cache of them.** No
  READS/WRITES path list (the frontmatter and the nodes have it), no CHECKLIST (the node's
  `## Checks` has it), no Context Budget table.
- **Constraints are stated positively, at the step they bind.** No `MUST`/`NEVER` block.
- **Calling a skill the collection does not ship.** The allowed names are `EXTERNAL_SKILLS` in
  `scripts/check.py`, each on one of three axes taken from the upstream frontmatter, and each
  phrased one way:
  - **`model`** — the model calls it: `Call the Skill tool with "<name>"`; two skills are
    `call the Skill tool twice, for "<a>" and "<b>"` (one skill per call, never "with a and b").
  - **`user`** — only the human runs it: an instruction to the human, `tell the user to run
    `/<name>``, never a Skill-tool call.
  - **`user-followed`** — upstream marks it `disable-model-invocation: true`, so the Skill tool
    cannot call it, yet the agent runs it: ``Read the installed `<name>` skill and follow it``,
    optionally followed by `, with <inputs>`. "Installed" means the harness's skill directory
    (`.agents/skills/<name>/SKILL.md` or `.claude/skills/<name>/SKILL.md`); the route names no
    path. These are `setup-matt-pocock-skills`, `to-tickets` and `implement-spec`. A Skill-tool
    call to one is an error, and so is the phrase for a `model` skill.

  Every external skill a skill uses is declared in its `metadata.requires` as
  `skill:@mattpocock/<name>#0.1.0`, an exact store version because skaile resolves no caret
  range in `requires`, and every one declared is used (`scripts/check.py` rule
  `external-skill-declared`). A hard dependency says in the same step what happens when the
  skill is absent.
- **`## Depth Behavior`, `## Standalone Mode`, `## Context Budget`** describe how the
  collection works, not what the skill does. They belong in one place, once —
  `tree/protocol/running.md § How a skill runs` — not in thirty skills each.
