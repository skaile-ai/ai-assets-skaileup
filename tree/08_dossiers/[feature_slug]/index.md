---
path: _concept/08_dossiers/<feature_slug>/index.md
summary: one feature's framing, grill answers and rejected options, frozen at the end
owner: [spec-feature]
may_propose: []
---

# _concept/08_dossiers/<feature_slug>/index.md

The reasons behind one feature's spec: the framing, what each grill round settled, the options rejected, and what each later step settled that the spec will not hold. A session that dies mid-feature leaves its reasons on disk; a frozen dossier hands the next reader the decisions together with why they were made. `spec-feature` opens it at the similarity check that precedes the grill and freezes it last.

## Format

```yaml
---
status: open | frozen
last_updated: YYYY-MM-DD
---
```

The body holds the framing, `## Similar features` (each match from the similarity check with the option taken (reuse, pattern `DR-<n>`, or separate) and the reason, or one line saying nothing matched), and one appended entry per round or step. The scope line is not copied in: the body links to the spec's `## Scope`, which stays the one record of what was considered. Once frozen, the body also links forward to the feature spec and each screen its `screens:` lists.

## Writing it

1. **Open it at the similarity check**, once its batch is answered. Write `08_dossiers/<feature_slug>/index.md` with `status: open`, the framing and `## Similar features` (`tree/05_features/[featureset]/[feature].md § Writing it`, step 2); on reuse, the slug is the existing feature's. An `open` dossier already there is an interrupted run: load it and continue.
2. **Append as the run goes.** After each grill round add what it settled — answers, rejected options — and after every later step what that step settled that the spec will not hold.
3. **Freeze it last.** Append the links forward to the spec (its `## Scope` included) and the screens it lists, then set `status: frozen` once the spec and its roster row have landed (`tree/08_dossiers/README.md § Freeze lifecycle`). Skipping the dossier leaves the next reader the decisions without any of the reasons.

## Checks

- `status` is `open` while the run is live and `frozen` after the last write.
- A frozen dossier links to the spec and to every screen the spec's `screens:` lists.
- `## Similar features` is present.
