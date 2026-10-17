---
path: _concept/06_behaviors/
summary: optional state machines and rules, one file per featureset
writers: []
---

# _concept/06_behaviors/

Optional: the pipeline runs without this folder, and a reader checks that it exists before reading. It earns its place when an entity's lifecycle has enough states that a feature spec's prose can no longer say precisely what is legal. One file per featureset, described in `tree/06_behaviors/[featureset].md`; the feature loop reads it where it exists.
