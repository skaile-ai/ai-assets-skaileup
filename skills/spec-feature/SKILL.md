---
name: spec-feature
description: "Use when one feature needs its permanent spec — grills the user, draws the in/out line, then writes the feature spec and every screen it needs. Triggers on 'spec this feature', 'design a new feature', 'lock down acceptance criteria', 'what is in vs out'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: scope }
      - { id: brief }
      - { id: journeys }
      - { id: brand-tokens }
      - { id: datamodel }
      - { id: glossary }
    produces:
      - { id: features, path: "_concept/05_features/<featureset>/<feature>.md" }
      - { id: screens, path: "_concept/07_screens/<feature_slug>/<screen>.md" }
      - { id: dossier, path: "_concept/08_dossiers/<feature_slug>/index.md" }
      - { id: decisions, path: "_concept/10_blueprint/decisions.md" }
  prerequisites:
    files:
      - { path: "_concept/01_meta/scope.yaml", gate: hard }
      - { path: "_concept/brief.md", gate: hard }
      - { path: "_concept/glossary.md", gate: hard }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/10_blueprint/datamodel", gate: soft }
---

# spec-feature

One feature, from a sentence to a spec somebody can build: the interview, the scope line, the feature spec, its screen specs and the frozen dossier. It is the only writer of screen specs and of their `elements:` blocks, handles one feature per run, and is re-entered once per feature in `05_features/featuresets.md` — the flow graph draws it once.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Run the feature procedure** — `tree/05_features/[featureset]/[feature].md`. Its steps 1–9 are the run's order; steps 2, 6–7 and 9 hand to items 2–3 below at the moment they name. Step 2 calls the Skill tool with "grilling"; without it, run the rounds yourself. Steps 3–4 pin each decision that passes the gate in `_concept/10_blueprint/decisions.md` (format and gate: `tree/10_blueprint/decisions.md`) while the grill runs; an OUT that clears the gate lands as `rejected`.
2. **Open the dossier at the grill, freeze it last** — `_concept/08_dossiers/<feature_slug>/index.md`, format and lifecycle in `tree/08_dossiers/[feature_slug]/index.md`.
3. **Write the screens and register both directions** — `_concept/07_screens/<feature_slug>/<screen>.md`: `tree/07_screens/README.md` for the `elements:` block, then `tree/07_screens/[feature_slug]/[screen].md`.

**Done when** the spec, every screen it names and the frozen dossier are on disk, and the feature's `screens:` and each screen's `implements:` resolve to each other.
