# Task 2C — `impl-plan/{align, plan-vertical}` Cluster Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author the two new `impl-plan/*` skills (`align`, `plan-vertical`) — and refresh the already-migrated `impl-plan/brainstorm` — that compose into the per-slice impl-loop entry sequence (`brainstorm → align → plan-vertical`). They consume `_concept/_meta/scope.yaml` (Task 2A) plus the permanent feature artifacts produced by `concept-slice/design-feature` (Task 2B), and produce the slice scratch handoffs `_slice/impl/<id>/{brainstorm,align,plan}.md` consumed by Task 2D's `impl-slice/implement`.

**Architecture:**
- Three sibling skills under `impl-plan/{brainstorm,align,plan-vertical}/`, all path-named per CONTRIBUTING.md.
- Strict baton-pass identical in shape to `concept-slice/*`: each skill `READS` the previous phase's handoff in `_slice/impl/<slice_id>/`, refuses on miss (Iron Law § 7), `WRITES` its own phase file. None of the three permanent-writes; only Task 2D's `impl-slice/commit` deletes the slice dir.
- Tier context read once per phase from `_concept/_meta/scope.yaml`. Tier composition table (SKILL_GRAPH § 6) determines whether a phase is in this tier's bundle: `brainstorm` only for standard-app/complex-app; `align` for simple-app/standard-app/complex-app; `plan-vertical` for ALL tiers including mvp.
- All three ask interview questions; Iron Law § 9 enforced as "one question per assistant message".
- `plan-vertical`'s prompt actively resists horizontal decomposition (a high-frequency LLM failure mode) — anti-horizontal language is baked into MUST/NEVER + STEP wording, not just mentioned.

**Tech Stack:**
- Skill DSL per `contracts/skill_grammar.md`; frontmatter per `contracts/asset_frontmatter.md` (skills).
- Markdown handoffs (`_slice/impl/<slice_id>/<phase>.md`) with YAML frontmatter on each.
- Python 3.12+ for per-skill `validator.py` (PyYAML, stdlib only).

---

## Pre-flight

- [ ] **Pre-1: Confirm cwd**

Run: `pwd`
Expected: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

- [ ] **Pre-2: Confirm git state**

Run: `git status -sb`
Expected: clean tree, or only untracked plan docs on the active migration branch. If unrelated dirty files, stop and clarify.

- [ ] **Pre-3: Confirm target dirs**

Run: `ls -la impl-plan/`
Expected: contains `brainstorm/` (with old `SKILL.md` to refresh), `plan-vertical/` (with old `SKILL.md` to overwrite), `supervised/` (untouched here), `skills/` (placeholder), `DOMAIN.md`. The dir `impl-plan/align/` does **NOT** yet exist — Task 2 creates it.

Run: `ls -la impl-plan/brainstorm/ impl-plan/plan-vertical/ 2>&1 | head -20`
Expected: each contains a single `SKILL.md` from Phase 1 migration.

- [ ] **Pre-4: Confirm source documents readable**

Run: `wc -l SKILL_GRAPH.md contracts/iron_laws.md contracts/skill_grammar.md contracts/asset_frontmatter.md contracts/plans.md CONTRIBUTING.md docs/superpowers/plans/2A-scope-project.md docs/superpowers/plans/2B-concept-slice-cluster.md impl-plan/brainstorm/SKILL.md impl-plan/plan-vertical/SKILL.md`
Expected: all line counts non-zero.

- [ ] **Pre-5: Confirm 2A and 2B mini-plans pin the schemas this cluster reads**

Run: `grep -n "schema_version\|tier:" docs/superpowers/plans/2A-scope-project.md | head -3`
Expected: matches (the `scope.yaml` schema is pinned in 2A).

Run: `grep -n "product-spec/features\|experience/screens" docs/superpowers/plans/2B-concept-slice-cluster.md | head -5`
Expected: matches (the per-feature artifact paths are pinned in 2B).

- [ ] **Pre-6: Confirm naming convention**

Per `CONTRIBUTING.md` § Naming Conventions, the three `name:` fields MUST be:
- `impl-plan-brainstorm` (dir: `impl-plan/brainstorm/`)
- `impl-plan-align` (dir: `impl-plan/align/`)
- `impl-plan-plan-vertical` (dir: `impl-plan/plan-vertical/`)

Each `name:` MUST equal the parent directory name exactly (no shortening).

---

## Source-of-Truth Anchors (read before authoring any skill)

The executing agent MUST read each of these once, in this order, before starting Task 1:

1. `docs/superpowers/plans/2A-scope-project.md` — § "Pinned Schema — `_concept/_meta/scope.yaml`". The `tier`/`signals` schema is the contract for every read in this cluster. **Do not redefine.**
2. `docs/superpowers/plans/2B-concept-slice-cluster.md` — pinned permanent artifact paths (`_concept/product-spec/features/<group>/<feature_slug>.md`, `_concept/experience/screens/<feature_slug>/<screen>.md`, `_concept/walkthrough-mockup/<tier>/<feature_slug>.<ext>`) AND § "Pinned: Slice-ID Format" (this cluster reuses the `<feature_slug>` rule — see § "Slice-id continuity" below). **Note the lifecycle distinction:** `_slice/concept/<id>/` has been DELETED by `concept-slice/design-feature` before this cluster runs; this cluster reads PERMANENT artifacts only.
3. `SKILL_GRAPH.md` — § 5.2 (per-slice impl loop, brainstorm/align/plan-vertical phases) and § 7 (workspace zones; `_slice/impl/<id>/` lifetime).
4. `contracts/iron_laws.md` — § 7 (no artifact without prerequisites), § 9 (questions are standalone messages).
5. `contracts/skill_grammar.md` — DSL keywords (ROLE, READS, WRITES, MUST, NEVER, STEP, CHECKPOINT, OUTPUT, IF/ELSE, EMIT, CHECKLIST, INPUT, REQUIRES). Especially § "Authoring tips" #4 (place constraints early).
6. `contracts/asset_frontmatter.md` — § "Skill — SKILL.md" frontmatter schema; especially `metadata.prerequisites.{files,inputs_required,inputs_optional,reads,produces}`.
7. `contracts/plans.md` — PLANS.md convention; this cluster's `plan.md` schema is **slice-scoped**, not full-project (the `plan.md` here is per-slice, distinct from project-level `_implementation/PLANS.md`). § "Pinned: plan.md schema" below proposes the slice-plan format and flags the gap.
8. `CONTRIBUTING.md` — § Naming Conventions, § Integrity Checklist.
9. `impl-plan/brainstorm/SKILL.md` (existing) — sibling reference; current content is the Phase-1 migrated version with old paths (`_implementation/brainstorm.md`) — refresh in Task 1.
10. `impl-plan/plan-vertical/SKILL.md` (existing) — also Phase-1 migrated; old content writes `_implementation/superpowers-plan.md` (project-wide), NOT `_slice/impl/<id>/plan.md` (per-slice). Task 3 effectively rewrites this skill. Keep the dependency-ordering insight from the old version where useful but the WRITES path and per-slice scope are NEW.

---

## Pinned: `scope.yaml` Read Pattern (consistent with 2A)

Every skill in this cluster reads `_concept/_meta/scope.yaml` once at start. Fields consumed:

```python
import yaml
scope = yaml.safe_load(open("_concept/_meta/scope.yaml"))
tier         = scope["tier"]              # mvp | simple-app | standard-app | complex-app
description  = scope["description"]       # one-sentence project description (context)
features_est = scope["signals"]["features_estimate"]
```

**Refuse-to-run gates (Iron Law § 7):**

| Skill | scope.yaml gate | predecessor handoff gate | concept-artifact gate |
|---|---|---|---|
| `impl-plan-brainstorm` | hard: tier ∈ {standard-app, complex-app} (per SKILL_GRAPH § 6 row "impl-plan/brainstorm") | none (cluster entry for tiers that include brainstorm) | hard: `_concept/product-spec/features/<group>/<feature_slug>.md` for the slice's feature |
| `impl-plan-align` | hard: tier ∈ {simple-app, standard-app, complex-app} (per SKILL_GRAPH § 6 row) | hard: `_slice/impl/<id>/brainstorm.md` IF tier ∈ {standard-app, complex-app}; if tier == simple-app, brainstorm is not in the bundle so align is the entry point | hard: same feature artifact path |
| `impl-plan-plan-vertical` | hard: tier ∈ ALL (mvp/simple/standard/complex per SKILL_GRAPH § 6 — every tier runs plan-vertical) | hard: `_slice/impl/<id>/align.md` IF tier ∈ {simple, standard, complex}; if tier == mvp, align is not in the bundle so plan-vertical is the entry point | hard: same feature artifact path |

