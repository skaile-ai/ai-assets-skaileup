# 0025 — Archetypes are an optional declared default

**Status:** accepted

Extends [ADR 0018](0018-the-rulebook-is-a-second-contract-asset.md): the rulebook gains one file,
`archetypes.md`, shipped in the same asset. Extends
[ADR 0015](0015-interaction-decisions-live-in-app-design.md): `APP-DESIGN.md § Navigation model`
carries one more field, `archetype:`.

## Context

The ARC effort researched ten app archetypes — a device and a data weight pick a shell frame, the
frame holds screen floorplans in journey order, and a short list names the defaults that commonly
bend — as cards under `docs/app-archetypes/`, each with three to five free sources, a journey, the
`P18` phrase per floorplan, the phone case and open questions. A throwaway dashboard rendered every
screen as its rulebook preview at two widths for comment.

The question was whether any of it belongs in the skill set, given that models improve at laying
out a screen. Two findings decided it. First, most of a card restates `rulebook/rules.md` in prose,
and the review of the cards found that prose drifting from the rules within one session: paraphrased
`P18` quotes, two bends their `DF` texts do not support, one contradiction with a cited source. A
second copy of a rule is a maintenance cost the rulebook itself does not pay. Second, what the cards
carry that a better model does not supply on its own is small and specific: one *name* for a
composition that holds across sessions and agents, so screen five stays coherent with screen one and
a check has a baseline to diff against; and about eight measured facts (pane ratios, breakpoints,
column widths, step limits) that belong to the floorplan they describe.

## Decision

**K1 — Optional.** `APP-DESIGN.md § Navigation model` names `archetype: <id>` or
`archetype: none`. With `none`, every skill behaves as it does today; `P18` and `P22` decide the
frame and the floorplans. With an id, the row's frame and floorplans are the app's defaults, and
the checks in `tree/APP-DESIGN.md` and `tree/07_screens/shell.md` hold the shell and the screen
defaults to them. No skill requires an archetype and no skill route changes.

**K2 — One normative table, in the rulebook.** `rulebook/archetypes.md` holds ten rows: id,
device, data weight, organization, primary surface, shell frame, journey floorplans, the `DF` ids
that usually bend. No purpose prose, no example apps, no sources. It ships in the
`app-design-rulebook` asset because it sits in the directory; `rulebook/README.md § Files` and
`rules.md § P18` make it reachable.

**K3 — The cards are evidence, not rules.** `docs/app-archetypes/<id>.md` stay as the research
behind each row and the place to refine one. A refinement reaches a skill only when the row
changes; `scripts/check.py` fails while a card's frame or journey floorplans differ from its row,
or while a row and a card do not pair up.

**K4 — Departures are entries, not exceptions.** An archetype is a default. An app that starts
from one and changes a frame or a floorplan writes a NAV entry naming the departure and why; it is
not a `§ Exceptions` row, because no rule's obligation is removed.

**K5 — The measured facts go where readers look.** Each number the research established is one
sentence in the floorplan section or default it binds, ending with its source title, and the source
has a row in `docs/layout-pattern-sources.md`.

## Options rejected

- **Ship the cards as an asset.** Prose copies of rules drift, as the review showed within a
  session; `## Example apps` is plausible and unsourced; and ten reviewed compositions read by
  every skill become the design, which is the convergence the rulebook's exceptions exist to
  prevent.
- **Require the field.** Same convergence, by a shorter path: the moment a skill needs an
  archetype, a project that fits none is pushed into one.
- **Keep the research as docs only.** Nothing reads `docs/`, so the one thing worth keeping — a
  declared name a check can hold the app to — never decides a tie.

## Consequences

- `rulebook/archetypes.md` is the one normative form; a change to an archetype is a change to a row,
  after its card.
- `experience-interaction` proposes a matching row when device and data weight are known and
  prefills `§ Screen defaults` from its journey, marked `[inferred]`; `experience-shell` starts from
  the declared row's frame.
- `quality-design` and `quality-interaction` have a baseline: with a declared id, a shell frame or
  a floorplan that differs from the row without a NAV entry is a finding.
- `scripts/check.py` gains `archetype-shape` and `archetype-card-sync`; a repo without
  `rulebook/archetypes.md` has nothing to check.
- The dashboard stays a throwaway under `.scratch/` and is not part of the collection.
- If after a few projects the declared archetype never decides a tie, the field and the table are
  removed; the cards remain research either way.
