---
path: [_concept/, _concept/README.md]
summary: the artifact tree and how to read it
owner: [skaileup]
may_propose: []
---

# _concept/

`_concept/` is the one directory every skill reads and writes inside the target project; the host fixes the name, and there is no sibling `_implementation/` (the build half is `11_build/`). This directory mirrors it one node per part, and a path with no node here is a path no reader will find.

## The rule

Before reading or writing anything under `_concept/<p>`, read the node at the same path `<p>` in this directory (installed at `<contracts>/shared-contracts/<p>`, where `<contracts>` is the harness's contract directory: `.agents/contracts` for omp, Codex, pi and dsh, `.claude/contracts` for Claude Code): the folder's `README.md`, then the file's node. If the exact node is missing, the nearest `README.md` up the path applies.

| `_concept/` thing | node |
|---|---|
| directory `X/` | `X/README.md` here (also the node of `X/README.md` when that artifact exists) |
| file `X/name.ext` | `X/name.md` here (extension always `.md`: `stories.yaml` → `stories.md`) |
| placeholder segment `<x>` | `[x]` in the node path: `05_features/[featureset]/[feature].md` |
| siblings sharing a stem, or children a directory README covers | one node whose `path:` is a list |

A node's `path:` entries are matched first, `<x>` matching any one segment; the location column applies next, for directories only (a file resolves through its node's `path:` entry); a path below a directory entry of a list-form `path:` resolves to that README.

## The tree

