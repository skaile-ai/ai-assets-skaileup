# CONTEXT — skaileup-tree

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
The asset that ships the tree: one dir-scoped thing named `shared-contracts`, installed
whole. There is exactly one contract and it holds nothing but the tree — what a skill
actually cites is a node inside it.
_Avoid_: reference file, shared docs

**Tree**:
The instruction mirror of `_concept/`, shipped as the one contract asset. One node per
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
A graph over skills, and the unit a project is sized by. Flow nodes name skills; edges order them;
the flow, not the filesystem, carries sequence. Choosing a flow and sizing the project are one
act — `01_meta/scope.yaml` records the flow id, and a skill that varies its depth reads that.
_Avoid_: pipeline, workflow, chain, tier

**Route**:
The ordered list of nodes a skill visits. A skill's body is its route and nothing else.
_Avoid_: steps, workflow

**Router**:
The one skill that names another skill instead of doing work — `skaileup`, the collection's
front door. It answers only where nothing else already does: work arriving from outside the
collection, and a `_concept/` tree opened cold. Which flow a project runs is `concept-scope`'s
answer and the host's before that; what follows a completed skill is the flow's own edges.
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

**Template**:
A tech-stack reference an implementation skill reads after the stack is chosen. Carries
**atoms** in its frontmatter (one value each, extracted by name) and **recipes** as named
sections (paragraphs, cited by heading). All stack-specific knowledge lives here; a skill
that needs a stack branch has found a missing template section. Not a profile, not a skill.
_Avoid_: stack profile, scaffold, boilerplate

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
`10_blueprint/datamodel/`. A description of data, not any running store.
_Avoid_: schema, data layer

**Database**:
The *materialised* datamodel — migrations applied and seed scenarios loaded in the built
app. What `build-database` produces from what `architecture-datamodel` designed.
_Avoid_: db, persistence, store

**Implementation**:
The build half — plans, slices, and the code itself.

**Grounding**:
Research, reference material and captured user input, available to every skill as
input regardless of which artifact it owns.
_Avoid_: context, background, inputs

**Standard**:
A convention discovered in an existing codebase, applied to new work.

**Glossary**:
A project's ubiquitous language — its own domain terms. Grown lazily as terms get
pinned, read by every skill so vocabulary does not drift. Distinct from this file.

**Decision record**:
An append-only note of a choice that was **hard to reverse**, **surprising without
context**, and a **real trade-off**. All three, or it is not one. A rejected scope
decision is a decision record marked rejected, not a separate store. Recorded at the
level it binds: the collection, the design, or the build.
_Avoid_: ADR log, rationale, out-of-scope file

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
One specified view of the application.

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
_Avoid_: object class (the rulebook uses *class* for core/supporting/child/junction/system),
entity (that is the data model's word for the stored thing), resource, model

**Floorplan**:
The map of where each object type's information lives in the app, and how the rooms
connect.
_Avoid_: sitemap, navigation tree, IA

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
documentation. Only dossiers freeze.

**Seed scenario**:
One named shape of sample data — empty, single user, populated, edge cases — each
independently runnable against the database.
_Avoid_: seed mode, fixture, seed set
