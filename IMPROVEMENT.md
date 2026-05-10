# Improvements & Roadmap

Findings from the 2026-05-10 catalog review across all 17 domains, 94 SKILL.md files, the contracts/, flows/, bundles/ layers, and the `CLAUDE.md` / `CONTRIBUTING.md` / `SKILL_GRAPH.md` / `REFACTOR_MOCKUP.md` reference docs. Items are grouped by **severity × cost-to-fix**; each item names the affected files and the proposed action.

> **Methodology.** Programmatic frontmatter audit on every SKILL.md (`/tmp/skill_audit.json`) plus four parallel domain-deep-read agents (concept-side, mockup, impl-side, meta+templates). Numbers below are reproducible from the audit script in `docs-site/scripts/`.

---

## A. Critical (block other improvements)

### A1. Naming convention contradiction between `CLAUDE.md` and `CONTRIBUTING.md`

- **What's wrong.** `CLAUDE.md` says skill `name:` follows the **path** under repo root with `/` → `-` (84 of 94 skills follow this). `CONTRIBUTING.md` § Naming Conventions says `name:` must match the **parent directory name exactly**. These rules are mutually exclusive: with the catalog's flat `concept/brief/` layout, `name: concept-brief` violates CONTRIBUTING.md, and `name: brief` violates CLAUDE.md.
- **Why it matters.** New contributors get conflicting advice. The CLI's directory-fallback can register a skill under the wrong identifier if the convention isn't clarified.
- **Recommended action.** Rewrite `CONTRIBUTING.md § Naming Conventions` to match the path-prefix convention (the implementation reality). Note that the directory name is the **last segment** of the path-based name. Document the two acknowledged exceptions (`skaileup/skills/skaileup`, `skaileup/skills/skaileup-build`) and the templates shorthand.
- **Affected files.** `CONTRIBUTING.md`, optionally `CLAUDE.md` for clarity.

### A2. 19 skills missing `metadata.version`

- **What's wrong.** `metadata.version` is required by `contracts/asset_frontmatter.md` but absent from 19 SKILL.md files: all of `lab/{learn,report,judge,improve,validate}`, all 7 `impl-architecture/templates/template-*`, all 3 `impl-quality/standards-*`, and all 4 `ops/project-*`.
- **Why it matters.** Flow nodes can pin skill versions (`version: "^1.0.0"`); skills without versions can't participate. CI version-bump checks will silently pass on these files.
- **Recommended action.** Bulk-add `metadata.version: "1.0.0"` (or `"0.1.0"` for alpha-stage) in a single PR. ~20-line patch per file.

### A3. 51 skills missing `metadata.stage`

- **What's wrong.** Required field per `contracts/asset_frontmatter.md`. Missing on most concept-side skills (concept/, design/, experience/, product-spec/, concept-slice/), all 6 storybook sub-skills, all 7 impl-architecture skills, all 7 impl-build skills, all 4 ops/project-* skills, and a few more. See `/tmp/skill_audit.json` for the full list.
- **Recommended action.** Bulk-set `stage: alpha` (default for catalog-wide migration in flux) or `beta` (for skills with validators and tests). Use audit script to flag any new occurrences in CI.

### A4. 18 skills still use deprecated `metadata.user_inputs`

- **What's wrong.** Per `contracts/asset_frontmatter.md`, `user_inputs` is deprecated in favor of `prerequisites.inputs_required` / `prerequisites.inputs_optional`. 18 skills haven't migrated.
- **Affected.** `design/brand-{voice,visual}`, `concept/brief`, `concept/grounding/{onboard,research}`, `product-spec/features`, `impl-plan/supervised`, `impl-architecture/techstack`, `impl-quality/{standards-sync,standards-discover,test-plan}`, `ops/{add-feature,reverse-engineer,review}`, `impl-slice/{git-prepare,finish}`, `skaileup/skills/{skaileup,skaileup-build}`.
- **Recommended action.** `lab/compile-validators`-style mechanical migration: read each `user_inputs.dialog[]` entry, emit `prerequisites.inputs_required[]` (when `required: true`) or `prerequisites.inputs_optional[]`. Add a CI check that fails on `metadata.user_inputs`.

### A5. Templates classified as skills but shouldn't be

