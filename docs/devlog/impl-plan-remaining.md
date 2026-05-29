# Remaining Implementation Plan

Status as of 2026-05-29. Picks up after the cleanup session that closed A2, A3, A4 (22/24 skills), C1.

Items reference IMPROVEMENT.md codes (A1–F4).

---

## Phase 1 — Mechanical fixes (1 commit)

All are grep-and-replace or small targeted edits. No authoring judgment required. ~1–2h.

### A1 — Fix CONTRIBUTING.md §Naming Conventions
Rewrite the naming section to match the path-prefix convention (the implementation reality): `name:` = domain-relative path with `/` → `-`. Document the two short-name exceptions (`skaileup`, `skaileup-build`) and the `template-*` shorthand. File: `CONTRIBUTING.md`.

### A4 residual — 2 remaining user_inputs
Two skills were missed in the eba7c8c migration pass:
- `skaileup/design/brand-voice/SKILL.md`
- `skaileup/impl-architecture/techstack/SKILL.md`

Migrate `user_inputs.dialog[]` → `prerequisites.inputs_required[]` / `inputs_optional[]` per the same schema used in eba7c8c.

### B3 — Add ROLE to 3 eval skills
Files missing `ROLE` keyword:
- `skaileup/ops/eval-concept/SKILL.md`
- `skaileup/ops/eval-feature/SKILL.md`
- `skaileup/ops/eval-product/SKILL.md`

Add a one-line `ROLE` opener to each body (e.g. `ROLE Concept completeness evaluator — gates pipeline progress.`).

### B4 — Replace `_grounding/general/` → `_grounding/research/`
The original IMPROVEMENT.md B4 listed 4 files; the actual count is 12. All SKILL.md files that read from the old path:
- `skaileup/experience/screens/SKILL.md`
- `skaileup/experience/behaviors/SKILL.md`
- `skaileup/experience/journeys/SKILL.md`
- `skaileup/experience/screens-technical/SKILL.md`
- `skaileup/design/brand-visual/SKILL.md`
- `skaileup/product-spec/features/SKILL.md`
- `skaileup/mockup-walkthrough/text/SKILL.md`
- `skaileup/concept/grounding/research/SKILL.md`
- `skaileup/concept/brief/SKILL.md`
- `skaileup/impl-architecture/techstack/SKILL.md`
- `skaileup/impl-architecture/system/SKILL.md`
- `skaileup/impl-architecture/datamodel/SKILL.md`

Bulk `sed -i 's|_grounding/general/|_grounding/research/|g'` on all 12.

### B5 — Migrate deprecated reads_from/writes_to (6 skills)
Move root-level `reads_from`/`writes_to` to `metadata.prerequisites.reads`/`produces`:
- `skaileup/impl-plan/supervised/SKILL.md`
- `skaileup/impl-build/docs/SKILL.md`
- `skaileup/ops/project-review/SKILL.md`
- `skaileup/ops/project-overview/SKILL.md`
- `skaileup/ops/project-integration/SKILL.md`
- `skaileup/ops/project-subsystem-map/SKILL.md`

### C4 — Add metadata.gate to eval skills
Add `metadata.gate: pre-impl` (eval-concept), `per-feature` (eval-feature), `release` (eval-product) to the three eval SKILL.md frontmatter blocks. Update descriptions to lead with the gate position.

### D1 — Fix MIGRATION.md stale path
`docs/devlog/MIGRATION.md` line 6 references `skaileup-contracts/scripts/validator_lib.py`. Update to `contracts/scripts/validator_lib.py`.

### D2 — Fix README.md domain count
Line 5 says "17 domains". True count with DOMAIN.md files: 8 concept + 5 impl + 4 meta-user + 1 contracts + 1 flows + 1 lab = 20 top-level domains. Update the count and definition.

### D3 — Trim experience-screens description
`experience/screens/SKILL.md` description exceeds 190 chars. Trim to ≤120 chars.

### F4 — Rename REFACTOR_MOCKUP.md → mockup-design.md
The refactor is complete. `docs/devlog/REFACTOR_MOCKUP.md` is now reference documentation. Rename to `docs/devlog/mockup-design.md`. Update any cross-references (CLAUDE.md, README.md, IMPROVEMENT.md).

