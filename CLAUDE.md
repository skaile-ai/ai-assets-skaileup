# Skaileup Skill Catalog

## What This Is

All skaileup-\* skills for the concept, build, and quality pipelines. Extracted from `ai-assets/` as a standalone submodule.

**GitHub:** `github.com/skaile-ai/ai-assets-skaileup`

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
walkthrough-mockup/            clickable application: text · static-html · lit · astro · framework
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
├── SKILL.md        ← YAML frontmatter + markdown body (the agent prompt)
├── CLI.md          ← Optional: CLI invocation docs
├── references/     ← Optional: reference material
└── validator.py    ← Optional: output validation script
```

## Contracts

Shared contracts live in `contracts/contracts/`. All skills reference these.

## Naming Convention

Every skill's `name:` follows the pattern of its **path under the repo root** with `/` replaced by `-`. Examples:

| Path | `name:` |
|---|---|
| `concept/brief/SKILL.md` | `concept-brief` |
| `concept/grounding/onboard/SKILL.md` | `concept-grounding-onboard` |
| `design/brand-visual/SKILL.md` | `design-brand-visual` |
| `experience/screens/SKILL.md` | `experience-screens` |
| `impl-architecture/techstack/SKILL.md` | `impl-architecture-techstack` |
| `impl-architecture/templates/template-postxl/SKILL.md` | `template-postxl` (shortened) |
| `component-mockup/storybook/SKILL.md` | `component-mockup-storybook` |

**Exception — base orchestrator skills:** Skills inside `skaileup/skills/` keep their short names (`skaileup`, `skaileup-build`) instead of the path-based form. The base orchestrator is the catalog's entry point; doubled prefixes would be awkward.

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