- **What's wrong.** All 7 `impl-architecture/templates/template-*/SKILL.md` files are 420–720 lines of pure reference content (scaffold recipes, version constraints, API tables) with **no procedural steps, no MUST/NEVER, no checkpoints**. They are reference assets dressed up as skills.
- **Why it matters.** Template SKILL.md files inflate the catalog count and don't fit the "agent prompt" mental model. They blow past the `<5000 token` body guideline (template-sveltekit-minimal is 720 lines).
- **Recommended action.** Convert templates to `.md` reference files under each domain or to a new `template:` asset kind in `contracts/asset_frontmatter.md`. Either way, drop the SKILL.md filename. The single `impl-architecture/templates-select` cluster selector skill (Phase 3 in SKILL_GRAPH.md) is the right place to encapsulate "which template to use" — it should `READ` the templates rather than them being skills the agent invokes directly.

---

## B. High (worth doing in the next pass)

### B1. concept-slice/ skills are alpha stubs with truncated workflows

- **What's wrong.** All four concept-slice skills (`brainstorm`, `align`, `scope-feature`, `design-feature`) carry `stage: alpha` and have truncated workflow sections — `brainstorm` stops at STEP 4, `align` at STEP 6, `scope-feature` at STEP 4. Compare to the comparable impl-plan/ skills which have complete bodies.
- **Why it matters.** standard-app and complex-app tiers depend on the concept-slice loop (per SKILL_GRAPH.md and bundles inheritance). Running these tiers today would fail mid-loop.
- **Recommended action.** Author the missing steps. Mirror the impl-plan/ shape (which is the working analog) — both halves were designed to follow the same five-phase loop.

### B2. Bidirectional feedback loop is one-way in practice

- **What's wrong.** `mockup-feedback/{annotate,triage,patch,apply}` correctly write to `_concept/_feedback/devlog.md`. **But** the `walkthrough-mockup-{text,static-html,astro}` regenerators don't read `devlog.md` in STEP 1. Every regeneration loses prior human intent.
- **Why it matters.** REFACTOR_MOCKUP.md §5 specifies a *bidirectional* sync. The forward direction works (annotation → patch → apply → devlog). The backward direction (devlog → regeneration) is missing.
- **Recommended action.** Add a STEP 1 to each walkthrough-mockup-* skill: "Read `_feedback/devlog.md`, filter to entries that mention any path the regeneration will touch, and treat their patch summaries as required preserved-intent before regenerating." This is one ~15-line addition per renderer, three renderers — small change, completes the design intent.

### B3. Three eval skills missing `ROLE` keyword

- **What's wrong.** `ops/eval-concept` (and to a lesser degree `ops/eval-feature` / `ops/eval-product`) skip the canonical `ROLE` opener. Most other skills have `ROLE` on or near line 60–80 of the body.
- **Recommended action.** Add a one-line `ROLE` to each. Cosmetic but cheap and improves the consistency the lab/judge skill scores against.

### B4. Some concept-side paths still reference the old `_grounding/general/` layout

- **What's wrong.** `design/brand-{visual,voice}`, `product-spec/features`, `experience/journeys` all reference `_concept/_grounding/general/{competitors,audiences,domain,design_inspiration}.md`. The new `concept-grounding-research` skill writes to `_grounding/research/` (no `general/`). The reads will fail when the new research skill is the writer.
- **Recommended action.** Bulk find-and-replace `_grounding/general/` → `_grounding/research/` in the four affected SKILL.md files. Verify the writers and readers agree on the new path.

### B5. impl-plan/supervised + impl-build/docs use deprecated root `reads_from`/`writes_to`

- **What's wrong.** Per `contracts/asset_frontmatter.md` migration table, root-level `reads_from`/`writes_to` should move under `metadata.prerequisites.{reads,produces}`.
- **Affected.** `impl-plan/supervised/SKILL.md`, `impl-build/docs/SKILL.md`.
- **Recommended action.** Mechanical migration in same PR as A4.

### B6. `screens-technical` is dead weight

- **What's wrong.** `experience/screens-technical/SKILL.md` declares itself "experimental — not in default pipeline" and has no body past STEP 3. It's not in any flow or bundle.
- **Recommended action.** Move to `lab/archive/` (where the precedent exists) or delete. If kept, mark `do_not_invoke: true` so skill discovery doesn't surface it.

---

## C. Medium (improves coherence, low urgency)

### C1. DOMAIN.md files are stubs

- **What's wrong.** All 20 DOMAIN.md files are 11–43 line scaffolds. SKILL_GRAPH.md Phase 2 calls out "DOMAIN.md content authored" as a deferred deliverable. The Starlight site embeds them as the per-domain index page; a richer DOMAIN.md = a more useful overview page.
- **Recommended action.** Author each DOMAIN.md with: (1) when this domain runs in the pipeline; (2) inputs / outputs at the domain level; (3) cross-domain dependencies; (4) a short example call. ~30 minutes per domain, parallelizable.

