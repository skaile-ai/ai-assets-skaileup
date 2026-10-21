# 0020 — Screens are independent artifacts

**Status:** accepted

Replaces the slug-directory rule for `07_screens/` in `tree/README.md § Naming` and the
screen half of `spec-feature`'s output. Amends nothing in [ADR 0007](0007-one-numbered-artifact-tree.md):
the tree still has `07_screens/` at the same place; only what sits below it changes.

## Context

A screen cannot be authored on its own (U2; sol graded it a blocker). `spec-feature` owned a
feature, its screens, its dossier and its decisions, and a screen's path lay under one feature
slug (`07_screens/<feature_slug>/<screen>.md`) although screens are shared between features. A
shell spec was gated on `05_features`. Describing a screen that already exists in code
therefore needed a feature first, and a second feature that used the same screen had no
honest path for it.

The screen spec also had no layout contract: `layout:` was fixed to the shell file, there was
no floorplan id, posture, density or tier declaration (U6, U7), and the wireframe sat in a
collapsed panel that does not prove the built UI realises the layout.

## Decision

**A screen is `_concept/07_screens/<screen>.md`, flat, with its own skill `experience-screen`.**

- The `[feature_slug]/` level disappears. `shell` stays reserved: `07_screens/shell.md` is the
  shell, not a screen.
- Identity is feature-free: `screen_id`. A screen carries `implements:` references to the
  features it realises; a feature carries `screens:` references. Both directions are
  references, each owned by the artifact that carries it; neither copies the other's content.
- A screen declares `floorplan:`, `posture:`, `density:`, region bindings and sparse
  `tier_overrides:` (see [ADR 0018](0018-the-rulebook-is-a-second-contract-asset.md) for the
  floorplan assets and [ADR 0021](0021-the-glossary-carries-the-light-ontology.md) for the
  terms the regions show).
- `experience-screen` derives a screen from scoped code evidence or asks, chooses a floorplan
  with the rulebook, and offers an early prototype from the floorplan preview with sample data
  (two variants on request) before the screen is specified.
- `spec-feature` calls the screen route; it does not write screen files itself. Where it
  needs something added to a screen it appends a `proposed` entry
  ([ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md)).

## Consequences

- The skill count gains `experience-screen`; `spec-feature` loses the screen half of its
  output but keeps feature, dossier and decision records.
- The shell is no longer gated on features; it reads the navigation model and the one
  destination list.
- `mockup-walkthrough` can render the screen's floorplan geometry, wide and narrow, instead of
  only the wireframe text.
- Existing `07_screens/<feature>/<screen>.md` trees are not migrated: the owner chose a clean
  slate, with no legacy path.
