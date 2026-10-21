---
path: _concept/01_meta/
summary: project metadata — the sizing skills read when they need it
owner: []
may_propose: []
---

# _concept/01_meta/

Holds `scope.yaml` only — the project's recorded `flow`, `project_type` and `depth`, written by `skaileup` when the first skill that needs a key finds it absent. A skill reads the file for how deep to go before it reads anything else, and works from the key's default when it is absent; the file's own node is `tree/01_meta/scope.md`.
