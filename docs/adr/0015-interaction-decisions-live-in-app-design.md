# 0015 — Interaction decisions live in `APP-DESIGN.md` at the project root

**Status:** accepted

Amends the path rule in [ADR 0011](0011-the-machine-layer-sits-under-metadata.md) and the
`produces` path rule in [ADR 0013](0013-a-skill-declares-what-it-produces.md): one named
artifact may sit outside `_concept/`.

## Context

The collection decides what a product is and what it is built from. It does not decide *how
people use it*: where an object's information lives, whether it is edited inline, in a panel or
in a modal, when a change saves, what a message says and how it is worded, how users find and
act on things. Those decisions get made anyway — by whichever skill writes the screen, one
screen at a time — and the app drifts into several interaction dialects.

Three global skills already work this problem: `experience-app-guideline`, `experience-app-objects`
and `experience-app-interview` (v0.3.2), with a pattern library (P1–P17), an `APP-DESIGN.md`
shape and a UI-detection recipe. They record their decisions in `APP-DESIGN.md` at the project
root, and coding agents and the global skills look for it there.

Two facts stop a straight reuse. This collection never calls the global skills — ADR 0012 lets
five foreign skills stay global and gate-checked, and these are not among them — so a
dependence would be an unchecked one. And the global skills coin names: an object type is
named from the conversation, where this collection reads entity names from the data model and
the glossary.

The placement is the sharper problem. ADR 0011 requires every declared path outside
`PROJECT_ROOT_PREREQUISITES` (`package.json`) to start with `_concept/`, and ADR 0013
requires every `produces` path to appear in the tree fence. An interaction record at the
project root satisfies neither.

## Decision

**`APP-DESIGN.md` lives at the project root — the directory that holds `_concept/` — and is
the one project-root artifact a skill may produce.** It is named in `scripts/check.py`'s
`PROJECT_ROOT_ARTIFACTS`; a `produces` path is legal if it starts with `_concept/` and is in
the tree, or if it is named there. Nothing else leaves `_concept/`. There is one per project: a
monorepo whose apps each carry a `_concept/` has one `APP-DESIGN.md` per app, because each app
is a project.

**The rulebook is forked, not called.** The patterns, the `APP-DESIGN.md` shape and the
UI-detection recipe become three contract files — `contracts/interaction_patterns.md`,
`contracts/app_design.md` and `contracts/ui_detection.md` — read at the step that needs them.
The global skills are not `EXTERNAL_SKILLS` (ADR 0012), because the collection never calls
them. The two new skills take distinct names so the collection and the global skills install
side by side without a collision. The fork is deliberate: it drifts on its own lifecycle, and
a change to either side is not a defect in the other.

**One writer.** `experience-interaction` plans interaction and is the only skill that writes
`APP-DESIGN.md`. `quality-interaction` checks the app's source (`src/` or the stack's own
roots) against it and writes its own verdict, `_concept/11_build/interaction.yaml`; it never
edits `APP-DESIGN.md`. A contested item goes
back to `experience-interaction`, which decides.

**Verdict path amended by [ADR 0016](0016-published-formats-where-one-exists.md)**
(2026-10-17). `quality-interaction`'s verdict moved from `11_build/interaction.yaml` to
`11_build/interaction.sarif` (SARIF 2.1.0). The one-writer rule above stands.

**Names are read, never coined.** Object types take their names from `model.json` and
`glossary.md`. Pattern P13 (naming) points at `_concept/glossary.md`; a concept with no term
goes back to `concept-glossary` (ADR 0014).

## Alternatives

**Inside the tree — `_concept/07_screens/interaction.md`.** It satisfies ADR 0011 and ADR 0013
without an exception. Rejected by the user: coding agents and the global skills look for
`APP-DESIGN.md` at the project root, and a file that exists only where nothing looks for it
records decisions no later session reads.

**Both — a concept file plus an exported copy at the root.** Rejected on the argument that
rejected the generated registry in ADR 0013: two copies need a freshness rule — a check that
they match and a step that regenerates one — to stay honest. That trades a missing placement
for a standing maintenance obligation.

## Consequences

- **No host reads `produces` yet** (ADR 0013). When one does, it must join `APP-DESIGN.md` to
  the project root and not to `_concept/`; a reader that prefixes every `produces` path with
  `_concept/` would look in the wrong place.
- `scripts/check.py` gains `PROJECT_ROOT_ARTIFACTS` beside `PROJECT_ROOT_PREREQUISITES`. The
  exception is a named list, not a pattern, for ADR 0011's drift reason: a loose rule would
  let a superseded concept path pass as "some project-root file".
- `contracts/concept_structure.md` names `APP-DESIGN.md` in a section beside the tree and
  adds two files to the tree: `02_grounding/findings/interaction.md` (written by
  `concept-reverse`, the census of how the code behaves today) and
  `11_build/interaction.yaml` (written by `quality-interaction`).
- `CONTEXT.md` gains the terms the planning skill and the check share: App design, Object
  type, Floorplan, Surface, Representation.
- `APP-DESIGN.md` also joins `PROJECT_ROOT_PREREQUISITES`, so skills may gate on it.
- The five-skill foreign list (ADR 0012) is unchanged; the forked contracts are ordinary
  contract files and obey ADR 0004 — each is read at a step in a body.
- **Existing projects are not migrated.** A project that already has an `APP-DESIGN.md` from
  the global skills keeps it; the first `experience-interaction` run reads it as input.
