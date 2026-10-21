---
path: _concept/08_dossiers/<feature_slug>/index.md
summary: one feature's framing, grill answers and rejected options, frozen at the end
owner: [spec-feature]
may_propose: []
---

# _concept/08_dossiers/<feature_slug>/index.md

The reasons behind one feature's spec: the framing, what each grill round settled, the options rejected, and what each later step settled that the spec will not hold. A session that dies mid-feature leaves its reasons on disk; a frozen dossier hands the next reader the decisions together with why they were made. `spec-feature` opens it at the start of the grill and freezes it last.

## Format

```yaml
---
status: open | frozen
last_updated: YYYY-MM-DD
---
```

The body holds the framing and one appended entry per round or step. The scope line is not copied in: the body links to the spec's `## Scope`, which stays the one record of what was considered. Once frozen, the body also links forward to the feature spec and each screen.

## Writing it

1. **Open it as the grill starts.** Write `08_dossiers/<feature_slug>/index.md` with `status: open` and the framing. An `open` dossier already there is an interrupted run: load it and continue.
2. **Append as the run goes.** After each grill round add what it settled — answers, rejected options — and after every later step what that step settled that the spec will not hold.
3. **Freeze it last.** Append the links forward to the spec (its `## Scope` included) and the screens, then set `status: frozen` once every spec and screen write has landed (`tree/08_dossiers/README.md § Freeze lifecycle`). Skipping the dossier leaves the next reader the decisions without any of the reasons.

## Checks

- `status` is `open` while the run is live and `frozen` after the last write.
- A frozen dossier links to the spec and to every screen the run wrote.
