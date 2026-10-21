---
path: _concept/09_mockup/feedback/triage/
summary: deterministic routing of each annotation to the file it belongs in
owner: [mockup-feedback]
may_propose: []
---

# _concept/09_mockup/feedback/triage/

`triage/<sid>.json`, written by `skills/mockup-feedback/scripts/triage.py` from `sessions/<sid>.json`. It groups the session's annotations by target file and records the ones that route nowhere, so the patch step works one file at a time and no comment is dropped silently.

## Format

JSON Schema (draft-07) for a triage file; field names are pinned and `triage.py` emits exactly these. `file` is relative to `_concept/`.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Triage",
  "type": "object",
  "required": ["sessionId", "triagedAt", "groups", "unresolved"],
  "properties": {
    "sessionId":  { "type": "string" },
    "triagedAt":  { "type": "string" },
    "groups": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["file", "annotations"],
        "properties": {
          "file": { "type": "string" },
          "annotations": { "type": "array", "items": { "type": "string" }, "minItems": 1 }
        }
      }
    },
    "unresolved": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["annotationId", "reason"],
        "properties": {
          "annotationId": { "type": "string" },
          "reason":       { "type": "string" }
        }
      }
    }
  }
}
```

An instance, showing the value shapes the schema leaves open (`triagedAt` is ISO-8601 UTC, `file` a path under `_concept/`, `reason` the router's sentence):

```json
{
  "sessionId": "<sid>",
  "triagedAt": "2026-01-01T12:00:00Z",
  "groups": [
    { "file": "07_screens/login.md", "annotations": ["ann-c1", "ann-c2"] }
  ],
  "unresolved": [
    { "annotationId": "ann-x", "reason": "no specRef target (screen and journey both absent or null)" }
  ]
}
```

## Writing it

Run `python skills/mockup-feedback/scripts/triage.py <session-json> <concept-root> <output-dir>` (exit 0 even with unresolved annotations; exit 1 on bad arguments or a malformed session). Routing by an annotation's `specRef`, screen before journey:

- `screen` set → `07_screens/<screen>.md`, which must exist on disk.
- `journey` set → the whole of `04_journeys/stories.yaml`, where journeys live (the value identifies a journey within that file); the file must exist.
- Neither → unresolved. An annotation made on `index.html` is unresolved by design: the site root carries no screen and no journey.
- There is no `feature` route, because no renderer emits `data-spec-feature`; routing a key nothing produces would read as coverage the loop lacks.

Report the unresolved count and every reason, since an unresolved annotation is a comment nobody will see again.

## Checks

`python skills/mockup-feedback/scripts/validate_triage.py <triage-json> [<session-json>]` exits 0: every session annotation appears in exactly one of `groups` or `unresolved`, none twice, group files are non-empty strings, unresolved entries carry `annotationId` and `reason`.
