---
path: _concept/09_mockup/feedback/patches/
summary: proposed anchored patches and the review file a human approves
owner: [mockup-feedback]
may_propose: []
---

# _concept/09_mockup/feedback/patches/

Per round, `patches/<round>.json` (the machine patch set) and `patches/<round>.review.md` (the approval gate), written together by `mockup-feedback` and gitignored. `apply.py` applies only the patches the human left checked in the review file, so every format below is read by a script: a drifting anchor or a de-bolded patch id makes a patch fail or vanish.

## Format

### Anchored diffs

Every diff anchors to a heading or to a named block, never to a line number: concept files are edited by hand between feedback rounds, so an offset computed at proposal time is wrong by apply time.

```
@@ ## Section Name @@
- line to remove (full content, including the markdown bullet)
+ line to add
```

The anchors `apply.py` knows:

| Anchor | Target | Diff |
|---|---|---|
| `## Heading` | a markdown section | removes and adds; no removes appends to the end of the section, and a missing section is appended to the file as `kind: create-section` |
| `frontmatter:elements` | a screen's `elements:` block | removes and adds inside the YAML frontmatter |
| `before:## Heading` | the line above a heading | adds only; used for a glossary term placed ahead of `## Relations` |
| `ts:entity/<Id>/fields` | the `fields: { … }` block of entity `<Id>` in `model.ts` | adds only: one field line each, inserted before the block's closing `  },` |
| `ts:model/entities` | the entity exports of `model.ts` | adds only: one complete `export const <Id> = entity({ … })` block, inserted above `export const model = defineModel({`, and its `    <Id>,` line in the model's `entities` map |

What `apply.py` does with these:

- A heading anchor matches a heading line **exactly**: `@@ ## Layout @@` needs a literal `## Layout` line in the file.
- Removed lines exist in that section as a **consecutive block**, matched exactly; the first mismatch fails that patch and only that patch.
- There are no context lines; a line starting with neither `-` nor `+` is ignored.
- A `ts:` anchor names an entity `model.ts` declares, else the patch fails; after the file is written `gen.ts` runs and a rejection restores the file and fails every `ts:` patch of the round.

### Kinds

| Kind | Edits | Diff |
|---|---|---|
| `content` | a screen spec | anchored section diff; the author rewrites the section the note's element sits in, scoped to the lines that move |
| `create-section` | a screen spec | the section did not exist: adds appended to the file |
| `model-proposal` | `10_blueprint/datamodel/model.ts` | `ts:` anchors, adds only |
| `glossary-proposal` | the project glossary | `before:` or heading anchor, adds only |

**`model-proposal`.** A field line or an entity block in the layout of `tree/10_blueprint/datamodel/model.md § Format` (two-space indent, one field per line), carrying the marker `proposed: { by: 'mockup-feedback', on: '<YYYY-MM-DD>', source: '<inboxId>' }`: as a field option on a field line, as an entity option on an entity block. `source` names a note the patch resolves. The diff removes nothing.

```
@@ ts:entity/Task/fields @@
+    estimate: f.decimal({ required: false, proposed: { by: 'mockup-feedback', on: '2026-10-23', source: 'k3m9x2-1' } }),
```

**`glossary-proposal`.** One term, with its four marker lines (`- status: proposed`, `- proposed_by: mockup-feedback`, `- proposed_on: <date>`, `- source: <the note's words> (<inboxId>)`), in the layout the glossary's mode asks for (`tree/glossary.md § Where the words live`, *Proposed terms*). It accompanies the model proposal that introduces the entity: a term and its entity are filed together, or the model entry has no word to point at (`glossary: '<id>'`). The patch step reads `scope.yaml` `glossary` to choose the file; the triage file never names it.

### `patches/<round>.json`

`file` is relative to the concept root, with no `_concept/` prefix. Ids follow `p-<inboxId>-<kind>` (`-content`, `-model`, `-glossary`). Every patch carries `resolves[]`: the notes it answers, each with the status the inbox will record and the resolution sentence.

```json
{
  "roundId": "<round>",
  "proposedAt": "<ISO-8601 UTC>",
  "patches": [
    {
      "id": "p-k3m9x2-1-model",
      "inboxId": "k3m9x2-1",
      "file": "10_blueprint/datamodel/model.ts",
      "section": "ts:entity/Task/fields",
      "kind": "model-proposal",
      "category": null,
      "body": "The editor needs an estimate field.",
      "diff": "@@ ts:entity/Task/fields @@\n+    estimate: f.decimal({ required: false, proposed: { by: 'mockup-feedback', on: '2026-10-23', source: 'k3m9x2-1' } }),\n",
      "resolves": [
        { "id": "k3m9x2-1", "status": "implemented", "resolution": "Task.estimate proposed in model.ts." }
      ]
    }
  ],
  "needs_manual": [
    { "inboxId": "<id>", "reason": "<why no patch could be authored>" }
  ]
}
```

