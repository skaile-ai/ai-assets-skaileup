# CONTEXT — skaileup

The ubiquitous language of this collection: the words its skills use to talk to each
other, to the flow engine, and to forge-concept. Every skill uses the canonical term
and never redefines it locally.

This file is a **glossary and nothing else** — no paths, no schemas, no process. Where
a thing lives is the tree's job (its `README.md`); what it *is* is this file's.

## The collection

**Asset**:
A versioned thing this repo ships and a workspace installs — a skill, a flow, or a
contract. The unit of identity and of install; a file that is not part of one reaches
no workspace.
_Avoid_: resource, module, package

**Contract**:
An asset that ships shared reference, dir-scoped and installed whole. There are two: the
tree (`shared-contracts`) and the rulebook (`app-design-rulebook`). What a skill actually
cites is a node inside the first or a rule or floorplan inside the second.
_Avoid_: reference file, shared docs

**Tree**:
The instruction mirror of `_concept/`, shipped as one of the two contract assets. One node per
`_concept/` part; adding a part to `_concept/` means adding its node.
_Avoid_: contracts folder, reference layer

**Node**:
One file in the tree: the instruction for one `_concept/` part — purpose, format,
procedure, checks — named by the part's path. A node is read at the step that touches its
part. Not a **flow node** — that is a vertex of a flow graph, always written "flow node".
_Avoid_: contract file, reference file

**Skill**:
One unit of agent work with a `name:` that is its whole identity — install path, flow
flow node reference, and grounding key all at once.

**Flow**:
A recipe over skills. Flow nodes name skills; edges suggest an order and gate nothing — what
a project runs follows from what it asks for, and how far each skill goes is its **depth**.
A project follows one of two flows, greenfield or reverse (starting from existing code);
`01_meta/scope.yaml` records which.
_Avoid_: pipeline, workflow, chain, tier

**Route**:
The ordered list of nodes a skill visits. A skill's body is its route and nothing else.
_Avoid_: steps, workflow

**Router**:
The one skill that names another skill instead of doing work — `skaileup`, the collection's
front door. Given a want (an artifact, a screen, a question) it names the skill that produces
it and says, for each of that skill's inputs, whether it is present, derivable from the code,
or still to ask. It also asks, lazily, for the flow, project type and depth, and records them.
_Avoid_: dispatcher, orchestrator, entry skill

