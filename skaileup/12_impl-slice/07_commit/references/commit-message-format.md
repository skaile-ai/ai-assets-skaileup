# Commit message format

Pinned format for every commit produced by `impl-slice-commit`. The body is
the **only** durable place where slice context survives — once
`_implementation/slices/<id>/` is deleted, the commit body is the audit trail.

## Format

```
<type>(<slice_id>): <one-line summary>

Slice: <slice_id>
Feature: <feature_title>
Feature spec: <feature_path>
```

- **Subject** — `<type>(<slice_id>): <summary>`. Soft cap 72 chars (Conventional
  Commits convention); hard cap 80 chars (validator-enforced).
- **Body** — three required lines, exactly. `Slice:`, `Feature:`,
  `Feature spec:`. Values are copied from `recap.md` / `plan.md` frontmatter
  verbatim (no rewording).

## Type vocabulary

- `feat` — user-visible behavior added or extended.
- `fix` — user-visible behavior corrected.
- `chore` — schema migration, config, dependency bump.
- `test` — test files only (no production-code change).
- `docs` — documentation only.
- `refactor` — internal restructure with no behavior change. (This is the
  Conventional-Commits `refactor` type, distinct from the `impl-slice-refactor`
  skill — that skill is a phase; this is a commit type.)

## Worked examples

### chore — schema migration

```
chore(team-todo-comments): migrate comments table

Slice: team-todo-comments
Feature: Comments on team todo items
Feature spec: _concept/product-spec/features/team-todo/team-todo-comments.md
```

### feat — handler/route/data logic

```
feat(team-todo-comments): comments handler + route

Slice: team-todo-comments
Feature: Comments on team todo items
Feature spec: _concept/product-spec/features/team-todo/team-todo-comments.md
```

### feat — UI

```
feat(team-todo-comments): wire UI for comments

Slice: team-todo-comments
Feature: Comments on team todo items
Feature spec: _concept/product-spec/features/team-todo/team-todo-comments.md
```

### test — coverage

```
test(team-todo-comments): cover comments flow

Slice: team-todo-comments
Feature: Comments on team todo items
Feature spec: _concept/product-spec/features/team-todo/team-todo-comments.md
```

## Audit-trail note

The slice scratch dir is gone after this skill; the commit body is the only
place where `slice_id` + `feature_title` + `feature_path` persist. Future
agents reconstruct slice provenance by `git log --grep "Slice: "` and
matching the values back to the permanent feature artifact at `Feature spec:`.
