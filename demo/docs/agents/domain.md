# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`GLOSSARY.md`** at the repo root.
- **`docs/adr/`**: read ADRs that touch the area you're about to work in.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## File structure

Single-context repo:

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-one-nuxt-container.md
│   └── 0002-a-tie-is-settled-by-a-visible-draw.md
└── src/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `GLOSSARY.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0002 (a tie is settled by a visible draw), but worth reopening because…_

## skaileup artifacts

This project's concept lives in `_concept/` (skaileup). Read before working on a feature:

- **Specs**: `_concept/05_features/<featureset>/<feature>.md`; `tracker.issue` in its frontmatter is the spec's parent issue.
- **Glossary**: `GLOSSARY.md` (words); `_concept/glossary.md` (ontology: kinds, is-a, relations).
- **Decisions**: `docs/adr/` (frontmatter `level`/`kind`; a `pattern` binds every later feature it `applies_when`).
- **Interaction rules**: `APP-DESIGN.md`.
- **Data model**: `_concept/10_blueprint/datamodel/model.yaml`, `seed.yaml`.
- **Instruction nodes**: `<contracts>/shared-contracts/` (the node at the same path as a `_concept/` file says its format and owner).
- **Pending proposals**: `_concept/proposals/` — a `status: proposed` entry is not yet true; do not build on it.
