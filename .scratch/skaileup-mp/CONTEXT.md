# CONTEXT — skaileup-mp

The ubiquitous language of this collection: the words its skills use to talk to each
other, to the flow engine, and to forge-concept. Every skill uses the canonical term
and never redefines it locally.

This file is a **glossary and nothing else** — no paths, no schemas, no process. Where
a thing lives is `contracts/concept_structure.md`'s job; what it *is* is this file's.

## The collection

**Asset**:
A versioned thing this repo ships — a skill, a flow, a contract, or a reference file.
_Avoid_: resource, module, package

**Skill**:
One unit of agent work with a `name:` that is its whole identity — install path, flow
node reference, and grounding key all at once.

**Flow**:
A graph over skills. Nodes name skills; edges order them. The flow, not the filesystem,
carries sequence.
_Avoid_: pipeline, workflow, chain

**Tier**:
How much of the pipeline a project runs. A sizing decision made once, at the start.
_Avoid_: level, mode, depth

**Phase**:
The lane a flow node belongs to — conceptualization, implementation, or review. A
machine-read contract with forge-concept; never used loosely for "stage of work".
_Avoid_: stage, step, lane

**Session boundary**:
The point where an agent hands work on — continue, clear, hand off, or dispatch a
subagent. Deliberately *not* called a phase boundary, because `phase` is taken.

**Gate**:
A precondition on running a skill. **Hard** refuses to proceed; **soft** warns and
continues. Every gate is one or the other, stated at the step it binds.
_Avoid_: guard, check, blocker, prerequisite

**Profile**:
A project's type — web-app, cli-tool, api-service, library, mobile-app, data-pipeline.
Chosen once; selects which artifacts a project is expected to grow.
_Avoid_: kind, category, project type

**Template**:
A tech-stack reference an implementation skill reads after the stack is chosen. Not a
profile, not a skill.
_Avoid_: stack profile, scaffold, boilerplate

## What a project grows

**Artifact**:
A file a skill writes into a target project. The unit of everything this collection
produces.
_Avoid_: output, deliverable, result, product

**Concept**:
The design half of a project — what is being built and why, before any code.
_Avoid_: discovery, spec phase

**Blueprint**:
The technical design a concept resolves to: stack, architecture, data model, glossary.
Still design, not code.

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
