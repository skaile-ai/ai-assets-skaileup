---
title: "reverse-engineer"
description: "Variant flow that extracts a concept from an existing codebase, then optionally enriches it with concept steps."
order: 9
---

The **reverse-engineer** flow starts from an existing repository instead of an
idea. It extracts a concept (`ops-reverse-engineer`), with optional project
orientation and convention discovery, then lets you enrich the extracted concept
with the standard concept steps. No build pass — hand off to a tier flow to
implement.

## When to use

Picked when the input is an existing codebase: documenting a legacy app,
onboarding to an inherited project, or seeding a rebuild.

| Signal | reverse-engineer |
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

Self-contained: `reverse-engineer.flow.yaml` carries a top-level `requires:`
block — `shared-contracts` + `meta-concept-contract` + `conceptualization-contract`
+ `standards-contract` plus exactly the skills its nodes run. No inheritance, no
extras.

## Run it

```bash
skaile add flow:reverse-engineer       # install the flow + its skills + contracts
skaile run flow:reverse-engineer       # execute the extraction pipeline
```

## See also

- [`concept-only`](../concept-only/) — the inverse: concept *from* an idea
- [`appbuilder-standard`](../appbuilder-standard/) — the tier to continue into for a rebuild
