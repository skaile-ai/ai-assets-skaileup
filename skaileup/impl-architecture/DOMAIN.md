---
name: impl-architecture
description: "techstack · system · datamodel · templates/"
metadata:
  stage: alpha
  type: domain
---

# impl-architecture

Establishes the technical foundation before any code is written: stack selection, system architecture, and data model. Agents run these three skills once per project, then pick a scaffold template to bootstrap the repo.

## Skills

- **impl-architecture-techstack** (`techstack/`) — Reads `templates/` profiles, asks plain-language questions, recommends a stack, writes `stack.md`.
- **impl-architecture-system** (`system/`) — Produces `architecture.md`: system overview, backend structure, data flow, communication protocols, external integrations, infrastructure.
- **impl-architecture-datamodel** (`datamodel/`) — Produces `_concept/blueprint/datamodel/model.dbml`, `model.json`, `seed.json`, and `feature_map.json`.
- **templates/** (`templates/`) — 7 scaffold templates (PostXL, Next.js + Radix, Next.js + shadcn, Nuxt minimal/UI/PrimeVue, SvelteKit minimal). Each is a standalone skill; the agent picks one after `techstack` selects a stack.

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