---

## Phase 2 — Structural cleanup (1–2 commits)

Requires moving/removing files and making judgment calls on existing content. ~2–3h.

### B6/E3 — Archive screens-technical
`skaileup/experience/screens-technical/SKILL.md` is explicitly "experimental — not in default pipeline" and has no body past STEP 3. It is not in any flow or bundle.

**Action:** Move to `ai-assets-dev/lab/archive/` (mirrors the existing archival precedent) OR add `metadata.do_not_invoke: true` and a notice at the top of the body that this skill is not production-ready. Prefer the archive move — it removes it from skill discovery entirely.

### A5/E4 — Convert 7 template-* SKILL.md to reference files
The 7 `skaileup/impl-architecture/templates/template-*/SKILL.md` files (420–720 lines, pure reference content, no MUST/NEVER/CHECKLIST) are not skills. They are scaffold recipes.

**Action:**
1. Rename each `SKILL.md` → `TEMPLATE.md` inside its directory.
2. Add `template:` asset kind to `skaileup/contracts/asset_frontmatter.md` with a minimal frontmatter schema:
   ```yaml
   name: template-name
   description: "One-line summary"
   metadata:
     stage: alpha | beta | stable
     type: template
     stack: [...]
   ```
3. Update `impl-architecture/DOMAIN.md` and the Starlight docs site config to render `TEMPLATE.md` files.
4. Remove the 7 entries from any flow/bundle YAML that currently lists them as skills.

### D4 — Resolve lit/framework references
README.md, CLAUDE.md, and SKILL_GRAPH.md reference `mockup-walkthrough-lit` but no such skill exists (`mockup-walkthrough/` only has `text/`, `static-html/`, `astro/`).

**Action (choose one):**
- **Remove:** Delete the lit references from README, CLAUDE.md, SKILL_GRAPH.md tier tables. Update any bundle YAML that lists it.
- **Author:** Add `mockup-walkthrough/lit/SKILL.md` with the CDN-embed pattern (Lit Web Components, no build step). This is a real gap for the "embedded widget" use case mentioned in the docs.

Recommended: remove for now, file as a future addition under E6.

### E7 — Consider unnesting impl-slice/implement-page
`impl-slice/implement/impl-slice-implement-page/SKILL.md` is dispatched FROM `impl-slice/implement/SKILL.md`. This is the only nested skill pair in the catalog. All other orchestrator+sub-skill pairs are siblings.

**Action:** Promote to `impl-slice/implement-page/SKILL.md` (sibling to `impl-slice/implement/`). Update the parent skill's EMIT/STEP that dispatches it. Update any flow/bundle that references the old path.

---

## Phase 3 — Content authoring (2–3 commits)

Requires writing new skill body content. Each item is a real writing task.

### B1 — Complete concept-slice skill bodies
Four skills have truncated workflow sections:
- `concept-slice/brainstorm/SKILL.md` — stops at STEP 4
- `concept-slice/align/SKILL.md` — stops at STEP 6
- `concept-slice/scope-feature/SKILL.md` — stops at STEP 4
- `concept-slice/design-feature/SKILL.md` — needs verification

**Reference:** Mirror the impl-plan/ cluster shape (the working analog), which has complete 5-phase loops. Both were designed with the same rhythm: brainstorm → align → scope → design/plan → implement.

**Action:** Author the missing steps for each skill, following the impl-plan/ counterparts as structural templates. Add MUST/NEVER/CHECKLIST blocks to match catalog quality. Mark `stage: beta` once complete.

### B2 — Add devlog read to mockup-walkthrough-* regenerators
Three regenerator skills don't read `_feedback/devlog.md` before regenerating, causing loss of prior human annotations.

Files:
- `skaileup/mockup-walkthrough/text/SKILL.md`
- `skaileup/mockup-walkthrough/static-html/SKILL.md`
- `skaileup/mockup-walkthrough/astro/SKILL.md`

**Action:** Add STEP 1 to each:
```
STEP 1 — Read devlog
  Read `_feedback/devlog.md` if it exists.
  Filter to entries that mention any path this regeneration will touch.
  Treat their patch summaries as preserved-intent constraints — do not undo them.
```
~15 lines per file, 3 files.

