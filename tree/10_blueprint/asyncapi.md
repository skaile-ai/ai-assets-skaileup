---
path: _concept/10_blueprint/asyncapi.yaml
summary: AsyncAPI 3.1 contract of the channels the project publishes or consumes
owner: []
may_propose: []
---

# _concept/10_blueprint/asyncapi.yaml

The machine-readable contract of the messages the project publishes or consumes on a channel — a broker, a websocket, a webhook stream — written by `architecture-system` only when the project has such a channel. It is not a `produces` entry of any skill, because the router and the host call a node done when every listed path exists; readers gate on it softly and treat a missing file as "no channels". `build-scaffold` creates channel and handler stubs from it and `build-implement` builds each send and receive operation against it. A reader that needs a channel or a message changed hands back to `architecture-system` and never edits the file itself.

## Format

An [AsyncAPI 3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0) document in YAML, with its channels, messages and the operations that send or receive them:

```yaml
asyncapi: 3.1.0
info:
  title: Task events
  version: 0.1.0
channels:
  taskCreated:
    address: tasks.created
    messages:
      TaskCreated:
        $ref: "#/components/messages/TaskCreated"
operations:
  publishTaskCreated:
    action: send
    channel:
      $ref: "#/channels/taskCreated"
    summary: Emitted once a task is saved
components:
  messages:
    TaskCreated:
      payload:
        $ref: "#/components/schemas/Task"
  schemas:
    Task:
      type: object
      required: [id, title]
      properties:
        id: { type: string, format: uuid }
        title: { type: string }
```

- Message payload schemas are named for the entities in `_concept/10_blueprint/datamodel/model.json`, with field names and enum values as the model has them; where the model does not exist the names come from `_concept/glossary.md`, and a payload concept with neither stops the step: name it and hand back to `concept-glossary`. Names are read, never coined.
- Each failed message names what the sender or receiver sees, which is the behaviour `tree/10_blueprint/architecture.md` wrote in prose.

## Writing it

Written by `architecture-system` in step 7 of `tree/10_blueprint/architecture.md § Writing it`, after `architecture.md` and approved with it. Start from the `protocols` list and the real-time and background-work signals in the features, add one channel per stream, then the operations and messages.

## Checks

- The document is valid AsyncAPI 3.1.0.
- Every payload schema that matches an entity is named by that entity's `id`; no payload concept is invented.
- Every channel and operation traces to a protocol in `architecture.md` or a feature.
