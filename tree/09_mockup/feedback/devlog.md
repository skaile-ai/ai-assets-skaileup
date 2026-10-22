---
path: _concept/09_mockup/feedback/devlog.md
summary: append-only log of feedback edits, read so a regeneration keeps them
owner: [mockup-feedback]
may_propose: []
---

# _concept/09_mockup/feedback/devlog.md

Committed, append-only. `apply.py` adds one block per applied round. Whoever regenerates a screen's story or an entity's components from the changed spec reads it first and treats every applied line for the screen or model file as a constraint: a regeneration that reverts a change a stakeholder already asked for reads as the tool ignoring the feedback round.

## Format

```markdown

## 2026-10-23 · round <round>

### 07_screens/inbox.md

- p-k3m9x2-2-content applied (change): 'Put the filter bar above the list, not beside it.'

### 10_blueprint/datamodel/model.ts

- p-k3m9x2-1-model applied (model-proposal): 'The editor needs an estimate field.'
```

A block is `## <UTC date> · round <round>`, then one `### <file>` per file with at least one applied patch (path relative to `_concept/`), then one bullet per applied patch: `<patchId> applied (<category|kind>): <note comment, first 80 chars, repr-quoted>`; the label is the patch's category, or its kind when it has none. Failed patches are not logged here; they are in `applied/<round>.json`.

## Writing it

Only `apply.py` appends. A first-ever apply creates the file; if that apply's commit fails the script deletes the file again. A reader never writes to it.
