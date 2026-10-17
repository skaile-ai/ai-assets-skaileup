---
name: spec-featuresets
description: "Use when the journeys are approved and nothing has decided what the app's features are or how they group. Derives the feature roster from the stories and cuts it into featuresets, one entry per feature the loop will then specify. Triggers on 'what features do we need', 'group the features', 'plan the feature set'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: goals }
      - { id: journeys }
      - { id: research-competitors }
      - { id: glossary }
      - { id: datamodel }
    produces:
      - { id: featuresets, path: "_concept/05_features/featuresets.md" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: hard }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
      - { path: "_concept/02_grounding/research/competitors.md", gate: soft }
      - { path: "_concept/glossary.md", gate: soft }
      - { path: "_concept/10_blueprint/datamodel", gate: soft }
    inputs_optional:
      - { id: feature_scope, label: "How broad should the feature set be?", type: select, options: ["must-have only", "must-have + nice-to-have", "comprehensive"] }
---

# spec-featuresets

Writes `05_features/featuresets.md`: the featuresets this product has, and the features in each, named and prioritised. It draws the boundaries and writes no feature spec — `spec-feature` takes one roster entry at a time and turns it into the spec and its screens.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Derive, cluster, prioritise and write the roster** — `tree/05_features/featuresets.md`. The optional `feature_scope` answer calibrates what survives the priority cut.

**Done when** `05_features/featuresets.md` lists every featureset with its features, priorities and `story_refs`, every feature traces to a story or an explicit line of the brief, and the user has approved the roster.
