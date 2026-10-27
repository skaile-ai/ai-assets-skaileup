---
path: [_concept/, _concept/README.md]
summary: the artifact tree, its ownership rule and how a skill runs
owner: [skaileup]
may_propose: []
---

# _concept/

`_concept/` is the one directory every skill reads and writes inside the target project; the host fixes the name, and there is no sibling `_implementation/` (the build half is `11_build/`). This directory mirrors it one node per part, and a path with no node here is a path no reader will find.

## The rule

Before reading or writing anything under `_concept/<p>`, read the node at the same path `<p>` in this directory (installed at `<contracts>/shared-contracts/<p>`, where `<contracts>` is the harness's contract directory: `.omp/contracts` for omp, `.claude/contracts` for Claude Code, `.codex/contracts` for Codex): the folder's `README.md`, then the file's node. If the exact node is missing, the nearest `README.md` up the path applies.

| `_concept/` thing | node |
|---|---|
| directory `X/` | `X/README.md` here (also the node of `X/README.md` when that artifact exists) |
| file `X/name.ext` | `X/name.md` here (extension always `.md`: `stories.yaml` → `stories.md`) |
| placeholder segment `<x>` | `[x]` in the node path: `05_features/[featureset]/[feature].md` |
| siblings sharing a stem, or children a directory README covers | one node whose `path:` is a list |

A node's `path:` entries are matched first, `<x>` matching any one segment; the location column applies next, for directories only (a file resolves through its node's `path:` entry); a path below a directory entry of a list-form `path:` resolves to that README.

## The tree

