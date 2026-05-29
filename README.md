# ai-assets-skaileup

The Skaileup skill catalog — concept, build, and quality pipeline skills for the Skaile ecosystem.

**94 SKILL.md files in 20 top-level domains across three groups (Concept · Implementation · Meta)** covering the full product lifecycle: from problem-space discovery through per-slice implementation and quality gates, with a cross-cutting ops/lab/contracts meta layer.

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
        mockup-component        impl-quality
        mockup-walkthrough
        mockup-feedback
```

> **Two slice loops, same shape on both sides.** Concept and implementation
> each have a per-feature iteration cluster. Big apps slice both; small apps
> skip slicing on one or both sides.

## Documentation

- 📖 **[Browse the full Starlight site](docs/)** — `npm run docs` to read it locally; every skill has its own page with the SKILL.md body embedded.
- 🔧 **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — how to author a skill that installs correctly with the `skaile` CLI.
- 📁 **[`docs/devlog/`](docs/devlog/)** — plans, specs, design notes, improvement backlog.

## Layout

### Concept

| Domain | Purpose |
|---|---|
| [`skaileup/concept/`](skaileup/concept/DOMAIN.md) | Project brief, goals, comparable apps |
| [`skaileup/design/`](skaileup/design/DOMAIN.md) | Brand identity, tokens, voice |
| [`skaileup/product-spec/`](skaileup/product-spec/DOMAIN.md) | Feature specs + acceptance criteria |
| [`skaileup/experience/`](skaileup/experience/DOMAIN.md) | Journeys, behaviors, screens, components |
| [`skaileup/concept-slice/`](skaileup/concept-slice/DOMAIN.md) | Per-feature concept loop (big apps) |
| [`skaileup/mockup-component/`](skaileup/mockup-component/DOMAIN.md) | Storybook + isolated HTML |
| [`skaileup/mockup-walkthrough/`](skaileup/mockup-walkthrough/DOMAIN.md) | text · static-html · astro · framework |
| [`skaileup/mockup-feedback/`](skaileup/mockup-feedback/DOMAIN.md) | Annotation → patch loop |

### Implementation

| Domain | Purpose |
|---|---|
| [`skaileup/impl-architecture/`](skaileup/impl-architecture/DOMAIN.md) | Techstack · system · datamodel · templates/ |
| [`skaileup/impl-plan/`](skaileup/impl-plan/DOMAIN.md) | Brainstorm · align · plan-vertical · supervised |
| [`skaileup/impl-slice/`](skaileup/impl-slice/DOMAIN.md) | Per-slice loop: implement → test → recap → refactor → commit |
| [`skaileup/impl-build/`](skaileup/impl-build/DOMAIN.md) | One-time: scaffold · foundation · migrate · seed · generate · docs |
| [`skaileup/impl-quality/`](skaileup/impl-quality/DOMAIN.md) | Tests · audit · ready · standards · debug |

### Meta — user-facing

| Domain | Purpose |
|---|---|
| [`skaileup/skaileup-orchestrator/`](skaileup/skaileup-orchestrator/DOMAIN.md) | Base orchestrators + `scope/` — pipeline entry point |
| [`skaileup/ops/`](skaileup/ops/DOMAIN.md) | Cross-cutting: review · sync · eval · add-feature · project-* |

### Meta — system assets

| Location | Purpose |
|---|---|
| [`skaileup/contracts/`](skaileup/contracts/DOMAIN.md) | Reference layer (every skill reads) |
| [`skaileup/flows/`](skaileup/flows/) | Flow + bundle YAMLs, co-located per app-type |
| [`ai-assets-dev/lab/`](ai-assets-dev/lab/DOMAIN.md) | Skill-on-skill: validate · improve · compile-bundle |
| [`ai-assets-dev/scripts/`](ai-assets-dev/scripts/) | CI scripts (check-bundles.sh) |

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
skaileup/flows/
├── complex-app/
│   ├── complex-app.flow.yaml
│   └── complex-app.bundle.yaml
├── concept-slice/
│   ├── concept-slice.flow.yaml
│   └── concept-slice.bundle.yaml
├── impl-slice/
│   ├── impl-slice.flow.yaml
│   └── impl-slice.bundle.yaml
├── mvp/
│   ├── mvp.flow.yaml
│   └── mvp.bundle.yaml
├── simple-app/
│   ├── simple-app.flow.yaml
│   └── simple-app.bundle.yaml
├── standard-app/
│   ├── standard-app.flow.yaml
│   └── standard-app.bundle.yaml
└── _meta/
    ├── verify_flows.py
    ├── test_verify.py
    └── deferred_skills.yaml
```

`ai-assets-dev/lab/compile-bundle` walks a flow's node graph and emits the matching bundle YAML next to the flow file — run on every flow change to prevent drift. CI: `ai-assets-dev/scripts/check-bundles.sh`.

## How this is consumed

The `skaile` CLI and the agent runtime read SKILL.md files from disk. This repo is added as a git submodule at `ai-assets-skaileup/` in the skaile-dev shell repo.

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

- [Skill DSL Grammar](skaileup/contracts/skill_grammar.md)
- [Iron Laws](skaileup/contracts/iron_laws.md)
- [Golden Principles](skaileup/contracts/golden_principles.md)
- [Asset Frontmatter Schema](skaileup/contracts/asset_frontmatter.md)
