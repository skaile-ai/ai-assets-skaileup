# Feature-Portion Rule

The cluster's hardest invariant — `concept-slice-design-feature` writes
ONLY paths whose path-segment matches `<feature_slug>` in the relevant
position. This document spells out the rule with examples.

## The rule

| Target dir                                  | Path-segment match required                         |
|---------------------------------------------|-----------------------------------------------------|
| `_concept/product-spec/features/<group>/`   | filename stem MUST equal `<feature_slug>`           |
| `_concept/experience/screens/`              | first dir under `screens/` MUST equal `<feature_slug>` |
| `_concept/mockup-walkthrough/<tier>/`       | filename stem MUST equal `<feature_slug>`           |

## Why this rule

A slice is per-feature. It must not touch other features' files even
incidentally — staleness is not this skill's problem to fix. Editing a
sibling's file makes slices non-composable: if two slices both touch
the same screen, the order of execution becomes load-bearing.

## Example A — feature spec write (allowed)

`<feature_slug>` = `team-todo-comments`

Allowed:
```
_concept/product-spec/features/team-todo/team-todo-comments.md
                                          ^^^^^^^^^^^^^^^^^^ matches
```

Rejected:
```
_concept/product-spec/features/team-todo/team-todo-list.md
                                          ^^^^^^^^^^^^^ does not match
```

## Example B — screen file write (allowed)

`<feature_slug>` = `team-todo-comments`

Allowed:
```
_concept/experience/screens/team-todo-comments/list.md
                            ^^^^^^^^^^^^^^^^^^ first segment matches
```

Rejected:
```
_concept/experience/screens/team-todo/comments-list.md
                            ^^^^^^^^^ first segment does not match
```

## Example C — walkthrough stub (allowed)

`<feature_slug>` = `team-todo-comments`, tier = `appbuilder-standard`

Allowed:
```
_concept/mockup-walkthrough/appbuilder-standard/team-todo-comments.astro
                                          ^^^^^^^^^^^^^^^^^^ matches
```

Rejected:
```
_concept/mockup-walkthrough/appbuilder-standard/index.astro
                                          ^^^^^ does not match
```

## Counter-example — cross-feature edit (rejected)

The slice for `team-todo-comments` notices that
`_concept/experience/screens/team-todo-list/index.md` references an
outdated entity name. **The slice MUST NOT fix it.** The path-segment
rule rejects the write because `team-todo-list` ≠ `team-todo-comments`.

The fix belongs to either:
- a follow-up slice owning `team-todo-list`, or
- an `ops/sync` pass.

The cluster intentionally trades manual cleanup overhead for slice
composability.

## Diff format for overwrite CHECKPOINT

When a target path exists, `concept-slice-design-feature` shows a
unified diff and requires explicit approval. Format:

```
diff --git a/<path> b/<path>
--- a/<path>     (existing)
+++ b/<path>     (proposed)
@@ -<line>,<count> +<line>,<count> @@
-<old line>
+<new line>
```

The user replies with:
- `yes` — overwrite
- `no` — abort the entire skill (no other writes happen, no scratch deleted)
- `edit` — prompt for changes, regenerate, re-show diff

## Validator hook

`validator.py` (mode C — manifest mode) cross-checks every produced
path against the rule. Any path that violates the segment rule causes
exit 2.
