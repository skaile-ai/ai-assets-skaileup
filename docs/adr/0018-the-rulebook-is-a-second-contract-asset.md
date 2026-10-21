# 0018 — The rulebook is a second contract asset

**Status:** accepted

Supersedes the "no cross-cutting rulebooks" consequence and the "one dir-scoped contract
asset" sentence of [ADR 0017](0017-the-instruction-tree-mirrors-the-artifact-tree.md) for this
one asset. Amends [ADR 0015](0015-interaction-decisions-live-in-app-design.md): the rules leave
the `APP-DESIGN.md` node; the file itself, its root placement and its single owner stand.

## Context

The application-design rules — patterns P1–P17 and a catalogue of surface, modal, popup,
editing, message, button, find and navigation decisions — sit inside `tree/APP-DESIGN.md`, a
322-line node that is at the same time the format of the per-app file. Two different things
share one page: what a project's `APP-DESIGN.md` looks like, and the rules every project's
design is judged by. Both critics reached the same finding (U5): the rulebook is cross-cutting
but hidden inside one artifact's node, and ADR 0017 says a cross-cutting rulebook cannot exist.

Field evidence makes the cost concrete. CLINICO and weiterbildungsplaner each re-derived about
fifteen of the same rules in their own `APP-DESIGN.md` (surface ladder, drawer never an editor,
no dialog over a dialog, footer order, one editor per type, one action registry). Layout rules
landed in surface and navigation entries because the rulebook had no slot for them; one project
split its floorplan out of the file because it blew the line budget. A review also needs the
rules separated into invariants and tunable heuristics (a dialog field limit of ~12 or
~16 is a decision, not a law).

ADR 0017's argument was that a rule at the part it binds cannot drift from it. That holds for
a rule about one `_concept/` part. An app-design rule binds screens, the shell, interaction
planning and the quality check at once; there is no single part to host it.

## Decision

**A second contract asset, `rulebook/`, contract `app-design-rulebook`.** It holds the rules
skills cite, not the artifacts they write:

- `CONTRACT.md` — the asset's manifest.
- `README.md` — how to read the rules, the id scheme and strength grades.
- `rules.md` — P1–P17 revised, new rules from the research (floorplan selection, posture,
  density, information tiers, navigation model, view-state restore, disclosure depth, visible
  modes, latency feedback, and others), and a **heuristics table**: each tunable value with
  its source strength and the rule that the app adopts a value in `APP-DESIGN.md`.
- `defaults.md` — the rules two projects re-derived independently, as an adoptable bundle.
- `floorplans/<id>/` — layout templates, each a README plus a self-contained preview
  (see the Floorplan and Shell frame entries in [`CONTEXT.md`](../../CONTEXT.md)).

`tree/APP-DESIGN.md` shrinks to the artifact node: the format of the per-app file, its
decisions and its checks. Rule ids keep their P-numbers where the rule survives, so existing
per-project files stay readable.

**Skills that read rules declare the contract** in their `metadata`, the way tree readers
already do. `scripts/check.py` replaces its one-manifest rule with exactly two: the tree
(`shared-contracts`) and the rulebook.

**The exception is this asset only.** Any other topic that spans parts is still stated at each
part it binds, in one clause, or lives in `tree/README.md` when it is about the tree itself.

## Alternatives

**Keep the rules in the `APP-DESIGN.md` node.** Rejected: it is the status quo and the source
of U5 — the node is already 322 lines and has no room for floorplans or heuristics.

**A `_rulebook/` directory inside `tree/`, hidden from the mirror.** One manifest, no installer risk,
but a non-mirror directory in a tree that ADR 0017 defines as a mirror of `_concept/`, and it
needs a `load_tree` exemption. Held back as the fallback: [INFERENCE] `@skaile/workspaces`
discovers every `CONTRACT.md` recursively; if the installer refuses a second contract, this
option replaces the second manifest.

## Consequences

- The `APP-DESIGN.md` node loses its rulebook; skills that planned or checked against the rules
  cite the rulebook contract instead.
- Floorplan assets get typed checks in `check.py` (preview present, id cited by a rule); a new
  asset subtype needs its own contract, as templates do ([ADR 0009](0009-stack-knowledge-lives-in-templates.md)).
- Invariants and heuristics are separated: a check enforces invariants always and heuristics
  only at the value the app adopted.
- ADR 0017's remaining decisions (mirror, node shape, route) stand unchanged.