### C2. Description quality is inconsistent

- **What's wrong.** Per the agentskills.io spec, descriptions should start with "Use when…" for trigger-based agent routing. ~30% of skills do this; the rest are statement-style ("Concept completeness and clarity gate.", "Full app implementation orchestrator.").
- **Why it matters.** The agent's skill router uses `description` to pick which skill to invoke. Statement-style descriptions force the router to infer triggers, which is brittle.
- **Recommended action.** Audit the 50+ statement-style descriptions and rewrite to "Use when …" form. Orchestrator skills (`skaileup`, `skaileup-build`) and gating skills (`eval-*`) are legitimate exceptions — flag them with `metadata.do_not_invoke: true` if they are only invoked from flows.

### C3. DSL grammar consistency

- **What's wrong.** The canonical grammar in `contracts/skill_grammar.md` defines `ROLE / READS / WRITES / REFERENCES / MUST / NEVER / STEP / CHECKLIST`. Adoption varies:
  - 57/94 use ROLE
  - 60/94 use MUST, 59/94 use NEVER
  - 49/94 use CHECKLIST
  - The storybook sub-skills and mockup-feedback skills use older REQUIRES / numbered prose / non-canonical headers
  - The concept-slice cluster invented its own `# ── Workflow ───` divider style
- **Recommended action.** Run `lab/judge` against `contracts/skill_grammar.md` once to score every skill's DSL compliance. Backfill missing CHECKLIST blocks first (highest leverage for validation tooling).

### C4. Triple-eval split needs domain markers

- **What's wrong.** `ops/eval-concept`, `ops/eval-feature`, `ops/eval-product` are correctly split by pipeline gate but their descriptions don't make the gate explicit. The reader has to inspect each to know which runs when.
- **Recommended action.** Add `metadata.gate: pre-impl | per-feature | release` to each. Update descriptions to lead with the gate position.

### C5. `mockup-feedback-patch` references missing schema files

- **What's wrong.** patch and triage skills reference `mockup-feedback/schemas/*.schema.json`, which don't exist in the repo tree.
- **Recommended action.** Either author the schemas (canonical patch payload, triage outcome) or remove the reference and inline the shape.

### C6. `lab/validate-elements-block` is a special case worth normalizing

- **What's wrong.** `lab/validate` runs Docker-isolated test cases from a generic test manifest. `lab/validate-elements-block` is a focused validator for the screen `elements:` frontmatter block. It's a precedent for "narrowly scoped, deterministic validators" sitting in lab/.
- **Recommended action.** Document the pattern in `lab/DOMAIN.md`: "Narrow validators (e.g., elements-block, frontmatter-shape) live alongside the general `validate` runner." Then create explicit slots for the next ones (`validate-frontmatter`, `validate-cross-references`).

---

## D. Low (cosmetic, nice-to-haves)

### D1. `MIGRATION.md` references the old Phase-0 path

- **What's wrong.** `contracts/MIGRATION.md` line 6 references `skaileup-contracts/scripts/validator_lib.py` (Phase 0 naming).
- **Action.** Update to `contracts/scripts/validator_lib.py` or mark the migration row as historical.

### D2. README.md says "17 domains" but the count is closer to 20

- **What's wrong.** `README.md` line 5 says "17 domains in three groups". Counting top-level domain directories with DOMAIN.md: 8 (concept) + 5 (impl) + 4 (meta) = 17. Counting all domains including sub-domains (`concept-grounding`, `impl-architecture/templates`, `component-mockup/storybook`) is more like 20–22. Pick a definition and stick to it.

### D3. `experience-screens` description is overlong (~190 chars)

- **What's wrong.** Some descriptions are way over the typical 100-char band, others are 8 chars (DOMAIN files: `"brief · goals · comparable"`). Consistency check with a CI lint would help.

### D4. `skaileup-build` README mentions `lit` walkthrough variant that isn't in the repo