---

## Phase 4 — Quality sweep (1–2 commits)

High volume, parallelizable, mostly cosmetic but improves routing accuracy.

### C2 — Rewrite statement-style descriptions
~30% of skills currently have `description:` as a statement ("Concept completeness and clarity gate.") rather than the required trigger form ("Use when…"). Routing accuracy degrades when descriptions aren't trigger-oriented.

**Action:** Audit every SKILL.md `description:` field. Rewrite statement-style entries to "Use when [trigger conditions]. NOT when [exclusion]." Orchestrator skills and system contracts (`do_not_invoke: true`) are exempt.

### C3 — DSL grammar consistency
Key gaps per catalog-wide count:
- 37/94 skills missing `ROLE`
- 45/94 missing `CHECKLIST`
- mockup-feedback and storybook sub-skills use older prose style

**Action:** Run `lab/judge` against `contracts/skill_grammar.md` to score each skill. Backfill missing `CHECKLIST` blocks first (highest leverage for validation tooling). Add `ROLE` to all skills missing it. This is parallelizable across domains.

### C6 — Document narrow validator pattern in lab/DOMAIN.md
`lab/validate-elements-block` established a pattern for narrowly scoped deterministic validators. Document it in `ai-assets-dev/lab/DOMAIN.md`:

> Narrow validators (e.g. `validate-elements-block`, `validate-frontmatter`) live alongside the general `validate` runner and follow the same Docker-isolated test manifest schema. Create one when a contract has a bounded schema that can be deterministically checked.

Add placeholder slots for `validate-frontmatter` and `validate-cross-references`.

---

## Phase 5 — CI / process (1 commit)

### F1 — Frontmatter audit CI gate
Promote `docs/scripts/audit.py` to a CI check. Fail on:
- Missing `metadata.{version,stage,tags}`
- Use of deprecated `user_inputs` / `reads_from` / `writes_to`
- Skills with `stage: stable` and no `validator.py`

### F2 — Wire check-bundles.sh
`ai-assets-dev/scripts/check-bundles.sh` exists but isn't referenced from any CI config. Add it as a pre-merge step (GitHub Actions `.github/workflows/` or equivalent).

### F3 — Path-reference pre-commit hook
Add a pre-commit hook that greps for `_grounding/general/` in SKILL.md files and fails if any match. This prevents B4-style regressions after domain renames.

---

## Status summary

| Item | Phase | Effort | Status |
|---|---|---|---|
| A1 CONTRIBUTING.md naming | 1 | small | todo |
| A4 residual (2 skills) | 1 | small | todo |
| A5/E4 templates → reference | 2 | medium | todo |
| B1 concept-slice body | 3 | large | todo |
| B2 devlog read in regenerators | 3 | small | todo |
| B3 ROLE in eval skills | 1 | small | todo |
| B4 _grounding/general/ → research/ (12 files) | 1 | small | todo |
| B5 reads_from/writes_to migration (6 files) | 1 | small | todo |
| B6/E3 archive screens-technical | 2 | small | todo |
| C2 description rewrites | 4 | large | todo |
| C3 DSL grammar sweep | 4 | large | todo |
| C4 gate metadata on eval skills | 1 | small | todo |
| C5 mockup-feedback schemas | — | — | done (schemas exist) |
| C6 lab validator pattern doc | 4 | small | todo |
| D1 MIGRATION.md path | 1 | small | todo |
| D2 README domain count | 1 | small | todo |
| D3 experience-screens description | 1 | small | todo |
| D4 lit references | 2 | small | todo |
| D5 validator.py CI rule | 5 | small | todo |
| E5 split mockup-walkthrough-text | — | medium | deferred |
| E6 author lit/framework skills | — | large | deferred |
| E7 unpack impl-slice/implement-page | 2 | small | todo |
| F1 frontmatter CI gate | 5 | medium | todo |
| F2 wire check-bundles.sh | 5 | small | todo |
| F3 path-reference pre-commit hook | 5 | small | todo |
| F4 rename REFACTOR_MOCKUP.md | 1 | small | todo |

**Deferred (explicitly out of scope):** E5 (text skill split), E6 (author lit/framework skills), E1 (standards merge — kept as-is by design).
