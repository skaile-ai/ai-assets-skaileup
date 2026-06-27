# Anti-Horizontal Rules

Long-form expansion of the verbatim anti-horizontal-nudge template embedded
in `impl-plan-plan-vertical`. Read this when the SKILL.md body's nudge feels
abstract; come back when a row table looks vertical but smells horizontal.

## The verbatim nudge

> **DO NOT build all UI first, then all logic, then all data.**
>
> The default LLM failure mode for implementation planning is horizontal
> layering: "first scaffold every screen, then wire every handler, then run
> every migration." This produces N half-finished slices and zero working ones.
>
> Instead: pick ONE row from `## Vertical decomposition` and complete it
> end-to-end (UI renders → handler responds → data round-trips → test green)
> BEFORE starting the next row.

## Three counter-examples (horizontal decompositions this skill MUST refuse)

### Counter-example 1 — "screens first, wire later"

```markdown
| # | UI                | Logic | Data |
|---|-------------------|-------|------|
| 1 | All 5 screens     | -     | -    |
| 2 | -                 | All handlers | - |
| 3 | -                 | -     | All migrations |
```

Why it fails:
- Row 1 produces 5 screens that render nothing real. They drift visually
  before Row 2 even starts.
- Row 2 wires handlers against schemas that don't exist yet. Half the
  handlers will be rewritten in Row 3.
- Row 3 ships migrations whose contracts were guessed in Row 2.
- At every milestone, NOTHING is shippable.

### Counter-example 2 — "backend / frontend split"

```markdown
| # | UI               | Logic                     | Data |
|---|------------------|---------------------------|------|
| 1 | -                | API endpoints + handlers  | All migrations |
| 2 | All screens hooked up | -                    | -    |
```

Why it fails:
- This is the classic "agree on a contract, meet in the middle" pattern.
  In an LLM context it produces one massive blob row that's effectively
  the whole feature, not a slice.
- The UI in Row 2 finds at least one contract mismatch with Row 1's API
  shape. Rework cascades.
- The work is decomposed by ROLE (BE/FE), not by USER-FACING SLICE.

### Counter-example 3 — "MVP means just data"

```markdown
| # | UI       | Logic         | Data            |
|---|----------|---------------|-----------------|
| 1 | -        | CRUD handlers | New schema + seed |
| 2 | (later)  | (later)       | -               |
```

Why it fails:
- Row 1 produces a schema with no consumer. The schema reflects
  speculation, not verified UI need.
- Row 2 is a TODO, not a row.
- "MVP means just data" confuses TIER (appbuilder-mvp tier of skaileup) with
  LAYER (data layer). The appbuilder-mvp TIER still ships vertical rows.

## Worked example — a small, correctly vertical decomposition

Feature: `team-todo-comments` (members can comment on team todo items).

```markdown
| # | UI                                                | Logic                                           | Data                                              |
|---|---------------------------------------------------|-------------------------------------------------|---------------------------------------------------|
| 1 | List on todo detail panel (`screens/.../list.md`) | `comments.listForTodo(todoId)` query           | `comments` table read; FK→`todos`                 |
| 2 | Composer modal (`screens/.../composer.md`)        | `comments.create({todoId, body})` mutation      | `comments` insert; broadcast via Pusher           |
| 3 | Edit-own + delete-own affordances on row          | `comments.update`, `comments.softDelete`        | `comments.body` update; soft-delete via `deleted_at` |
```

Why this works:
- Row 1 is shippable: the panel renders comments end-to-end. If you stop
  here, you've delivered "view comments" — a real user value.
- Row 2 is shippable on top of Row 1: the create flow round-trips and
  broadcasts. If you stop here, you've delivered "view + create."
- Row 3 layers edit/delete on top. Each row is a vertical slice; each row
  passes its tests before the next begins.

## Why horizontal is the LLM default

LLMs learn to plan from textbooks and API docs that organise information
by LAYER (UI / Logic / Data). When asked "decompose this feature," the
gravity is toward the same layered taxonomy.

But layered planning is not work decomposition. It's an information
architecture. Real work is vertical: one user-facing slice at a time, each
with its UI/Logic/Data wired and tested before the next.

The anti-horizontal nudge has to be aggressive because the gravity is
strong. A soft "consider verticals" rolls right past the LLM's prior;
a verbatim DO-NOT block + four banned-thought triggers + an exact-string
validator check is the level of friction that compliance requires.

## Signals your decomposition is going horizontal

Stop and re-decompose if you find:

- Every Data cell is the same migration listed in three places.
- One row's UI cell is "all screens for this feature."
- One row's Logic cell is "all handlers."
- The number of rows equals the number of layers (UI/Logic/Data) — not
  the number of user-facing slices.
- A row title starts with "Phase" or "Sprint" or "Iteration."

## When a cell legitimately may be `-`

Rare cases where a row genuinely doesn't touch one column:

- A pure-UI polish row (e.g. row 5: "tighten label spacing on row 1's
  composer modal"). Logic and Data may be `-` IF the user has explicitly
  confirmed and the notes column logs the rationale.
- A pure-data migration row that exists only to back a row already
  shipped in a previous slice (and which therefore should arguably be in
  THAT slice's plan.md, not this one).

The validator emits a WARNING (not error) on empty cells precisely so
these legitimate cases pass — but the warning forces the author to
confirm the rationale rather than silently approve a horizontal smell.