- **What's wrong.** README.md, CLAUDE.md and SKILL_GRAPH.md reference `walkthrough-mockup-lit` but no `walkthrough-mockup/lit/SKILL.md` exists. Only `text/`, `static-html/`, `astro/` are present.
- **Action.** Either author the lit variant (the docs say it's an "alt for embedded") or remove the references.

### D5. `validator.py` coverage is uneven

- **What's wrong.** 38 of 94 skills have a `validator.py`. The catalog could use a CI gate that enforces: every `stage: stable` skill must have a validator, every `stage: beta` must have a TESTS dir, every `stage: alpha` is allowed to skip both.
- **Action.** Add the rule to `lab/compile-validators` as the validation contract.

---

## E. Splits / merges / removals to consider

### E1. **Merge:** `impl-quality/standards-{discover,inject,sync}` → 1 skill with three modes?

The three skills form a clean discover → inject → sync pipeline (per the impl-side review). They could be merged into a single `impl-quality/standards` skill that takes `--mode={discover|inject|sync}`. Trade-off: simpler catalog, but loses the per-mode SKILL.md as a routable agent prompt. **Verdict: keep as-is.** The split makes them individually invokable from flows, which is the design intent.

### E2. **Don't merge:** `impl-slice/{commit,git-prepare,finish}`

The three appear redundant on first reading but `git-prepare` runs once per project at start, `commit` runs N times during the slice loop, `finish` runs once per project at end. Different lifetimes — keep the split.

### E3. **Remove:** `experience/screens-technical/SKILL.md` (see B6)

### E4. **Remove or convert:** templates as skills (see A5)

### E5. **Split:** `walkthrough-mockup-text` is doing too much

`walkthrough-mockup/text/SKILL.md` (139 lines) describes Alpine, Vue, Preact, Shoelace CDN-based mockups — four different stacks behind one skill. Compare: `walkthrough-mockup/static-html/` (534 lines) does one thing precisely. **Action:** consider splitting `text/` into `text-alpine/`, `text-vue/`, `text-preact/`, or document the multi-stack case explicitly with a sub-skill pattern.

### E6. **Add:** missing `walkthrough-mockup-lit` and `walkthrough-mockup-framework` skills

Both are referenced in the docs and tier composition tables but don't exist as files. Either author them or update the tier tables.

### E7. **Split:** `impl-slice/implement` overlaps with `impl-slice/implement/impl-slice-implement-page`

The nested skill (`impl-slice-implement-page`) is dispatched FROM the parent (`impl-slice-implement`). This works but is structurally unique in the catalog — every other "orchestrator + sub-skill" pair lives at sibling paths. Consider promoting the sub-skill to `impl-slice/implement-page/` (sibling) and removing the unique nesting pattern.

---

## F. Process improvements

### F1. CI gate: frontmatter audit

Wrap the audit script (used to produce `/tmp/skill_audit.json`) into a CI step that fails on:
- Missing `metadata.{version,stage,tags}`
- Use of deprecated `user_inputs` / `reads_from` / `writes_to`
- Skills with `stage: stable` and no `validator.py`

### F2. CI gate: bundle ↔ flow drift

`scripts/check-bundles.sh` already exists but isn't invoked from anywhere visible. Wire it into a pre-merge check so flow edits force bundle regeneration.

### F3. Path-reference sweep on every domain rename

The reorganization moved 14 `skaileup-*` domains to the two-group structure. Cross-domain `READS` / `REFERENCES` paths broke in the four cases noted in B4. Add a pre-commit hook that runs `grep -rE 'skaileup-|_grounding/general/' --include='SKILL.md'` and fails on non-zero matches.

### F4. Rename `REFACTOR_MOCKUP.md` → `docs/mockup-design.md` once the refactor lands

The refactor was the design doc that drove Phase 2 of the mockup work. With Phase 2 mostly complete (per CLAUDE.md), the file is now reference documentation, not a refactor proposal. Move it under `docs/` to reflect that.

---

## Appendix — Audit data

The structured audit lives at `/tmp/skill_audit.json` (re-run from `docs-site/scripts/audit.py` if needed). Key counts:

| Dimension | Count |
|---|---|
| Total skills | 94 |
| Has metadata block | 85 |
| Missing version | 19 |
| Missing stage | 51 |
| Missing tags | 9 |
| Uses prerequisites schema | 72 |
| Uses deprecated user_inputs | 18 |
| Uses deprecated reads_from / writes_to | 2 |
| Has validator.py | 38 |
| Has CLI.md | 17 |
| Has references/ | 28 |
| Has tests/ | 21 |
| Has ROLE keyword | 57 |
| Has CHECKLIST | 49 |

---

*Findings sourced from a 2026-05-10 catalog review. Each entry names the affected files; the proposed actions are the smallest changes the reviewer believes accomplish the stated goal. None of these have been applied yet.*
