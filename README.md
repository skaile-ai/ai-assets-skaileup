# ai-assets-skaileup

The Skaileup skill catalog — concept, build, and quality pipeline skills for the Skaile ecosystem.

Organized into 17 domains in three groups (Concept, Implementation, Meta) covering the full product lifecycle: from problem-space discovery through per-slice implementation and quality gates, with a cross-cutting ops/lab/contracts meta layer. See `SKILL_GRAPH.md` for the design rationale.

## Top-level layout

### Concept

| Domain | Purpose |
|---|---|
| [`concept/`](concept/DOMAIN.md) | Project brief, goals, comparable apps |
| [`design/`](design/DOMAIN.md) | Brand identity, tokens, voice |
| [`product-spec/`](product-spec/DOMAIN.md) | Feature specs + acceptance criteria |
| [`experience/`](experience/DOMAIN.md) | Journeys, behaviors, screens, components |
| [`concept-slice/`](concept-slice/DOMAIN.md) | Per-feature concept loop (big apps) |
| [`component-mockup/`](component-mockup/DOMAIN.md) | Storybook + isolated HTML |
| [`walkthrough-mockup/`](walkthrough-mockup/DOMAIN.md) | text · static-html · lit · astro · framework |
| [`mockup-feedback/`](mockup-feedback/DOMAIN.md) | Annotation → patch loop |

### Implementation

| Domain | Purpose |
|---|---|
| [`impl-architecture/`](impl-architecture/DOMAIN.md) | Techstack, system, datamodel, templates |
| [`impl-plan/`](impl-plan/DOMAIN.md) | Brainstorm, align, plan-vertical, supervised |
| [`impl-slice/`](impl-slice/DOMAIN.md) | Per-slice loop: implement → test → recap → refactor → commit |
| [`impl-build/`](impl-build/DOMAIN.md) | One-time: scaffold, foundation, migrate, seed, ... |
| [`impl-quality/`](impl-quality/DOMAIN.md) | Tests, audit, ready, standards, debug |

### Meta

| Domain | Purpose |
|---|---|
| [`skaileup/`](skaileup/DOMAIN.md) | Base orchestrators — entry point for all pipelines |
| [`ops/`](ops/DOMAIN.md) | Cross-cutting: review, sync, eval, add-feature, project-* |
| [`lab/`](lab/DOMAIN.md) | Skill-on-skill: validate, improve, compile-validators |
| [`contracts/`](contracts/DOMAIN.md) | Reference layer (every skill reads) |

## Lineage

Extracted from [`skaile-ai/ai-assets`](https://github.com/skaile-ai/ai-assets) as part of the skill catalog reorganization (April 2026). The reorganization applied these structural changes:

- **Phase 1 of the SKILL_GRAPH proposal applied 2026-05-07** (this branch): 14 `skaileup-*` domains migrated to the two-group structure (Concept + Implementation + Meta). See `SKILL_GRAPH.md` for the proposal and `docs/superpowers/plans/2026-05-07-skill-graph-migration.md` for the migration plan.

- `skaileup-onboard` + `skaileup-research` merged into `skaileup-grounding`
- `skaileup-standards` merged into `skaileup-quality`
- `skaileup-blueprint` dissolved into `skaileup-architecture` + `skaileup-datamodel`
- `skaileup-prototype` renamed to `skaileup-concept-mockup`
- `skaileup-storybook` renamed to `skaileup-concept-storybook`
- `skaileup-concept-meta` renamed to `skaileup-concept-ops`
- `skaileup-shared` renamed to `skaileup-contracts`
- `skaileup/` (base orchestrators) renamed to `skaileup/`

See `_devlog/plans/2026-04-26-skill-reorganization-proposal.md` in the skaile-dev shell repo for the full design rationale.

## How This Is Consumed

The skaile CLI and platform consume these at runtime by reading SKILL.md files from disk. This repo is added as a git submodule at `ai-assets-skaileup/` in the skaile-dev shell repo, alongside `ai-assets/`.