Each skill MUST emit a clear refusal message (with the exact missing path) before exiting. Refusal is not a warning — it's a hard stop.

**Tier-driven entry-point rule:** the cluster uses the same composability pattern as `concept-slice/*` — a phase's predecessor gate is *conditional on tier*. The frontmatter declares the predecessor file as `gate: soft`; the body's STEP 1 enforces the tier-dependent hard gate.

---

## Pinned: Slice-ID Continuity Between Concept and Impl Clusters

**Rule:** the impl-plan slice REUSES the same `<feature_slug>` slice-id assigned by `concept-slice/brainstorm` (or, for simple-app, `concept-slice/align`). The slice-id flows from concept → impl through the **feature filename**, not through any cross-cluster file (since `_slice/concept/<id>/` is deleted by `concept-slice/design-feature` before this cluster runs).

**Derivation:**
1. `impl-plan-brainstorm` (or `impl-plan-align` for simple-app, or `impl-plan-plan-vertical` for mvp) collects `feature_slug` as a required input.
2. The skill resolves the slug to a feature path: `_concept/product-spec/features/<group>/<feature_slug>.md`. If the file does not exist, refuse and ask the user which feature.
3. `slice_id := feature_slug`. Same kebab-case format as 2B (regex `^[a-z][a-z0-9-]{1,47}$`).
4. The impl-slice scratch dir is `_slice/impl/<slice_id>/` — same shape as concept's `_slice/concept/<slice_id>/`, different parent dir (`impl/` vs `concept/`). Both can coexist briefly during a tier where concept and impl interleave per-feature, but per the lifecycle invariant in § "Pinned: `_slice/impl/<id>/` Lifecycle" below, only ONE impl slice for a given feature is active at a time.

**Justification for slug reuse:** the concept and impl slices for a single feature are conceptually "one slice in two phases." Reusing the slug makes traceability mechanical (find slice scratch + concept scratch by the same name during cross-phase debugging if needed; though concept scratch is gone by the time impl runs, the slug still appears in the permanent feature filename).

**Open caveat (flagged):** the parent plan and 2B's open question §1 left UUID vs date+slug vs raw slug undecided. **This plan adopts raw slug** for symmetry with 2B. If 2B's slug rule changes during execution, this cluster must update its slug regex in lockstep.

**Where the slug is stored:** every phase file has YAML frontmatter:

```yaml
---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
feature_path: _concept/product-spec/features/<group>/team-todo-comments.md
phase: brainstorm   # | align | plan
tier: standard-app
created_at: 2026-05-08T12:34:56Z
last_updated: 2026-05-08T12:34:56Z
---
```

Each phase reads `slice_id`, `feature_title`, `feature_path` from the predecessor's handoff frontmatter (no re-prompting).

---

## Pinned: `_slice/impl/<id>/` Lifecycle

```
+--------------------------+--------------------------+----------------------------------+
| Phase                    | Owner                    | Action                           |
+--------------------------+--------------------------+----------------------------------+
| dir creation             | first phase that runs    | mkdir -p _slice/impl/<id>/       |
|                          | for the tier:            |                                  |
|                          |   standard/complex →     |                                  |
|                          |     impl-plan-brainstorm |                                  |
|                          |   simple →               |                                  |
|                          |     impl-plan-align      |                                  |
|                          |   mvp →                  |                                  |
|                          |     impl-plan-plan-      |                                  |
|                          |     vertical             |                                  |
| brainstorm.md  write     | impl-plan-brainstorm     | append phase file                |
| align.md       write     | impl-plan-align          | append phase file                |
| plan.md        write     | impl-plan-plan-vertical  | append phase file                |
| (impl-slice/* runs)      | (Task 2D)                | reads plan.md, may write recap.md|
| dir deletion             | impl-slice-commit (2D)   | rm -rf _slice/impl/<id>/         |
|                          |                          | (only after atomic commit lands) |
+--------------------------+--------------------------+----------------------------------+
```

