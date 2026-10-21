---
path: _concept/08_dossiers/
summary: the concept-side working record of each feature, frozen when its loop ends
owner: []
may_propose: []
---

# _concept/08_dossiers/

One directory per feature, `<feature_slug>/`, holding `index.md` — the concept-side working record for that feature: the framing, the questions, the answers. `11_build/slices/<slice_id>/` is its build-side counterpart. A dossier is one file and one writer (`spec-feature`); it carries the reasons behind the spec so a later reader, who may be a different session, host or person, has the decisions with their reasons.

## Freeze lifecycle

A dossier is **frozen** when it is indexed and closed: it stops being working state and becomes the record of how the feature got specified. A feature dossier is opened at the start of the grill with `index.md` at `status: open`, appended to as the loop runs, and frozen by setting `status: frozen` once every spec and screen write has landed. Nothing in a dossier is deleted. A frozen `index.md` links forward to the canonical artifacts — the spec and its screens — and stands on its own.

A dossier that already exists is a resume, not a collision: load what is there, show what would change, and write after the user agrees. Overwriting one silently discards the reasoning it holds, which is the only thing a dossier is for.

Each dossier is described in `tree/08_dossiers/[feature_slug]/index.md`.