```text
_concept/                                the artifact tree, its ownership rule and how a skill runs
├── README.md                            the artifact tree, its ownership rule and how a skill runs
├── brief.md                             the pitch, with its comparables — what the user said, no more
├── glossary.md                          the ubiquitous language and its light ontology — terms, kinds, relations
├── goals.md                             success criteria, KPIs, constraints and explicit non-goals
├── 01_meta/                             project metadata — the sizing skills read when they need it
│   └── scope.yaml                       flow, project type and depth — written when the first skill needs one
├── 02_grounding/                        everything that came from outside the room, readable by every skill
│   ├── findings/                        graded evidence and raw material from outside the room
│   │   ├── brand.md                     colours, type, radius, spacing and mode the repository's theme carries
│   │   ├── brief-seeds.md               pitch, audience, problem and comparables as the repository's docs state them
│   │   ├── datamodel.md                 entities, fields, relations and enums the schema declares
│   │   ├── index.md                     catalogue of findings files and raw material, with the skill that took each
│   │   ├── interaction.md               surfaces, editors, save models, messages, search as the code has them today
│   │   ├── routes.md                    every route or endpoint, the file defining it, what a user does there
│   │   ├── screens.md                   page components behind the routes, with bindings, interactions and states
│   │   └── stack.md                     the platform, frameworks, database and tooling the manifests declare
│   ├── onboarding/                      the preferences, constraints and material a project arrives with
│   │   ├── answers.json                 the onboarding intake record — values, confidence, seed inventory, approval
│   │   └── questions.md                 open questions routed to someone who is not in the room
│   ├── research/                        sourced findings per topic that other skills design against
│   │   ├── audiences.md                 personas with real job titles, tools, pain points and design implications
│   │   ├── behavioral-patterns.md       state machines and lifecycles seen in the field
│   │   ├── colors-fonts.md              palette and typography research for the domain
│   │   ├── competitors.md               per-product analysis of comparable products
│   │   ├── design-inspiration.md        layout, colour, typography and component references with sources
│   │   ├── domain.md                    terminology, regulations, trends and workflows the domain already has
│   │   ├── patterns.md                  UX and architectural patterns for this domain
│   │   └── step/                        research dispatched alongside one skill, in a folder named for that skill
│   │       └── <skill-name>/
│   ├── seeds/                           material the user dropped in; nothing generates it
│   └── standards/                       conventions discovered in an existing codebase, one file per convention
│       ├── index.yml                    fast matching of conventions by applies_to and keywords
│       └── <domain>/
├── 03_brand/                            the visual identity folder and the procedure that fills it
│   ├── brand.dark.tokens.json           brand as W3C design tokens, with optional dark overlay and resolver
│   ├── brand.resolver.json              brand as W3C design tokens, with optional dark overlay and resolver
│   ├── brand.tokens.json                brand as W3C design tokens, with optional dark overlay and resolver
│   ├── brandbook.html                   self-contained visual reference for the brand
│   └── identity.md                      colours, fonts, tone of voice and copy guidelines
├── 04_journeys/                         personas and the staged story map
│   └── stories.yaml                     personas, story map by stage, EARS criteria with ids
├── 05_features/                         the feature roster and one spec per feature, grouped into featuresets
│   ├── featuresets.md                   the roster of featuresets and the features in each, with priorities
│   └── <featureset>/                    one featureset — a user purpose and its feature specs
│       └── <feature>.md                 one feature's permanent spec — scope line, permissions, acceptance criteria
├── 06_behaviors/                        optional state machines and rules, one file per featureset
│   └── <featureset>.md                  states, transitions and named constants for one featureset's entities
├── 07_screens/                          the app shell and one flat spec per screen, with the elements block
│   ├── shell.md                         the app frame — shell frame, navigation model, the one destination list
│   └── <screen>.md                      one screen on its own — floorplan, region bindings, tier overrides, elements
├── 08_dossiers/                         the concept-side working record of each feature, frozen when its loop ends
│   └── <feature_slug>/                  the dossier directory of one feature
│       └── index.md                     one feature's framing, grill answers and rejected options, frozen at the end
├── 09_mockup/                           the reviewable mockup of the design and the feedback that edits the specs
│   ├── feedback/                        how open mockup notes become spec edits and model proposals
│   │   ├── devlog.md                    append-only log of feedback edits, read so a regeneration keeps them
│   │   ├── applied/                     committed per-round record of patches landed, failed and notes closed
│   │   ├── patches/                     proposed anchored patches and the review file a human approves
│   │   └── triage/                      deterministic routing of each open inbox note to the file it belongs in
│   └── storybook/                       one Vue Storybook package — floorplans, screens, entities, the app, journeys
├── 10_blueprint/                        how the app is built — stack, architecture, API contracts, decisions, data model
│   ├── architecture.md                  C4 levels — system context, containers, components, deployment, risks
│   ├── asyncapi.yaml                    AsyncAPI 3.1 contract of the channels the project publishes or consumes
│   ├── decisions.md                     design-time decision records, append-only
│   ├── openapi.yaml                     OpenAPI 3.2 contract of the HTTP API served to clients other than the own UI
│   ├── techstack.md                     chosen technologies, resolved to one template id; no third-party services
│   └── datamodel/                       stack-neutral data model, naming rules and how it becomes a database
│       ├── datamodel-model.schema.json  tool files copied into the project — the model DSL, its generator, two schemas
│       ├── datamodel-seed.schema.json   tool files copied into the project — the model DSL, its generator, two schemas
│       ├── gen.ts                       tool files copied into the project — the model DSL, its generator, two schemas
│       ├── model.dbml                   model.ts is authored; model.json and model.dbml are generated from it
│       ├── model.json                   model.ts is authored; model.json and model.dbml are generated from it
│       ├── model.ts                     model.ts is authored; model.json and model.dbml are generated from it
│       ├── seed.json                    seed.ts is authored and typed against the model; seed.json is generated
│       ├── seed.ts                      seed.ts is authored and typed against the model; seed.json is generated
│       └── skaile-model.ts              tool files copied into the project — the model DSL, its generator, two schemas
└── 11_build/                            slices, trace, criteria ledger, reviews, release verdict and decisions
    ├── decisions.md                     build-time decision records, append-only
    ├── design-candidates.md             evidenced candidates for a better design, found in the code
    ├── interaction.sarif                SARIF 2.1.0 verdict of the code against APP-DESIGN.md
    ├── release.yaml                     the whole-app release verdict: goals, seven scores, findings, improvements
    ├── trace.yaml                       feature to slices to commits to code, the one feature-to-commit join
    ├── acceptance-criteria/             the criteria status ledger, one checkbox file per feature
    │   └── <featureset>/
    │       └── <feature_slug>.ac.md     the criteria status ledger, one checkbox file per feature
    ├── reviews/                         one feature's code-review verdict and findings
    │   └── <feature_slug>.yaml          one feature's code-review verdict and findings
    └── slices/                          one dossier per vertical slice, cut from a frozen feature spec
        └── <slice_id>/                  one slice's dossier directory: plan, working state, frozen index
            ├── index.md                 the frozen slice record and its transient progress file
            ├── plan.md                  one slice's scope, rows, criteria by id, tests and carry-overs
            └── progress.yaml            the frozen slice record and its transient progress file
```

## Numbering

