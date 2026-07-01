# Task 2B — `concept-slice/*` Cluster Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author the four `concept-slice/*` skills that compose the per-feature concept loop for `standard-app` and `complex-app` tiers — `brainstorm → align → scope-feature → design-feature` — each consuming the previous output via `_slice/concept/<id>/<phase>.md`, with `design-feature` writing this feature's portion of `product-spec/features/<feature>.md`, `experience/screens/<feature>/*.md`, and `_concept/walkthrough-mockup/<tier>/<feature>.*` and deleting the slice scratch on success.

**Architecture:**
- Four sibling skills under `concept-slice/{brainstorm,align,scope-feature,design-feature}/`, all path-named per CONTRIBUTING.md (`concept-slice-<phase>`).
- Strict baton-pass: each skill `READS` the previous phase's handoff file in `_slice/concept/<slice_id>/`, refuses to run if missing (Iron Law § 7), and `WRITES` its own phase file. `design-feature` is the only skill that touches permanent `_concept/` artifacts; it deletes the slice scratch on success (mirrors `impl-slice/finish` / `impl-slice/commit`).
- Tier context is read once per phase from `_concept/_meta/scope.yaml` (schema pinned by Task 2A). `tier` selects the walkthrough-mockup output sub-dir for `design-feature`.
- All four skills ask interview questions; Iron Law § 9 enforced as "one question per assistant message, wait for answer before continuing."
- `design-feature` is feature-scoped: it writes ONLY paths whose path-segment matches `<feature_slug>` and refuses to touch any other feature's files.

**Tech Stack:**
- Skill DSL per `contracts/skill_grammar.md`; frontmatter per `contracts/asset_frontmatter.md` (skills) and `contracts/frontmatter.md` (concept artifacts written by `design-feature`).
- Markdown handoffs (`_slice/concept/<slice_id>/<phase>.md`) and YAML frontmatter on all permanent outputs.
- Python 3.12+ for per-skill `validator.py` (PyYAML, stdlib only otherwise).

---

## Pre-flight

- [ ] **Pre-1: Confirm cwd**

Run: `pwd`
Expected: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

- [ ] **Pre-2: Confirm git state is clean enough**

Run: `git status -sb`
Expected: clean tree, or only untracked plan docs on the active migration branch. If unrelated dirty files, stop and clarify with the user.

- [ ] **Pre-3: Confirm target dir exists and is empty (only `skills/` placeholder allowed)**

Run: `ls -la concept-slice/`
Expected: contains only `skills/` (Phase 1 stub). The four target sub-dirs (`brainstorm/`, `align/`, `scope-feature/`, `design-feature/`) do NOT yet exist.

- [ ] **Pre-4: Confirm source documents are readable**

Run: `wc -l SKILL_GRAPH.md REFACTOR_MOCKUP.md contracts/iron_laws.md contracts/skill_grammar.md contracts/asset_frontmatter.md contracts/frontmatter.md CONTRIBUTING.md docs/devlog/2A-scope-project.md`
Expected: all line counts non-zero.

- [ ] **Pre-5: Confirm Task 2A's mini-plan exists and pins the `scope.yaml` schema**

