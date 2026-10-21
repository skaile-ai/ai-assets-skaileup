---
path: _concept/09_mockup/feedback/devlog.md
summary: append-only log of feedback edits, read by renderers so re-renders keep them
owner: [mockup-feedback]
may_propose: []
---

# _concept/09_mockup/feedback/devlog.md

Committed, append-only. `apply.py` adds one block per applied session. Both walkthrough renderers read it before rendering and treat every applied line for a screen or feature file they are about to render as a constraint: a regeneration that reverts a change a stakeholder already asked for reads as the tool ignoring the feedback round.

## Format

```markdown

## 2026-07-05 · session <sid>

### 07_screens/01_user_auth/login.md

- p-ann-c1-content applied (change): 'this should be on the right'
- p-ann-c1-promotion applied (derived): 'this should be on the right'
```

A block is `## <UTC date> · session <sid>`, then one `### <file>` per file with at least one applied patch (path relative to `_concept/`), then one bullet per applied patch: `<patchId> applied (<category|derived>): <annotation body, first 80 chars, repr-quoted>`. Failed patches are not logged here; they are in `applied/<sid>.json`.

## Writing it

Only `apply.py` appends. A first-ever apply creates the file; if that apply's commit fails the script deletes the file again. A renderer reads it and never writes to it (`tree/09_mockup/walkthrough/README.md § Writing it`, step 3).
