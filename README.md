# ai-assets-skaileup

The Skaileup skill collection — concept, build, and quality pipeline skills for the Skaile ecosystem.

**93 SKILL.md files in 15 numbered domains across three groups (Concept · Implementation · Meta)** covering the full product lifecycle: from problem-space discovery through per-slice implementation and quality gates, with a cross-cutting ops/lab/contracts meta layer.

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
| [`skaileup/01_concept/`](skaileup/01_concept/DOMAIN.md) | Project brief, goals, comparable apps |
| [`skaileup/02_design/`](skaileup/02_design/DOMAIN.md) | Brand identity, tokens, voice |
| [`skaileup/03_experience/`](skaileup/03_experience/DOMAIN.md) | Journeys, behaviors, screens, components |
| [`skaileup/04_product-spec/`](skaileup/04_product-spec/DOMAIN.md) | Feature specs + acceptance criteria |
| [`skaileup/05_mockup-walkthrough/`](skaileup/05_mockup-walkthrough/DOMAIN.md) | text · static-html · astro · framework |
| [`skaileup/06_mockup-component/`](skaileup/06_mockup-component/DOMAIN.md) | Storybook + isolated HTML |
| [`skaileup/07_mockup-feedback/`](skaileup/07_mockup-feedback/DOMAIN.md) | Annotation → patch loop |
| [`skaileup/08_concept-slice/`](skaileup/08_concept-slice/DOMAIN.md) | Per-feature concept loop (big apps) |

### Implementation

| Domain | Purpose |
|---|---|
| [`skaileup/09_impl-architecture/`](skaileup/09_impl-architecture/DOMAIN.md) | Techstack · system · datamodel · templates/ |
| [`skaileup/10_impl-build/`](skaileup/10_impl-build/DOMAIN.md) | One-time: scaffold · foundation · migrate · seed · generate · docs |
| [`skaileup/11_impl-plan/`](skaileup/11_impl-plan/DOMAIN.md) | Brainstorm · align · plan-vertical · supervised |
| [`skaileup/12_impl-slice/`](skaileup/12_impl-slice/DOMAIN.md) | Per-slice loop: implement → test → recap → refactor → commit |
| [`skaileup/13_impl-quality/`](skaileup/13_impl-quality/DOMAIN.md) | Tests · audit · ready · standards · debug |

### Meta — user-facing

| Domain | Purpose |
|---|---|
| [`skaileup/00_skaileup-orchestrator/`](skaileup/00_skaileup-orchestrator/DOMAIN.md) | Base orchestrators + `scope/` — pipeline entry point |
| [`skaileup/14_ops/`](skaileup/14_ops/DOMAIN.md) | Cross-cutting: review · sync · eval · add-feature · project-* |

### Meta — system assets

| Location | Purpose |
|---|---|
| [`skaileup/contracts/`](skaileup/contracts/DOMAIN.md) | Reference layer (every skill reads) |
| [`skaileup/flows/`](skaileup/flows/) | Self-contained flow YAMLs (graph + `requires:` manifest), per app-type |
| [`skaileup/contracts/scripts/`](skaileup/contracts/scripts/) | CI scripts (pre-commit hook, artifact/flow verifiers) |

## Tiers

The first thing the agent does is pick a tier. The rest of the pipeline is shaped by that choice.

| Tier | Concept | Implementation | Supervision |
|---|---|---|---|
| `appbuilder-mvp` | Linear, minimal (no design slicing) | Single impl-slice (skip recap, refactor) | Autonomous |
| `appbuilder-simple` | Linear, full (one pass) | N × impl-slice (full slice loop) | Autonomous |
| `appbuilder-standard` | Linear high-level + N × concept-slice | N × impl-slice (full + recap mandatory) | Mostly autonomous, plan checkpoint per slice |
| `appbuilder-complex` | Linear high-level + N × concept-slice + project-overview | N × impl-slice (supervised + audit between slices) | HITL |

## Flows

**Each flow is its own install manifest — there are no separate bundles.** A
`<name>.flow.yaml` carries a top-level `requires:` block naming the contracts its
skills read plus every skill its nodes run. Install the whole collection, or just
one flow's dependencies, via the **skaile workspace CLI**:

```
$ skaile add skill:*                    # install every skill (whole collection)
$ skaile add flow:appbuilder-simple            # OR install exactly what appbuilder-simple needs
```

The `requires:` set is **exact** — the skills the flow's nodes run, no
inheritance and no extras. **Flows are run two interchangeable ways** once installed:

```
$ skaile run flow:appbuilder-simple            # 1. the skaile workspace flow engine (connector)
#                                         2. OR the orchestrator (skaileup / skaileup-build),
#                                            which understands the flow files and runs them
#                                            conversationally (human-in-the-loop)
```

```
skaileup/flows/
├── appbuilder-complex/
│   ├── appbuilder-complex.flow.yaml     ← graph + requires: manifest
│   └── appbuilder-complex.md
├── concept-slice/
│   ├── concept-slice.flow.yaml
│   └── concept-slice.md
├── impl-slice/
│   ├── impl-slice.flow.yaml
│   └── impl-slice.md
├── appbuilder-mvp/
│   ├── appbuilder-mvp.flow.yaml
│   └── appbuilder-mvp.md
├── appbuilder-simple/
│   ├── appbuilder-simple.flow.yaml
│   └── appbuilder-simple.md
├── appbuilder-standard/
│   ├── appbuilder-standard.flow.yaml
│   └── appbuilder-standard.md
└── _meta/
    ├── verify_flows.py
    ├── test_verify.py
    └── deferred_skills.yaml
```

`skaileup/flows/_meta/verify_flows.py` validates each flow and enforces that its
`requires:` manifest exactly matches the skills its nodes run — run on every flow
change to prevent drift.

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
$ skaile add flow:appbuilder-standard          # a flow + all its dependencies
```

Local checkouts use `path:` instead of `url:` and are symlinked so edits to SKILL.md are immediately reflected.

## Lineage

Extracted from [`skaile-ai/ai-assets`](https://github.com/skaile-ai/ai-assets) as part of the skill collection reorganization (April 2026). The two reorganizations are documented in [`CLAUDE.md`](CLAUDE.md) § Reorganization Status and in `_devlog/plans/2026-05-07-skill-graph-migration.md` in the skaile-dev shell repo.

## Quick links

- [Skill DSL Grammar](skaileup/contracts/skill_grammar.md)
- [Iron Laws](skaileup/contracts/iron_laws.md)
- [Golden Principles](skaileup/contracts/golden_principles.md)
- [Asset Frontmatter Schema](skaileup/contracts/asset_frontmatter.md)
