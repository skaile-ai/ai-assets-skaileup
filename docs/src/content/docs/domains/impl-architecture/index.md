---
title: "impl-architecture"
description: "techstack · system · datamodel · templates/"
sourcePath: "skaileup/impl-architecture/DOMAIN.md"
sidebar:
  label: "Overview"
  order: 0
---


# impl-architecture

Establishes the technical foundation before any code is written: stack selection, system architecture, and data model. Agents run these three skills once per project, then pick a scaffold template to bootstrap the repo.

## Skills

The collection references this cluster via the **selector** skill `impl-architecture-templates-select` (`../templates-select/SKILL.md`). At runtime the selector reads `_concept/_meta/scope.yaml` + `_concept/blueprint/techstack.md`, scores the concrete templates on frontend → UI library → backend/database, and writes the winner back as `tech_stack_skill` so the build skills resolve exactly one of the templates below.

## When to Use

- Features are approved (`product-spec` done) and no `stack.md` exists yet.
- Starting the implementation pipeline: `impl-plan` needs `stack.md` and `architecture.md` as inputs.
- Data model is blank (`_concept/blueprint/datamodel/` empty) but features reference entities.
- Scaffolding a new repo from scratch (templates cluster).

## When NOT to Use

- Stack already locked and documented — skip `techstack`, run `system` and `datamodel` only.
- Prototype or MVP tier with no backend — `datamodel` is optional; scaffold directly from a template.
- Adding a feature to an existing repo — use `impl-plan` or `impl-slice` directly.

## Sequence

```
impl-architecture-techstack
        ↓
impl-architecture-system   (parallel with)   impl-architecture-datamodel
        ↓
templates/<chosen-template>   (scaffold — one-time)
```

## Cross-references

- `../impl-plan/` — consumes `stack.md` and `architecture.md`.
- `../impl-build/` — scaffold step also uses the chosen template.
- `templates/DOMAIN.md` — template cluster details.
- `../contracts/` — iron laws and golden principles every skill reads.


## Skills in this domain

- [impl-architecture-datamodel](./impl-architecture-datamodel/) — Use when features are approved but _concept/blueprint/datamodel/ is empty. Produces model.dbml (DBML), model.json (editor canvas), seed.json
- [impl-architecture-system](./impl-architecture-system/) — Use after features and techstack are approved to document system architecture. Produces architecture.md with system overview, backend struct
- [impl-architecture-techstack](./impl-architecture-techstack/) — Use when the project brief exists and tech stack hasn't been chosen. Discovers available stacks from impl-architecture/templates/, asks plai
- [impl-architecture-templates-select](./impl-architecture-templates-select/) — Use after techstack.md exists to resolve the abstract stack decision to exactly one concrete scaffold template (template-postxl, template-ne