```text
_concept/                             the artifact tree and how to read it
├── README.md                         the artifact tree and how to read it
├── brief.md                          the pitch, with its comparables — what the user said, no more
├── glossary.md                       the ubiquitous language and its light ontology — terms, kinds, relations
├── goals.md                          success criteria, KPIs, constraints and explicit non-goals
├── 01_meta/                          project metadata — the user's expectations and the project's sizing
│   ├── expectations.md               what the user judges the result by and how they want to work with the agents
│   ├── scope.yaml                    flow, project type and depth — written when the first skill needs one
│   └── walkthrough.yaml              the four concept stages and the user's yes on each — what the build waits for
├── 02_grounding/                     everything that came from outside the room, readable by every skill
│   ├── findings/                     graded evidence and raw material from outside the room
│   │   ├── brand.md                  colours, type, radius, spacing and mode the repository's theme carries
│   │   ├── brief-seeds.md            pitch, audience, problem and comparables as the repository's docs state them
│   │   ├── datamodel.md              entities, fields, relations and enums the schema declares
│   │   ├── index.md                  catalogue of findings files and raw material, with the skill that took each
│   │   ├── interaction.md            surfaces, editors, save models, messages, search as the code has them today
│   │   ├── routes.md                 every route or endpoint, the file defining it, what a user does there
│   │   ├── screens.md                page components behind the routes, with bindings, interactions and states
│   │   └── stack.md                  the platform, frameworks, database and tooling the manifests declare
│   ├── onboarding/                   the preferences, constraints and material a project arrives with
│   │   ├── answers.json              the onboarding intake record — values, confidence, seed inventory, approval
│   │   └── questions.md              open questions routed to someone who is not in the room
│   ├── research/                     sourced findings per topic that other skills design against
│   │   ├── audiences.md              personas with real job titles, tools, pain points and design implications
│   │   ├── behavioral-patterns.md    state machines and lifecycles seen in the field
│   │   ├── colors-fonts.md           palette and typography research for the domain
│   │   ├── competitors.md            per-product analysis of comparable products
│   │   ├── design-inspiration.md     layout, colour, typography and component references with sources
│   │   ├── domain.md                 terminology, regulations, trends and workflows the domain already has
│   │   ├── patterns.md               UX and architectural patterns for this domain
│   │   └── step/                     research dispatched alongside one skill, in a folder named for that skill
│   │       └── <skill-name>/
│   ├── seeds/                        material the user dropped in; nothing generates it
│   └── standards/                    conventions discovered in an existing codebase, one file per convention
│       ├── index.yml                 fast matching of conventions by applies_to and keywords
│       └── <domain>/
├── 03_brand/                         the visual identity folder and the procedure that fills it
│   ├── brand.dark.tokens.json        brand as W3C design tokens, with optional dark overlay and resolver
│   ├── brand.resolver.json           brand as W3C design tokens, with optional dark overlay and resolver
│   ├── brand.tokens.json             brand as W3C design tokens, with optional dark overlay and resolver
│   ├── brandbook.html                self-contained visual reference for the brand
│   └── identity.md                   colours, fonts, tone of voice and copy guidelines
├── 04_journeys/                      personas and the staged story map
│   └── stories.yaml                  personas, story map by stage, EARS criteria with ids
├── 05_features/                      the feature roster and one spec per feature, grouped into featuresets
│   ├── featuresets.md                the roster of featuresets, their features and priorities, and the open ideas
│   └── <featureset>/                 one featureset — a user purpose and its feature specs
│       └── <feature>.md              one feature's permanent spec — scope line, permissions, acceptance criteria
├── 06_behaviors/                     optional state machines and rules, one file per featureset
│   └── <featureset>.md               states, transitions and named constants for one featureset's entities
├── 07_screens/                       the app shell and one flat spec per screen, with the elements block
│   ├── shell.md                      the app frame — shell frame, navigation model, the one destination list
│   └── <screen>.md                   one screen on its own — floorplan, region bindings, tier overrides, elements
├── 08_dossiers/                      the concept-side working record of each feature, frozen when its loop ends
│   └── <feature_slug>/               the dossier directory of one feature
│       └── index.md                  one feature's framing, grill answers and rejected options, frozen at the end
├── 09_mockup/                        the reviewable mockup of the design and the feedback that edits the specs
│   ├── feedback/                     how open mockup notes become spec edits and model proposals
│   │   ├── devlog.md                 append-only log of feedback edits, read so a regeneration keeps them
│   │   ├── applied/                  committed per-round record of patches landed, failed and notes closed
│   │   ├── patches/                  proposed anchored patches and the review file a human approves
│   │   └── triage/                   deterministic routing of each open inbox note to the file it belongs in
│   └── storybook/                    one Vue Storybook — features, floorplans, screens, entities, the app, journeys
├── 10_blueprint/                     how the app is built — stack, architecture, API contracts, data model
│   ├── architecture.md               C4 levels — system context, containers, components, deployment, risks
│   ├── asyncapi.yaml                 AsyncAPI 3.1 contract of the channels the project publishes or consumes
│   ├── openapi.yaml                  OpenAPI 3.2 contract of the HTTP API served to clients other than the own UI
│   ├── techstack.md                  chosen technologies, resolved to one template id; no third-party services
│   └── datamodel/                    stack-neutral data model, naming rules and how it becomes a database
│       ├── model.yaml                the authored data model; checked and read through @skaile/model
│       └── seed.yaml                 named scenarios of sample data, every row checked against model.yaml
├── 11_build/                         criteria ledger, reviews, release and interaction verdicts
│   ├── design-candidates.md          evidenced candidates for a better design, found in the code
│   ├── interaction.sarif             SARIF 2.1.0 verdict of the code against APP-DESIGN.md
│   ├── release.yaml                  the whole-app release verdict: goals, seven scores, findings, improvements
│   ├── acceptance-criteria/          the criteria status ledger, one checkbox file per feature
│   │   └── <featureset>/
│   │       └── <feature_slug>.ac.md  the criteria status ledger, one checkbox file per feature
│   └── reviews/                      one feature's code-review verdict and findings
│       └── <feature_slug>.yaml       one feature's code-review verdict and findings
└── proposals/                        one file per run that proposes entries to artifacts other skills own
    └── <date>-<skill>-<scope>.yaml   one file per run that proposes entries to artifacts other skills own
```

## Numbering

