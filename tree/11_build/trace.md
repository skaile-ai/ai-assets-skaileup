---
path: _concept/11_build/trace.yaml
summary: feature to slices to commits to code, the one feature-to-commit join
writers: [build-implement]
---

# _concept/11_build/trace.yaml

The one feature → commit join. `quality-review`, `quality-release` and `ops-review` read it
instead of rebuilding it from slice dossiers, and `quality-review` takes its fixed point from
it; a feature spec holds no commits or code paths.

## Format

```yaml
features:
  <feature_slug>:
    featureset: <featureset>
    slices:
      - { id: <slice_id>, commits: [<sha>, ...], code: [<path>, ...] }
last_updated: YYYY-MM-DD
```

`featureset` and the slug come from the feature file, found by globbing `_concept/05_features/*/<feature_slug>.md`. `commits` are the landed shas; `code` is the source files those commits touched, with tests and everything under `_concept/` excluded. The JSON Schema `tree/11_build/trace.schema.json` (2020-12) is the authority on shape: beyond the keys above it admits the host's coverage columns per feature (`specced`, `sliced`, `committed`, `evaluated`, `documented`, `code_refs`) and a top-level `orphans: [{ path, reason }]` (code the host's coverage page found with no feature behind it); `build-implement` writes neither.

## Writing it

Validate the file against `tree/11_build/trace.schema.json` before writing it, after turning YAML dates into ISO text (`last_updated` is `YYYY-MM-DD`; `tree/README.md § Frontmatter every markdown artifact carries`).

Written by `build-implement` after the last commit of a slice has landed:

1. Create the file with the first slice. A feature cut into several slices has one `slices[]` entry each.
2. An entry for a slice id already present is replaced and never duplicated.
3. Leave the feature spec alone.

## Checks

- Every landed slice has an entry with non-empty `commits` and `code`.
- No slice id appears twice under one feature.
