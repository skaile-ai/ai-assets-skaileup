---
path: [_concept/11_build/slices/]
summary: one dossier per vertical slice, cut from a frozen feature spec
writers: [build-plan]
---

# _concept/11_build/slices/

One directory per **vertical slice** of a feature: a tracer bullet through every layer the
feature crosses, demoable alone and sized for one fresh context window. `build-plan` cuts a
frozen feature spec into slices and writes each slice's `plan.md`; `build-implement` builds
one and freezes it with `index.md`. The `blocked_by` edges in the plans are the whole
ordering, since the directory name carries no number.

## Format

```
slices/<slice_id>/
├── plan.md        build-plan: scope, rows, criteria by id, tests, carry-overs   (tree/11_build/slices/[slice_id]/plan.md)
├── progress.yaml  build-implement: working state while the slice is built; removed at freeze
└── index.md       build-implement: the frozen record                            (tree/11_build/slices/[slice_id]/index.md)
```

**`slice_id`** is the slug (`tree/05_features/[featureset]/[feature].md § Slug`: pattern, derivation
and the resume rule for an id that already exists) of the slice's own title. A feature
decomposes into several slices, so it is not the feature slug; the plan's frontmatter carries
`feature` and `blocked_by`.

A slice dossier is **frozen** when `index.md` exists with `status: frozen`: it stops being
working state and becomes the record of how the slice got built. Nothing in it is deleted
except the transient `progress.yaml`, dropped by the freeze that makes it moot. A slice
dossier with no `index.md` is work that was built and never committed, so `build-branch`
refuses to close a branch while one exists. A frozen dossier must stand on its own: the next
reader may be a different session, host or person.

## Writing it

`build-plan` cuts the feature, in this order:

1. **Read the feature, then the code.** Load `_concept/05_features/<featureset>/<feature_slug>.md`
   (`tree/05_features/[featureset]/[feature].md`), every screen under
   `_concept/07_screens/<feature_slug>/`, and `_concept/10_blueprint/` for stack, architecture
   and data model where they exist. Only the feature spec is required: without `techstack.md`
   the slices name no framework and the first one has to establish it, and without a data
   model every slice that touches storage carries its own schema decision. Where the project
   type grows no screens (`tree/01_meta/scope.md § Project types`), plan from the spec and the
   roster `_concept/05_features/featuresets.md`: the roster places the feature among its
   neighbours, the spec's behaviour and criteria give the seams, and a slice's UI row becomes
   the entry point the product has (endpoint, command, public function). Then explore the
   codebase for what is already there. Where `_concept/02_grounding/standards/index.yml`
   exists, match its entries on `applies_to: build-plan` and the feature's keywords and load
   the hits, so seams and names follow the conventions the code already has. Slice titles use
   the glossary's terms (`_concept/glossary.md`; format `tree/glossary.md`) and respect the
   decision records in the area they touch (`_concept/10_blueprint/decisions.md`; format
   `tree/10_blueprint/decisions.md`), because a plan in different words than the code
   is one the implementer has to translate. Look for prefactoring that makes the change easy
   first; it becomes the slice everything else is blocked by.
2. **Cut vertical slices.** Each slice is a narrow but complete path through every layer the
   feature crosses (UI renders real data, the handler is callable from it, the data layer
   round-trips, its tests are green), demoable on its own and sized for one fresh context
   window. Every acceptance criterion in the spec lands in at least one slice. A candidate
   slice that cannot be described as something a user can do is a layer wearing a slice's
   name ("all the screens", "all the migrations", "wire it up after"): merge it into the slice
   that needs it or split it by user-facing seam. The data model sets slice *order* (parents
   before children) and never reshapes a slice into an entity.
3. **Sequence a wide refactor as expand–contract, not as a slice.** A wide refactor is one
   mechanical change (rename a column, retype a shared symbol) whose blast radius fans across
   the codebase, so no vertical slice can land green. Expand first: add the new form beside
   the old, one slice, blocking the rest. Then migrate call sites in batches sized by blast
   radius (per package, per directory), each batch its own slice blocked by the expand, CI
   green batch to batch because the old form still exists. Contract last: delete the old form
   in a slice blocked by every batch. When even the batches cannot stay green alone, keep the
   sequence but let them share an integration branch and promise green only at a final
   integrate-and-verify slice.
4. **Give each slice its blocking edges.** `blocked_by` lists the slices that genuinely gate
   it; a slice with none can start immediately, and an edge left off is a slice picked up
   before the thing it needs exists.
5. **Quiz the user before writing anything.** Present the breakdown as a numbered list: title,
   blocked by, and the end-to-end behaviour the slice delivers. Ask whether the granularity is
   right, whether each edge is a real gate rather than a hunch, and what should merge or
   split. Iterate until they approve; a mis-cut slice costs a sentence here and a rewrite
   later.
6. **Write `plan.md` for each approved slice** and then the ledger, per
   `tree/11_build/slices/[slice_id]/plan.md` and
   `tree/11_build/acceptance-criteria/README.md § Creating the ledger`.
7. **Report the frontier**: the slices whose blockers are all satisfied, in the order they can
   start. That list is what `build-implement` is handed.

## Checks

- Every acceptance criterion in the spec is claimed by at least one slice.
- Every `blocked_by` names a slice that exists.
- Every approved slice has a `plan.md`; the slice has `index.md` only after `build-implement`
  has landed every commit.
