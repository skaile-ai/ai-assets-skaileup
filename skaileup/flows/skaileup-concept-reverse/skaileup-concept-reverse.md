---
title: "concept-reverse"
description: "Variant flow that reverses a concept out of an existing codebase, then optionally enriches it with concept steps."
order: 9
---

The **skaileup-concept-reverse** flow starts from an existing repository instead
of an idea. It reverses a concept out of the code (the `ops-reverse-engineer`
skill), with optional project orientation and convention discovery, then lets you
enrich the extracted concept with the standard concept steps. No build pass —
hand off to `skaileup-implementation` or a tier flow to build.

## When to use

Picked when the input is an existing codebase: documenting a legacy app,
onboarding to an inherited project, or seeding a rebuild.

| Signal | concept-reverse |
|---|---|
| Input | existing repo |
| Extraction | ops-reverse-engineer (required) |
| Convention discovery | standards-discover → standards-inject (optional) |
| Enrichment | journeys, architecture, datamodel, screens (optional) |

## Pipeline

```
ops-reverse-engineer
  → ops-project-overview?  ·  ops-project-subsystem-map?
  → standards-discover? → standards-inject?
  → [enrich]  experience-journeys? → impl-architecture-system?
                → impl-architecture-datamodel? → experience-screens?
```

Every node after extraction is optional — run only the orientation and
enrichment the repo needs.

## Install manifest

Self-contained: `skaileup-concept-reverse.flow.yaml` carries a top-level
`requires:` block — `shared-contracts` + `meta-concept-contract` +
`conceptualization-contract` + `standards-contract` plus exactly the skills its
nodes run. No inheritance, no extras.

## Run it

```bash
skaile add flow:skaileup-concept-reverse       # install the flow + its skills + contracts
skaile run flow:skaileup-concept-reverse       # execute the extraction pipeline
```

## See also

- [`skaileup-concept-only`](../skaileup-concept-only/) — the inverse: concept *from* an idea
- [`skaileup-implementation`](../skaileup-implementation/) · [`appbuilder-standard`](../appbuilder-standard/) — hand off to build the reversed concept
