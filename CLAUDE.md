# Skaileup Skill Catalog

## What This Is

All `skaileup-*` skills for the concept, build, and quality pipelines. Extracted from `ai-assets/` as a standalone submodule.

**GitHub:** `github.com/skaile-ai/ai-assets-skaileup`

## Documentation

- **Starlight site** at [`docs-site/`](./docs-site/) — `cd docs-site && npm install && npm run dev`. Every SKILL.md is rendered as its own page with frontmatter + body, plus pages for the mental model, slice loops, tiers, flows + bundles, and the contracts reference layer.
- **[`SKILL_GRAPH.md`](./SKILL_GRAPH.md)** — design rationale and migration map.
- **[`REFACTOR_MOCKUP.md`](./REFACTOR_MOCKUP.md)** — mockup cluster design (component / walkthrough / feedback).
- **[`CONTRIBUTING.md`](./CONTRIBUTING.md)** — skill-authoring guide for the `skaile` CLI.
- **[`IMPROVEMENT.md`](./IMPROVEMENT.md)** — open issues and roadmap from the 2026-05-10 review.

## Structure

Skills are organized into 17 top-level domains in three groups (Concept, Implementation, Meta).

### Concept
```
concept/                       brief · goals · comparable
design/                        brand-identity · tokens · voice
product-spec/                  features · acceptance criteria
experience/                    journeys · behaviors · screens · components
concept-slice/                 per-feature concept loop (big apps only)
component-mockup/              components in isolation: storybook + isolated-html
walkthrough-mockup/            clickable application: text · static-html · astro · framework
mockup-feedback/               annotation → patch loop
```

### Implementation
```
impl-architecture/             techstack · system · datamodel · templates/
impl-plan/                     brainstorm · align · plan-vertical · supervised
impl-slice/                    per-slice loop: implement · test · recap · refactor · commit
impl-build/                    one-time: scaffold · foundation · infrastructure · migrate · seed · generate · docs
impl-quality/                  test-* · eval-code · audit · ready · standards-* · debug-*
```

### Meta
```
skaileup/                      base orchestrators (skaileup, skaileup-build) + scope/ — pipeline entry
ops/                           cross-cutting: review · sync · eval · add-feature · reverse-engineer · project-*
lab/                           skill-on-skill: validate · judge · improve · learn · compile-validators
contracts/                     shared reference layer (every skill reads)
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

The DSL grammar is documented in [`contracts/skill_grammar.md`](./contracts/skill_grammar.md):
`ROLE / READS / WRITES / REFERENCES / REQUIRES / INPUT / STEP / RUN / OUTPUT / EMIT / CHECKPOINT / IF / ELSE / UNTIL / MUST / NEVER / CHECKLIST / PROCEDURE / PATTERNS`.

The frontmatter schema is documented in [`contracts/asset_frontmatter.md`](./contracts/asset_frontmatter.md). It follows the [agentskills.io](https://agentskills.io/specification) spec — `name` and `description` at root, everything else under `metadata:`.

## Contracts

Shared contracts live in the top-level [`contracts/`](./contracts/) directory. **Every skill reads from here.** The non-negotiable constraints (iron laws + golden principles) and shared schemas (semantic types, frontmatter, EARS acceptance criteria) live there.

## Naming Convention

Every skill's `name:` follows the **path under the repo root** with `/` replaced by `-`. Examples:

| Path | `name:` |
|---|---|
| `concept/brief/SKILL.md` | `concept-brief` |
| `concept/grounding/onboard/SKILL.md` | `concept-grounding-onboard` |
| `design/brand-visual/SKILL.md` | `design-brand-visual` |
| `experience/screens/SKILL.md` | `experience-screens` |
| `impl-architecture/techstack/SKILL.md` | `impl-architecture-techstack` |
| `impl-architecture/templates/template-postxl/SKILL.md` | `template-postxl` (shortened — the directory already starts with `template-`) |
| `component-mockup/storybook/SKILL.md` | `component-mockup-storybook` |

**Exception — base orchestrator skills:** Skills inside `skaileup/skills/` keep their short names (`skaileup`, `skaileup-build`) instead of the path-based form. The base orchestrator is the catalog's entry point; doubled prefixes would be awkward.

> **Note.** The `CONTRIBUTING.md` § Naming Conventions section says `name:` must match the parent directory name exactly. The catalog actually uses path-based naming where the parent directory is just the last segment (`brief/` → `concept-brief`). The path-prefix convention here is authoritative; `CONTRIBUTING.md` is being reconciled. See [`IMPROVEMENT.md`](./IMPROVEMENT.md) item A1.

## Two-Group Architecture

The catalog is shaped by one observation: **the work of figuring out a product and the work of building it have the same rhythm.** Each side benefits from a per-feature loop when the product is too big to design or build in one pass. The result is the same shape on both halves — `concept-slice/` on one side, `impl-slice/` on the other.

```
                    user input  /  existing repo
                              │
                              ▼
                    ╔═════════════════════╗
                    ║    skaileup-base    ║   routes user, runs flows
                    ╚══════════╤══════════╝
                               │
                               ▼
                    ┌──────────────────────────┐
                    │ skaileup/scope/scope-... │   2-3 questions →
                    └────────────┬─────────────┘   tier + flow
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

Both slice loops follow the same five-phase shape with `/clear` between every phase: brainstorm → align → (scope-feature | plan-vertical) → (design-feature | implement → test → recap → refactor → commit). Phases read from the prior phase's scratch file in `_slice/concept/<id>/` or `_slice/impl/<id>/`. **No phase carries the whole slice in context** — that's how big apps stay buildable past the dumb-zone (~100k tokens).

Scratch is **deleted on commit**: truth lives in code (impl-slice) or in permanent `_concept/` artifacts (concept-slice).

## Flows + Bundles

Each flow has a paired bundle. The bundle lists exactly the skills the flow runs:

```
$ skaile add bundle:standard-app        # install the skills
$ skaile run flow:standard-app          # execute the flow
```

Bundles inherit: `mvp ⊂ simple-app ⊂ standard-app ⊂ complex-app`. Each file lists only its *additions*. `lab/compile-bundle` walks a flow's node graph and emits the matching bundle YAML; run on every flow change to prevent drift. CI: `scripts/check-bundles.sh`.

## Reorganization Status

The catalog underwent two reorganizations:

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
- [ ] DOMAIN.md content authored (Phase 2)
- [ ] Validator creation for skills that lack them (Phase 2)

### Phase 2 — to be planned
Tracked in [`IMPROVEMENT.md`](./IMPROVEMENT.md). Highlights:

- **A2/A3:** 19 skills missing `metadata.version`, 51 missing `metadata.stage` — bulk-add.
- **A4:** 18 skills still on deprecated `metadata.user_inputs` — migrate to `prerequisites.inputs_required` / `inputs_optional`.
- **A5:** Templates (7 skills, 420–720 lines each) shouldn't be skills — convert to a new `template:` asset kind.
- **B1:** concept-slice cluster has truncated workflows; standard-app and complex-app tiers depend on these.
- **B2:** Mockup feedback loop is one-way — walkthrough-mockup-* regenerators don't read the devlog.
- **C1:** All 20 DOMAIN.md files are stubs.
