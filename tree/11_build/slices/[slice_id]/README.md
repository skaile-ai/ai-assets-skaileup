---
path: _concept/11_build/slices/<slice_id>/
summary: "one slice's dossier directory: plan, working state, frozen index"
owner: [build-plan, build-implement]
may_propose: []
---

# _concept/11_build/slices/<slice_id>/

The dossier of one vertical slice, named by its `slice_id` (slug rule in `tree/11_build/slices/README.md`). `plan.md` is written by `build-plan` and read by `build-implement`; `progress.yaml` is `build-implement`'s working state while the slice is built; `index.md` freezes the dossier once every commit has landed. A directory with no `index.md` is an unlanded slice.

## Contents

- `plan.md`: see `tree/11_build/slices/[slice_id]/plan.md`
- `index.md`, `progress.yaml`: see `tree/11_build/slices/[slice_id]/index.md`
