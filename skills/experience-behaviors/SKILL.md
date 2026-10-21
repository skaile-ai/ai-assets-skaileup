---
name: experience-behaviors
description: "Use when an entity's lifecycle has enough states that prose stops being precise about it. Writes the state machines and rules the feature specs and the screens are built against. Triggers on 'state machine', 'behavioral rules', 'formalize the lifecycle', 'what states can this be in'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: featuresets }
      - { id: grounding-findings }
      - { id: research-behavioral-patterns }
      - { id: glossary }
      - { id: datamodel }
      - { id: journeys }
    produces:
      - { id: behaviors, path: "_concept/06_behaviors/<featureset>.md" }
  prerequisites:
    files:
      - { path: "_concept/05_features", gate: soft }
      - { path: "_concept/02_grounding/findings", gate: soft }
      - { path: "_concept/02_grounding/research/behavioral-patterns.md", gate: soft }
      - { path: "_concept/glossary.md", gate: soft }
      - { path: "_concept/10_blueprint/datamodel", gate: soft }
      - { path: "_concept/04_journeys/stories.yaml", gate: soft }
---

# experience-behaviors

Writes `06_behaviors/<featureset>.md`: the states an entity can be in, what moves it between them, and what has to hold on either side. It is the optional step — the pipeline runs without it — and earns its place when a lifecycle has enough states that a feature spec's prose can no longer say precisely what is legal.

## Route

Read `tree/README.md` once per session, then these nodes in order — each holds the format and procedure for its part; this file holds only the order.

1. **Write the state tables** — `tree/06_behaviors/[featureset].md`: read the featuresets (or propose the featureset slug), find the entities with a life, write one file per featureset, name the constants, record open questions, report them to the user.
2. **Name entities and enums as the data model does** — `tree/10_blueprint/datamodel/README.md § Naming`; these tables read the model's names where it exists, else the glossary's (`tree/glossary.md § Where the words live`), and coin none.

**Done when** every featureset with a real lifecycle has a file, each entity in it has its states and a transition table, and the open questions have been put to the user.