The first level is numbered and contiguous, and nothing below it is: the prefix orders the tree and the sidebar strips it before display. Below the first level the artifact orders itself (a featureset's priority is the story stage its features carry), so `<featureset>` and `<feature_slug>` directories carry no prefix. Adding a twelfth kind renumbers the ones after it, which touches every skill that writes there.

## Naming

- Filenames are lowercase and hyphenated (`design-inspiration.md`), and one artifact has exactly one path.
- No two siblings differ only by singular and plural (`review.yaml` beside `reviews/`), because a path written from memory then silently reads nothing; a whole-tree fact and a per-thing collection carry unrelated names.
- Directories under `05_features/` are slugs: lowercase, hyphenated, no spaces, no numeric prefix. A screen is one flat file `07_screens/<screen>.md` whose stem is its `screen_id` (`^[a-z][a-z0-9-]{1,47}$`); `shell` is reserved there for the app frame.
- `02_grounding/research/step/` subfolders are named for the dispatching skill's `name:`, character for character.
- Term ids come from the glossary, not from features: the data model cites glossary ids rather than coin names, so a feature that invents a name splits one concept into two. The id is the slug of the term, whether the words live in `_concept/glossary.md` or in the project's own glossary (`tree/glossary.md § Where the words live`).

## Ownership

Read anything, in any order; write only the artifacts you own, through the owner node's contract. `02_grounding/` is readable by every skill. An artifact another skill owns takes only `proposed` entries, and only from a skill listed under that node's `may_propose`. A project file outside `_concept/` other than `APP-DESIGN.md` (a `CONTEXT.md`, docs, ADRs) is a source to read and cite, and stays the project's own: a term or decision it lacks is proposed into the `_concept/` artifact that owns that kind of entry. The one exception is the project glossary, the file that holds the words when the project keeps its own: `concept-glossary` writes there only the definitions of terms it adds or moves, the promotion of a proposed entry (dropping its marker lines) and the rejection of one (removing it), keeps every entry written by `domain-modeling` or by hand as it stands, and a proposed term is filed there too (`tree/glossary.md § Where the words live`). `06_behaviors/` and `10_blueprint/architecture.md` are optional; a reader checks for existence before reading.

A node's frontmatter carries two keys, both required:

```yaml
owner: [concept-glossary]   # skills whose `produces` resolve here; [] when nothing generates it
may_propose: []             # skills that may append `proposed` entries through this node; disjoint from owner
```

A directory node lists the owners of the parts it covers. `may_propose` names skills of this collection and repeats no owner.

**Proposed entry.** An entry a non-owner skill appends to the owner's artifact, marked `status: proposed`, with `proposed_by: <skill>`, `proposed_on: YYYY-MM-DD` and its source (an evidence reference or the user's words). It adds and never edits a confirmed entry. When the owner's artifact does not exist yet, the proposer creates it holding only its proposed entries and no `approved:` key, so the owner's first write fills it instead of finding a gap. The owner reviews each entry with the user and promotes it by dropping the marker, or rejects it and records the rejection in `_concept/10_blueprint/decisions.md`. Each node's `## Format` holds the per-artifact shape, one shape per node.

## Frontmatter every markdown artifact carries

```yaml
---
last_updated: YYYY-MM-DD    # valid ISO date, updated on every write
approved: YYYY-MM-DD        # ISO date of the user's yes; absent = not yet approved
---
```

The skill holding an artifact's approval step writes `approved:` in the same write that records the user's yes, and only then; a file still pending carries no `approved:` key rather than an empty one, and a later edit that changes the substance clears it until the user says yes again. `tree/frontmatter.schema.json` is the machine-readable form of these two fields. To validate, load the YAML, turn date values into ISO text — PyYAML reads an unquoted `2026-10-17` as a date, and `json.loads(json.dumps(doc, default=str))` does it — then validate. Data files without frontmatter carry the same key where their node says so: `answers.json` at its top level, `brand.tokens.json` under `$extensions["ai.skaile"]` (`tree/03_brand/brand.tokens.md`). Each node adds that artifact's own fields to these two.

## How a skill runs

Every skill binds these rules at its interviewing step by citing `tree/README.md § How a skill runs`; a node does not restate them.

**The route is the todo list.** On entry the route's numbered items become the first todo items, verbatim and in order; an item that does not apply stays listed as `skip: <reason>`, and **Done when** is the last item. Where the harness has no todo tool, the first message lists them and each later message names the item it is on.