Every triaged note ends in `patches[]` (as the `inboxId` of a patch or in a `resolves[]`) or in `needs_manual[]` (exactly once), never both and never neither. A note several patches answer (a model proposal and its glossary term) carries the same status and resolution in each. A `needs_manual` note stays open in the inbox, and the next triage lists it again. JSON Schema (draft-07):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Patches",
  "type": "object",
  "required": ["roundId", "proposedAt", "patches", "needs_manual"],
  "properties": {
    "roundId":    { "type": "string" },
    "proposedAt": { "type": "string" },
    "patches": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "inboxId", "file", "section", "kind", "body", "diff", "resolves"],
        "properties": {
          "id":      { "type": "string" },
          "inboxId": { "type": "string" },
          "file":    { "type": "string" },
          "section": { "type": "string" },
          "kind":    { "type": "string", "enum": ["content", "create-section", "model-proposal", "glossary-proposal"] },
          "category": { "type": ["string", "null"] },
          "body":    { "type": "string", "description": "The note's comment, copied verbatim; kept in applied/ as the lasting record" },
          "diff":    { "type": "string" },
          "resolves": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "required": ["id", "status", "resolution"],
              "properties": {
                "id":         { "type": "string" },
                "status":     { "type": "string", "enum": ["implemented", "rejected"] },
                "resolution": { "type": "string", "minLength": 1 }
              }
            }
          }
        }
      }
    },
    "needs_manual": {
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

### Content categories

A `content` patch may carry one `category` that names its diff shape; `null` means a free rewrite. The shapes are templates, matched exactly.

| Category | Diff |
|---|---|
| `change` | Rewrite the section the note's element sits in, scoped to the lines that move. |
| `add` | `@@ ## States @@` then `+ - <note comment>`, under the section the addition belongs to: `## States` for a state, `## Behavior` for a behaviour. |
| `remove` | `@@ ## <section> @@`, then the original line as a remove and the same line struck through as an add: `+ - ~~<original line>~~`. Strikethrough, not deletion, so the review file shows what a reader asked to drop. |
| `question` | `@@ ## Open Questions @@` then `+ - <note comment>`, creating the section if absent. |

### `patches/<round>.review.md`

The approval gate. `apply.py` reads exactly one thing from it, `- [x] **<patch-id>**`, so the patch id is bold and immediately follows the checkbox.

```markdown
# Review patches for round <round> (N patches across M files)

## Needs manual review

- note `<id>` — <reason>

## <file path>

- [x] **<patch-id>** · <kind or category> · note: "<comment preview>"
  ```diff
  <diff text>
  ```

## Test impact

Re-run the quality-test skill after applying — these spec changes affect coverage:

- `<file>` — <Happy|Error|Edge|Permissions>: <suggested scenario> (AC: <story-id>)
```

Every auto-generated patch starts checked; the user unchecks to skip and may edit a diff or a resolution in place. Omit `## Needs manual review` and `## Test impact` when they would be empty. A patch changes testable behaviour when it touches `## Behavior`, `## States`, `## Requirements`, `## Error States`, `## Success Criteria` or `## Permissions` in a screen file, or when an `add` introduces a new state, behaviour or error case; each gets one suggested scenario under `## Test impact`. The scenarios are notes, not patches: no checkbox, and `apply.py` ignores them. Copy, token and layout changes have no test impact; leave them out rather than listing them as unaffected.

## Writing it

Author one patch per note per `tree/09_mockup/feedback/README.md § Filing feedback (mockup-feedback)` step 3, then write `.json` and `.review.md` together.

## Checks

`python skills/mockup-feedback/scripts/validate_patches.py <triage-json> <patches-json> <review-md>` exits 0: the partition invariant above holds; a `content` patch's `file` matches its note's triaged file and a `model-proposal` patch edits `10_blueprint/datamodel/model.ts`; each diff starts with a valid `@@` anchor and `ts:` anchors appear on `model-proposal` patches only; every patch has `resolves[]` listing its own note with a status and a non-empty resolution, identical across the patches of one note; a `model-proposal` adds lines only, each marker well formed with a `source` that names a resolved note; a `glossary-proposal` carries the four marker lines; every patch has a `- [x]` item in the review file; every `needs_manual` entry has a bullet under `## Needs manual review` and no checklist item; `add` / `remove` / `question` diffs match their templates.
