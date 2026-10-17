# ai-assets-skaileup-tree

[![ci](https://github.com/skaile-ai/ai-assets-skaileup-tree/actions/workflows/ci.yml/badge.svg)](https://github.com/skaile-ai/ai-assets-skaileup-tree/actions/workflows/ci.yml)

The skaileup skill collection as a mirror tree. Same product domains, skills and flows as
[`ai-assets-skaileup-mp`](https://github.com/skaile-ai/ai-assets-skaileup-mp) — design,
spec, mockups, build, quality — with one shared vocabulary ([`CONTEXT.md`](./CONTEXT.md)) and
a flat tree. What changes is where the instructions live: `tree/` mirrors the `_concept/`
artifact tree one node per part, holding that part's purpose, format, procedure and checks,
and each `SKILL.md` is just the route of nodes it visits.

This repo is built **in parallel** with `-mp` and the original
[`ai-assets-skaileup`](https://github.com/skaile-ai/ai-assets-skaileup). Nothing is cut
over: projects opt in by pointing `skaile.yaml` at `-tree`.

## Layout

```
skills/<name>/SKILL.md     one directory per skill; the directory name IS the name: field
tree/                      mirror of _concept/, one node per part (APP-DESIGN.md's node, schemas beside nodes) — the contract asset
flows/<id>/<id>.flow.yaml  the graph over skills — order lives here, not in the filesystem
templates/                 tech-stack references an implementation skill reads
docs/                      skill and node templates, decision records
CONTEXT.md                 the collection's glossary — the words skills use with each other
```

No `NN_` prefixes anywhere, no domain folders: the domain is the first segment of the
skill's name (`concept-brief`, `mockup-walkthrough`, `build-implement`). The nine
domains are **concept · design · experience · spec · mockup · architecture · build ·
quality · ops**.

One skill carries no domain: [`skaileup`](./skills/skaileup/), the router. It is named for
the collection because it is the door into it rather than a step inside one domain — run it
when work arrives from outside a flow, or when a `_concept/` tree is opened cold and the
next skill is unclear.

## How a project moves through it

A **flow** is the unit a project is sized by: it names the skills and the order, so the
graph carries the sequence and no prose restates it. Four ship:

| Flow | For |
|---|---|
| [`appbuilder-mvp`](./flows/appbuilder-mvp/) | The lean end-to-end path — 9 skills, one featureset pass |
| [`appbuilder-standard`](./flows/appbuilder-standard/) | A multi-user app in full — 31 skills, discovery through review |
| [`skaileup-concept-only`](./flows/skaileup-concept-only/) | The conceptualization half alone, to hand a specified product on |
| [`skaileup-concept-reverse`](./flows/skaileup-concept-reverse/) | A concept built out of an existing repository |

A host picks the flow (in forge-concept the profile key *is* the flow id) and runs its
nodes; each writes into `_concept/`, the one artifact tree, whose instruction mirror is
[`tree/README.md`](./tree/README.md).

## Skills

| skill | does |
|---|---|
| [skaileup](skills/skaileup/) | Routes cold work or an unclear next step to the right skill |
| [concept-onboard](skills/concept-onboard/) | Captures what the user already knows: tech preferences, brand, material |
| [concept-scope](skills/concept-scope/) | Records the flow the project is sized by and its project type |
| [concept-brief](skills/concept-brief/) | Writes the pitch, goals and comparables everything downstream reads |
| [concept-glossary](skills/concept-glossary/) | Pins the product's words — terms, definitions, words to avoid — right after the brief |
| [concept-research](skills/concept-research/) | Grounds decisions in domain, competitor, audience and visual research |
| [concept-reverse](skills/concept-reverse/) | Extracts a concept from an existing repository |
| [design-brand](skills/design-brand/) | Discovers a visual direction and writes the project's brand |
| [experience-journeys](skills/experience-journeys/) | Defines personas and the staged story map features derive from |
| [experience-shell](skills/experience-shell/) | Specifies navigation, layout areas, breakpoints and shared screen patterns |
| [experience-behaviors](skills/experience-behaviors/) | Writes state machines and rules for entity lifecycles |
| [experience-interaction](skills/experience-interaction/) | Decides where information lives and how it is edited, saved and found, and writes APP-DESIGN.md |
| [spec-featuresets](skills/spec-featuresets/) | Derives the feature roster and cuts it into featuresets |
| [spec-feature](skills/spec-feature/) | Writes one feature's permanent spec and every screen it needs |
| [mockup-walkthrough](skills/mockup-walkthrough/) | Renders a clickable browser walkthrough, one page per screen and journey |
| [mockup-storybook](skills/mockup-storybook/) | Builds Storybook stories, screen compositions and journey walkthroughs |
| [mockup-annotate](skills/mockup-annotate/) | Injects the annotation overlay so stakeholders can comment on a walkthrough |
| [mockup-feedback](skills/mockup-feedback/) | Routes stakeholder annotations back into the concept as reviewable diffs |
| [architecture-techstack](skills/architecture-techstack/) | Chooses the technology stack and records its id |
| [architecture-system](skills/architecture-system/) | Records custom modules, protocols and integrations beyond the stack |
| [architecture-datamodel](skills/architecture-datamodel/) | Derives the stack-neutral data model and seed scenarios from feature specs |
| [build-branch](skills/build-branch/) | Opens the build branch before slices and merges or discards it after |
| [build-scaffold](skills/build-scaffold/) | Scaffolds, themes, wires auth and builds the shell of a running app |
| [build-database](skills/build-database/) | Translates the data model into a migrated schema with seed scripts |
| [build-plan](skills/build-plan/) | Cuts a frozen feature spec into vertical slices with slice dossiers |
| [build-implement](skills/build-implement/) | Implements a slice test-first, reviews it, commits and freezes it |
| [quality-standards](skills/quality-standards/) | Records an existing codebase's conventions as standards |
| [quality-test](skills/quality-test/) | Writes unit tests that trace back to feature specs |
| [quality-e2e](skills/quality-e2e/) | Proves journeys end to end in a real browser |
| [quality-review](skills/quality-review/) | Reviews a finished feature's code adversarially against its spec |
| [quality-release](skills/quality-release/) | Grades the running app against its brief on seven axes before release |
| [quality-interaction](skills/quality-interaction/) | Checks the code against APP-DESIGN.md and writes an interaction conformance verdict |
| [ops-review](skills/ops-review/) | Health-checks _concept/: cross-references and build/ship coverage |

## Writing a skill or a node

**R1 — the tree mirrors `_concept/`.** Every `_concept/` part has one node under `tree/`:
directory `X/` → `X/README.md`, file `X/name.ext` → `X/name.md`, placeholder `<x>` → `[x]`.
Instructions live in the node for the part they bind, never in a cross-cutting file.

- A **skill** is a route through nodes — start from
  [`docs/skill-template.md`](./docs/skill-template.md).
- A **node** is the instruction for one part — start from
  [`docs/node-template.md`](./docs/node-template.md).
- Why it is shaped this way: [ADR 0017](./docs/adr/0017-the-instruction-tree-mirrors-the-artifact-tree.md).

## Gate

There is **no documentation site**. Here the flows are the pipeline, `tree/` is the
instruction layer, `docs/adr/` holds why the collection is shaped as it is, and
`scripts/check.py` answers whether it still hangs together.

**Green means `python scripts/check.py`** — it checks the collection and then runs its own
fixtures, so one command is the whole gate. `python scripts/check.py --print-tree` prints the
artifact tree generated from the nodes. The badge above is the same answer for anyone who
did not run it.
