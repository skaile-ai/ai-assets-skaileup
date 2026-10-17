---
path: [_concept/, _concept/README.md]
summary: the artifact tree, its read direction and how a skill runs
writers: [concept-scope]
---

# _concept/

`_concept/` is the one directory every skill reads and writes inside the target project; the host fixes the name, and there is no sibling `_implementation/` (the build half is `11_build/`). This directory mirrors it one node per part, and a path with no node here is a path no reader will find.

## The rule

Before reading or writing anything under `_concept/<p>`, read the node at the same path `<p>` in this directory (installed at `.claude/contracts/shared-contracts/<p>`): the folder's `README.md`, then the file's node. If the exact node is missing, the nearest `README.md` up the path applies.

| `_concept/` thing | node |
|---|---|
| directory `X/` | `X/README.md` here (also the node of `X/README.md` when that artifact exists) |
| file `X/name.ext` | `X/name.md` here (extension always `.md`: `tokens.json` → `tokens.md`) |
| placeholder segment `<x>` | `[x]` in the node path: `05_features/[featureset]/[feature].md` |
| siblings sharing a stem, or children a directory README covers | one node whose `path:` is a list |

A node's `path:` entries are matched first, `<x>` matching any one segment; the location column applies next; a path below a directory whose node lists the directory resolves to that README.

## The tree

```text
_concept/                             the artifact tree, its read direction and how a skill runs
├── README.md                         the artifact tree, its read direction and how a skill runs
├── brief.md                          the pitch, with its comparables — what the user said, no more
├── glossary.md                       the project's ubiquitous language — terms, definitions, _Avoid_ lists
├── goals.md                          success criteria, KPIs, constraints and explicit non-goals
├── 01_meta/                          project metadata — the sizing every skill reads its depth from
│   └── scope.yaml                    flow and project type — the sizing every skill reads its depth from
├── 02_grounding/                     everything that came from outside the room, readable by every skill
│   ├── findings/                     graded evidence and raw material from outside the room
│   │   ├── brand.md                  colours, type, radius, spacing and mode the repository's theme carries
│   │   ├── brief-seeds.md            pitch, audience, problem and comparables as the repository's docs state them
│   │   ├── datamodel.md              entities, fields, relations and enums the schema declares
│   │   ├── index.md                  catalogue of findings files and raw material, with the skill that took each
│   │   ├── routes.md                 every route or endpoint, the file defining it, what a user does there
│   │   ├── screens.md                page components behind the routes, with bindings, interactions and states
│   │   └── stack.md                  the platform, frameworks, database and tooling the manifests declare
│   ├── onboarding/                   the preferences, constraints and material a project arrives with
│   │   ├── answers.json              the one answer record — values, confidence, seed inventory, approval
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
│   ├── brandbook.html                self-contained visual reference for the brand
│   ├── identity.md                   colours, fonts, tone of voice and copy guidelines
│   └── tokens.json                   machine-readable design tokens
├── 04_journeys/                      personas and the staged story map
│   └── stories.yaml                  personas, story map by stage, EARS criteria with ids
├── 05_features/                      the feature roster and one spec per feature, grouped into featuresets
│   ├── featuresets.md                the roster of featuresets and the features in each, with priorities
│   └── <featureset>/                 one featureset — a user purpose and its feature specs
│       └── <feature>.md              one feature's permanent spec — scope line, permissions, acceptance criteria
├── 06_behaviors/                     optional state machines and rules, one file per featureset
│   └── <featureset>.md               states, transitions and named constants for one featureset's entities
├── 07_screens/                       the app shell and one spec per screen, with the elements block
│   ├── shell.md                      the app frame — navigation, layout areas, breakpoints, shared patterns
│   └── <feature_slug>/               the screen specs of one feature
│       └── <screen>.md               one screen's spec — body sections, links to its feature, elements block
├── 08_dossiers/                      the concept-side working record of each feature, frozen when its loop ends
│   └── <feature_slug>/               the dossier directory of one feature
│       └── index.md                  one feature's framing, grill answers and rejected options, frozen at the end
├── 09_mockup/                        reviewable prototypes of the design and the feedback that edits the specs
│   ├── feedback/                     stakeholder annotations, their triage, reviewed patches and the audit trail
│   │   ├── devlog.md                 append-only log of feedback edits, read by renderers so re-renders keep them
│   │   ├── applied/                  committed per-session record of which patches landed and which failed
│   │   ├── patches/                  proposed section-anchored patches and the review file a human approves
│   │   ├── sessions/                 raw annotation sessions downloaded from the overlay, one file per round
│   │   │   └── <sessionId>.json      raw annotation sessions downloaded from the overlay, one file per round
│   │   └── triage/                   deterministic routing of each annotation to the file it belongs in
│   ├── storybook/                    standalone Storybook of components, page compositions and journey click-dummies
│   └── walkthrough/                  clickable site per screen and journey, plus the manifest mockup-annotate reads
├── 10_blueprint/                     how the app is built — stack, custom architecture, decisions, data model
│   ├── architecture.md               custom modules, protocols and every external integration beyond the template
│   ├── decisions.md                  design-time decision records, append-only
│   ├── techstack.md                  chosen technologies, resolved to one template id; no third-party services
│   └── datamodel/                    stack-neutral data model, naming rules and how it becomes a database
│       ├── model.dbml                the canonical stack-neutral model — semantic types, relations, metadata
│       ├── model.json                the canonical stack-neutral model — semantic types, relations, metadata
│       └── seed.json                 realistic seed scenarios for mockups, screen specs and E2E tests
└── 11_build/                         slices, trace, criteria ledger, reviews, release verdict and decisions
    ├── decisions.md                  build-time decision records, append-only
    ├── release.yaml                  the whole-app release verdict: goals, seven scores, findings, improvements
    ├── trace.yaml                    feature to slices to commits to code, the one feature-to-commit join
    ├── acceptance-criteria/          the criteria status ledger, one checkbox file per feature
    │   └── <featureset>/
    │       └── <feature_slug>.ac.md  the criteria status ledger, one checkbox file per feature
    ├── reviews/                      one feature's code-review verdict and findings
    │   └── <feature_slug>.yaml       one feature's code-review verdict and findings
    └── slices/                       one dossier per vertical slice, cut from a frozen feature spec
        └── <slice_id>/               one slice's dossier directory: plan, working state, frozen index
            ├── index.md              the frozen slice record and its transient progress file
            ├── plan.md               one slice's scope, rows, criteria by id, tests and carry-overs
            └── progress.yaml         the frozen slice record and its transient progress file
```

