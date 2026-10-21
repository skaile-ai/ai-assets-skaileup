---
path: [_concept/09_mockup/feedback/sessions/, _concept/09_mockup/feedback/sessions/<sessionId>.json]
summary: raw annotation sessions downloaded from the overlay, one file per round
owner: [mockup-annotate]
may_propose: []
---

# _concept/09_mockup/feedback/sessions/

One `<sessionId>.json` per stakeholder round: the file the overlay's **Download** button writes, filed here by `mockup-feedback` when it adopts it. The directory is gitignored; `applied/<sid>.json` is the lasting record once sessions rotate. The file is named from its own `sessionId` field and never from the path it arrived under, because triage, patching and the audit trail key on that field and a disagreeing stem produces a round that reads as unapplied forever.

## Format

JSON Schema (draft-07) for a session file; field names and the `category` / `status` values are pinned. `label` is absent in a fresh download and written by `mockup-feedback` on adoption. Extra properties are allowed.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Session",
  "type": "object",
  "required": ["sessionId", "annotations"],
  "properties": {
    "sessionId": { "type": "string", "minLength": 1 },
    "label": {
      "description": "Human-readable name for this feedback round, written by mockup-feedback when it adopts the file. Absent in a freshly downloaded session.",
      "type": "string",
      "minLength": 1
    },
    "annotations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "sessionId", "specRef", "body", "category", "status"],
        "properties": {
          "id":        { "type": "string" },
          "sessionId": { "type": "string" },
          "createdAt": { "type": "string" },
          "specRef": {
            "type": "object",
            "required": ["element"],
            "properties": {
              "element":     { "type": "string", "minLength": 1 },
              "screen":      { "type": ["string", "null"] },
              "journey":     { "type": ["string", "null"] },
              "route":       { "type": ["string", "null"] },
              "provisional": { "type": "boolean" }
            }
          },
          "body":     { "type": "string" },
          "category": { "type": "string", "enum": ["change", "add", "remove", "question"] },
          "status":   { "type": "string", "enum": ["open", "applied", "dismissed"] }
        }
      }
    }
  },
  "additionalProperties": true
}
```

Each annotation carries the element, screen, journey and route it was made against, the reader's text, a category, and whether the element's id was provisional. An annotation id is unique within its session only.

## Writing it

`mockup-annotate` creates the empty directory and gitignores it; it never writes a session. `mockup-feedback` adopts a returned file (`tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)`, step 1): validate against the schema above, copy to `sessions/<sessionId>.json`, ask the user for the round's name and store it as `label`, and replace an existing file of the same `sessionId` while keeping its `label`.

## Checks

The file validates against the schema; its filename stem equals its `sessionId`.
