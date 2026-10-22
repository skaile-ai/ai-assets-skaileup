---
path: _concept/09_mockup/feedback/triage/
summary: deterministic routing of each open inbox note to the file it belongs in
owner: [mockup-feedback]
may_propose: []
---

# _concept/09_mockup/feedback/triage/

`triage/<round>.json`, written by `skills/mockup-feedback/scripts/triage.py` from the open items of the annotation inbox. It groups the notes by target file and records the ones that route nowhere, so the patch step works one file at a time and no comment is dropped silently.

## Format

JSON Schema (draft-07) for a triage file; field names are pinned and `triage.py` emits exactly these. `file` is relative to `_concept/`; `entity` appears on a group routed to the data model.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Triage",
  "type": "object",
  "required": ["roundId", "triagedAt", "groups", "unresolved"],
  "properties": {
    "roundId":    { "type": "string" },
    "triagedAt":  { "type": "string" },
    "groups": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["file", "items"],
        "properties": {
          "file":   { "type": "string" },
          "entity": { "type": "string" },
          "items":  { "type": "array", "items": { "type": "string" }, "minItems": 1 }
        }
      }
    },
    "unresolved": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["inboxId", "reason"],
        "properties": {
          "inboxId": { "type": "string" },
          "reason":  { "type": "string" }
        }
      }
    }
  }
}
```

An instance, showing the value shapes the schema leaves open (`triagedAt` is ISO-8601 UTC, `items` hold inbox ids, `reason` the router's sentence):

```json
{
  "roundId": "r-20261020T090000Z",
  "triagedAt": "2026-10-20T09:00:00Z",
  "groups": [
    { "file": "10_blueprint/datamodel/model.ts", "entity": "Task", "items": ["k3m9x2-1"] },
    { "file": "07_screens/inbox.md", "items": ["k3m9x2-2"] }
  ],
  "unresolved": [
    { "inboxId": "k3m9x2-3", "reason": "no component: note targets route /iframe.html" }
  ]
}
```

## Writing it

Run `python skills/mockup-feedback/scripts/triage.py <concept-root> <output-dir> [--inbox <dir>] [--round <id>]` (exit 0 even with unresolved notes; exit 1 on bad arguments or a missing inbox directory). It reads every `items/*.json` of the inbox whose `status` is `open`; the default inbox is `.data/annotations` beside `_concept/`. A note is routed by the first rule that matches, reading the source files the note names (the `target.ref` first, then the `vueComponents` chain from the innermost component out) and the story id in `url` (its `id=` query parameter):

- A source file under `src/entities/<Entity>/` → `10_blueprint/datamodel/model.ts` with `entity: <Entity>`; the file must exist and declare `export const <Entity>`, else the note is unresolved (`file not found` or `entity not found`).
- A source file `src/screens/<screen>.vue` → `07_screens/<screen>.md`, which must exist on disk.
- A story id `entities-<entity>-…` or `screens-<screen>--…` routes the same way when no source file names one, for a note whose chain ended in a library component.
- A story id starting `journeys-` → the whole of `04_journeys/stories.yaml`, where journeys live (the id identifies a journey within that file); the file must exist.
- A source file under `src/floorplans/` → unresolved, `rulebook asset`: the floorplan ships with `mockup-storybook`, no concept file carries it.
- Neither a source file nor a story id places the note → unresolved, `no component`. A click inside a library component (a Nuxt UI button) is a `target.kind: route` note without a source position of its own; the `vueComponents` chain still names our components, so it routes by the first rules. Paths under `node_modules/` are never ours and are skipped.

Every other source file is unresolved too (`no concept file for <path>`). The router never routes to the glossary: which glossary file holds a term depends on the project's `scope.yaml` `glossary` key, so the patch step chooses it for the notes that introduce a term. Report the unresolved count and every reason, since an unresolved note is a comment nobody will see again.

## Checks

`python skills/mockup-feedback/scripts/validate_triage.py <triage-json> [<inbox-dir>]` exits 0: every open note of the inbox appears in exactly one of `groups` or `unresolved`, none twice, group `file` values are non-empty strings, a group on `model.ts` names its `entity`, unresolved entries carry `inboxId` and `reason`.