The first level is numbered and contiguous, and nothing below it is: the prefix orders the tree and the sidebar strips it before display. Below the first level the artifact orders itself (a featureset's priority is the story stage its features carry), so `<featureset>` and `<feature_slug>` directories carry no prefix. Adding a twelfth kind renumbers the ones after it, which touches every skill that writes there.

## Naming

- Filenames are lowercase and hyphenated (`design-inspiration.md`), and one artifact has exactly one path.
- No two siblings differ only by singular and plural (`review.yaml` beside `reviews/`), because a path written from memory then silently reads nothing; a whole-tree fact and a per-thing collection carry unrelated names.
- Directories under `05_features/` are slugs: lowercase, hyphenated, no spaces, no numeric prefix. A screen is one flat file `07_screens/<screen>.md` whose stem is its `screen_id` (`^[a-z][a-z0-9-]{1,47}$`); `shell` is reserved there for the app frame.
- `02_grounding/research/step/` subfolders are named for the dispatching skill's `name:`, character for character.
- Term ids come from the glossary, not from features: the data model cites glossary ids rather than coin names, so a feature that invents a name splits one concept into two. The id is the slug of the term, whether the words live in `_concept/glossary.md` or in the project's own glossary (`tree/glossary.md § Where the words live`).

## Frontmatter every markdown artifact carries

```yaml
---
last_updated: YYYY-MM-DD    # valid ISO date, updated on every write
approved: YYYY-MM-DD        # ISO date of the user's yes; absent = not yet approved
---
```

The skill holding an artifact's approval step writes `approved:` in the same write that records the user's yes, and only then; a file still pending carries no `approved:` key rather than an empty one, and a later edit that changes the substance clears it until the user says yes again. `tree/frontmatter.schema.json` is the machine-readable form of these two fields. To validate, load the YAML, turn date values into ISO text — PyYAML reads an unquoted `2026-10-17` as a date, and `json.loads(json.dumps(doc, default=str))` does it — then validate. Data files without frontmatter carry the same key where their node says so: `answers.json` at its top level, `brand.tokens.json` under `$extensions["ai.skaile"]` (`tree/03_brand/brand.tokens.md`). Each node adds that artifact's own fields to these two.

## arc42 map

[arc42](https://arc42.org) 9.0 has twelve sections. The tree is not organised by them; this is where each one lives, so a reader who thinks in arc42 finds the same content.

| arc42 | `_concept/` home |
|---|---|
| 1 Introduction & Goals | `_concept/brief.md`, `_concept/goals.md`, `_concept/01_meta/expectations.md` |
| 2 Constraints | `_concept/goals.md` (constraints, non-goals) |
| 3 Context & Scope | `_concept/10_blueprint/architecture.md`, section System context |
| 4 Solution Strategy | `_concept/10_blueprint/techstack.md` |
| 5 Building Block View | `_concept/10_blueprint/architecture.md`, sections Containers and Components |
| 6 Runtime View | `_concept/06_behaviors/`, `_concept/04_journeys/` |
| 7 Deployment View | `_concept/10_blueprint/architecture.md`, section Deployment |
| 8 Crosscutting Concepts | `APP-DESIGN.md`, `_concept/07_screens/shell.md` |
| 9 Architecture Decisions | `docs/adr/` at the project root (`tree/docs/adr/README.md`) |
| 10 Quality Requirements | `_concept/goals.md`, `_concept/11_build/release.yaml` |
| 11 Risks & Technical Debt | `_concept/10_blueprint/architecture.md`, section Risks and technical debt |
| 12 Glossary | `_concept/glossary.md` |

## Protocol

How skills work on the tree lives beside it in `protocol/`, cited by file and section, never restated:

- `tree/protocol/ownership.md` — who writes what, and the proposed entry.
- `tree/protocol/running.md` — how a skill runs: the route as todo list and rules 1–8.
- `tree/protocol/delegation.md` — handing work to another agent context: the status block and the interview relay.
- `tree/protocol/beside-the-tree.md` — `APP-DESIGN.md`, `docs/adr/`, `docs/agents/domain.md` and the rulebook, the assets outside `_concept/`.

## _concept/README.md

`skaileup` writes this fixed pointer into the project, once, the first time it creates `_concept/`, and nothing else:

```
This tree is maintained by the skaileup collection. Every path here has an instruction node at
`<contracts>/shared-contracts/<same path>` (directory → `README.md`, file → same name with `.md`),
where `<contracts>` is the agent harness's contract directory: `.agents/contracts` (omp, Codex,
pi, dsh) or `.claude/contracts` (Claude Code), whichever exists.
Read the folder README and the node before editing a file here; the node says who owns it and who may propose into it,
its format, and what reads it.
The three artifacts outside this tree, APP-DESIGN.md, docs/adr/ and docs/agents/domain.md at the project
root, have their nodes at `<contracts>/shared-contracts/APP-DESIGN.md`,
`<contracts>/shared-contracts/docs/adr/README.md` and `<contracts>/shared-contracts/docs/agents/domain.md`.
```

## Checks

- Every part of `_concept/` resolves to a node by the rule above; the tree block lists exactly the nodes' `path:` entries.
