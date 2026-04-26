# Skaileup Skill Catalog

## What This Is

All skaileup-* skills for the concept, build, and quality pipelines. Extracted from `ai-assets/` as a standalone submodule.

**GitHub:** `github.com/skaile-ai/ai-assets-skailup`

## Structure

Skills are organized into domains. Each domain has a `DOMAIN.md` and contains skills under `skills/`.

```
skaileup/                      ← base orchestrators (skailup, skailup-concept, skailup-build)
skaileup-grounding/            ← onboard dialog + web research + seed ingestion
skaileup-discovery/            ← brief, goals, brand identity
skaileup-experience/           ← journeys, features, screens, components
skaileup-concept-mockup/       ← static text wireframes
skaileup-concept-storybook/    ← living Storybook prototypes
skaileup-architecture/         ← techstack + concept-level system architecture
skaileup-datamodel/            ← data model, seed schema, feature map
skaileup-concept-ops/          ← review, evaluate, drift detect, sync
skaileup-build/                ← scaffold, foundation, features, migrations
skaileup-quality/              ← standards + audit + tests + readiness
skaileup-lab/                  ← skill testing and improvement
skaileup-contracts/            ← shared contracts (referenced by all skills)
```

## Skill Structure

Every skill lives in its own directory:

```
my-skill/
├── SKILL.md        ← YAML frontmatter + markdown body (the agent prompt)
├── CLI.md          ← Optional: CLI invocation docs
├── references/     ← Optional: reference material
└── validator.py    ← Optional: output validation script
```

## Contracts

Shared contracts live in `skaileup-contracts/contracts/`. All skills reference these.

## Naming Convention

- **Domain directories:** `skaileup-<name>/` (with 'e')
- **Skill directories:** `skailup-<name>/` (without 'e' — matches the CLI command prefix)
- **Proposed skill rename:** Skills will be renamed to `skailup-<domain>-<function>` pattern (e.g., `skailup-discovery-brief`, `skailup-build-scaffold`). Current names are pre-rename.

## Reorganization Status

This repo was created by extracting and restructuring skaileup domains from `ai-assets/`. The directory-level reorganization (merges, splits, renames) is complete. Remaining work:

- [ ] Skill-level renames (e.g., `skailup-overview` → `skailup-discovery-brief`)
- [ ] DOMAIN.md updates for all domains (enriched frontmatter)
- [ ] SKILL.md frontmatter updates (context_budget, MVC dispatch sections)
- [ ] Validator creation for skills that lack them
- [ ] CHANGELOG.md per domain
