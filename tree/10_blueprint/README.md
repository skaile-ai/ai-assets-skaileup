---
path: _concept/10_blueprint/
summary: how the app is built — stack, architecture, API contracts, decisions, data model
owner: []
may_propose: []
---

# _concept/10_blueprint/

The design half of the build: the chosen technology (`techstack.md`), what the project adds beyond it as C4 levels (`architecture.md`), the HTTP and message contracts when the project has them (`openapi.yaml`, `asyncapi.yaml`), the decisions behind all of it (`decisions.md`) and the stack-neutral data model (`datamodel/`). Every skill from `build-scaffold` onward reads it, so a wrong entry here is built into every slice. Third-party services are recorded in `architecture.md § System context` and nowhere else in `_concept/`; `techstack.md` carries none. `openapi.yaml` and `asyncapi.yaml` are conditional: `architecture-system` writes each only when the project serves an HTTP API to other clients or publishes and consumes messages, and readers treat a missing one as "none".
