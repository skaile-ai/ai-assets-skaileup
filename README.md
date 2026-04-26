# ai-assets-skailup

The Skaileup skill catalog — concept, build, and quality pipeline skills for the Skaile ecosystem.

Organized into 14 focused domains covering the full product lifecycle: grounding (research + onboarding), discovery (brief + brand), experience (journeys + features + screens), architecture, data modeling, prototyping, implementation (autonomous + supervised), quality assurance, and skill meta-improvement.

## Domains

| Domain | Purpose |
|---|---|
| [`skaileup/`](skaileup/DOMAIN.md) | Base orchestrators — the main entry point for all pipelines |
| [`skaileup-architecture/`](skaileup-architecture/DOMAIN.md) | Techstack selection + concept-level system architecture |
| [`skaileup-build/`](skaileup-build/DOMAIN.md) | Implementation pipeline (scaffold, features, migrations) |
| [`skaileup-build-supervised/`](skaileup-build-supervised/DOMAIN.md) | Supervised build: git-prepare, brainstorm, plan, finish |
| [`skaileup-concept-mockup/`](skaileup-concept-mockup/DOMAIN.md) | Static text wireframes from screen specs |
| [`skaileup-concept-ops/`](skaileup-concept-ops/DOMAIN.md) | Cross-cutting concept operations (review, eval, drift, sync) |
| [`skaileup-concept-storybook/`](skaileup-concept-storybook/DOMAIN.md) | Living interactive prototypes (Storybook) |
| [`skaileup-contracts/`](skaileup-contracts/DOMAIN.md) | Shared contracts and conventions (not directly invocable) |
| [`skaileup-datamodel/`](skaileup-datamodel/DOMAIN.md) | Data model: DBML, model.json, seed schema, feature map |
| [`skaileup-discovery/`](skaileup-discovery/DOMAIN.md) | Project definition: brief, goals, comparable, brand identity |
| [`skaileup-experience/`](skaileup-experience/DOMAIN.md) | User journeys, features, screens, components |
| [`skaileup-grounding/`](skaileup-grounding/DOMAIN.md) | All context-gathering: onboard dialog + web research + seed ingestion |
| [`skaileup-lab/`](skaileup-lab/DOMAIN.md) | Skill testing, improvement, validation |
| [`skaileup-quality/`](skaileup-quality/DOMAIN.md) | Standards + code audit + test generation + readiness gates |

## Lineage

Extracted from [`skaile-ai/ai-assets`](https://github.com/skaile-ai/ai-assets) as part of the skill catalog reorganization (April 2026). The reorganization applied these structural changes:

- `skaileup-onboard` + `skaileup-research` merged into `skaileup-grounding`
- `skaileup-standards` merged into `skaileup-quality`
- `skaileup-blueprint` dissolved into `skaileup-architecture` + `skaileup-datamodel`
- `skaileup-prototype` renamed to `skaileup-concept-mockup`
- `skaileup-storybook` renamed to `skaileup-concept-storybook`
- `skaileup-concept-meta` renamed to `skaileup-concept-ops`
- `skaileup-shared` renamed to `skaileup-contracts`
- `skailup/` (base orchestrators) renamed to `skaileup/`

See `_devlog/plans/2026-04-26-skill-reorganization-proposal.md` in the skaile-dev shell repo for the full design rationale.

## How This Is Consumed

The skaile CLI and platform consume these at runtime by reading SKILL.md files from disk. This repo is added as a git submodule at `ai-assets-skailup/` in the skaile-dev shell repo, alongside `ai-assets/`.