## Numbering

The first level is numbered and contiguous, and nothing below it is: the prefix orders the tree and the sidebar strips it before display. Below the first level the artifact orders itself (a featureset's priority is the story stage its features carry), so `<featureset>` and `<feature_slug>` directories carry no prefix. Adding a twelfth kind renumbers the ones after it, which touches every skill that writes there.

## Naming

- Filenames are lowercase and hyphenated (`design-inspiration.md`), and one artifact has exactly one path.
- No two siblings differ only by singular and plural (`review.yaml` beside `reviews/`), because a path written from memory then silently reads nothing; a whole-tree fact and a per-thing collection carry unrelated names.
- Directories under `05_features/` and `07_screens/` are slugs: lowercase, hyphenated, no spaces, no numeric prefix; `shell` is reserved under `07_screens/`.
- `02_grounding/research/step/` subfolders are named for the dispatching skill's `name:`, character for character.
- Entity names come from the data model, not from features: the data model is built from the journeys and features read its names rather than coin them, so a feature that invents an entity name splits one concept into two.

## Read direction

A skill reads from anywhere earlier in the tree and writes only into the folder it owns. `02_grounding/` is readable by every skill at any point.

| writes to | may read |
|---|---|
| `brief.md` · `goals.md` | `02_grounding/` |
| `glossary.md` | `02_grounding/`, `brief.md` |
| `03_brand/` | `02_grounding/`, `brief.md`, `glossary.md` |
| `04_journeys/` | `02_grounding/`, `brief.md`, `goals.md`, `glossary.md` |
| `10_blueprint/datamodel/` | `02_grounding/`, `brief.md`, `glossary.md`, `04_journeys/`, and `10_blueprint/techstack.md` · `architecture.md` when they exist |
| `05_features/` | the above, and `10_blueprint/datamodel/` |
| `06_behaviors/` | the above + `05_features/` |
| `07_screens/` | the above, and `10_blueprint/` when it exists |
| `08_dossiers/` | everything the feature loop touched |
| `09_mockup/` | `03_brand/`, `04_journeys/`, `05_features/`, `07_screens/`, `10_blueprint/datamodel/` |
| `10_blueprint/` (the rest) | everything above it |
| `11_build/` | everything |

`06_behaviors/` and `10_blueprint/architecture.md` are optional; a reader checks for existence before reading.

## Frontmatter every markdown artifact carries

```yaml
---
last_updated: YYYY-MM-DD    # valid ISO date, updated on every write
approved: YYYY-MM-DD        # ISO date of the user's yes; absent = not yet approved
---
```

The skill holding an artifact's approval step writes `approved:` in the same write that records the user's yes, and only then; a file still pending carries no `approved:` key rather than an empty one, and a later edit that changes the substance clears it until the user says yes again. Data files without frontmatter (`answers.json`, `tokens.json`) carry the same key at the top level where their node says so. Each node adds that artifact's own fields to these two.

## How a skill runs

1. **Gates first.** Check the `metadata.prerequisites.files` gates before any output and stop, naming the missing path and the skill that produces it, when a hard one fails. Then read every required input and the optional ones where present; `_concept/` outranks the conversation, so a disagreement between them is a question for the user.
2. **The route is the todo list.** On entry the route's numbered items become the first todo items, verbatim and in order; an item that does not apply stays listed as `skip: <reason>`, and **Done when** is the last item. Where the harness has no todo tool, the first message lists them and each later message names the item it is on.
3. **One question per message.** A question goes out as its own message, built on the user's last answer, with a status update or explanation in the message before it; a technical term is explained in parentheses, because a question buried at the end of a long message gets skimmed.
4. **Completion summary.** Report the files written or modified with one line each, the key decisions, the cross-references established, then the next steps. Each claim says how it is known — **measured** (seen in a file, a command's output, the running app) or **inferred** (follows from something measured, and names it); a prediction or unseen cause is a guess and goes under its own `Unverified:` line. A check the agent could run is run, not handed to the user.
5. **Standalone or in a flow.** A standalone run applies the same gates, and its next steps are the skills whose required paths are now satisfied, which are the edges leaving this skill's node in the flow file; when none is unblocked, show what is missing and which skill produces it. When a flow is running the host dispatches the next step itself.

## _concept/README.md

`concept-scope` writes this fixed pointer into the project and nothing else:

```
This tree is maintained by the skaileup-tree collection. Every path here has an instruction node at
`.claude/contracts/shared-contracts/<same path>` (directory → `README.md`, file → same name with `.md`).
Read the folder README and the node before editing a file here; the node says who writes it,
its format, and what reads it.
```

## Checks

- Every part of `_concept/` resolves to a node by the rule above; the tree block lists exactly the nodes' `path:` entries.
