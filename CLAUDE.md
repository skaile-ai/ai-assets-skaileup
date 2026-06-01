# Skaileup Skill Collection

## What This Is

All `skaileup-*` skills for the concept, build, and quality pipelines. Extracted from `ai-assets/` as a standalone submodule.

**GitHub:** `github.com/skaile-ai/ai-assets-skaileup`

## Documentation

- **Starlight site** at [`docs/`](./docs/) — `npm run docs` (or `cd docs && npm install && npm run dev`). Every SKILL.md is rendered as its own page with frontmatter + body, plus pages for the mental model, slice loops, tiers, flows + bundles, and the contracts reference layer.
- **[`CONTRIBUTING.md`](./CONTRIBUTING.md)** — skill-authoring guide for the `skaile` CLI.
- **[`docs/devlog/`](./docs/devlog/)** — plans, specs, design notes, and the improvement backlog.

## Structure

Skills are organized into 17 domains in three groups (Concept, Implementation, Meta).
User-facing skill domains live under `skaileup/`. System/meta assets live under `ai-assets-dev/`.

### Concept  (`skaileup/`)
```
skaileup/concept/                       brief · goals · comparable
skaileup/design/                        brand-identity · tokens · voice
skaileup/product-spec/                  features · acceptance criteria
skaileup/experience/                    journeys · behaviors · screens · components
skaileup/concept-slice/                 per-feature concept loop (big apps only)
skaileup/mockup-component/              components in isolation: storybook + isolated-html
skaileup/mockup-walkthrough/            clickable application: text · static-html · astro · framework
skaileup/mockup-feedback/               annotation → patch loop
```

### Implementation  (`skaileup/`)
```
skaileup/impl-architecture/             techstack · system · datamodel · templates/
skaileup/impl-plan/                     brainstorm · align · plan-vertical · supervised
skaileup/impl-slice/                    per-slice loop: implement · test · recap · refactor · commit
skaileup/impl-build/                    one-time: scaffold · foundation · infrastructure · migrate · seed · generate · docs
skaileup/impl-quality/                  test-* · eval-code · audit · ready · standards-* · debug-*
```

### Meta — user-facing  (`skaileup/`)
```
skaileup/skaileup-orchestrator/         base orchestrators (skaileup, skaileup-build) + scope/ — pipeline entry
skaileup/ops/                           cross-cutting: review · sync · eval · add-feature · reverse-engineer · project-*
```

### Meta — system assets  (`ai-assets-dev/` and `skaileup/`)
```
skaileup/contracts/                     shared reference layer (every skill reads)
skaileup/flows/                         flow + bundle YAMLs, co-located per app-type
skaileup/flows/_meta/                   verify_flows.py · test_verify.py · deferred_skills.yaml
ai-assets-dev/lab/                      skill-on-skill: validate · judge · improve · learn · compile-bundle
ai-assets-dev/scripts/                  CI scripts (check-bundles.sh — drift guard against skaileup/flows/)
ai-assets-dev/tests/                    test fixtures
docs/devlog/                            plans, specs, design notes, improvement backlog
```

## Skill Structure

Every skill lives in its own directory:

```
my-skill/
├── SKILL.md        ← YAML frontmatter + DSL body (the agent prompt)
├── CLI.md          ← Optional: CLI invocation docs
├── references/     ← Optional: reference material loaded on demand
├── scripts/        ← Optional: helper scripts
├── tests/          ← Optional: test manifest + fixtures (lab/validate)
└── validator.py    ← Optional: compiled MUST/NEVER validator
```

The DSL grammar is documented in [`skaileup/contracts/skill_grammar.md`](./skaileup/contracts/skill_grammar.md):
`ROLE / READS / WRITES / REFERENCES / REQUIRES / INPUT / STEP / RUN / OUTPUT / EMIT / CHECKPOINT / IF / ELSE / UNTIL / MUST / NEVER / CHECKLIST / PROCEDURE / PATTERNS`.