**Lifecycle invariant:** at most one `_slice/impl/<id>/` exists per active impl slice. Files are append-only across phases (brainstorm doesn't touch align.md, etc.). Only `impl-slice-commit` (Task 2D) deletes — and only after atomic commit lands. **None of the three skills in this cluster delete the dir.**

**Why the entry-point rule varies by tier:** SKILL_GRAPH § 6 tier composition table:

| | mvp | simple | standard | complex |
|---|---|---|---|---|
| `impl-plan/brainstorm` | | | ✓ | ✓ |
| `impl-plan/align` | | ✓ | ✓ | ✓ |
| `impl-plan/plan-vertical` | ✓ | ✓ | ✓ | ✓ |

So mvp's flow is just `plan-vertical → impl-slice/implement`; simple-app's is `align → plan-vertical → impl-slice/*`; standard/complex run all three. Each potential entry point must be capable of `mkdir -p _slice/impl/<id>/`.

---

## Pinned: `align.md` Schema (output of `impl-plan-align`)

Path: `_slice/impl/<slice_id>/align.md`

Frontmatter shape (cross-phase contract; same shape as concept-slice align.md but `phase: align`, scope is impl):

```yaml
---
slice_id: <slug>
feature_title: <free-text title>
feature_path: _concept/product-spec/features/<group>/<feature_slug>.md
phase: align
tier: <enum from scope.yaml>
created_at: <ISO-8601 UTC Z>
last_updated: <ISO-8601 UTC Z>
---
```

**Required body sections (validator-enforced):**

1. `## Feature recap (1-2 lines)` — copied/condensed from `_concept/product-spec/features/<group>/<feature_slug>.md` so the reader doesn't have to re-open the feature file.
2. `## Concept summary` — 1 paragraph summary of WHAT the screens for this feature are (derived from `_concept/experience/screens/<feature_slug>/*.md`). Names every screen file by relative path.
3. `## Open questions surfaced by the grill` — numbered list. Each item has `[P1|P2|P3]` priority. P1 = blocks plan-vertical; P2 = blocks a sub-task; P3 = nice-to-know. **Validator checks: at least one P1-or-P2 question is present (otherwise the grill was too soft).**
4. `## Edge cases to handle` — bullets, each with a 1-sentence rationale. Sourced from grilling, not invented.
5. `## Constraints` — three sub-headings:
   - `### Technical` — stack/library limitations, performance bounds, browser/runtime targets.
   - `### Scope` — what's IN this slice vs what's deferred to a later slice.
   - `### Deadline / supervision` — supervision tier from scope.yaml (autonomous / mostly autonomous / HITL per SKILL_GRAPH § 3).
6. `## Decisions made` — Q/A list. Empty list is allowed only if `## Open questions` has ZERO P1 items (validator-enforced).
7. `## Acceptance handoff` — restates the EARS criteria from `_concept/product-spec/features/<group>/<feature_slug>.md` § "Acceptance Criteria" verbatim, so plan-vertical doesn't have to re-read the feature file.

**Validator strategy for `align.md`:**
- Frontmatter has all required keys + `phase == "align"` + `slice_id` matches dir.
- All 7 body section headers present.
- `## Open questions` body has ≥ 1 line containing `[P1]` or `[P2]` (regex `^\d+\.\s+\[P[12]\]`), OR `## Decisions made` has ≥ 1 entry resolving every prior P1.
- `## Acceptance handoff` body contains at least one EARS line (regex `WHEN .* THE SYSTEM SHALL .*`, case-insensitive).

---

## Pinned: `plan.md` Schema (output of `impl-plan-plan-vertical`)

Path: `_slice/impl/<slice_id>/plan.md`

**Note (gap flagged):** `contracts/plans.md` defines a project-level `PLANS.md` (concept + implementation phases). It does NOT define a per-slice `plan.md`. This plan PROPOSES the per-slice schema below; the format should be promoted to `contracts/plans.md` as a sibling section (`Per-Slice Plan` distinct from `Implementation Plan`) in a follow-up. Open Question §1.

Frontmatter:

```yaml
---
slice_id: <slug>
feature_title: <free-text title>
feature_path: _concept/product-spec/features/<group>/<feature_slug>.md
phase: plan
tier: <enum from scope.yaml>
created_at: <ISO-8601 UTC Z>
last_updated: <ISO-8601 UTC Z>
---
```

**Required body sections (validator-enforced):**

1. `## Slice scope` — exactly one line, ≤ 200 chars, the goal of this slice in plain English.
2. `## Vertical decomposition` — a markdown table with three columns and exactly ONE row per atomic unit of work. **CRITICAL:** each row crosses ALL THREE columns (UI, Logic, Data) for a single user-facing slice. A row with content only in one column is a horizontal-decomposition smell — see § "Anti-horizontal nudge" below.

   Schema:
   ```markdown
   ## Vertical decomposition

   | # | UI | Logic | Data |
   |---|----|-------|------|
   | 1 | Login form (`screens/login.md`) | `auth.signIn(email, pw)` handler | `users` table read |
   | 2 | Email-verification banner | `auth.checkVerified()` middleware | `users.email_verified_at` field |
   ```

3. `## Testing strategy` — three sub-headings:
   - `### Manual checks` — bullet list of click-paths the human runs before approving the slice.
   - `### Automated tests` — bullet list of tests to write, each with `[unit | integration | e2e]` tag. Sourced from `align.md ## Acceptance handoff` (each EARS line should map to ≥ 1 test).
   - `### Exit criteria` — bullets that, when all true, mean the slice is "done" and ready for `impl-slice/recap`. Must include "all rows in `## Vertical decomposition` complete end-to-end" verbatim.
4. `## Anti-horizontal nudge` — a fixed `> DO NOT` block (template; validator pins exact wording — see § "Anti-horizontal nudge" below).
5. `## Definition of done` — checkbox list. Validator requires:
   - [ ] All vertical rows complete end-to-end (UI + Logic + Data wired)
   - [ ] All tests in § "Automated tests" pass
   - [ ] All manual checks in § "Manual checks" verified by user
   - [ ] No row left half-implemented (no "UI built but data not wired", etc.)
   - [ ] `_concept/product-spec/features/<group>/<feature_slug>.md` § Acceptance Criteria all green
6. `## Open carry-overs` — items pulled from `align.md ## Open questions` that are P3 or got DEFERRED to a later slice. Empty section is allowed (literally `_(none)_`).

**Validator strategy for `plan.md`:**
- Frontmatter has all required keys + `phase == "plan"` + `slice_id` matches dir.
- All 6 body section headers present in order.
- `## Vertical decomposition` body contains a markdown table with header `| # | UI | Logic | Data |` and ≥ 1 data row.
- Validator scans each data row: if any of UI/Logic/Data column cells equals `-`, `n/a`, or empty → emit a warning (not error; some rows legitimately don't touch data, e.g. pure-UI polish — but a flagged warning forces the author to confirm).
- `## Anti-horizontal nudge` body contains the EXACT string from § "Anti-horizontal nudge" template (regex match, case-sensitive). This guards against the LLM softening the language.
- `## Definition of done` body contains the 5 required checkbox items verbatim.
- `## Testing strategy ### Automated tests` body has ≥ 1 line tagged `[unit]`, `[integration]`, or `[e2e]`.

---

## Pinned: Anti-Horizontal Nudge Template (verbatim, baked into `plan-vertical`'s SKILL.md AND output)

The SKILL.md body MUST contain this language EARLY (before STEP 1) and the OUTPUT plan.md MUST contain it verbatim in its `## Anti-horizontal nudge` section:

```markdown
## Anti-horizontal nudge

> **DO NOT build all UI first, then all logic, then all data.**
>
> The default LLM failure mode for implementation planning is horizontal layering: "first scaffold every screen, then wire every handler, then run every migration." This produces N half-finished slices and zero working ones.
>
> Instead: pick ONE row from `## Vertical decomposition` and complete it end-to-end (UI renders → handler responds → data round-trips → test green) BEFORE starting the next row.
>
> If you find yourself thinking any of the following, **stop**:
> - "I'll come back and wire the data after I've built all the screens."
> - "Let me get the UI looking right across the whole feature first."
> - "I'll batch the migrations and run them at the end."
> - "I'll add tests once everything is hooked up."
>
> A row is **not done** until: UI renders real data, the handler is callable from the UI, the data layer persists round-trips, and the test for that row is green. Then — and only then — start the next row.
```

Additionally, `plan-vertical`'s SKILL.md body MUST include MUST/NEVER lines that mirror this:

```
MUST   produce one row per user-facing slice; each row crosses UI + Logic + Data
MUST   refuse to write a plan whose rows have empty UI, Logic, or Data cells
       without an explicit user-confirmed reason logged in the row's notes
MUST   embed the verbatim anti-horizontal-nudge template in the output plan.md
NEVER  produce a plan that batches all UI as one task, then all logic as another
NEVER  decompose by technical layer (frontend / backend / db) instead of by
       user-facing vertical
NEVER  defer testing strategy to a later phase — it goes in plan.md, this skill
```

The same MUST/NEVER lines (or at least the first three) MUST be repeated INSIDE the relevant STEP body (per `skill_grammar.md` § Authoring tip 1: "Inline critical rules into STEPs.").

---

## File Targets

All paths absolute, inside `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`.

For each of the three skills (`brainstorm`, `align`, `plan-vertical`):
- `impl-plan/<phase>/SKILL.md`
- `impl-plan/<phase>/validator.py`
- `impl-plan/<phase>/tests/test_validator.py`

Plus, for `align` and `plan-vertical` (new skills):
- `impl-plan/<phase>/references/<phase>-prompt-style.md` — interview/decomposition tone reference; ≤80 lines. Optional but recommended.

For `plan-vertical` only:
- `impl-plan/plan-vertical/references/anti-horizontal-rules.md` — long-form expansion of the anti-horizontal-nudge template with three worked counter-examples (showing what horizontal decomposition looks like and why it fails).
- `impl-plan/plan-vertical/examples/team-todo-comments-plan.md` — golden plan.md the validator pins against in tests.

For `align` only:
- `impl-plan/align/examples/team-todo-comments-align.md` — golden align.md the validator pins against in tests.

For `brainstorm` (refresh):
- The existing `impl-plan/brainstorm/SKILL.md` is REWRITTEN to read concept artifacts (per Task 2B paths) and write to `_slice/impl/<id>/brainstorm.md` instead of the old `_implementation/brainstorm.md`. Also adds the `feature_slug` input requirement, `_concept/_meta/scope.yaml` read, and the new frontmatter (`slice_id`, `feature_title`, `feature_path`, `phase`, `tier`, ...).
- Adds new files `impl-plan/brainstorm/validator.py` and `impl-plan/brainstorm/tests/test_validator.py` (the Phase-1 migrated brainstorm has none).

**No edits** to existing files outside `impl-plan/` (no flows touched, no base orchestrator touched).

---

## Iron Laws — How They Apply Across the Cluster

| Law | How enforced | Where to verify |
|---|---|---|
| § 7 No artifact without prerequisites | Each SKILL.md `metadata.prerequisites.files[]` lists the predecessor's handoff (`gate: soft` because tier-conditional, `gate: hard` for `_concept/_meta/scope.yaml` and the feature artifact); STEP 1 verifies and EXITs on miss with explicit message | All 3 skills |
| § 8 No overwrite without approval | Each skill writes only into `_slice/impl/<id>/<phase>.md`. If that file already exists (re-entry), the skill loads it and shows a diff before any change. Since `_slice/impl/` is scratch, the gate is lighter than `concept-slice/design-feature`'s overwrite gate, but still enforced. | All 3 skills |
| § 9 Questions are standalone messages | MUST line near top of each SKILL.md: "MUST send each interview question as its own assistant message; never bundle multiple questions in one turn; wait for answer before sending next." | All 3 skills (especially `align`, which is the heaviest grill) |

---

## Per-skill commit boundary

**Recommended:** three commits, one per skill, in dependency order:

1. `feat(impl-plan): refresh brainstorm for new _slice/impl/<id>/ paths (Task 2C step 1)`
2. `feat(impl-plan): add align skill (Task 2C step 2)`
3. `feat(impl-plan): rewrite plan-vertical for per-slice scope + anti-horizontal nudge (Task 2C step 3)`

Each commit covers `SKILL.md` + `validator.py` + `tests/` + (where applicable) `references/` + `examples/`.

Then a final task (Task 4 below) for cross-skill verification with one wrap-up commit:

4. `feat(impl-plan): finalize cluster + cross-skill verification (Task 2C complete)`

---

## Task 1: Refresh `impl-plan-brainstorm`

**Skill `name:` field:** `impl-plan-brainstorm` (already correct in existing SKILL.md — verify, don't change).

**Skill role:** Sparring partner on what *this one feature* needs from an implementation perspective: risks, unknowns, dependencies, and questions that would block planning if unanswered. Per-feature scope, NOT project-wide (the existing skill is project-wide; this is the key behavior change).

**Files:**
- Modify: `impl-plan/brainstorm/SKILL.md` (full rewrite of body; preserve frontmatter `name`, bump `metadata.version` to `2.0.0` because this is a breaking change to `produces` paths per `asset_frontmatter.md` § Version Bump Rules)
- Create: `impl-plan/brainstorm/validator.py`
- Create: `impl-plan/brainstorm/tests/test_validator.py`

### Required Pre-checks (read existing skill before rewriting)

- [ ] **Step 1: Read the existing SKILL.md to confirm frontmatter `name` is correct**

Run: `python3 -c "import yaml; fm=yaml.safe_load(open('impl-plan/brainstorm/SKILL.md').read().split('---')[1]); print(fm['name'])"`
Expected: `impl-plan-brainstorm`. If anything else, that's a Phase-1 mismatch — flag it.

- [ ] **Step 2: Note the deprecated fields in current SKILL.md**

Existing fm uses `metadata.user_inputs`, `metadata.reads_from`, `metadata.writes_to` (deprecated per `contracts/asset_frontmatter.md` § "Migration from Previous Schema"). The refresh migrates these to `metadata.prerequisites.{inputs_required, inputs_optional, reads, produces}`.

### READS / WRITES (pinned)

```
READS
  _concept/_meta/scope.yaml                                   — required; tier + project description (per Task 2A schema)
  _concept/product-spec/features/<group>/<feature_slug>.md    — required; the feature being planned (per Task 2B output paths)
  ? _concept/experience/screens/<feature_slug>/*.md           — optional; screen specs for this feature
  ? _concept/blueprint/datamodel/model.json                   — optional; data model (used to identify entity-touching risks)
  ? _concept/blueprint/techstack.md                           — optional; stack-specific risks
  ? _slice/impl/<slice_id>/brainstorm.md                      — re-entry mode (resume/refine existing)

WRITES
  _slice/impl/<slice_id>/brainstorm.md                        — handoff file for `impl-plan-align`
```

### Handoff file body sections

1. `## App-level summary (1 paragraph)` — pulled from `_concept/_meta/scope.yaml.description` + 1 line of "what tier".
2. `## Feature summary (1 paragraph)` — pulled from feature.md frontmatter + first paragraph of body.
3. `## Risks and unknowns` — six sub-headings (data, auth, integrations, stack, performance, UX) each with 0–N bullets. Empty sub-heading is allowed but must contain `_(no risks identified for this feature)_` literal.
4. `## Open questions` — markdown table `| Priority (P1/P2/P3) | Question | Blocks |`. P1 = blocks align/plan-vertical; P2 = blocks a sub-task; P3 = nice-to-know.
5. `## Recommended mitigations` — for each risk, what to do about it in plan-vertical.

### Authoring steps

- [ ] **Step 3: Rewrite frontmatter**

Replace the existing frontmatter with the new schema. Critical changes:
- Bump `metadata.version` to `2.0.0`.
- Remove `metadata.source: 'MERGED'` (this is a rewrite; source tracking no longer accurate).
- Replace `metadata.user_inputs` with `metadata.prerequisites.inputs_required` (`feature_slug` required) and `inputs_optional` (`focus_area` optional).
- Replace `metadata.reads_from` with `metadata.prerequisites.files[]` (hard gates: `_concept/_meta/scope.yaml`, `_concept/product-spec/features/<group>/<feature_slug>.md`) plus `metadata.prerequisites.reads[]` (optional: screens, model, techstack, prior brainstorm).
- Replace `metadata.writes_to` with `metadata.prerequisites.produces`: `_slice/impl/<slice_id>/brainstorm.md`.
- Update `description:` to start with "Use when..." (per CONTRIBUTING.md naming rule); current description lacks this prefix. New description: `Use when starting per-slice implementation work for a feature in a standard-app or complex-app tier project. Sparring partner on risks, unknowns, dependencies for THIS feature only. Writes _slice/impl/<slice_id>/brainstorm.md for impl-plan-align to consume.`
- Add tags: keep existing `brainstorm`, `planning`, `risks`, `decomposition`, `pre-implementation`, `unknowns`. Add: `impl-plan`, `per-slice`, `feature-scoped`.

- [ ] **Step 4: Rewrite SKILL.md body**

Sections in order:
- `# Implementation Brainstorm — per-slice` (replaces old `# Brainstorm`)
- `## Overview` — 3-4 sentences explaining per-slice scope (NOT project-wide; this is the key behavior change from the migrated version).
- `## When to Use` and `## When NOT to Use` (keep existing structure but update for per-slice scope).
- `ROLE` line.
- `READS` / `WRITES` (copy from § "READS / WRITES (pinned)").
- `REFERENCES`: `SKILL_GRAPH.md` § 5.2, `contracts/iron_laws.md`, `docs/superpowers/plans/2A-scope-project.md` (for scope.yaml schema), `docs/superpowers/plans/2B-concept-slice-cluster.md` (for permanent artifact paths).
- MUST/NEVER block (place EARLY per skill_grammar.md § Authoring tip 4):
  - `MUST  ask each interview question as its own standalone message (iron_laws § 9)`
  - `MUST  refuse to run if scope.yaml is missing or tier is not in {standard-app, complex-app}`
  - `MUST  resolve feature_slug to _concept/product-spec/features/<group>/<feature_slug>.md before any other step; refuse if file missing`
  - `MUST  scope brainstorm to THIS ONE feature; do NOT enumerate risks for other features`
  - `MUST  surface every P1 question to the user as a standalone message before writing brainstorm.md`
  - `MUST  write the handoff frontmatter exactly per the cross-phase contract (slice_id, feature_title, feature_path, phase, tier, created_at, last_updated)`
  - `NEVER  expand the scope to project-wide risks (that's a different skill — ops/audit or impl-quality/audit)`
  - `NEVER  write brainstorm.md before unresolved P1 blockers are surfaced`
- `INPUT` block — read from `_concept/_grounding/impl-plan-brainstorm/input.json` if present; else interview.
- `STEP 1` — read `scope.yaml`, validate `tier ∈ {standard-app, complex-app}` (refuse otherwise — simple-app and mvp do not run brainstorm per SKILL_GRAPH § 6).
- `STEP 2` — collect `feature_slug` (required) and resolve to feature_path. Check directory collision on `_slice/impl/<slice_id>/`.
- `STEP 3` — read feature.md, screens (if any), model.json (if any), techstack.md (if any).
- `STEP 4` — assess risks across the six dimensions (data, auth, integrations, stack, performance, UX), scoped to THIS feature.
- `STEP 5` — surface P1 questions (each STANDALONE).
- `STEP 6` — draft handoff file in memory; show to user.
- `STEP 7` — `CHECKPOINT brainstorm_draft`.
- `STEP 8` — write `_slice/impl/<slice_id>/brainstorm.md`.
- `EMIT  [impl-plan-brainstorm] completed slice_id=<id> tier=<tier> p1_count=<n>`
- `CHECKLIST` (5 items: scope.yaml read, feature.md read, all 5 body sections present, P1s surfaced + answered, file written).

- [ ] **Step 5: Verify frontmatter parses + `name` correct**

```bash
python3 - <<'EOF'
import yaml
fm = yaml.safe_load(open('impl-plan/brainstorm/SKILL.md').read().split('---')[1])
assert fm['name'] == 'impl-plan-brainstorm', fm['name']
assert fm['description'].startswith('Use when'), fm['description'][:30]
assert fm['metadata']['version'].startswith('2.'), 'expected major bump to 2.x'
assert 'prerequisites' in fm['metadata'], 'must use prerequisites schema'
assert 'reads_from' not in fm['metadata'], 'deprecated field reads_from must be removed'
assert 'writes_to' not in fm['metadata'], 'deprecated field writes_to must be removed'
assert 'user_inputs' not in fm['metadata'], 'deprecated field user_inputs must be removed'
print("OK")
EOF
```
Expected: `OK`

- [ ] **Step 6: Author `validator.py`**

Validator scope (deterministic, doesn't test the LLM body):
- Loads `_slice/impl/<slug>/brainstorm.md`.
- Asserts frontmatter has all 7 required keys (`slice_id, feature_title, feature_path, phase, tier, created_at, last_updated`).
- Asserts `phase == "brainstorm"`.
- Asserts `slice_id` matches the regex `^[a-z][a-z0-9-]{1,47}$` and equals the parent directory name.
- Asserts `tier` ∈ {`standard-app`, `complex-app`}.
- Asserts body contains all 5 `## ...` section headers.
- Asserts `## Open questions` body has a markdown table with header `| Priority` (validator regex match).
- Exit 0 on success, 2 on any failure.

CLI: `python3 validator.py <path/to/brainstorm.md>`.

- [ ] **Step 7: Author `tests/test_validator.py`**

Tests:
1. Golden good-case fixture passes.
2. Missing `phase` frontmatter key fails.
3. Wrong `phase` value (`align` instead of `brainstorm`) fails.
4. `slice_id` not matching parent dir fails.
5. Missing one of the 5 section headers fails.
6. `tier == mvp` fails (out-of-scope tier).
7. `## Open questions` without a Priority table header fails.

- [ ] **Step 8: Run tests**

Run: `pytest impl-plan/brainstorm/tests/ -v`
Expected: all 7 pass.

- [ ] **Step 9: Commit Task 1**

```bash
git add impl-plan/brainstorm/
git commit -m "feat(impl-plan): refresh brainstorm for new _slice/impl/<id>/ paths (Task 2C step 1)"
```

---

## Task 2: Author `impl-plan-align`

**Skill `name:` field:** `impl-plan-align`

**Skill role:** Grill-me-style interview that surfaces unstated assumptions, edge cases, technical constraints, and acceptance handoff for THIS feature's implementation. Inverts brainstorm: now the AI asks pointed questions, the user defends. Mirrors `concept-slice/align`'s tone but scope is implementation-readiness, not concept-readiness.

**Files:**
- Create: `impl-plan/align/SKILL.md`
- Create: `impl-plan/align/validator.py`
- Create: `impl-plan/align/tests/test_validator.py`
- Create (recommended): `impl-plan/align/references/grill-style.md` (≤80 lines on grill-question pillars)
- Create: `impl-plan/align/examples/team-todo-comments-align.md` (golden output for tests)

### READS / WRITES (pinned)

```
READS
  _concept/_meta/scope.yaml                                   — required; tier
  _concept/product-spec/features/<group>/<feature_slug>.md    — required; permanent feature artifact
  _concept/experience/screens/<feature_slug>/*.md             — required; permanent screen specs (≥1 file expected)
  _slice/impl/<slice_id>/brainstorm.md                        — required IF tier ∈ {standard-app, complex-app}
                                                              — ENTRY POINT IF tier == simple-app (creates _slice/impl/<id>/)
  ? _concept/blueprint/datamodel/model.json                   — optional; data model for entity-related grilling
  ? _concept/blueprint/techstack.md                           — optional; stack constraints
  ? _slice/impl/<slice_id>/align.md                           — re-entry mode

WRITES
  _slice/impl/<slice_id>/align.md                             — handoff file for `impl-plan-plan-vertical`
```

### Handoff file

Path: `_slice/impl/<slice_id>/align.md`

Frontmatter and body sections per § "Pinned: `align.md` Schema" above.

### Authoring steps

- [ ] **Step 1: Create dir**

```bash
mkdir -p impl-plan/align/references impl-plan/align/examples impl-plan/align/tests
```

Verify: `ls impl-plan/align/` → all four sub-dirs.

- [ ] **Step 2: Write `SKILL.md` frontmatter**

`metadata.prerequisites`:
- `files`:
  - `_concept/_meta/scope.yaml` (gate: hard).
  - `_concept/product-spec/features/{feature_slug}.md` — note path uses placeholder; the validator and the runtime expand `{feature_slug}` from input. Gate: hard. Description: "Permanent feature artifact written by concept-slice-design-feature."
  - `_concept/experience/screens/{feature_slug}/` — gate: hard, min_entries: 1. Description: "Permanent screen specs for this feature."
  - `_slice/impl/{slice_id}/brainstorm.md` — gate: soft (tier-conditional; body STEP 1 enforces hard for standard/complex tiers).
- `inputs_required`:
  - `feature_slug` (text, "Kebab-case feature slug; resolves to a feature.md path").
- `inputs_optional`:
  - `slice_id_override` (text, "Override the auto-derived slice_id (rarely needed; default = feature_slug)").
- `reads`: model.json, techstack.md, prior align.md.
- `produces`: `_slice/impl/{slice_id}/align.md`.

Tags: `impl-plan`, `align`, `interview`, `grill-me`, `acceptance-criteria`, `edge-cases`, `per-slice`. Stage `alpha`. Version `1.0.0`.

`description:` MUST start with `Use when ...`.

Suggested: `Use when an implementation slice has its concept artifacts (feature.md + screens) frozen and needs a grill-me interview to surface unstated assumptions, technical constraints, and edge cases before plan-vertical writes the slice plan. Reads _concept/product-spec/features/<group>/<feature_slug>.md + _slice/impl/<id>/brainstorm.md (if standard/complex tier). Writes _slice/impl/<id>/align.md.`

- [ ] **Step 3: Write SKILL.md body**

Sections in order:
- `ROLE` — implementation-readiness grill partner, per-slice.
- `READS` / `WRITES` — copy from § "READS / WRITES (pinned)".
- `REFERENCES`: `SKILL_GRAPH.md` § 5.2, `contracts/iron_laws.md`, `contracts/skill_grammar.md`, `impl-plan/align/references/grill-style.md`, `docs/superpowers/plans/2A-scope-project.md`, `docs/superpowers/plans/2B-concept-slice-cluster.md`.
- MUST/NEVER block (EARLY):
  - `MUST  ask each grill question as its own standalone message (iron_laws § 9)`
  - `MUST  refuse to run if scope.yaml is missing or tier == mvp (mvp skips align per SKILL_GRAPH § 6)`
  - `MUST  refuse to run if the feature.md at _concept/product-spec/features/<group>/<feature_slug>.md is missing (iron_laws § 7)`
  - `MUST  refuse to run if tier ∈ {standard-app, complex-app} and brainstorm.md is missing`
  - `MUST  copy slice_id and feature_title from brainstorm.md when present; never re-derive`
  - `MUST  surface every P1 question to the user as a standalone message before writing align.md`
  - `MUST  copy EARS acceptance criteria from feature.md verbatim into "## Acceptance handoff"`
  - `NEVER  invent edge cases the user did not confirm — every "## Edge cases" bullet must trace to a Q/A in "## Decisions made" or to a feature.md/screen line`
  - `NEVER  proceed past question N until the user has answered question N`
- `INPUT` block — read from `_concept/_grounding/impl-plan-align/input.json` if present; else interview.
- `STEP 1` — read scope.yaml. Validate tier. Resolve `feature_slug → feature_path`. If tier ∈ {standard, complex}, hard-gate brainstorm.md. If tier == simple-app, this is the entry point — `mkdir -p _slice/impl/<slice_id>/` and collect feature_title.
- `STEP 2` — read brainstorm.md (when present), feature.md (always), screens (always), model.json + techstack.md (optional).
- `STEP 3` — recap to the user: "I'm grilling on `<feature_title>`, tier `<tier>`. Concept summary: <1 paragraph>. Anything wrong before I start?" CHECKPOINT.
- `STEP 4-10` — the grill. Sample question pillars (each STANDALONE — at least one per pillar):
  - **State transitions:** "What happens if the user starts the flow but doesn't complete it? Is the partial state persisted, discarded, or shown as 'in progress'?"
  - **Boundary inputs:** "What's the max/min/zero case for <X>? What does the system do at each?"
  - **Concurrency:** "Two users hit this at the same time on the same row. What's the rule — last-write-wins, optimistic locking, conflict UI?"
  - **Permissions:** "Can a guest do this? An admin? What's the role matrix?"
  - **Persistence and offline:** "If the user closes the tab mid-action, what's saved? What happens on reload?"
  - **Errors:** "What does the user see when <Y> fails — toast, inline error, modal, retry button?"
  - **Cross-feature data:** "Does this feature touch any other feature's entities? Any FKs that span features?"
  - **Performance:** "What's the worst-case data size — 10 rows, 1000 rows, 100k rows? Pagination strategy?"
  - **Test seam:** "How will we know this is working without manually clicking through? What's the smallest automated test?"
- `STEP 11` — draft align.md in memory; show to user.
- `STEP 12` — `CHECKPOINT align_draft`.
- `STEP 13` — write `_slice/impl/<slice_id>/align.md`.
- `EMIT  [impl-plan-align] completed slice_id=<id> tier=<tier> p1_count=<n> p2_count=<n>`
- `CHECKLIST` — 8 items including: all 7 body sections present, EARS criteria copied verbatim, P1 questions surfaced, file written.

- [ ] **Step 4: Author `validator.py`** — per § "Pinned: `align.md` Schema" validator strategy.

- [ ] **Step 5: Author `tests/test_validator.py`**

Tests:
1. Golden fixture (`examples/team-todo-comments-align.md`) passes.
2. Missing EARS line in `## Acceptance handoff` fails.
3. Missing one of the 7 section headers fails.
4. Empty `## Open questions` AND empty `## Decisions made` fails (the implication: nothing was grilled).
5. `phase == "brainstorm"` fails.
6. `slice_id` mismatch with parent dir fails.
7. Frontmatter missing `feature_path` fails.

- [ ] **Step 6: Author `examples/team-todo-comments-align.md`**

A complete, valid align.md output for the `team-todo-comments` feature (use the same example feature as 2B's worked example for consistency). Includes all 7 sections; tier = `standard-app`; ≥ 2 P1 or P2 questions; ≥ 1 EARS criterion in handoff.

- [ ] **Step 7: Author `references/grill-style.md`** (recommended, ≤ 80 lines)

Documents the 9 grill pillars listed in STEP 4-10 with one sample good question and one sample weak question per pillar.

- [ ] **Step 8: Run tests**

Run: `pytest impl-plan/align/tests/ -v`
Expected: all 7 pass.

- [ ] **Step 9: Commit Task 2**

```bash
git add impl-plan/align/
git commit -m "feat(impl-plan): add align skill (Task 2C step 2)"
```

---

## Task 3: Author `impl-plan-plan-vertical` (effectively a rewrite)

**Skill `name:` field:** `impl-plan-plan-vertical`

**Skill role:** Decomposes a single feature into vertical slices (UI + Logic + Data per row), embeds the testing strategy, and bakes in an anti-horizontal-decomposition nudge. Reads `_slice/impl/<id>/align.md` (or for mvp/simple, the predecessor's handoff or directly feature.md) and writes `_slice/impl/<id>/plan.md`.

**Note:** the existing `impl-plan/plan-vertical/SKILL.md` writes `_implementation/superpowers-plan.md` (project-wide, dependency-ordered). This is a **different skill in everything but name** — bump `metadata.version` to `2.0.0` (major: `produces` path changed). Some content (dependency-ordering insights) can be salvaged into the per-row notes column, but the file is effectively rewritten.

**Files:**
- Modify (full rewrite): `impl-plan/plan-vertical/SKILL.md`
- Create: `impl-plan/plan-vertical/validator.py`
- Create: `impl-plan/plan-vertical/tests/test_validator.py`
- Create: `impl-plan/plan-vertical/references/anti-horizontal-rules.md` (long-form expansion of the nudge with three counter-examples)
- Create: `impl-plan/plan-vertical/examples/team-todo-comments-plan.md` (golden plan.md)

### READS / WRITES (pinned)

```
READS
  _concept/_meta/scope.yaml                                   — required; tier
  _concept/product-spec/features/<group>/<feature_slug>.md    — required; permanent feature artifact
  _concept/experience/screens/<feature_slug>/*.md             — required; permanent screen specs (≥1)
  _slice/impl/<slice_id>/align.md                             — required IF tier ∈ {simple-app, standard-app, complex-app}
                                                              — ENTRY POINT IF tier == mvp (creates _slice/impl/<id>/)
  ? _slice/impl/<slice_id>/brainstorm.md                      — optional; referenced for "why this row" context
  ? _concept/blueprint/datamodel/model.json                   — optional; entity dependency hints (salvaged from old plan-vertical)
  ? _concept/blueprint/techstack.md                           — optional; stack constraints for "Logic" column
  ? _slice/impl/<slice_id>/plan.md                            — re-entry mode

WRITES
  _slice/impl/<slice_id>/plan.md                              — handoff file for `impl-slice/implement` (Task 2D)
```

### Handoff file

Path: `_slice/impl/<slice_id>/plan.md`

Frontmatter + 6 body sections per § "Pinned: `plan.md` Schema" above. Anti-horizontal nudge VERBATIM per § "Pinned: Anti-Horizontal Nudge Template".

### Authoring steps

- [ ] **Step 1: Read existing SKILL.md to verify current state**

Run: `python3 -c "import yaml; fm=yaml.safe_load(open('impl-plan/plan-vertical/SKILL.md').read().split('---')[1]); print(fm['name'])"`
Expected: `impl-plan-plan-vertical`. Note that current `description:` does NOT start with "Use when" — fix in rewrite.

- [ ] **Step 2: Rewrite frontmatter**

Critical changes:
- Bump `metadata.version` to `2.0.0` (major: `produces` path changed).
- Update `description:` to start with "Use when..." Suggested: `Use when an implementation slice has its align.md (or, for mvp, its feature.md) ready and needs a vertical-decomposition plan. Reads _slice/impl/<id>/align.md + concept artifacts. Writes _slice/impl/<id>/plan.md containing one row per user-facing slice (UI + Logic + Data), testing strategy, and an anti-horizontal-nudge block. Resists the LLM default of horizontal decomposition.`
- Replace deprecated `metadata.user_inputs`, `metadata.reads_from`, `metadata.writes_to` with `metadata.prerequisites.{inputs_required, inputs_optional, files, reads, produces}`.
- `prerequisites.files`:
  - `_concept/_meta/scope.yaml` (hard).
  - `_concept/product-spec/features/{feature_slug}.md` (hard).
  - `_concept/experience/screens/{feature_slug}/` (hard, min_entries: 1).
  - `_slice/impl/{slice_id}/align.md` (soft; tier-conditional, body STEP 1 enforces hard for simple/standard/complex).
- `prerequisites.inputs_required`: `feature_slug` (text).
- `prerequisites.inputs_optional`: `slice_id_override` (text, rarely used), `task_granularity` (select: `feature` | `screen`, default `feature` — kept from old skill but scoped to per-slice).
- `prerequisites.produces`: `_slice/impl/{slice_id}/plan.md`.
- Tags: `impl-plan`, `plan`, `vertical-slice`, `decomposition`, `testing-strategy`, `anti-horizontal`, `per-slice`. Stage `alpha`. Version `2.0.0`.

- [ ] **Step 3: Rewrite SKILL.md body**

Sections in order:
- `# Plan-Vertical — per-slice vertical decomposition` (replaces old `# Write Plan`).
- `## Overview` — 4-5 sentences explaining vertical decomposition AND that this skill actively fights horizontal decomposition. Quote the anti-horizontal nudge first sentence inline.
- `## When to Use` and `## When NOT to Use`.
- `ROLE` — Per-slice plan writer; resists horizontal decomposition.
- `READS` / `WRITES` — copy from § "READS / WRITES (pinned)".
- `REFERENCES`: `SKILL_GRAPH.md` § 5.2, `contracts/iron_laws.md`, `contracts/plans.md`, `impl-plan/plan-vertical/references/anti-horizontal-rules.md`, `docs/superpowers/plans/2A-scope-project.md`, `docs/superpowers/plans/2B-concept-slice-cluster.md`.
- **The verbatim anti-horizontal nudge template** (per § "Pinned: Anti-Horizontal Nudge Template") goes EARLY in the body — before MUST/NEVER. This is critical: per `skill_grammar.md` § Authoring tip 4, constraints early in the body have better compliance. The nudge IS a constraint.
- MUST/NEVER block (EARLY, immediately after the nudge):
  - `MUST  produce one row per user-facing slice; each row crosses UI + Logic + Data`
  - `MUST  refuse to write a plan whose rows have empty UI, Logic, or Data cells without an explicit user-confirmed reason logged in the row's notes`
  - `MUST  embed the verbatim anti-horizontal-nudge template (see references/anti-horizontal-rules.md) in the output plan.md`
  - `MUST  ask any clarification question as its own standalone message (iron_laws § 9)`
  - `MUST  refuse to run if scope.yaml is missing`
  - `MUST  refuse to run if tier ∈ {simple, standard, complex} and align.md is missing (iron_laws § 7)`
  - `MUST  refuse to write the plan if feature.md is missing`
  - `MUST  copy EARS acceptance criteria from feature.md (or align.md "## Acceptance handoff") verbatim into "## Testing strategy ### Automated tests" — every EARS line maps to ≥ 1 test`
  - `MUST  include the 5 required Definition of Done items verbatim (see schema)`
  - `NEVER  produce a plan that batches all UI as one row, then all logic as another row, then all data as a third`
  - `NEVER  decompose by technical layer (frontend / backend / db) instead of by user-facing vertical`
  - `NEVER  defer testing strategy to a later phase — it goes in plan.md, this skill`
  - `NEVER  write more than one plan.md per slice (re-entry: load existing, show diff, ask before any change)`
- `INPUT` block — read from `_concept/_grounding/impl-plan-plan-vertical/input.json` if present; else interview.
- `STEP 1` — read scope.yaml. Validate tier. Resolve feature_slug. If tier ∈ {simple, standard, complex}, hard-gate align.md. If tier == mvp, this is the entry point — `mkdir -p _slice/impl/<slice_id>/`.
- `STEP 2` — read align.md (when present), feature.md (always), screens (always).
- `STEP 3` — identify the user-facing slices. Each slice = one row in `## Vertical decomposition`. Heuristic: walk `_concept/experience/screens/<feature_slug>/*.md` — each screen file is roughly one row, OR each interaction (button-click that mutates state) is one row, depending on `task_granularity`. Resist the temptation to make rows = layers.
- `STEP 4` — for each row, fill UI / Logic / Data columns. **Inline the anti-horizontal MUST here** ("Each row crosses all three columns; if you can't fill all three for a row, the row is not vertical and should be merged or split"). Reference any data-entity dependencies from `model.json` for ordering hints, but do NOT use entity dependencies to override vertical decomposition (they inform row order, not row shape).
- `STEP 5` — derive testing strategy. For each EARS line in feature.md "## Acceptance Criteria" (or align.md "## Acceptance handoff"), assign at least one row to cover it AND at least one test in `### Automated tests`. Tag each test `[unit | integration | e2e]`.
- `STEP 6` — draft plan.md in memory. Include the verbatim anti-horizontal nudge in `## Anti-horizontal nudge`. Include the 5 verbatim Definition of Done items.
- `STEP 7` — `CHECKPOINT plan_draft`. Show the user the row table and ask: "Does any row have empty UI / Logic / Data cells without a justification? If so, we should split or merge it."
- `STEP 8` — write `_slice/impl/<slice_id>/plan.md`.
- `STEP 9` — Run validator.py against the just-written file. On failure: report errors and STOP. Do not commit.
- `EMIT  [impl-plan-plan-vertical] completed slice_id=<id> tier=<tier> rows=<n> tests=<n>`
- `CHECKLIST` — 9 items including: anti-horizontal nudge embedded verbatim, all 6 sections present, ≥ 1 row, every EARS line covered, validator passes.

- [ ] **Step 4: Author `validator.py`** — per § "Pinned: `plan.md` Schema" validator strategy. Critical checks:
  - Frontmatter shape + `phase == "plan"` + slice_id matches dir.
  - All 6 body section headers present in order.
  - `## Vertical decomposition` table parses (header `| # | UI | Logic | Data |`, ≥ 1 data row).
  - Per-row warning if any cell is `-`, `n/a`, or empty.
  - `## Anti-horizontal nudge` body matches the verbatim template (regex match).
  - `## Definition of done` body contains the 5 required checkbox items verbatim.
  - `## Testing strategy ### Automated tests` body has ≥ 1 line tagged `[unit]`, `[integration]`, or `[e2e]`.

- [ ] **Step 5: Author `tests/test_validator.py`**

Tests:
1. Golden fixture (`examples/team-todo-comments-plan.md`) passes.
2. Missing one of the 6 section headers fails.
3. Anti-horizontal nudge altered (one word changed) fails.
4. Definition of done missing one of the 5 required items fails.
5. `## Vertical decomposition` table absent fails.
6. `## Vertical decomposition` table present but with all empty Data cells emits a warning (validator returns 0 but stderr contains warning).
7. `## Testing strategy ### Automated tests` with no `[unit/integration/e2e]` tags fails.
8. `phase == "align"` fails.
9. `slice_id` mismatch with parent dir fails.

- [ ] **Step 6: Author `references/anti-horizontal-rules.md`**

Contents (≤ 100 lines):
- Restate the verbatim anti-horizontal-nudge template at the top.
- Three worked counter-examples showing horizontal decomposition that this skill MUST refuse to produce:
  1. "First build all 5 screens, then wire all the handlers, then run all the migrations."
  2. "Backend developer does the API; frontend developer does the UI; meet in the middle."
  3. "MVP first means just the data layer; UI is for later."
- One worked example showing correct vertical decomposition for a small feature (3-4 rows, each crossing UI+Logic+Data).
- Reasoning section: why horizontal decomposition is the LLM default and why the nudge has to be aggressive.

- [ ] **Step 7: Author `examples/team-todo-comments-plan.md`**

Golden plan.md output for `team-todo-comments`. Use the same example feature as 2B's worked example. Includes:
- Full frontmatter.
- All 6 sections.
- ≥ 3 vertical-decomposition rows (e.g. row 1: list comments on a todo; row 2: post a new comment; row 3: edit/delete own comment).
- Anti-horizontal nudge verbatim.
- 5 Definition of Done items verbatim.
- ≥ 4 automated tests covering the EARS lines.

- [ ] **Step 8: Run tests**

Run: `pytest impl-plan/plan-vertical/tests/ -v`
Expected: all 9 pass (1 expected as warning, not failure).

- [ ] **Step 9: Commit Task 3**

```bash
git add impl-plan/plan-vertical/
git commit -m "feat(impl-plan): rewrite plan-vertical for per-slice scope + anti-horizontal nudge (Task 2C step 3)"
```

---

## Task 4: Cross-skill verification & finalization

- [ ] **Step 1: Tree shape**

Run: `find impl-plan -type f \( -name 'SKILL.md' -o -name 'validator.py' -o -name 'test_validator.py' \) | sort`
Expected: at least 9 files (3 SKILL.md + 3 validator.py + 3 test_validator.py). The `impl-plan/supervised/` skill is untouched (existed before this task; not in scope).

Run: `find impl-plan -mindepth 2 -maxdepth 2 -type d | sort`
Expected: includes `impl-plan/brainstorm/`, `impl-plan/align/`, `impl-plan/plan-vertical/`, plus pre-existing `impl-plan/supervised/`, `impl-plan/skills/`.

- [ ] **Step 2: Frontmatter integrity (per CONTRIBUTING.md § Integrity Checklist)**

```bash
python3 - <<'EOF'
import yaml
expected = {
  "impl-plan/brainstorm/SKILL.md": ("impl-plan-brainstorm", "2."),
  "impl-plan/align/SKILL.md": ("impl-plan-align", "1."),
  "impl-plan/plan-vertical/SKILL.md": ("impl-plan-plan-vertical", "2."),
}
for path, (name, vmajor) in expected.items():
    fm = yaml.safe_load(open(path).read().split('---')[1])
    assert fm['name'] == name, (path, fm['name'])
    assert fm['description'].startswith('Use when'), path
    assert isinstance(fm['metadata']['tags'], list) and len(fm['metadata']['tags']) >= 3, path
    assert fm['metadata']['stage'] in ('alpha','beta','stable'), path
    assert fm['metadata']['version'].startswith(vmajor), (path, fm['metadata']['version'])
    assert 'prerequisites' in fm['metadata'], (path, "must use prerequisites schema")
    for legacy in ('reads_from','writes_to','user_inputs'):
        assert legacy not in fm['metadata'], (path, f"deprecated field {legacy} present")
print("OK: 3/3 SKILL.md files pass integrity check")
EOF
```
Expected: `OK: 3/3 SKILL.md files pass integrity check`.

- [ ] **Step 3: All three validators green**

Run: `pytest impl-plan/brainstorm/tests/ impl-plan/align/tests/ impl-plan/plan-vertical/tests/ -v`
Expected: all tests pass.

- [ ] **Step 4: End-to-end handoff sequence (dry, against fixtures)**

Build a fixture that walks the full chain:
- Place a fake `_concept/_meta/scope.yaml` (tier=standard-app) in a tmpdir.
- Place fake `_concept/product-spec/features/team-todo/team-todo-comments.md` and `_concept/experience/screens/team-todo-comments/list.md` (golden).
- Place fake `_slice/impl/team-todo-comments/brainstorm.md` (golden).
- Run `impl-plan/align/validator.py` against `examples/team-todo-comments-align.md`. Expect exit 0.
- Run `impl-plan/plan-vertical/validator.py` against `examples/team-todo-comments-plan.md`. Expect exit 0.

This is a deterministic check; it doesn't exercise the LLM body but proves the structural contract holds.

- [ ] **Step 5: Iron-Laws spot-check**

Visually verify each SKILL.md body contains:
- A `MUST` line referencing `iron_laws § 9` (standalone questions).
- A `MUST` line referencing `iron_laws § 7` (refuse if predecessor handoff missing).
- For `plan-vertical` only: the verbatim anti-horizontal nudge near the top of the body AND in `OUTPUT plan.md` template.

- [ ] **Step 6: Handoff to Task 2D documentation check**

Run: `grep -n "_slice/impl/<id>/plan.md\|_slice/impl/<slice_id>/plan.md" impl-plan/plan-vertical/SKILL.md | head -3`
Expected: ≥ 1 match (the plan-vertical SKILL.md must declare its WRITES path so Task 2D's `impl-slice/implement` knows where to read).

This is the cross-cluster contract: **`impl-slice/implement` (Task 2D) reads `_slice/impl/<slice_id>/plan.md` produced by `impl-plan-plan-vertical` here.** No code change here — this step is documentation-only confirmation that the handoff path is pinned in the SKILL.md.

- [ ] **Step 7: Composition smoke check (flows are wired in a later task)**

Run: `grep -l "impl-plan-brainstorm\|impl-plan-align\|impl-plan-plan-vertical" flows/ 2>/dev/null || echo "no flows yet (expected — wired up in later task)"`
Expected: either no matches (flows wired later) or an existing file lists them — both acceptable. Logged note only.

- [ ] **Step 8: Final commit**

```bash
git add -A impl-plan/
git commit -m "feat(impl-plan): finalize cluster + cross-skill verification (Task 2C complete)"
```

---

## Validator strategy (per skill, summarized)

| Skill | Validator scope (deterministic) | Test count |
|---|---|---|
| brainstorm | Frontmatter shape (7 keys) + 5 body sections + slice_id/dir match + tier whitelist + Priority table presence | 7 |
| align | Frontmatter shape + 7 body sections + EARS regex in handoff + non-empty grill (P1/P2 OR Decisions) | 7 |
| plan-vertical | Frontmatter shape + 6 body sections in order + table parse + anti-horizontal nudge verbatim + DoD verbatim + test-tag presence | 9 |

Validators do NOT test the LLM-driven interview body; they test that the *handoff files* conform to the cluster's structural contract. LLM determinism is out of scope here (same approach as 2A and 2B).

---

## Handoff to Task 2D

`impl-slice/implement` (the next skill in the chain, authored in Task 2D) reads `_slice/impl/<slice_id>/plan.md` produced here. The handoff is **the plan.md schema pinned in this document** (§ "Pinned: `plan.md` Schema"). Task 2D MUST honor this schema — specifically:
- The `## Vertical decomposition` table is the work order: `impl-slice/implement` walks the rows in order, completing each end-to-end before starting the next.
- The `## Testing strategy` is the contract for `impl-slice/test`.
- The `## Definition of done` is the gate for `impl-slice/recap` and `impl-slice/commit`.

`impl-slice/commit` (also Task 2D) is responsible for **deleting `_slice/impl/<slice_id>/`** after the atomic commit lands. **None of the three skills in this Task 2C cluster delete the dir.** This mirrors `concept-slice/design-feature`'s deletion of `_slice/concept/<id>/`.

---

## Definition of Done

- [ ] `impl-plan/{brainstorm,align,plan-vertical}/SKILL.md` all exist with valid frontmatter (`name:` matching dir, `description:` starts with "Use when", `metadata.version`, `metadata.tags ≥ 3`, `metadata.stage`, `metadata.prerequisites`)
- [ ] `impl-plan/brainstorm/SKILL.md` is REWRITTEN: `metadata.version: 2.x`, deprecated fields (`user_inputs`, `reads_from`, `writes_to`) removed, READS now point at `_concept/product-spec/features/<group>/<feature_slug>.md` + screens (NOT old project-wide paths), WRITES now point at `_slice/impl/<slice_id>/brainstorm.md`
- [ ] `impl-plan/plan-vertical/SKILL.md` is REWRITTEN: `metadata.version: 2.x`, WRITES now point at `_slice/impl/<slice_id>/plan.md` (NOT `_implementation/superpowers-plan.md`), the verbatim anti-horizontal nudge template appears EARLY in the body
- [ ] `impl-plan/align/SKILL.md` is NEW with `metadata.version: 1.0.0`, full DSL body, `name: impl-plan-align`
- [ ] Each skill enforces Iron Law § 7 via `prerequisites.files` (hard gate on scope.yaml + feature.md, soft/conditional gate on predecessor handoff) AND via STEP 1 explicit refusal logic
- [ ] Each skill enforces Iron Law § 9 via a top-of-body MUST line ("each interview question is a standalone message")
- [ ] `impl-plan-plan-vertical` embeds the verbatim anti-horizontal nudge in BOTH the SKILL.md body (early) AND the OUTPUT plan.md template; the validator checks exact-string match for the output
- [ ] Each skill writes ONLY to `_slice/impl/<slice_id>/<phase>.md` (no permanent `_concept/` or `_implementation/` writes from this cluster)
- [ ] None of the three skills delete `_slice/impl/<slice_id>/` (deletion is `impl-slice/commit`'s job in Task 2D)
- [ ] All 3 `validator.py` files exist; all 3 `tests/test_validator.py` files exist; `pytest impl-plan/{brainstorm,align,plan-vertical}/tests/ -v` is green
- [ ] Golden examples (`team-todo-comments-align.md`, `team-todo-comments-plan.md`) pass their respective validators
- [ ] Slice-id continuity rule documented and consistent: `slice_id == feature_slug` (kebab-case, regex `^[a-z][a-z0-9-]{1,47}$`), reused from concept-slice via the feature filename (no cross-cluster scratch handoff)
- [ ] `_slice/impl/<id>/` lifecycle documented in each skill's body (who creates per tier, who deletes — `impl-slice/commit` from Task 2D)
- [ ] `scope.yaml` is read consistently per Task 2A's pinned schema (no field renames, no schema drift)
- [ ] No edits to existing files outside `impl-plan/` (no flows touched, no base orchestrator touched)
- [ ] All 4 commits land with `feat(impl-plan): ...` prefix on the active migration branch

---

## Open Questions / Ambiguities

1. **Per-slice plan.md format is not in `contracts/plans.md`.** This plan PROPOSES the per-slice schema (§ "Pinned: `plan.md` Schema"). `contracts/plans.md` defines a project-level `PLANS.md` with concept + implementation phases — that's a different artifact. The per-slice schema should be added to `contracts/plans.md` as a sibling section in a follow-up. Until then, this plan is the source of truth for per-slice plan format. Flag for the contracts owner.

2. **Slice-id derivation — is `slice_id == feature_slug` correct or should it carry a date prefix?** This plan adopts `slice_id := feature_slug` (kebab-case) for symmetry with 2B's slug rule. 2B left this as Open Question §1 (raw slug vs UUID vs `<YYYY-MM-DD>-<slug>`). Whatever 2B decides at execution time, this cluster MUST follow in lockstep — the slug regex and derivation rule are shared. Flag if 2B execution diverges.

3. **Anti-horizontal nudge wording strength.** The template in § "Pinned: Anti-Horizontal Nudge Template" is intentionally aggressive (multiple "DO NOT", four "stop" triggers). If user testing finds this language too strong (false positives where rows legitimately don't span all three columns — e.g. a pure-UI polish slice), the template should be tuned. Validator currently checks exact-string match — tuning means a coordinated update to the template, the validator regex, and the golden plan.md fixture. Flag for the first plan-vertical user-test.

4. **`impl-plan-brainstorm` for simple-app.** Per SKILL_GRAPH § 6, `impl-plan/brainstorm` is NOT in the simple-app or mvp bundle. This plan refuses to run for those tiers. If the orchestrator team decides simple-app should also brainstorm, the gate in this plan must loosen to `tier ∈ {simple, standard, complex}`. Flag for orchestrator-team confirmation.

5. **mvp tier as plan-vertical entry point.** SKILL_GRAPH § 6 shows `impl-plan/plan-vertical` ✓ for mvp. So mvp's flow is `plan-vertical → impl-slice/implement` with no brainstorm or align. This plan handles mvp as the entry-point case (plan-vertical creates `_slice/impl/<id>/`). Open: for an mvp with only one feature, should there even BE a `_slice/impl/<id>/` dir, or should plan-vertical write directly to a project-level plan? This plan says: keep the `_slice/impl/<id>/` dir for consistency (1 slice = 1 dir, even for mvp's single slice). Flag for sanity-check.

6. **Empty UI/Logic/Data cells in vertical-decomposition rows.** The validator emits a WARNING (not failure) on empty cells, allowing rows that legitimately don't touch one column (e.g. a pure-UI label change in row 5 of a polish-pass slice). The skill's STEP 7 CHECKPOINT asks the user to justify any such row. Open: should the validator ESCALATE the warning to error if more than 50% of rows have an empty column? That would catch the LLM defaulting to layered decomposition in a row table that LOOKS vertical. Flag as a possible v1.1 tightening.

7. **Existing `impl-plan/plan-vertical/SKILL.md` salvage.** The Phase-1 migrated version has useful content on entity dependency ordering (model.json walking, parents-before-children) and journey-stage ordering (hero/vital/hygiene). This plan says "salvage where useful" but the per-slice scope makes most of it redundant (a per-slice plan only covers ONE feature, so cross-feature ordering is moot). The dependency-walking insight survives as "row order within `## Vertical decomposition`" (parents before children for entity rows). Flag for the executor to decide how aggressively to copy-paste vs rewrite.

8. **Single-question-per-message enforcement.** Iron Law § 9 says questions are standalone messages. The plan adds a MUST line to every skill body, but there's no automatic check that the LLM honored it (only post-hoc transcript review). Same as 2B's open question §8. Out of scope here.

9. **Description-field length.** `contracts/asset_frontmatter.md` says descriptions are 1-1024 chars. The proposed `impl-plan-align` description in Task 2 Step 2 is ~350 chars; `impl-plan-plan-vertical` is ~400 chars. Both within bounds. Flag only if a future spec tightens the limit.