1. **Resolve facts, then ask.** Read existing artifacts in any order, and an optional one only after checking it exists; `_concept/` outranks the conversation, so a disagreement between them is a question for the user. Run `concept-reverse` scoped for evidence the code holds; mark inferred facts; batch only what tools cannot settle. A `hard`-gated input that is missing stops the skill in one sentence naming the missing path and the skill that produces it.
2. **One decision batch per message.** At most 7 independently answerable questions on one topic; each with the recommendation first and a one-line consequence; an "accept all defaults" option; questions whose options depend on an unanswered one are deferred to the next batch; a status line precedes the batch. A technical term is explained in parentheses.
3. **Match the user's specificity.** Infer depth from the material supplied; where it matters, ask per artifact how deep to go (`sketch · standard · exhaustive`) and say what each level produces; a user precise about roles and vague about layout gets precise role questions and a layout proposal.
4. **Sort before asking.** Restate the user's input as a coherent draft (terms, objects, screens, rules) with gaps marked, then ask about the gaps — never a questionnaire first.
5. **Show consequences before commitments** on data, feature and navigation choices: what the user sees, data and permission effects, affected artifacts, reversibility; for expensive choices compare genuinely different alternatives (design-it-twice).
6. **Show the layout when the choice is spatial.** A layout story with neutral placeholders (two floorplans on request, at the `narrow` and `wide` viewports) before the screen is specified.
7. **Record at the semantic home**, as `proposed` when another skill owns it; open questions get stable ids.
8. **Completion summary.** Report the files written or modified with one line each, the key decisions, the cross-references established, then the next steps, named by demand: the skills that own what is still missing. Each claim says how it is known — **measured** (seen in a file, a command's output, the running app) or **inferred** (follows from something measured, and names it); a prediction or unseen cause is a guess and goes under its own `Unverified:` line. A check the agent could run is run, not handed to the user.

## Beside the tree

One artifact sits outside `_concept/`: **`APP-DESIGN.md`**, at the project root (the directory that holds `_concept/`). It holds the project's interaction decisions and is owned by `experience-interaction`; `quality-interaction` checks code against it and writes its verdict to `_concept/11_build/interaction.sarif`, never to this file. Its node is `tree/APP-DESIGN.md` (installed at `<contracts>/shared-contracts/APP-DESIGN.md`), and a monorepo app has its own, one per project. It is the only such artifact; `AGENTS.md` is project code, not a concept artifact: `build-scaffold` writes a pointer to `APP-DESIGN.md` into it when it creates the project, and no skill lists it under `produces`.

A second contract asset, `rulebook/` (contract `app-design-rulebook`: rules, defaults, floorplans), holds the application-design rules skills cite. It is not a `_concept/` part and has no node here.

## arc42 map

[arc42](https://arc42.org) 9.0 has twelve sections. The tree is not organised by them; this is where each one lives, so a reader who thinks in arc42 finds the same content.

| arc42 | `_concept/` home |
|---|---|
| 1 Introduction & Goals | `_concept/brief.md`, `_concept/goals.md` |
| 2 Constraints | `_concept/goals.md` (constraints, non-goals) |
| 3 Context & Scope | `_concept/10_blueprint/architecture.md`, section System context |
| 4 Solution Strategy | `_concept/10_blueprint/techstack.md` |
| 5 Building Block View | `_concept/10_blueprint/architecture.md`, sections Containers and Components |
| 6 Runtime View | `_concept/06_behaviors/`, `_concept/04_journeys/` |
| 7 Deployment View | `_concept/10_blueprint/architecture.md`, section Deployment |
| 8 Crosscutting Concepts | `APP-DESIGN.md`, `_concept/07_screens/shell.md` |
| 9 Architecture Decisions | `_concept/10_blueprint/decisions.md`, `_concept/11_build/decisions.md` |
| 10 Quality Requirements | `_concept/goals.md`, `_concept/11_build/release.yaml` |
| 11 Risks & Technical Debt | `_concept/10_blueprint/architecture.md`, section Risks and technical debt |
| 12 Glossary | `_concept/glossary.md` |

## _concept/README.md

`skaileup` writes this fixed pointer into the project, once, the first time it creates `_concept/`, and nothing else:

```
This tree is maintained by the skaileup collection. Every path here has an instruction node at
`<contracts>/shared-contracts/<same path>` (directory → `README.md`, file → same name with `.md`),
where `<contracts>` is the agent harness's contract directory: `.omp/contracts`, `.claude/contracts`
or `.codex/contracts`, whichever exists.
Read the folder README and the node before editing a file here; the node says who owns it and who may propose into it,
its format, and what reads it.
The one artifact outside this tree, APP-DESIGN.md at the project root, has its node at
`<contracts>/shared-contracts/APP-DESIGN.md`.
```

## Checks

- Every part of `_concept/` resolves to a node by the rule above; the tree block lists exactly the nodes' `path:` entries.
