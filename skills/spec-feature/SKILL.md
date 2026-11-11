---
name: spec-feature
description: "Use when one feature needs its permanent spec — compares it with the features and ideas that exist, grills the user, draws the in/out line, then writes the feature spec and adds its roster row. Triggers on 'spec this feature', 'what features do we need', 'group the features', 'lock down acceptance criteria', 'what is in vs out'."
version: "0.2.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: scope }
      - { id: brief }
      - { id: goals }
      - { id: journeys }
      - { id: research-competitors }
      - { id: grounding-findings }
      - { id: datamodel }
      - { id: glossary }
    produces:
      - { id: featuresets, path: "_concept/05_features/featuresets.md" }
      - { id: features, path: "_concept/05_features/<featureset>/<feature>.md" }
      - { id: dossier, path: "_concept/08_dossiers/<feature_slug>/index.md" }
      - { id: decisions, path: "_concept/10_blueprint/decisions.md" }
  prerequisites:
    files:
      - { path: "_concept/01_meta/scope.yaml", gate: soft }
      - { path: "_concept/brief.md", gate: soft }
      - { path: "_concept/glossary.md", gate: soft }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/02_grounding/research/competitors.md", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
      - { path: "_concept/10_blueprint/datamodel", gate: soft }
    inputs_optional:
      - { id: feature_scope, label: "How broad should the feature set be?", type: select, options: ["must-have only", "must-have + nice-to-have", "comprehensive"] }
---

# spec-feature

One feature, from a sentence to a spec somebody can build: the interview, the scope line, the feature spec, its row in the featureset roster and the frozen dossier. It handles one feature per run and runs once per feature; the roster `05_features/featuresets.md` grows by that run's row, so there is no separate roster session. It lists the screens a feature uses and calls `experience-screen` for one that does not exist yet; it writes no screen itself, since a screen is `experience-screen`'s artifact.

## Route

Read `tree/protocol/running.md` and `tree/protocol/ownership.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Resolve the facts, then run the feature procedure** — `tree/05_features/[featureset]/[feature].md`. Its steps 1–10 are the run's order; steps 2, 7 and 10 hand to items 2–3 below at the moment they name. Step 2 compares the feature with every spec, idea and `pattern` record and settles reuse, a pattern or a reason to keep it separate (`tree/10_blueprint/decisions.md § Patterns`). A missing brief, glossary, journeys or model is never a stop: step 3 reads what exists, derives the rest with a scoped `concept-reverse`, and batch-asks what is left; a missing term is filed as a proposed term per `tree/glossary.md § Where the words live`. Step 3 calls the Skill tool with "grilling"; without it, run the rounds yourself. Steps 4–5 pin each decision that passes the gate in `_concept/10_blueprint/decisions.md` (format and gate: `tree/10_blueprint/decisions.md`) while the grill runs; an OUT that clears the gate lands as `rejected`.
2. **Open the dossier at the similarity check, freeze it last** — `_concept/08_dossiers/<feature_slug>/index.md`, format and lifecycle in `tree/08_dossiers/[feature_slug]/index.md`.
3. **Add the roster row** — `_concept/05_features/featuresets.md`, per `tree/05_features/featuresets.md`: candidates come from the roster's `## Ideas` and the journeys' `candidate_features`, the priority is asked in the grill's first batch (the optional `feature_scope` answer calibrates the recommendation), and the featureset and role vocabulary grow only when the user confirms; an idea the run specifies moves into its featureset's table.
4. **List the screens and link them** — the feature's `screens:` names each existing `_concept/07_screens/<screen>.md` and the screen gets a proposed `implements:` entry (`tree/05_features/README.md § Links in both directions`); a screen that does not exist yet is created by calling `experience-screen` for it (Call the Skill tool with "experience-screen"), after which its proposed `screens:` entry is confirmed.

**Done when** the spec, its roster row and the frozen dossier are on disk, `follows:` names every record the feature follows, and every `screens:` entry names a screen that exists and whose `implements:` names this feature, the screens the feature needed included.