Run: `grep -n "schema_version" docs/devlog/2A-scope-project.md | head -3`
Expected: at least one match. (This cluster reads `_concept/_meta/scope.yaml` and treats 2A's pinned schema as the contract.)

- [ ] **Pre-6: Confirm naming convention**

Per `CONTRIBUTING.md` § Naming Conventions and the parent plan (lines 1567-1571), the four `name:` fields MUST be:
- `concept-slice-brainstorm` (dir: `concept-slice/brainstorm/`)
- `concept-slice-align` (dir: `concept-slice/align/`)
- `concept-slice-scope-feature` (dir: `concept-slice/scope-feature/`)
- `concept-slice-design-feature` (dir: `concept-slice/design-feature/`)

Each `name:` MUST equal the parent directory name exactly (no shortening).

---

## Source-of-Truth Anchors (read before authoring any skill)

The executing agent MUST read each of these once, in this order, before starting Task 1:

1. `docs/devlog/2A-scope-project.md` — § "Pinned Schema — `_concept/_meta/scope.yaml`" is the contract for every `tier` read in this cluster. **Do not redefine.**
2. `SKILL_GRAPH.md` — § 4 (concept group artifact flow), specifically the concept-slice diagram on lines 222-249 and the per-screen card pattern on lines 256-268.
3. `REFACTOR_MOCKUP.md` — § 4 (walkthrough tiers + input/output contract), § 9 (tier composition table), § 7 (workspace zones). Pins where `design-feature` writes its walkthrough portion: `_concept/walkthrough-mockup/<tier>/<feature>.*`.
4. `contracts/iron_laws.md` — § 7 (no artifact without prerequisites), § 8 (no overwrite without approval), § 9 (questions are standalone messages).
5. `contracts/skill_grammar.md` — DSL keywords (ROLE, READS, WRITES, MUST, NEVER, STEP, CHECKPOINT, OUTPUT, IF/ELSE, EMIT, CHECKLIST, INPUT, REQUIRES).
6. `contracts/asset_frontmatter.md` — § "Skill — SKILL.md" frontmatter schema; especially `metadata.prerequisites.{files,inputs_required,inputs_optional,reads,produces}`.
7. `contracts/frontmatter.md` — schemas for `experience/features/<group>/<feature>.md` and `experience/screens/<group>/<screen>.md` that `design-feature` writes.
8. `CONTRIBUTING.md` — § Naming Conventions, § Integrity Checklist.
9. `impl-plan/brainstorm/SKILL.md` — tone reference (existing brainstorm skill).
10. `impl-slice/finish/SKILL.md` — pattern reference for slice-completion / scratch-deletion.

---

## Pinned: `scope.yaml` Read Pattern (consistent with 2A)

Every skill in this cluster reads `_concept/_meta/scope.yaml` once at start. The four fields it consumes:

```python
# Pseudocode — every concept-slice skill does this in STEP 1
import yaml
scope = yaml.safe_load(open("_concept/_meta/scope.yaml"))
tier            = scope["tier"]              # mvp | simple-app | standard-app | complex-app
flow_to_run     = scope["flow_to_run"]       # "flow:<tier>"  (informational; not used here)
description     = scope["description"]       # one-sentence project description (context for brainstorm)
features_est    = scope["signals"]["features_estimate"]
```

**Refuse-to-run gates (Iron Law § 7):**

| Skill | scope.yaml gate | predecessor handoff gate |
|---|---|---|
| `concept-slice-brainstorm` | hard: tier ∈ {standard-app, complex-app} | none (cluster entry) |
| `concept-slice-align` | hard: tier ∈ {simple-app, standard-app, complex-app} (per SKILL_GRAPH § 6 tier-composition row) | hard: `_slice/concept/<id>/brainstorm.md` exists OR tier == simple-app (which skips brainstorm per § 6) |
| `concept-slice-scope-feature` | hard: tier ∈ {simple-app, standard-app, complex-app} | hard: `_slice/concept/<id>/align.md` exists |
| `concept-slice-design-feature` | hard: tier ∈ {simple-app, standard-app, complex-app} | hard: `_slice/concept/<id>/scope-feature.md` exists |

Each skill MUST emit a clear refusal message (with the exact missing path) before exiting. Refusal is not a warning — it's a hard stop.

**Tier-driven branch in `design-feature`:** the walkthrough-mockup output path is `_concept/walkthrough-mockup/<tier>/<feature>.*`. The extension depends on the walkthrough variant active for that tier (per REFACTOR_MOCKUP.md § 4):

| tier | walkthrough variant active | extension |
|---|---|---|
| simple-app | walkthrough-mockup-static-html | `.html` |
| standard-app | walkthrough-mockup-astro (default) | `.astro` |
| complex-app | walkthrough-mockup-framework | depends on framework — emit `.html` placeholder + flag |

`design-feature` does NOT regenerate the walkthrough — it writes only the per-feature *source spec* (a stub `.txt`/`.html`/`.astro` file under that variant's directory) for the walkthrough renderer to pick up later. Keep this scoped tightly: one file per feature, no cross-feature edits.

---

## Pinned: `_slice/concept/<slice_id>/` Lifecycle

```
+-----------------------------+--------------+----------------------------------+
| Phase                       | Owner        | Action                           |
+-----------------------------+--------------+----------------------------------+
| dir creation                | brainstorm   | mkdir -p _slice/concept/<id>/    |
|                             |              | (or align if brainstorm skipped  |
|                             |              | for simple-app)                  |
| brainstorm.md  write        | brainstorm   | append phase file                |
| align.md       write        | align        | append phase file                |
| scope-feature.md write      | scope-feature| append phase file                |
| (artifact writes — feature, | design-feat. | write _concept/* permanent files |
|  screens, walkthrough stub) |              |                                  |
| dir deletion                | design-feat. | rm -rf _slice/concept/<id>/      |
|                             |              | (only after all permanent writes |
|                             |              |  succeed AND user approves)      |
+-----------------------------+--------------+----------------------------------+
```

**Why `brainstorm` creates the dir, not an orchestrator:** the cluster is composable. A user may invoke `align` directly for `simple-app` (where SKILL_GRAPH § 6 shows brainstorm is not in the bundle). In that case `align` creates the dir.

**Lifecycle invariant:** at most one `_slice/concept/<id>/` exists per active slice. The handoff files inside it are append-only across phases (brainstorm doesn't touch align.md, etc.). Only `design-feature` deletes — and only after committing all permanent artifacts.

---

## Pinned: Slice-ID Format

**Proposal:** `<feature_slug>` — kebab-case, derived from the feature name the user gives at the brainstorm interview.

Format: `^[a-z][a-z0-9-]{1,47}$` (kebab, leading letter, 2–48 chars, no consecutive hyphens, no trailing hyphen).

**Why:** the slice scratch is short-lived and per-feature; a feature slug is human-readable, collision-free within a single project (since features are unique), and makes the `_slice/concept/<slug>/` directory grep-friendly during a slice in progress. UUIDs are opaque; date+slug is unnecessary because slices don't survive their own commit. The slug can be derived deterministically from the feature title via:

```
slug = title.lower()
slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
slug = re.sub(r"-+", "-", slug)[:48]
```

**Collision handling:** if `_slice/concept/<slug>/` already exists, the entry-point skill (`brainstorm` or `align`) MUST refuse to start and ask the user whether to (a) resume the existing slice, or (b) suffix `-2` to the slug. Never silently overwrite.

**Justification for proposing this here, not Task 2A:** the slug is internal to the concept-slice cluster and not part of the `scope.yaml` schema. It belongs to this cluster's contract. **Open question** for the user: confirm vs. UUID vs. `<YYYY-MM-DD>-<slug>` (flagged in Open Questions § 1 below).

**Where the slug is stored:** at the top of every phase file as YAML frontmatter:

```yaml
---
slice_id: team-todo-comments
feature_title: "Comments on team todo items"
phase: brainstorm   # | align | scope-feature | design-feature
created_at: 2026-05-07T12:34:56Z
last_updated: 2026-05-07T12:34:56Z
---
```

This frontmatter is the cross-phase contract — every downstream phase reads `slice_id` and `feature_title` from the predecessor's handoff file (no need to re-prompt).

---

## File Targets

All paths absolute, inside `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`.

For each of the four skills:
- **Create:** `concept-slice/<phase>/SKILL.md`
- **Create:** `concept-slice/<phase>/validator.py`
- **Create:** `concept-slice/<phase>/tests/test_validator.py`
- **Create (optional, recommended):** `concept-slice/<phase>/references/<phase>-prompt-style.md` (interview tone reference; ≤80 lines)

Where `<phase>` ∈ {`brainstorm`, `align`, `scope-feature`, `design-feature`}.

For `design-feature` only:
- **Create:** `concept-slice/design-feature/references/feature-portion-rule.md` — the "writes ONLY this feature's portion" detection rule (path-segment match), with worked examples.
- **Create:** `concept-slice/design-feature/examples/team-todo-comments/` — a complete worked example: scope-feature.md input + 3 produced files (feature.md, screens/login.md stub, walkthrough-mockup/standard-app/comments.astro stub) for the validator to snapshot against.

**No edits** to existing files in this task. (The base orchestrator and tier flows that wire these skills together are updated in later tasks — do not touch them here.)

---

## Iron Laws — How They Apply Across the Cluster

| Law | How enforced | Where to verify |
|---|---|---|
| § 7 No artifact without prerequisites | Each SKILL.md `metadata.prerequisites.files[].gate: hard` for the predecessor's handoff file; STEP 1 verifies and EXITs on miss | All 4 skills |
| § 8 No overwrite without approval | `design-feature` runs a path-existence check + diff before each permanent write; CHECKPOINT pause for approval if any target exists | `design-feature` only (other skills only write into `_slice/`, where the slice-id collision rule already gates) |
| § 9 Questions are standalone messages | MUST line near top of each SKILL.md: "MUST send each interview question as its own assistant message; never bundle multiple questions in one turn; wait for answer before sending next." | All 4 skills (`brainstorm`, `align`, `scope-feature` interview heavily; `design-feature` may ask 1-2 confirmations) |

---

## Per-skill commit boundary

**Recommended:** one commit per task below (Tasks 1-4), so each skill lands as an atomic unit. After all four skills are committed, a final task wires up the cross-skill verification (Task 5) and produces a single "feat(concept-slice): finalize cluster" commit.

This produces 5 commits for the cluster:
1. `feat(concept-slice): add brainstorm skill (Task 2B step 1)`
2. `feat(concept-slice): add align skill (Task 2B step 2)`
3. `feat(concept-slice): add scope-feature skill (Task 2B step 3)`
4. `feat(concept-slice): add design-feature skill (Task 2B step 4)`
5. `feat(concept-slice): finalize cluster + cross-skill verification (Task 2B complete)`

Each per-skill commit covers its `SKILL.md` + `validator.py` + `tests/` + (optional) `references/`.

---

## Task 1: Author `concept-slice-brainstorm`

**Skill `name:` field:** `concept-slice-brainstorm`

**Skill role:** Sparring partner on what *this one feature* is. Surfaces the user's mental model: who uses it, what triggers it, what the happy path looks like, what's clearly out. Strictly *open-ended*; edge-case grilling is `align`'s job.

**Files:**
- Create: `concept-slice/brainstorm/SKILL.md`
- Create: `concept-slice/brainstorm/validator.py`
- Create: `concept-slice/brainstorm/tests/test_validator.py`

### READS / WRITES (pinned)

```
READS
  _concept/_meta/scope.yaml                  — required; tier + project description (per Task 2A schema)
  ? _concept/discovery/brief.md              — optional; full project context if available
  ? _concept/experience/journeys/stories.json — optional; existing journeys for context
  ? _slice/concept/<slice_id>/brainstorm.md  — re-entry mode (resume/refine existing brainstorm)

WRITES
  _slice/concept/<slice_id>/brainstorm.md    — handoff file for `concept-slice-align`
```

### Handoff file (the WRITES target)

Path: `_slice/concept/<slice_id>/brainstorm.md`

Frontmatter shape (cross-phase contract):

```yaml
---
slice_id: <slug>
feature_title: <free-text title>
phase: brainstorm
tier: <enum from scope.yaml>
created_at: <ISO-8601 UTC Z>
last_updated: <ISO-8601 UTC Z>
---
```

Body sections:
1. `## Feature in one sentence` — user's elevator pitch for THIS feature
2. `## Who uses it` — primary persona / role
3. `## Trigger` — what causes the user to enter this feature
4. `## Happy path (3-7 bullets)` — high-level flow; do NOT enumerate edge cases
5. `## Clearly out of scope` — bullets the user volunteered as "not this"
6. `## Open questions for align` — anything that came up but feels like a *grill-me* question

### Authoring steps

- [ ] **Step 1: Create directory and stub frontmatter**

```bash
mkdir -p concept-slice/brainstorm
```

Verify: `ls concept-slice/brainstorm` → empty.

- [ ] **Step 2: Write `SKILL.md` frontmatter**

`metadata.prerequisites`:
- `files`: `_concept/_meta/scope.yaml` (gate: hard, "Tier context required — produced by `skaileup-scope-scope-project`")
- `inputs_required`:
  - `feature_title` (text, "One-sentence title for the feature you want to design now")
- `inputs_optional`:
  - `slice_id_override` (text, "Override the auto-generated slice id (kebab-case)")
- `reads`: brief.md, stories.json, prior brainstorm.md
- `produces`: `_slice/concept/<slice_id>/brainstorm.md`

Tags: `concept-slice`, `brainstorm`, `interview`, `feature-discovery`, `per-feature`. Stage: `alpha`. Version: `1.0.0`.

Description must start with `Use when ...`.

- [ ] **Step 3: Write `SKILL.md` body (DSL)**

Sections in order:
- `ROLE` — feature-level brainstorm partner.
- `READS` / `WRITES` — copy from § "READS / WRITES (pinned)" above.
- `REFERENCES` — `SKILL_GRAPH.md` § 4, `contracts/iron_laws.md`, `concept-slice/brainstorm/references/brainstorm-prompt-style.md`.
- `MUST` lines (place EARLY per skill_grammar.md § "Authoring tips" #4):
  - `MUST  ask each interview question as its own standalone message (iron_laws § 9)`
  - `MUST  refuse to run if _concept/_meta/scope.yaml is missing (iron_laws § 7)`
  - `MUST  derive slice_id from feature_title via the kebab-case rule unless slice_id_override is set`
  - `MUST  refuse to overwrite an existing _slice/concept/<slice_id>/ — ask user to resume or suffix -2`
  - `MUST  write the handoff frontmatter exactly as specified (slice_id, feature_title, phase, tier, created_at, last_updated)`
- `NEVER` lines:
  - `NEVER  enumerate edge cases (that's align's job)`
  - `NEVER  write the handoff before the user has confirmed the feature_title and happy path`
- `INPUT` block — read from `_concept/_grounding/concept-slice-brainstorm/input.json` if present; else interview.
- `STEP 1` — read `scope.yaml`, validate `tier ∈ {standard-app, complex-app}` (refuse otherwise — simple-app does not run brainstorm per SKILL_GRAPH § 6 tier-composition table).
- `STEP 2` — collect `feature_title` (required) and derive `slice_id`. Check directory collision.
- `STEP 3` — open-ended interview (3-5 questions, each STANDALONE):
  - "In one sentence, what is this feature?"
  - "Who is the primary user, and what role do they have?"
  - "What event or moment triggers them to use this feature?"
  - "Walk me through the happy path in 3-7 bullets."
  - "What's clearly out of scope here? Anything you'd push back on if it came up?"
- `STEP 4` — draft handoff file in memory; show to user.
- `STEP 5` — `CHECKPOINT brainstorm_draft` — user approves or requests edits.
- `STEP 6` — write `_slice/concept/<slice_id>/brainstorm.md`.
- `EMIT` — `[concept-slice-brainstorm] completed slice_id=<id> tier=<tier>`
- `CHECKLIST` — all 6 sections present, frontmatter valid, slice_id matches dir name, file written.

- [ ] **Step 4: Verify frontmatter parses & body has expected anchors**

Run:
```bash
python3 -c "import yaml; fm=yaml.safe_load(open('concept-slice/brainstorm/SKILL.md').read().split('---')[1]); assert fm['name']=='concept-slice-brainstorm'; print('OK')"
```
Expected: `OK`.

Run: `grep -c "^STEP " concept-slice/brainstorm/SKILL.md`
Expected: `>= 6`.

- [ ] **Step 5: Author `validator.py`**

Validator scope (deterministic, doesn't test the LLM body):
- Loads `_slice/concept/<slug>/brainstorm.md`.
- Asserts frontmatter has all 6 required keys (`slice_id, feature_title, phase, tier, created_at, last_updated`).
- Asserts `phase == "brainstorm"`.
- Asserts `slice_id` matches the regex `^[a-z][a-z0-9-]{1,47}$` and equals the parent directory name.
- Asserts `tier` ∈ {`standard-app`, `complex-app`}.
- Asserts body contains all 6 `## ...` section headers.
- Exit 0 on success, 2 on any failure (with explicit error per failure).

CLI: `python3 validator.py <path/to/brainstorm.md>`.

- [ ] **Step 6: Author `tests/test_validator.py`**

Tests:
1. Golden good-case fixture passes.
2. Missing `phase` frontmatter key fails.
3. Wrong `phase` value (`align` instead of `brainstorm`) fails.
4. `slice_id` not matching parent dir fails.
5. Missing one of the 6 section headers fails.
6. `tier == mvp` fails (out-of-scope tier).

- [ ] **Step 7: Run tests**

Run: `pytest concept-slice/brainstorm/tests/ -v`
Expected: all pass.

- [ ] **Step 8: Commit Task 1**

```bash
git add concept-slice/brainstorm/
git commit -m "feat(concept-slice): add brainstorm skill (Task 2B step 1)"
```

---

## Task 2: Author `concept-slice-align`

**Skill `name:` field:** `concept-slice-align`

**Skill role:** Grill-me-style interview that surfaces edge cases, unstated rules, error states, role/permission gaps, and acceptance criteria for THIS feature. Inverts the brainstorm: now the AI asks pointed questions, the user defends their assumptions.

**Files:**
- Create: `concept-slice/align/SKILL.md`
- Create: `concept-slice/align/validator.py`
- Create: `concept-slice/align/tests/test_validator.py`

### READS / WRITES (pinned)

```
READS
  _concept/_meta/scope.yaml                  — required; tier
  _slice/concept/<slice_id>/brainstorm.md    — required IF tier ∈ {standard-app, complex-app}
                                               (simple-app skips brainstorm; align is the entry point)
  ? _concept/discovery/brief.md              — optional; project-level context
  ? _concept/experience/features/**/*.md     — optional; sibling features for cross-feature edge cases
  ? _slice/concept/<slice_id>/align.md       — re-entry mode

WRITES
  _slice/concept/<slice_id>/align.md         — handoff file for `concept-slice-scope-feature`
```

### Handoff file

Path: `_slice/concept/<slice_id>/align.md`

Frontmatter: same shape as brainstorm.md, with `phase: align` and `slice_id`/`feature_title` copied from brainstorm.md (or, in simple-app entry mode, collected fresh).

Body sections:
1. `## Feature recap (one sentence)` — copied from brainstorm or freshly captured
2. `## Acceptance criteria (EARS)` — must be in EARS format ("WHEN ... THE SYSTEM SHALL ...")
3. `## Edge cases` — surfaced via grilling; numbered list, each with a short rationale
4. `## Error states` — what fails, what the user sees
5. `## Permissions / roles` — who can do what (table; rows = roles, cols = actions)
6. `## Unstated assumptions exposed` — assumptions the user hadn't voiced; one bullet each
7. `## Resolved questions` — Q/A list for traceability
8. `## Open questions blocking scope-feature` — P1/P2 questions that scope-feature depends on

### Authoring steps

- [ ] **Step 1: Create dir + frontmatter**

```bash
mkdir -p concept-slice/align
```

Frontmatter: like brainstorm, but:
- `prerequisites.files`: `_concept/_meta/scope.yaml` (hard) AND a *conditional* `_slice/concept/{slice_id}/brainstorm.md` (described as "Required when tier is standard-app or complex-app; not required for simple-app entry").
- The conditional gate is enforced in `STEP 1` of the body (the frontmatter declares it as `gate: soft` because the strict gate is tier-dependent).
- Tags: `concept-slice`, `align`, `interview`, `edge-cases`, `acceptance-criteria`, `grill-me`. Stage `alpha`. Version `1.0.0`.

- [ ] **Step 2: Write body**

- `MUST  ask each grill question as its own standalone message (iron_laws § 9)`
- `MUST  produce acceptance criteria in EARS format (WHEN ... THE SYSTEM SHALL ...)`
- `MUST  refuse to run if scope.yaml says tier ∈ {standard-app, complex-app} and brainstorm.md is missing`
- `MUST  copy slice_id and feature_title from brainstorm.md when present; never re-derive`
- `MUST  surface every P1 (blocking) open question to the user as a standalone message before writing align.md`
- `NEVER  invent acceptance criteria the user did not confirm`
- `NEVER  proceed past step N until the user has answered question N`

- `STEP 1` — read scope.yaml; if `tier in {standard-app, complex-app}`, require brainstorm.md; if `tier == simple-app`, collect `feature_title` directly. Refuse with explicit message if missing.
- `STEP 2` — read brainstorm.md (when present); summarize in 1 paragraph back to the user as a sanity check.
- `STEP 3-7` — the grill. Sample question pillars (each STANDALONE):
  - State transitions: "What happens if the user starts the flow but doesn't complete it?"
  - Boundary inputs: "What's the maximum/minimum/zero case for <X>?"
  - Concurrency: "Two users hit this at the same time. What's the rule?"
  - Permissions: "Can a guest do this? An admin? What's the matrix?"
  - Persistence: "If the user closes the tab mid-action, what's saved?"
  - Errors: "What does the user see when <Y> fails?"
  - Cross-feature: "Does this feature touch any other feature's data?"
- `STEP 8` — draft align.md in memory; show to user.
- `STEP 9` — `CHECKPOINT align_draft`.
- `STEP 10` — write file.
- `EMIT  [concept-slice-align] completed slice_id=<id> tier=<tier>`

- [ ] **Step 3: validator.py**

Asserts:
- Frontmatter required keys + `phase == "align"` + `slice_id` matches dir.
- All 8 body section headers present.
- `## Acceptance criteria (EARS)` body contains at least one line matching `WHEN .* THE SYSTEM SHALL .*` (case-insensitive, multiline).
- `## Permissions / roles` body contains a markdown table (`|` characters in ≥ 2 lines).

- [ ] **Step 4: tests**

Tests:
1. Good fixture passes.
2. Missing EARS line fails.
3. Missing permission table fails.
4. `phase == "brainstorm"` fails.
5. `slice_id` mismatch fails.

- [ ] **Step 5: Run tests**

Run: `pytest concept-slice/align/tests/ -v`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add concept-slice/align/
git commit -m "feat(concept-slice): add align skill (Task 2B step 2)"
```

---

## Task 3: Author `concept-slice-scope-feature`

**Skill `name:` field:** `concept-slice-scope-feature`

**Skill role:** Drives the conversation toward the IN/OUT line for THIS feature. Reads align's edge-case list, forces the user to mark each as IN-scope, OUT-of-scope, or DEFER. Outputs the scope decision that `design-feature` honors.

**Files:**
- Create: `concept-slice/scope-feature/SKILL.md`
- Create: `concept-slice/scope-feature/validator.py`
- Create: `concept-slice/scope-feature/tests/test_validator.py`

### READS / WRITES (pinned)

```
READS
  _concept/_meta/scope.yaml                  — required; tier
  _slice/concept/<slice_id>/align.md         — required (predecessor handoff)
  ? _concept/experience/features/**/*.md     — optional; sibling features (to avoid in-scope items already owned)
  ? _slice/concept/<slice_id>/scope-feature.md — re-entry mode

WRITES
  _slice/concept/<slice_id>/scope-feature.md — handoff file for `concept-slice-design-feature`
```

### Handoff file

Path: `_slice/concept/<slice_id>/scope-feature.md`

Frontmatter: same shape, `phase: scope-feature`.

Body sections:
1. `## In scope` — bullet list. Each bullet has a 1-sentence rationale.
2. `## Out of scope` — bullet list. Each bullet has a 1-sentence rationale.
3. `## Deferred` — bullets the user would do "later but not this slice"; each bullet has a "next-revisit" note.
4. `## Owned by another feature` — items that surfaced in align but already live elsewhere. List the other feature path.
5. `## Acceptance criteria (final)` — copied from align.md, filtered to IN-scope only.
6. `## Required entities` — entity names this feature reads/writes (drives downstream datamodel work).
7. `## Required screens` — screen slugs (in `<group>/<screen>` form) this feature needs.

### Authoring steps

- [ ] **Step 1: Create dir + frontmatter**

```bash
mkdir -p concept-slice/scope-feature
```

Frontmatter:
- `prerequisites.files`: scope.yaml (hard), `_slice/concept/{slice_id}/align.md` (hard).
- Tags: `concept-slice`, `scope-feature`, `in-out`, `boundary`, `interview`. Stage `alpha`. Version `1.0.0`.

- [ ] **Step 2: Write body**

- `MUST  read align.md and surface each edge case to the user as a standalone IN/OUT/DEFER question`
- `MUST  refuse to run if align.md is missing (iron_laws § 7)`
- `MUST  copy slice_id and feature_title from align.md unchanged`
- `MUST  filter acceptance criteria to IN-scope only`
- `MUST  list required screens in "<group>/<screen>" form (matches experience/screens/ directory layout)`
- `NEVER  silently move an item between IN/OUT/DEFER buckets without user confirmation`
- `NEVER  add edge cases the align.md didn't surface (cite-only)`

- `STEP 1` — read scope.yaml + align.md. Refuse if either missing.
- `STEP 2` — for each edge case in align.md, send a STANDALONE IN/OUT/DEFER question.
- `STEP 3` — for each open question still in align.md, ask STANDALONE.
- `STEP 4` — draft scope-feature.md in memory; show to user.
- `STEP 5` — CHECKPOINT `scope_decision`.
- `STEP 6` — write file.
- `EMIT  [concept-slice-scope-feature] completed slice_id=<id> in_scope=<n> out=<n> deferred=<n>`

- [ ] **Step 3: validator.py**

Asserts:
- Frontmatter required keys + `phase == "scope-feature"` + slice_id matches dir.
- All 7 body section headers present.
- `## In scope` body has ≥ 1 bullet.
- `## Required screens` body uses `<group>/<screen>` form (regex `^- [a-z0-9-]+/[a-z0-9-]+$` per line).

- [ ] **Step 4: tests**

Tests:
1. Good fixture passes.
2. Empty `## In scope` fails.
3. Bad screen format (e.g. `- login` without group) fails.
4. `phase == "align"` fails.

- [ ] **Step 5: Run tests + commit**

Run: `pytest concept-slice/scope-feature/tests/ -v`
Expected: all pass.

```bash
git add concept-slice/scope-feature/
git commit -m "feat(concept-slice): add scope-feature skill (Task 2B step 3)"
```

---

## Task 4: Author `concept-slice-design-feature`

**Skill `name:` field:** `concept-slice-design-feature`

**Skill role:** The only writer of permanent `_concept/` artifacts in the cluster. Takes scope-feature.md and produces THIS feature's portion of:
- `_concept/product-spec/features/<group>/<feature_slug>.md` (one feature file)
- `_concept/experience/screens/<feature_slug>/<screen_slug>.md` (N screen files, N = `len(scope-feature.required_screens)`)
- `_concept/walkthrough-mockup/<tier>/<feature_slug>.<ext>` (one walkthrough stub; ext per tier — see § "Pinned: scope.yaml Read Pattern")

Then deletes `_slice/concept/<slice_id>/`.

**Files:**
- Create: `concept-slice/design-feature/SKILL.md`
- Create: `concept-slice/design-feature/validator.py`
- Create: `concept-slice/design-feature/tests/test_validator.py`
- Create: `concept-slice/design-feature/references/feature-portion-rule.md`
- Create: `concept-slice/design-feature/examples/team-todo-comments/` (worked example: scope-feature.md + 3 produced files)

### READS / WRITES (pinned)

```
READS
  _concept/_meta/scope.yaml                          — required; tier (for walkthrough-mockup sub-dir)
  _slice/concept/<slice_id>/scope-feature.md         — required (predecessor handoff)
  _slice/concept/<slice_id>/align.md                 — required (acceptance criteria source)
  ? _slice/concept/<slice_id>/brainstorm.md          — optional (referenced for "agent_notes" frontmatter field)
  ? _concept/discovery/brand/tokens.json             — optional; used in screens
  ? _concept/blueprint/datamodel/model.json          — optional; used to fill data_entities[]
  ? _concept/experience/features/**/*.md             — REQUIRED for the feature-portion-rule check (see below)
  ? _concept/experience/screens/**/*.md              — REQUIRED for the feature-portion-rule check

WRITES
  _concept/product-spec/features/<group>/<feature_slug>.md   — feature spec (per contracts/frontmatter.md)
  _concept/experience/screens/<feature_slug>/<screen_slug>.md — one file per required screen
  _concept/walkthrough-mockup/<tier>/<feature_slug>.<ext>    — one walkthrough source stub

DELETES
  _slice/concept/<slice_id>/                          — entire scratch dir, only on success
```

### The "writes ONLY this feature's portion" rule

This is the cluster's hardest invariant. Spelled out:

**Detection:** `design-feature` does NOT modify any file whose path-segment does not contain `<feature_slug>` (after the relevant base dir):

| Target dir | Path-segment match required |
|---|---|
| `_concept/product-spec/features/` | filename stem MUST equal `<feature_slug>` |
| `_concept/experience/screens/` | first dir under `screens/` MUST equal `<feature_slug>` |
| `_concept/walkthrough-mockup/<tier>/` | filename stem MUST equal `<feature_slug>` |

**Pre-write check (Iron Law § 8 enforcement):** before each write, the skill:

1. Computes the target path.
2. Stats it: if it doesn't exist, write it and continue.
3. If it exists:
   a. Loads existing content.
   b. Computes a unified diff against the proposed content.
   c. CHECKPOINT — show the diff and ask the user: "Approve overwrite? (yes / no / edit)"
   d. If `no`, stop the entire skill (don't proceed to other writes; do NOT delete scratch).
   e. If `edit`, prompt for changes, regenerate, repeat from step 3a.

**Cross-feature safety check:** before any write, scan `_concept/experience/screens/` and `_concept/product-spec/features/` for paths whose segments include `<feature_slug>` to ensure no two slices have collided on the same slug. If a collision exists (e.g. another feature's screen is at `screens/<feature_slug>/...` for a *different* feature), refuse and require the user to disambiguate.

**The skill MUST NOT modify any file whose path does not match the path-segment rule.** This is enforced by the validator (which inspects the diff plan before commit) and by a STEP 0 hard check.

### Authoring steps

- [ ] **Step 1: Create dirs + frontmatter**

```bash
mkdir -p concept-slice/design-feature/references
mkdir -p concept-slice/design-feature/examples/team-todo-comments
```

Frontmatter:
- `prerequisites.files`: scope.yaml (hard), `_slice/concept/{slice_id}/scope-feature.md` (hard), `_slice/concept/{slice_id}/align.md` (hard).
- `prerequisites.reads`: brand tokens, datamodel, sibling features, sibling screens (all soft / optional).
- `prerequisites.produces`: list all three target paths with `<feature_slug>` placeholder.
- Tags: `concept-slice`, `design-feature`, `commit`, `permanent-artifact`, `feature-portion`, `walkthrough`. Stage `alpha`. Version `1.0.0`.

- [ ] **Step 2: Write SKILL.md body**

EARLY MUST/NEVER block (per skill_grammar.md § Authoring tip 4):

- `MUST  read scope.yaml AND scope-feature.md AND align.md before any write (iron_laws § 7)`
- `MUST  apply the path-segment rule (see references/feature-portion-rule.md) to every proposed write`
- `MUST  show a unified diff and require explicit yes/no/edit on every existing-file overwrite (iron_laws § 8)`
- `MUST  copy acceptance criteria from align.md verbatim into feature.md (no paraphrasing)`
- `MUST  pick walkthrough-mockup extension from tier per the table in this plan`
- `MUST  delete _slice/concept/<slice_id>/ ONLY after every permanent write succeeds AND user has approved`
- `MUST  send each overwrite-approval question as its own standalone message (iron_laws § 9)`
- `NEVER  modify any path whose segment does not match <feature_slug>`
- `NEVER  delete _slice/concept/<slice_id>/ if any write was skipped, refused, or failed`
- `NEVER  invent screens not listed in scope-feature.md "## Required screens"`
- `NEVER  invent acceptance criteria not present in align.md`
- `NEVER  modify another feature's files even if they appear stale`

`STEP 0: Read all three handoffs + scope.yaml. Refuse with explicit error if any missing.`

`STEP 1: Cross-feature collision check (scan _concept/experience/screens and _concept/product-spec/features for <feature_slug> use by another slice).`

`STEP 2: Compose feature.md content (per contracts/frontmatter.md § "experience/features/...").`
- frontmatter: `priority`, `roles`, `permissions`, `story_refs` (empty if no journeys), `agent_notes` (= one-line summary from brainstorm), `screens: []` (filled in step 4), `data_entities: []` (filled from align "## Required entities"), `last_updated`.
- body: copy align.md acceptance criteria verbatim into a "## Acceptance Criteria" section.

`STEP 3: Pre-write check for feature.md` (path-segment rule + diff-on-existence). CHECKPOINT if exists.

`STEP 4: Compose each screen file (per contracts/frontmatter.md § "experience/screens/...").`
- For each `<group>/<screen>` in scope-feature `## Required screens`, build `_concept/experience/screens/<feature_slug>/<screen>.md`.
- frontmatter: `implements: [_concept/product-spec/features/<group>/<feature_slug>.md]`, `data_entities: [...]`, `layout: experience/screens/00_layout/shell.md` (or omit if shell.md doesn't yet exist), `last_updated`.
- After all screen paths are known, set `screens:` in feature.md frontmatter.

`STEP 5: Pre-write check for each screen file.` CHECKPOINT each existing file.

`STEP 6: Compose walkthrough-mockup stub (one file).`
- Path: `_concept/walkthrough-mockup/<tier>/<feature_slug>.<ext>` per the tier-extension table.
- For tier=simple-app, ext=`html` (placeholder static page).
- For tier=standard-app, ext=`astro` (placeholder Astro page).
- For tier=complex-app, ext=`html` with a comment flagging "framework variant pending"; emit a warning EMIT.
- For tier=mvp, **refuse to run** (mvp does not run concept-slice per SKILL_GRAPH § 6).

`STEP 7: Pre-write check for walkthrough stub.`

`STEP 8: Show full plan (all three writes + deletes) to user via CHECKPOINT design_feature_plan.`

`STEP 9: Execute writes in order: feature.md → screen files → walkthrough stub.`

`STEP 10: Verify all three (or N+2) writes succeeded by re-reading each file.`

`STEP 11: Delete _slice/concept/<slice_id>/.` Verify dir is gone.

`STEP 12: EMIT [concept-slice-design-feature] completed slice_id=<id> feature=<slug> tier=<tier> screens=<n>`

- [ ] **Step 3: Author `references/feature-portion-rule.md`**

Contents (≤ 100 lines):
- The path-segment rule, with the table from this plan.
- Three worked examples: feature-only write, screen-only write, walkthrough-only write.
- One worked counter-example: an attempted cross-feature edit that the rule rejects.
- A diff-format example for the overwrite CHECKPOINT.

- [ ] **Step 4: Author `examples/team-todo-comments/`**

Layout:
```
examples/team-todo-comments/
├── input/
│   ├── scope.yaml                  (tier: standard-app + signals)
│   ├── align.md                    (with EARS criteria, permissions table)
│   └── scope-feature.md            (in/out/deferred + required screens)
└── expected_output/
    ├── product-spec/features/<group>/team-todo-comments.md
    ├── experience/screens/team-todo-comments/list.md
    ├── experience/screens/team-todo-comments/detail.md
    └── walkthrough-mockup/standard-app/team-todo-comments.astro
```

These four expected files become the snapshot for the validator.

- [ ] **Step 5: Author `validator.py`**

Asserts (input = produced artifact path or a manifest of paths):

A. Standalone-file mode (`python3 validator.py <path/to/feature.md>`):
- Frontmatter has all required keys per `contracts/frontmatter.md` § "experience/features/...".
- `screens:` is a non-empty list.
- Body contains `## Acceptance Criteria` section.

B. Standalone-screen mode (`python3 validator.py <path/to/screen.md>`):
- Frontmatter has `implements:` (list of feature paths), `data_entities:`, `last_updated`.
- File path matches `_concept/experience/screens/<feature_slug>/<screen>.md`.

C. Manifest mode (`python3 validator.py --manifest <path/to/manifest.json>`):
- Manifest format: `{"feature_slug":"...", "tier":"...", "files":[<path>, ...]}`.
- For each file in manifest, run mode A or B based on filename pattern.
- Assert no file path leaks `<feature_slug>` segment outside the allowed dirs.
- Assert walkthrough stub exists at `_concept/walkthrough-mockup/<tier>/<feature_slug>.<ext>`.

- [ ] **Step 6: Author `tests/test_validator.py`**

Tests:
1. `examples/team-todo-comments/expected_output/...` all pass mode-A/B individually.
2. The `team-todo-comments` manifest passes mode C.
3. A feature.md with `screens: []` fails mode A.
4. A screen file at `_concept/experience/screens/wrong-feature/login.md` (with `<feature_slug>=team-todo-comments`) fails the path-segment rule.
5. A manifest with a missing walkthrough stub fails mode C.
6. A feature.md missing `## Acceptance Criteria` fails mode A.

- [ ] **Step 7: Run tests**

Run: `pytest concept-slice/design-feature/tests/ -v`
Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add concept-slice/design-feature/
git commit -m "feat(concept-slice): add design-feature skill (Task 2B step 4)"
```

---

## Task 5: Cross-skill verification & finalization

- [ ] **Step 1: Tree shape**

Run: `find concept-slice -type f -name 'SKILL.md' -o -name 'validator.py' -o -name 'test_validator.py' | sort`
Expected: at least 12 files (4 SKILL.md + 4 validator.py + 4 test_validator.py).

Run: `find concept-slice -mindepth 2 -maxdepth 2 -type d | sort`
Expected: includes `concept-slice/brainstorm/`, `concept-slice/align/`, `concept-slice/scope-feature/`, `concept-slice/design-feature/`, plus the existing `concept-slice/skills/`.

- [ ] **Step 2: Frontmatter integrity (per CONTRIBUTING.md § Integrity Checklist)**

For each of the four `SKILL.md` files, run:
```bash
python3 - <<'EOF'
import yaml, sys
expected = {
  "concept-slice/brainstorm/SKILL.md": "concept-slice-brainstorm",
  "concept-slice/align/SKILL.md": "concept-slice-align",
  "concept-slice/scope-feature/SKILL.md": "concept-slice-scope-feature",
  "concept-slice/design-feature/SKILL.md": "concept-slice-design-feature",
}
for path, name in expected.items():
    fm = yaml.safe_load(open(path).read().split('---')[1])
    assert fm['name'] == name, (path, fm['name'])
    assert fm['description'].startswith('Use when'), path
    assert isinstance(fm['metadata']['tags'], list) and len(fm['metadata']['tags']) >= 3, path
    assert fm['metadata']['stage'] in ('alpha','beta','stable'), path
print("OK: 4/4 SKILL.md files pass integrity check")
EOF
```
Expected: `OK: 4/4 SKILL.md files pass integrity check`.

- [ ] **Step 3: All four validators green**

Run: `pytest concept-slice/ -v`
Expected: all tests in all four `tests/` dirs pass.

- [ ] **Step 4: End-to-end handoff sequence (dry, against fixtures)**

Build a test fixture that walks the full chain:
- Place a fake `_concept/_meta/scope.yaml` in a tmpdir (tier=standard-app, signals filled).
- Place fake brainstorm.md + align.md + scope-feature.md (golden examples) under `_slice/concept/team-todo-comments/`.
- Run `concept-slice/design-feature/validator.py --manifest <fixture>/manifest.json` against the worked-example output.
- Verify exit 0.

This is a deterministic check; it doesn't exercise the LLM body but proves the deterministic baton-pass works.

- [ ] **Step 5: Iron-Laws spot-check**

Visually verify each SKILL.md body contains:
- A `MUST` line referencing `iron_laws § 9` (standalone questions).
- For `design-feature` only: a `MUST` line referencing `iron_laws § 8` (no overwrite without approval) AND an explicit overwrite-CHECKPOINT in the steps.
- For all four: a `MUST` line referencing `iron_laws § 7` (refuse if predecessor handoff missing).

- [ ] **Step 6: Composition smoke check**

Run: `grep -l "concept-slice-brainstorm\|concept-slice-align\|concept-slice-scope-feature\|concept-slice-design-feature" flows/ 2>/dev/null || echo "no flows yet (expected — wired up in later task)"`
Expected: either no matches (flows wired later) or an existing file lists them — both are acceptable here. This step just produces a logged note.

- [ ] **Step 7: Final commit**

```bash
git add -A concept-slice/
git commit -m "feat(concept-slice): finalize cluster + cross-skill verification (Task 2B complete)"
```

---

## Handoff to Task 2C (`impl-plan/{align, plan-vertical}`)

**The handoff:** `concept-slice-design-feature` produces THREE permanent artifacts and DELETES the slice scratch on success. Therefore Task 2C's `impl-plan-align` MUST read from the **permanent artifacts**, not from `_slice/concept/<id>/`:

| Task 2C input | Path | Owner |
|---|---|---|
| Feature spec | `_concept/product-spec/features/<group>/<feature_slug>.md` | written by `design-feature` |
| Screens | `_concept/experience/screens/<feature_slug>/<screen>.md` (1..N) | written by `design-feature` |
| (optional) walkthrough stub | `_concept/walkthrough-mockup/<tier>/<feature_slug>.<ext>` | written by `design-feature` |

The slice scratch dir `_slice/concept/<id>/` is **gone** by the time Task 2C runs. This is intentional and mirrors `impl-slice/commit`'s scratch deletion. The truth lives in permanent artifacts. Task 2C MUST NOT depend on slice scratch.

**Implication for Task 2C's mini-plan:** `impl-plan-align`'s `prerequisites.files` should hard-gate on `_concept/product-spec/features/<group>/<feature_slug>.md` (parameterized by feature slug) and the matching screen dir. It MUST NOT reference `_slice/concept/`.

This handoff is documented in this plan and will be cross-referenced from Task 2C.

---

## Validator strategy (per skill, summarized)

| Skill | Validator scope (deterministic) | Test count |
|---|---|---|
| brainstorm | Frontmatter shape + 6 body sections + slice_id/dir match + tier whitelist | 6 |
| align | Frontmatter shape + 8 body sections + EARS regex + permissions-table presence | 5 |
| scope-feature | Frontmatter shape + 7 body sections + screen-format regex + non-empty In-scope | 4 |
| design-feature | Mode A (feature.md) + Mode B (screen.md) + Mode C (manifest with cross-feature/path-segment + walkthrough-stub presence) | 6 |

Validators do NOT test the LLM-driven interview body; they test that the *handoff files* and *permanent artifacts* conform to the cluster's structural contract. LLM determinism is out of scope here (same approach as Task 2A's snapshot test).

---

## Definition of Done

- [ ] `concept-slice/{brainstorm,align,scope-feature,design-feature}/SKILL.md` all exist with valid frontmatter (`name:` matching dir, `description:` starts with "Use when", `metadata.version`, `metadata.tags ≥ 3`, `metadata.stage`)
- [ ] Each skill enforces Iron Law § 7 via `prerequisites.files` (hard gate on the predecessor's handoff file) AND via STEP 1 explicit refusal logic
- [ ] Each skill enforces Iron Law § 9 via a top-of-body MUST line ("each interview question is a standalone message")
- [ ] `concept-slice-design-feature` enforces Iron Law § 8 via the overwrite CHECKPOINT (diff + yes/no/edit)
- [ ] `concept-slice-design-feature` writes ONLY paths whose segment matches `<feature_slug>` (validator Mode C tested)
- [ ] `concept-slice-design-feature` deletes `_slice/concept/<slice_id>/` ONLY after all permanent writes succeed
- [ ] All 4 `validator.py` files exist; all 4 `tests/test_validator.py` files exist; `pytest concept-slice/ -v` is green
- [ ] The four skills compose: a fixture-driven dry-run produces a valid feature.md + screens + walkthrough stub from a brainstorm→align→scope-feature chain
- [ ] `_slice/concept/<id>/` lifecycle is documented in each skill's body (who creates, who deletes)
- [ ] `slice_id` derivation is consistent across all four skills (kebab-case from feature_title; collision rule explicit)
- [ ] `scope.yaml` is read consistently per Task 2A's pinned schema (no field renames, no schema drift)
- [ ] No edits to existing files outside `concept-slice/` (no flows touched, no base orchestrator touched)
- [ ] All 5 commits land with `feat(concept-slice): ...` prefix on the active migration branch

---

## Open Questions / Ambiguities

1. **Slice-id format — slug vs UUID vs date+slug.** This plan proposes `<feature_slug>` (kebab, derived from feature_title). Justification: human-readable, collision-detectable, deletes on commit so persistence isn't an issue. Open: confirm with whoever owns SKILL_GRAPH.md § 4 — they may prefer `<YYYY-MM-DD>-<slug>` for audit (since git history alone won't show which slice ran first if two are interleaved). If preferred, change the regex and the slug derivation rule in `brainstorm` STEP 2 (the rest of the plan is unaffected).

2. **`align` entry-point for simple-app.** The SKILL_GRAPH § 6 tier-composition table shows `concept-slice-align` ✓ for simple-app but `concept-slice-brainstorm` blank. So in simple-app, `align` is the entry point and creates the slice dir itself. This plan handles it (frontmatter declares brainstorm.md as a *conditional* soft gate, body STEP 1 enforces the tier-dependent hard gate). Confirm with the orchestrator team that simple-app's flow.yaml will indeed call `align` directly, not via `brainstorm`. If the orchestrator team decides `brainstorm` should run for simple-app too, simplify back to "brainstorm always creates the dir."

3. **Walkthrough-mockup extension for complex-app.** Per REFACTOR_MOCKUP.md § 9, complex-app uses `walkthrough-mockup-framework`, but the framework is stack-dependent. This plan emits a `.html` placeholder + warning EMIT. Open: should `design-feature` defer the walkthrough write entirely for complex-app and let the framework renderer create the stub on first build? Flagged for the design-feature implementer — pick the simpler option if SKILL_GRAPH is silent. The current plan errs toward "always emit a stub so downstream renderers have a target" but accepts a follow-up that strips the stub for complex-app.

4. **`design-feature` and the existing `experience/screens/00_layout/shell.md` shell layout.** `contracts/frontmatter.md` § "experience/screens/..." sets `layout:` to `experience/screens/00_layout/shell.md`. If the project hasn't generated a shell layout yet (Phase 1's screen domain owns that), `design-feature` either (a) omits the `layout:` field, or (b) refuses with "Run `experience-screens` for the project shell first." Plan currently picks (a) for resilience; flag for orchestrator team confirmation.

5. **Cross-feature collision detection performance.** STEP 1 of `design-feature` scans `_concept/experience/screens/` and `_concept/product-spec/features/` for `<feature_slug>` collisions. For projects with 50+ features, this is still cheap (filesystem glob). Flagged only because the rule is a hard refuse — false positives would be very disruptive. Recommend: the validator surface what triggered the collision so the user can act.

6. **Deferred items go where?** `scope-feature.md` produces a `## Deferred` section with "next-revisit" notes. `design-feature` does NOT write these to permanent artifacts (they're a slice-internal concern, deleted with scratch). This means deferred items are LOST after slice commit. Open: should `design-feature` append deferred items to a permanent `_concept/product-spec/features/_deferred.md` registry? Plan currently says "no, lost on purpose to match impl-slice's truth-lives-in-code rule," but flag for product-spec owner. If yes, add to design-feature WRITES + a 5th permanent artifact.

7. **EARS strictness in align.** The validator regex for EARS is `WHEN .* THE SYSTEM SHALL .*`. EARS has 5 patterns (Ubiquitous, Event-driven, Unwanted, State-driven, Optional). The validator currently checks only Event-driven. Plan accepts this as a soft check — strict EARS validation is out of scope for this cluster (it's `contracts/acceptance_criteria.md`'s job). Flag for downstream tightening.

8. **Single-question-per-message enforcement.** Iron Law § 9 says questions are standalone messages. The plan adds a MUST line to every skill body, but there's no automatic check that the LLM honored it (only post-hoc transcript review). The `lab/judge` skill (per SKILL_GRAPH § 8) could grade transcripts for this — flag as a candidate target for `lab/judge` once it exists. Out of scope here.
