---
path: _concept/01_meta/
summary: project metadata — the user's expectations and the project's sizing
owner: []
may_propose: []
---

# _concept/01_meta/

Holds two files. `expectations.md` — what the user judges the result by and how they want to work with the agents, written by `skaileup` when a project has none (`tree/01_meta/expectations.md`). `scope.yaml` — the project's recorded `flow`, `project_type` and `depth`, written by `skaileup` when the first skill that needs a key finds it absent. A skill reads `scope.yaml` for how deep to go before it reads anything else, and works from the key's default when it is absent; its node is `tree/01_meta/scope.md`.
