---
path: _concept/10_blueprint/openapi.yaml
summary: OpenAPI 3.2 contract of the HTTP API served to clients other than the own UI
writers: []
---

# _concept/10_blueprint/openapi.yaml

The machine-readable contract of the project's HTTP API, written by `architecture-system` only when the project serves an HTTP API to clients other than its own UI — always for project type `api-service`, never for `cli-tool` or `library`. It is not a `produces` entry of any skill, because the router and the host call a node done when every listed path exists; readers gate on it softly and treat a missing file as "no such API". `build-scaffold` creates route and client stubs from it, `build-implement` builds each endpoint against it, and `quality-e2e` derives its API-level cases (status codes, error bodies) from it. A reader that needs an endpoint or a payload changed hands back to `architecture-system` and never edits the file itself.

## Format

An [OpenAPI 3.2.0](https://spec.openapis.org/oas/v3.2.0.html) document in YAML, one path per endpoint that `protocols` in `tree/10_blueprint/architecture.md` and the features name:

```yaml
openapi: 3.2.0
info:
  title: Task API
  version: 0.1.0
paths:
  /tasks:
    get:
      operationId: listTasks
      summary: List the caller's tasks
      responses:
        "200":
          description: The tasks, newest first
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/Task" }
        "401":
          description: No valid credentials; the caller is asked to sign in
components:
  schemas:
    Task:
      type: object
      required: [id, title, status]
      properties:
        id: { type: string, format: uuid }
        title: { type: string, maxLength: 120 }
        status: { type: string, enum: [Draft, InReview, Published] }
```

- Request, response and error payload schemas are named for the entities in `_concept/10_blueprint/datamodel/model.json` (`Task`, `ProjectMember`), with field names and enum values as the model has them; where the model does not exist the names come from `_concept/glossary.md`. Names are read, never coined.
- Every operation carries an `operationId` and a response for each error behaviour the features and `tree/10_blueprint/architecture.md` describe, so the caller's view of a failure is written down once.
- Authentication is declared under `components.securitySchemes` and referenced by `security`, matching the auth the chosen template provides.

## Writing it

Written by `architecture-system` in step 7 of `tree/10_blueprint/architecture.md § Writing it`, after `architecture.md` and approved with it. Start from the endpoints the `protocols` list and the feature specs name, add one path per endpoint, then fill the schemas from the model.

## Checks

- The document is valid OpenAPI 3.2.0.
- Every schema name that matches an entity is that entity's `id`; no payload concept is invented.
- Every endpoint named in `architecture.md` and in the features has a path here, and no path exists that neither names.