The frontmatter schema is documented in [`skaileup/contracts/asset_frontmatter.md`](./skaileup/contracts/asset_frontmatter.md). It follows the [agentskills.io](https://agentskills.io/specification) spec — `name` and `description` at root, everything else under `metadata:`.

## Contracts

Shared contracts live in [`skaileup/contracts/`](./skaileup/contracts/). **Every skill reads from here.** The non-negotiable constraints (iron laws + golden principles) and shared schemas (semantic types, frontmatter, EARS acceptance criteria) live there.

## Naming Convention

Every skill's `name:` follows the **domain-relative path** (without the `skaileup/` prefix) with `/` replaced by `-`. Examples:

| Path | `name:` |
|---|---|
| `skaileup/concept/brief/SKILL.md` | `concept-brief` |
| `skaileup/concept/grounding/onboard/SKILL.md` | `concept-grounding-onboard` |
| `skaileup/design/brand-visual/SKILL.md` | `design-brand-visual` |
| `skaileup/experience/screens/SKILL.md` | `experience-screens` |
| `skaileup/impl-architecture/techstack/SKILL.md` | `impl-architecture-techstack` |
| `skaileup/impl-architecture/templates/template-postxl/SKILL.md` | `template-postxl` (shortened — the directory already starts with `template-`) |
| `skaileup/mockup-component/storybook/SKILL.md` | `mockup-component-storybook` |

**Exception — base orchestrator skills:** Skills inside `skaileup/skaileup-orchestrator/skills/` keep their short names (`skaileup`, `skaileup-build`) instead of the path-based form. The base orchestrator is the collection's entry point; doubled prefixes would be awkward.

> **Note.** The path-prefix convention is authoritative: `name:` = the domain-relative path with `/` → `-`, where the parent directory is the last segment (`brief/` → `concept-brief`). `CONTRIBUTING.md` § Naming Conventions matches this.

## Two-Group Architecture

The collection is shaped by one observation: **the work of figuring out a product and the work of building it have the same rhythm.** Each side benefits from a per-feature loop when the product is too big to design or build in one pass. The result is the same shape on both halves — `concept-slice/` on one side, `impl-slice/` on the other.

```
                    user input  /  existing repo
                              │
                              ▼
                    ╔═════════════════════╗
                    ║    skaileup-base    ║   routes user, runs flows
                    ╚══════════╤══════════╝
                               │
                               ▼
                    ┌──────────────────────────────────────────┐
                    │ skaileup/skaileup-orchestrator/scope/... │   2-3 questions →
                    └────────────────────┬─────────────────────┘   tier + flow
                                 │
              ┌──────────────────┴──────────────────┐
              ▼                                     ▼
   ╔═══════════════════════════╗        ╔══════════════════════════╗
   ║          CONCEPT          ║        ║      IMPLEMENTATION      ║
   ╚═══════════════════════════╝        ╚══════════════════════════╝
   linear (mvp/simple) OR                   one-time setup +
   high-level + slice loop ↻                slice loop ↻
                                                          │
                                                          ▼
                  ╔══════════════════════════╗
                  ║           META           ║
                  ║  skaileup · ops · lab ·  ║
                  ║  contracts               ║
                  ╚══════════════════════════╝
```

Both slice loops follow the same five-phase shape with `/clear` between every phase: brainstorm → align → (scope-feature | plan-vertical) → (design-feature | implement → test → recap → refactor → commit). Phases read from the prior phase's handoff file in `_concept/slices/<id>/` or `_implementation/slices/<id>/`. **No phase carries the whole slice in context** — that's how big apps stay buildable past the dumb-zone (~100k tokens).

The slice dossier is **frozen on commit, not deleted** (Suggestion-B organization): the terminator (`concept-slice-design-feature` / `impl-slice-commit`) writes an `index.md` and **keeps** the phase handoffs as permanent per-feature documentation under `_concept/slices/<id>/` and `_implementation/slices/<id>/`. Truth still lives in code (impl-slice) or in the canonical `_concept/experience/...` artifacts (concept-slice); the dossier is the decision record beside it. The **general (non-slice) part** — brief, goals, brand, journeys, datamodel, techstack, architecture — lives in its phase folders and is not per-slice. Only the impl side's transient `progress.json` is removed on freeze.

## Flows + Bundles

**Bundles are installation manifests, not runners.** A bundle names a subset of
skills to install via the **skaile workspace CLI**. You can install *all* skills,
or install only the subset some flow needs by adding its bundle:

```
$ skaile add skill:*                    # install every skill (whole collection)
$ skaile add bundle:standard-app        # OR install only the subset standard-app needs
```

**Flows are run, not installed** — two interchangeable ways:

1. **skaile workspace flow engine** (the flow connector) executes a `.flow.yaml` directly:
   ```
   $ skaile run flow:standard-app       # engine drives the flow node-by-node
   ```
2. **The orchestrator** (`skaileup` / `skaileup-build`) **understands the flow files** and
   guides/executes the same path conversationally — used when no flow engine is present, or
   when you want a human-in-the-loop run.

Either way the skills the flow references must already be installed (install everything, or the
flow's bundle). A flow has a paired bundle so "install what this flow needs" is one command.

Flows and bundles are co-located under `skaileup/flows/<app-type>/`:

```
skaileup/flows/
├── mvp/
│   ├── mvp.flow.yaml
│   └── mvp.bundle.yaml
├── simple-app/
│   ├── simple-app.flow.yaml
│   └── simple-app.bundle.yaml
... (standard-app, complex-app, concept-slice, impl-slice)
└── _meta/
    ├── verify_flows.py
    ├── test_verify.py
    └── deferred_skills.yaml
```

Bundles inherit: `mvp ⊂ simple-app ⊂ standard-app ⊂ complex-app`. Each file lists only its *additions*. `ai-assets-dev/lab/compile-bundle` walks a flow's node graph and emits the matching bundle YAML next to the flow file; run on every flow change to prevent drift. CI: `ai-assets-dev/scripts/check-bundles.sh`.

## Reorganization Status

The collection underwent two reorganizations:

### Phase 0 (2026-04, complete)
- [x] Domain extraction from ai-assets
- [x] Domain merges (onboard+research→grounding, standards→quality) and splits (blueprint→architecture+datamodel)
- [x] Skill-level directory renames to `skaileup-<domain>-<function>` pattern
- [x] SKILL.md `name:` frontmatter updates
- [x] New domain: `skaileup-build-supervised/` (extracted from build)
- [x] Cross-domain moves: sync→concept-ops, compile-validators→lab, implement→skaileup base

### Phase 1 (2026-05-07, this branch)
- [x] 14 `skaileup-*` domains migrated to the new two-group structure (Concept + Implementation + Meta)
- [x] 16 new top-level domains scaffolded with stub DOMAIN.md
- [x] All ~70 SKILL.md files moved to new homes; `name:` frontmatter updated
- [x] Stack profiles promoted from `skaileup-quality/profiles/` to `impl-architecture/templates/`
- [x] Bulk path-reference update across READS/WRITES/REFERENCES + validator.py imports
- [x] DOMAIN.md content authored (Phase 2)
- [x] Validator creation for skills that lack them (Phase 2)

### Phase 2 — collection quality remediation (2026-05, complete)
The 2026-05-10 collection review backlog has been worked through across five commits (`Phase 1`–`Phase 5` in git history): frontmatter completed on all skills (`version`/`stage`), `user_inputs` → `prerequisites` migration, templates demoted out of the skill model, DOMAIN.md files authored, descriptions normalized, and CI gates added (frontmatter audit, bundle↔flow drift, pre-commit hook).

### Phase 3 — SKILL_GRAPH migration (2026-05-30, complete)
Tracked in [`docs/devlog/SKILL_GRAPH.md`](./docs/devlog/SKILL_GRAPH.md). All 11 deferred tier-flow skills are built; [`skaileup/flows/_meta/deferred_skills.yaml`](./skaileup/flows/_meta/deferred_skills.yaml) is now empty and the flow verifier emits no deferred-skill warnings:

- `concept-goals`, `concept-comparable` (`concept/`), `design-inspiration` (`design/`) — high-level concept pass for standard/complex tiers.
- `impl-architecture-templates-select` — runtime selector over the 7 `template-*` reference assets; writes `tech_stack_skill`.
- `mockup-walkthrough-astro` / `-lit` / `-framework` and the `mockup-feedback-{annotate,triage,patch,apply}` cluster — walkthrough renderers + feedback loop.
