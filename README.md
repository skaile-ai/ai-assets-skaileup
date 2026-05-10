# ai-assets-skaileup

The Skaileup skill catalog — concept, build, and quality pipeline skills for the Skaile ecosystem.

**94 SKILL.md files in 17 domains across three groups (Concept · Implementation · Meta)** covering the full product lifecycle: from problem-space discovery through per-slice implementation and quality gates, with a cross-cutting ops/lab/contracts meta layer.

```
                              user input  /  existing repo
                                          ▼
                              ╔═════════════════════╗
                              ║ skaileup (base) +    ║
                              ║ skaileup/scope/      ║   2-3 questions →
                              ╚══════════╤══════════╝   pick a tier
                                         │
                  ┌──────────────────────┼──────────────────────┐
                  ▼                      ▼                      ▼
              CONCEPT              IMPLEMENTATION              META
        concept · design        impl-architecture        skaileup · ops
        product-spec            impl-plan                lab · contracts
        experience              impl-build
        concept-slice ↻         impl-slice ↻
        component-mockup        impl-quality
        walkthrough-mockup
        mockup-feedback
```

> **Two slice loops, same shape on both sides.** Concept and implementation
> each have a per-feature iteration cluster. Big apps slice both; small apps
> skip slicing on one or both sides.

## Documentation

- 📖 **[Browse the full Starlight site](docs-site/)** — `cd docs-site && npm install && npm run dev` to read it locally; every skill has its own page with the SKILL.md body embedded.
- 📐 **[`SKILL_GRAPH.md`](SKILL_GRAPH.md)** — design rationale for the catalog structure.
- 🧬 **[`REFACTOR_MOCKUP.md`](REFACTOR_MOCKUP.md)** — the mockup-cluster design: three orthogonal concerns (component / walkthrough / feedback), bidirectional sync via references + devlog, per-slice file-granularity rule.
- 🔧 **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — how to author a skill that installs correctly with the `skaile` CLI.
- 🚦 **[`IMPROVEMENT.md`](IMPROVEMENT.md)** — open issues, splits, merges, and process gaps from the 2026-05-10 review.

## Layout

### Concept

| Domain | Purpose |
|---|---|
| [`concept/`](concept/DOMAIN.md) | Project brief, goals, comparable apps |
| [`design/`](design/DOMAIN.md) | Brand identity, tokens, voice |
| [`product-spec/`](product-spec/DOMAIN.md) | Feature specs + acceptance criteria |
| [`experience/`](experience/DOMAIN.md) | Journeys, behaviors, screens, components |
| [`concept-slice/`](concept-slice/DOMAIN.md) | Per-feature concept loop (big apps) |
| [`component-mockup/`](component-mockup/DOMAIN.md) | Storybook + isolated HTML |
| [`walkthrough-mockup/`](walkthrough-mockup/DOMAIN.md) | text · static-html · astro · framework |
| [`mockup-feedback/`](mockup-feedback/DOMAIN.md) | Annotation → patch loop |

### Implementation

| Domain | Purpose |
|---|---|
| [`impl-architecture/`](impl-architecture/DOMAIN.md) | Techstack · system · datamodel · templates/ |
| [`impl-plan/`](impl-plan/DOMAIN.md) | Brainstorm · align · plan-vertical · supervised |
| [`impl-slice/`](impl-slice/DOMAIN.md) | Per-slice loop: implement → test → recap → refactor → commit |
| [`impl-build/`](impl-build/DOMAIN.md) | One-time: scaffold · foundation · migrate · seed · generate · docs |
| [`impl-quality/`](impl-quality/DOMAIN.md) | Tests · audit · ready · standards · debug |

### Meta

| Domain | Purpose |
|---|---|
| [`skaileup/`](skaileup/DOMAIN.md) | Base orchestrators + `scope/` — pipeline entry point |
| [`ops/`](ops/DOMAIN.md) | Cross-cutting: review · sync · eval · add-feature · project-* |
| [`lab/`](lab/DOMAIN.md) | Skill-on-skill: validate · improve · compile-validators |
| [`contracts/`](contracts/DOMAIN.md) | Reference layer (every skill reads) |

## Tiers

The first thing the agent does is pick a tier. The rest of the pipeline is shaped by that choice.

| Tier | Concept | Implementation | Supervision |
|---|---|---|---|
| `mvp` | Linear, minimal (no design slicing) | Single impl-slice (skip recap, refactor) | Autonomous |
| `simple-app` | Linear, full (one pass) | N × impl-slice (full slice loop) | Autonomous |
| `standard-app` | Linear high-level + N × concept-slice | N × impl-slice (full + recap mandatory) | Mostly autonomous, plan checkpoint per slice |
| `complex-app` | Linear high-level + N × concept-slice + project-overview | N × impl-slice (supervised + audit between slices) | HITL |

## Flows + bundles

Each flow is paired with a bundle of identical name. The bundle lists exactly the skills the flow runs.

```
$ skaile add bundle:simple-app          # install the skills the flow needs
$ skaile run flow:simple-app            # execute the flow
```

```
flows/                                              bundles/
├── concept-slice.flow.yaml   ◄── pair ──►        ├── concept-slice.bundle.yaml
├── impl-slice.flow.yaml      ◄── pair ──►        ├── impl-slice.bundle.yaml
├── mvp.flow.yaml             ◄── pair ──►        ├── mvp.bundle.yaml
├── simple-app.flow.yaml      ◄── pair ──►        ├── simple-app.bundle.yaml
├── standard-app.flow.yaml    ◄── pair ──►        ├── standard-app.bundle.yaml
├── complex-app.flow.yaml     ◄── pair ──►        ├── complex-app.bundle.yaml
└── custom.flow.yaml          ◄── pair ──►        └── custom.bundle.yaml
```

`lab/compile-bundle` walks a flow's node graph and emits the matching bundle YAML — run on every flow change to prevent drift. CI: `scripts/check-bundles.sh`.

## How this is consumed

The `skaile` CLI and the agent runtime read SKILL.md files from disk. This repo is added as a git submodule at `ai-assets-skaileup/` in the skaile-dev shell repo, alongside `ai-assets/`.

```yaml
# project skaile.yaml
repositories:
  skaileup:
    url: https://github.com/skaile-ai/ai-assets-skaileup
    branch: main
```

Then install:

```bash
$ skaile add skill:concept-brief        # one skill + its requires
$ skaile add bundle:standard-app        # full bundle, all dependencies
```

Local checkouts use `path:` instead of `url:` and are symlinked so edits to SKILL.md are immediately reflected.

## Lineage

Extracted from [`skaile-ai/ai-assets`](https://github.com/skaile-ai/ai-assets) as part of the skill catalog reorganization (April 2026). The two reorganizations are documented in [`CLAUDE.md`](CLAUDE.md) § Reorganization Status and in `_devlog/plans/2026-05-07-skill-graph-migration.md` in the skaile-dev shell repo.

## Quick links

- [Skill DSL Grammar](contracts/skill_grammar.md)
- [Iron Laws](contracts/iron_laws.md)
- [Golden Principles](contracts/golden_principles.md)
- [Asset Frontmatter Schema](contracts/asset_frontmatter.md)