**Host**:
A codebase that reads this collection at runtime rather than shipping in it —
forge-concept, `@skaile/workspaces`, platform. Always one of those. The word is *not*
used for the agent harness a session runs in (say **harness** for that), and a fact this
collection copies from one is a **host fact**: a row in `scripts/host_facts.py` naming
the file and the grep-able signature it rests on, so `check.py`'s rules cite it and
`verify_host.py` can prove it still holds.
_Avoid_: consumer, platform (that is one host's name), environment

**Phase**:
The lane a flow node belongs to — conceptualization, implementation, or review. A
machine-read interface with forge-concept; never used loosely for "stage of work".
_Avoid_: stage, step, lane

**Session boundary**:
The point where one skill's work ends and the next begins. Every boundary is warm or
cold. Deliberately *not* called a phase boundary, because `phase` is taken. Never
described with a harness's slash commands — those exist in one host and not the other.
_Avoid_: /clear, /compact, context switch

**Warm boundary**:
A session boundary the next skill may cross without starting over: the reasoning behind
the last step is still worth having verbatim. Continuing is the default, subject to a
soft gate on how full the context already is.

**Cold resume**:
A session boundary where nothing carries — a later day, another person, another host.
The durable artifact is the whole input, so it has to stand alone.
_Avoid_: handoff, restart

**Gate**:
A precondition on running a skill. **Hard** refuses to proceed; **soft** warns and
continues. Every gate is one or the other, stated at the step it binds.
_Avoid_: guard, check, blocker, prerequisite

**Project type**:
What kind of thing is being built — web-app, cli-tool, api-service, library, mobile-app,
data-pipeline. Chosen once, and it decides which artifacts a project is expected to grow, so
a missing screen in a cli-tool is not a gap. The word matches the key the machine reads,
`project_type`, because a glossary that disagrees with the schema loses the argument.
_Avoid_: shape, kind, category

**Profile**:
The description of one project type: what a project of that type grows and what it never
will. One row per type in the `## Project types` table of the tree's `01_meta/scope.md` node.
The word names the description; the project has a *project type*, not a profile.
_Avoid_: project profile, project shape; onboarding profile (that is forge-concept's, keyed by flow id — a different thing that shares the word)

**Depth**:
How far a project, or one artifact, is worked out — a sketch, a standard pass, or an
exhaustive one. Recorded once for the project and asked per artifact where it matters, with
what each level produces said up front. Replaces the old meaning of *tier* as project size.
_Avoid_: tier, size, level, scope (that is what is in the project, not how far each part goes)

**Template**:
A tech-stack reference an implementation skill reads after the stack is chosen. Carries
**atoms** in its frontmatter (one value each, extracted by name) and **recipes** as named
sections (paragraphs, cited by heading). All stack-specific knowledge lives here; a skill
that needs a stack branch has found a missing template section. Not a profile, not a skill.
_Avoid_: stack profile, scaffold, boilerplate

**Rulebook**:
The collection's shared application-design rules, shipped as the second contract asset:
numbered rules each with a strength grade, tunable heuristics, an adoptable bundle of
defaults, and the catalogue of floorplans. Invariants always apply; a heuristic applies at the
value the app adopted. Distinct from an app's own **app design**, which records what that app
decided under these rules.
_Avoid_: style guide, guidelines, design system, patterns file

## What a project grows

**Artifact**:
A file a skill writes into a target project. The unit of everything this collection
produces.
_Avoid_: output, deliverable, result, product

**Concept**:
The design half of a project — what is being built and why, before any code. The root
directory `_concept/` is *not* this word: its name is fixed by the host and it holds the
build half too.
_Avoid_: discovery, spec phase

**Blueprint**:
The technical design a concept resolves to: stack, architecture, data model.
Still design, not code.

**Datamodel**:
The *designed* schema — entities, fields, relations and seed scenarios in
`10_blueprint/datamodel/`. A description of data, not any running store. It is authored as
TypeScript (`model.ts`, `seed.ts`); `model.json`, `model.dbml` and `seed.json` are generated
from it and are what everything outside the mockup reads.
_Avoid_: schema, data layer

**Database**:
The *materialised* datamodel — migrations applied and seed scenarios loaded in the built
app. What `build-database` produces from what `architecture-datamodel` designed.
_Avoid_: db, persistence, store

**Mockup**:
The one Vue Storybook package at `09_mockup/storybook/` that grows beside the specs: a story
per floorplan, screen, entity component and journey, plus the whole app inside one story.
The only surface a stakeholder reviews the design on.
_Avoid_: prototype, walkthrough, click-dummy

**Annotation**:
A note a stakeholder leaves on a component of the running mockup. Stored in the project's
annotation inbox (`.data/annotations/`), not in `_concept/`, and closed with a resolution once
it has been acted on or rejected.
_Avoid_: feedback session, comment

**Implementation**:
The build half — plans, slices, and the code itself.

**Grounding**:
Research, reference material and captured user input, available to every skill as
input regardless of which artifact it owns.
_Avoid_: context, background, inputs

**Standard**:
A convention discovered in an existing codebase, applied to new work.

**Glossary**:
A project's ubiquitous language — its own domain terms and the light ontology around them:
what kind of thing each term is, what it is part of, what roles it plays, why it exists, and
how an object term is reached, owned and originated. Words and the relations between them;
stored fields stay with the datamodel. Grown lazily as terms get pinned, read by every skill so
vocabulary does not drift; any authoring skill may propose a term. Distinct from this file.

**Project glossary**:
The file outside `_concept/` that holds a project's words — term, definition and what to avoid
saying — when the project keeps its own, usually the root `CONTEXT.md` that the
`domain-modeling` skill tends. It stays the project's: this collection adds definitions to it and
rearranges nothing already there. What the words mean lives here; what kind of thing each one is
lives in the **glossary**.
_Avoid_: external glossary, words file, context file, CONTEXT.md (that is one project's name for it)

**Split mode**:
The way a project keeps its glossary when it has a **project glossary**: the words live there,
and the **glossary** holds only the ontology around them. Each term has its home for definition
and another for kind, so neither file repeats the other.
_Avoid_: dual glossary, hybrid mode, linked glossary

**Concept mode**:
The way a project keeps its glossary when it has no **project glossary**, or declares that it
wants none: the **glossary** holds words and ontology together, as one file. Not the **concept**,
which is the design half of a project.
_Avoid_: default mode, single-file mode, standalone glossary

**Decision record**:
An append-only note of a choice that was **hard to reverse**, **surprising without
context**, and a **real trade-off**. All three, or it is not one. One record per project,
open to every authoring skill; each entry says what was decided, by whom, which options were
rejected and what follows. A rejected scope decision, or a rejected **proposed entry**, is a
decision record marked rejected, not a separate store. Recorded at the level it binds: the
collection, the design, or the build.
_Avoid_: ADR log, rationale, out-of-scope file

**Owner**:
The skill whose output an artifact is, and the only one that confirms what it holds. Anyone
may read the artifact; another skill adds to it only as a **proposed entry**, and only when the
owner's contract lists it as a proposer.
_Avoid_: writer, author, maintainer

**Proposed entry**:
An entry a skill that does not own an artifact appends to it, marked as proposed with who
proposed it, when, and the evidence or the user's words behind it. It adds and never edits a
confirmed entry. The owner reviews it with the user and either promotes it or rejects it into
the **decision record**.
_Avoid_: suggestion, draft entry, TODO

**Answer**:
A value a user supplied to a question. Onboarding collects answers; they are inputs,
not decisions, and the decision gate does not apply to them.

## The product being described

**Feature**:
One capability a user can exercise, specified once and referenced everywhere.

**Featureset**:
A named group of related features. The only grouping level — features belong to exactly
one featureset, and nothing sits between them.
_Avoid_: feature group, group, epic, module

**Story**:
A user-facing goal in a journey, staged by importance. Feeds features; is not one.

**Screen**:
One specified view of the application. An artifact of its own: features reference screens,
a screen belongs to no feature.

**Component**:
A UI pattern shared across screens, specified once.

**Journey**:
An ordered path a persona takes across screens to reach a goal.

**App design**:
The set of interaction decisions for one application — where each object's information
lives, how it is edited, how users find and act on things, what saving and messages look
like. One per project, decided once and cited by every screen, so the app behaves as one
thing rather than as the sum of its screens.
_Avoid_: UX guidelines, style guide, design system (that is visual, not behavioural)

**Object type**:
A kind of thing users see and act on — an order, a customer, an invoice. The unit that app
design decides things for: each object type has its own place for information, editor and
representations.
_Avoid_: object class (what an object is, how it is reached and where it came from are three
separate facts in the glossary), entity (that is the data model's word for the stored thing),
resource, model

**Floorplan**:
A named layout template for one screen: its regions, which region is primary, where secondary
information sits, which surfaces tertiary information may use, how it folds on a narrow
viewport, and what may be a drawer and what must stay a page. Chosen from the rulebook per
screen, with a preview that can be seen before the screen is specified.
_Avoid_: wireframe, page template, layout, sitemap, IA (the per-object map is the **object map**)

**Shell frame**:
The app-wide floorplan, chosen once: the regions that persist around every screen and carry
navigation — a sidebar, a top bar, bottom tabs, a dock. Each screen's floorplan fills the
frame's work area.
_Avoid_: chrome, app layout, master page

**Navigation model**:
The app-wide choice of how people move between things: whether the app is organised by
objects, by tasks, or both, and which surface carries primary navigation. Recorded once, so
the shell frame realises it rather than re-inventing it; where it is still a fallback it is
visibly provisional.
_Avoid_: menu structure, sitemap, nav style

**Object map**:
The map of where each object type's information lives — its home, its index, its editor, how
it is created and deleted — and its representations. One row per object type. Not a
**floorplan**, which lays out a screen.
_Avoid_: floorplan, sitemap, navigation tree

**Posture**:
How a screen is used: **sovereign** (a long, daily work surface, optimised for people who
stay), **transient** (comes, does one job, leaves), or **auxiliary** (a supporting view beside
other work). Decides density, input richness and defaults; says nothing about who the user is.
_Avoid_: mode, persona, screen type

**Density**:
How much information a screen or table packs into its area — compact, default or comfortable,
one level per table. A floorplan and a posture each imply a default; a screen may override it.
_Avoid_: spacing (that is a brand token), size, zoom

**Tier**:
How much an attribute of an object type matters to the person looking: primary (always
shown), secondary (shown, summarised) or tertiary (only on demand, in a peek or popover, never
shown unasked). Set per object type and overridden sparingly per screen. Not a project's
**depth**.
_Avoid_: level, priority (that is a story's stage), rank

**Interaction concept**:
A named, reusable idea of how the app works — for example a saved view or a triage queue —
with its purpose, its operational principle, what it depends on, and where it appears.
Recorded once in the app design and referenced by screens, so one idea is not re-described on
each.
_Avoid_: pattern (a rule in the rulebook), feature, mode

**Surface**:
A place information appears or is edited — a page, a panel, a modal, a popover, an inline
field. App design assigns each object type's views and edits to surfaces.
_Avoid_: container, view, widget

**Representation**:
One way an object type is shown — a row, a card, a chip, a detail view, a table cell.
The same object type has several; app design fixes which appears where, so the same thing
looks the same wherever it turns up.
_Avoid_: view, display, layout

**Behavior**:
A formalized rule or state machine governing an entity's lifecycle.

## Doing the work

**Vertical slice**:
One user-facing increment built end to end — UI, logic, and data together. **Slice** is
its short form and always means this. Never a horizontal layer.
_Avoid_: tracer bullet, task, chunk, increment

**Dossier**:
The working directory for one feature's work — the notes, framing and decisions made
along the way, kept as documentation once done. A **feature dossier** carries concept
work; a **slice dossier** carries the build.
_Avoid_: workspace, scratch, folder

**Frozen**:
A dossier that has been indexed and closed. It stops being working state and becomes
documentation. Only dossiers freeze. Frozen says nothing about proof: a slice dossier's
`verification` says whether its manual checks have all been run.

**Seed scenario**:
One named shape of sample data — empty, single user, populated, edge cases — each
independently runnable against the database.
_Avoid_: seed mode, fixture, seed set
