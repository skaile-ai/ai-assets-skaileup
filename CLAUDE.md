# Skaileup Skill Catalog

## What This Is

All skaileup-* skills for the concept, build, and quality pipelines. Extracted from `ai-assets/` as a standalone submodule.

**GitHub:** `github.com/skaile-ai/ai-assets-skailup`

## Structure

Skills are organized into domains. Each domain has a `DOMAIN.md` and contains skills under `skills/`.

```
skaileup/                      ← base: meta-router (skailup) + build orchestrator (skailup-build)
skaileup-grounding/            ← onboard dialog + web research + seed ingestion
skaileup-discovery/            ← brief, goals, brand identity
skaileup-experience/           ← journeys, features, screens, components
skaileup-concept-mockup/       ← static text wireframes
skaileup-concept-storybook/    ← living Storybook prototypes
skaileup-architecture/         ← techstack + concept-level system architecture
skaileup-datamodel/            ← data model, seed schema, feature map
skaileup-concept-ops/          ← review, evaluate, drift detect, sync
skaileup-build/                ← scaffold, foundation, features, migrations
skaileup-build-supervised/     ← supervised build: git-prepare, brainstorm, plan, finish
skaileup-quality/              ← standards + audit + tests + readiness
skaileup-lab/                  ← skill testing + improvement + validator compilation
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
- **Skill naming:** Skills follow the `skailup-<domain>-<function>` pattern (e.g., `skailup-discovery-brief`, `skailup-build-scaffold`). Exception: concept-ops skills that are already unambiguous keep short names (e.g., `skailup-review`, `skailup-eval-concept`).

## Reorganization Status

This repo was created by extracting and restructuring skaileup domains from `ai-assets/`. Domain-level and skill-level reorganization is complete.

- [x] Domain extraction from ai-assets
- [x] Domain merges (onboard+research→grounding, standards→quality) and splits (blueprint→architecture+datamodel)
- [x] Skill-level directory renames to `skailup-<domain>-<function>` pattern
- [x] SKILL.md `name:` frontmatter updates
- [x] New domain: `skaileup-build-supervised/` (extracted from build)
- [x] Cross-domain moves: sync→concept-ops, compile-validators→lab, implement→skaileup base
- [ ] DOMAIN.md enriched frontmatter for all domains (layer, depends_on, feeds_into)
- [ ] SKILL.md content updates (context_budget, MVC dispatch sections)
- [ ] Validator creation for skills that lack them
- [ ] CHANGELOG.md per domain
