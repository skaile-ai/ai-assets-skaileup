# Task 2D — `impl-slice/{recap, refactor, test, commit}` Cluster Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author the four `impl-slice/*` skills that close the per-slice impl loop after `impl-slice-implement`: `recap → refactor → test → commit`. They consume `_slice/impl/<id>/plan.md` (produced by Task 2C's `impl-plan-plan-vertical`) plus the in-tree implementation, and produce three slice handoffs (`recap.md`, `refactor.md`, `test.md`) plus the lifecycle terminator `impl-slice-commit` which lands atomic git commits AND deletes `_slice/impl/<id>/`.

**Architecture:**
- Four sibling skills under `impl-slice/{recap,refactor,test,commit}/`, all path-named per `CONTRIBUTING.md`. `impl-slice/implement/`, `impl-slice/finish/`, `impl-slice/git-prepare/` already exist (Phase-1 migrated) — this task only adds the four new directories.
- Strict baton-pass identical in shape to `concept-slice/*` and `impl-plan/*`: each skill `READS` the previous phase's handoff in `_slice/impl/<slice_id>/`, refuses on miss (Iron Law § 7), `WRITES` its own phase file. **Only `impl-slice-commit` deletes `_slice/impl/<slice_id>/`** (the cluster's lifecycle terminator — mirrors `concept-slice/design-feature` for the concept side).
- Slice-id continuity: `slice_id == feature_slug` per Tasks 2B and 2C. Every skill in this cluster reads `slice_id` from the predecessor's frontmatter — never re-derives.
- `impl-slice-refactor` is the cluster's odd-skill-out: it actively resists the LLM default of *adding* complexity. The MUST/NEVER block, STEP wording, and the produced `refactor.md` schema are all engineered to bias toward subtraction. This is baked into the skill, not just mentioned.
- `impl-slice-test` is a NEW skill (not migrated). It is a per-slice usability gate (does the slice feel right?), distinct from the project-wide regression suites in `impl-quality/test-{unit,integration,e2e}`. Boundary documented in § "Boundary with `impl-quality/test-*`".

**Tech Stack:**
- Skill DSL per `contracts/skill_grammar.md`; frontmatter per `contracts/asset_frontmatter.md` (skills).
- Markdown handoffs (`_slice/impl/<slice_id>/<phase>.md`) with YAML frontmatter on each.
- Python 3.12+ for per-skill `validator.py` (PyYAML, stdlib only).
- `git` invoked from `commit` for atomic commit creation.

---

## Pre-flight

- [ ] **Pre-1: Confirm cwd**

Run: `pwd`
Expected: `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`

- [ ] **Pre-2: Confirm git state**

Run: `git status -sb`
Expected: clean tree, or only untracked plan docs on the active migration branch. If unrelated dirty files, stop and clarify.

- [ ] **Pre-3: Confirm target dirs**

Run: `ls -la impl-slice/`
Expected: contains `DOMAIN.md`, `finish/`, `git-prepare/`, `implement/`, `skills/` (Phase-1 migration). The four target sub-dirs (`recap/`, `refactor/`, `test/`, `commit/`) do **NOT** yet exist.

- [ ] **Pre-4: Confirm sibling skill front-matter is valid (we will compose with these)**

Run:
```bash
python3 - <<'EOF'
import yaml
for p in ("impl-slice/finish/SKILL.md","impl-slice/git-prepare/SKILL.md","impl-slice/implement/SKILL.md"):
    fm=yaml.safe_load(open(p).read().split('---')[1])
    print(p, "->", fm['name'])
EOF
```
Expected: prints `impl-slice-finish`, `impl-slice-git-prepare`, `impl-slice-implement`.

- [ ] **Pre-5: Confirm 2B and 2C mini-plans exist (this cluster reads schemas pinned there)**

Run:
```bash
ls -la docs/devlog/2B-concept-slice-cluster.md docs/devlog/2C-impl-plan-align-vertical.md
grep -n "Pinned: \`plan.md\` Schema\|Pinned: \`align.md\` Schema\|Slice-ID Continuity" docs/devlog/2C-impl-plan-align-vertical.md | head -5
grep -n "Pinned: Slice-ID Format\|Pinned: \`_slice/concept" docs/devlog/2B-concept-slice-cluster.md | head -5
```
Expected: both files exist; both `grep`s return matches. This cluster MUST NOT redefine `plan.md`, `align.md`, slice-id format, or the lifecycle invariant — they are pinned in 2B/2C.

- [ ] **Pre-6: Confirm naming convention**

Per `CONTRIBUTING.md` § Naming Conventions, the four `name:` fields MUST be:
- `impl-slice-recap` (dir: `impl-slice/recap/`)
- `impl-slice-refactor` (dir: `impl-slice/refactor/`)
- `impl-slice-test` (dir: `impl-slice/test/`)
- `impl-slice-commit` (dir: `impl-slice/commit/`)

Each `name:` MUST equal the parent directory name exactly (no shortening).

- [ ] **Pre-7: Source documents readable**

Run: `wc -l SKILL_GRAPH.md contracts/iron_laws.md contracts/skill_grammar.md contracts/asset_frontmatter.md CONTRIBUTING.md docs/devlog/2A-scope-project.md docs/devlog/2B-concept-slice-cluster.md docs/devlog/2C-impl-plan-align-vertical.md impl-slice/finish/SKILL.md impl-slice/git-prepare/SKILL.md impl-slice/implement/SKILL.md`
Expected: all line counts non-zero.

---

## Source-of-Truth Anchors (read before authoring any skill)

The executing agent MUST read each of these once, in this order, before starting Task 1:

1. `docs/devlog/2C-impl-plan-align-vertical.md` — § "Pinned: `_slice/impl/<id>/` Lifecycle", § "Pinned: `plan.md` Schema", § "Pinned: Slice-ID Continuity". This cluster is the LIFECYCLE TERMINATOR for the dir whose creation is owned by 2C. **Do not redefine.**
2. `docs/devlog/2B-concept-slice-cluster.md` — § "Pinned: `_slice/concept/<slice_id>/` Lifecycle" and § "Pinned: Slice-ID Format". The parallel pattern: `concept-slice/design-feature` is the concept-side lifecycle terminator. This cluster's `impl-slice-commit` mirrors that role for the impl side.
3. `SKILL_GRAPH.md` — § 5.2 (per-slice impl loop, lines 304-360). Pins the loop order: `implement → test → recap → refactor → commit` (note: SKILL_GRAPH puts `test` BEFORE `recap`; see § "Cluster ordering" below for the conflict and resolution).
4. `contracts/iron_laws.md` — § 7 (no artifact without prerequisites), § 8 (no overwrite without approval — relevant for `refactor` which proposes code edits), § 9 (questions are standalone messages — all four skills interview the user).
5. `contracts/skill_grammar.md` — DSL keywords (ROLE, READS, WRITES, MUST, NEVER, STEP, CHECKPOINT, OUTPUT, IF/ELSE, EMIT, CHECKLIST, INPUT, REQUIRES). Especially § "Authoring tips" #4 (place constraints early).
6. `contracts/asset_frontmatter.md` — § "Skill — SKILL.md" frontmatter schema; especially `metadata.prerequisites.{files,inputs_required,inputs_optional,reads,produces}`.
7. `CONTRIBUTING.md` — § Naming Conventions, § Integrity Checklist.
8. `impl-slice/implement/SKILL.md` — predecessor reference; what runs immediately before this cluster.
9. `impl-slice/finish/SKILL.md` — sibling reference (NOT a predecessor); compares to `commit` (boundary in § "Boundary with `git-prepare` and `finish`" below).
10. `impl-slice/git-prepare/SKILL.md` — sibling reference (one-time project setup); compares to `commit` (per-slice atomic commits) — different responsibilities.

---

## Cluster ordering — pinned, with the SKILL_GRAPH conflict resolved

`SKILL_GRAPH.md` § 5.2 shows: `implement → test → recap → refactor → commit`.

The parent plan task list (lines 1610-1613) lists: `recap → refactor → commit` and notes that `test` must be added.

**Resolution (this plan adopts the SKILL_GRAPH order):**

```
impl-slice/implement   (already exists — produced by Phase 1)
       │
       ▼
impl-slice/test        (NEW — per-slice usability gate; reads plan.md "## Testing strategy")
       │     writes _slice/impl/<id>/test.md
       ▼
impl-slice/recap       (NEW — feature-flow explanation + ASCII diagram)
       │     writes _slice/impl/<id>/recap.md
       ▼
impl-slice/refactor    (NEW — force-simplify; AI defaults to ADDING; resist that)
       │     writes _slice/impl/<id>/refactor.md
       │     may apply user-approved edits to in-tree code
       ▼
impl-slice/commit      (NEW — atomic git commits + deletes _slice/impl/<id>/)
       │     reads test.md + recap.md + refactor.md (all three required)
       └─► loop back to "pick next feature" in the parent plan
```

**Why this order (vs. the parent plan's listed order `recap → refactor → commit`):**
- `test` first makes sense: the slice is "done" only if it passes the per-slice usability gate. `recap` is wasted effort if `test` fails and we go back to `implement`.
- `recap` after `test` is mandatory because the user has just confirmed "this works"; capturing the diagram while the model is hot prevents recall drift in `refactor`.
- `refactor` after `recap` is correct: with the diagram in hand, the refactor skill can spot architectural smells the diagram exposes (a node with too many incoming arrows = god module).
- `commit` last is the lifecycle terminator: nothing is committed until all three artifacts exist.

**Each skill's frontmatter declares the predecessor's handoff as a hard gate (Iron Law § 7).** The chain is:
- `test`     gates on `_slice/impl/<id>/plan.md` (Task 2C output).
- `recap`    gates on `_slice/impl/<id>/test.md`.
- `refactor` gates on `_slice/impl/<id>/recap.md`.
- `commit`   gates on `_slice/impl/<id>/{test,recap,refactor}.md` (all three required; deletes scratch).

---

## Pinned: `_slice/impl/<id>/` Lifecycle (this cluster's responsibilities)

This cluster does NOT create `_slice/impl/<id>/` — Task 2C owns creation. This cluster appends three handoff files and DELETES the dir at the very end.

```
+---------------------+----------------------+----------------------------------+
| Phase               | Owner                | Action                           |
+---------------------+----------------------+----------------------------------+
| dir creation        | impl-plan-* (2C)     | (already done before this cluster)|
| brainstorm/align/   | impl-plan-* (2C)     | (already written)                |
|   plan.md           |                      |                                  |
| (implement runs)    | impl-slice-implement | reads plan.md; writes code       |
| test.md write       | impl-slice-test      | append phase file (THIS CLUSTER) |
| recap.md write      | impl-slice-recap     | append phase file (THIS CLUSTER) |
| refactor.md write   | impl-slice-refactor  | append phase file (THIS CLUSTER) |
| atomic git commits  | impl-slice-commit    | git add + git commit (per logical|
|                     |                      |   unit; user-approved file list) |
| dir deletion        | impl-slice-commit    | rm -rf _slice/impl/<id>/         |
|                     |                      | (only after all commits land)    |
+---------------------+----------------------+----------------------------------+
```

**Lifecycle invariant:** at most one `_slice/impl/<id>/` exists per active impl slice. Files are append-only across phases. Only `impl-slice-commit` deletes — and only after all atomic commits land successfully.

---

## Pinned: Slice-ID Continuity (consistent with 2B and 2C)

Every skill in this cluster reads the same `slice_id` (== `feature_slug`) used since `concept-slice-brainstorm`. The slug flows through the predecessor's handoff frontmatter:

```yaml
---
slice_id: <feature_slug>          # kebab-case, regex ^[a-z][a-z0-9-]{1,47}$
feature_title: <free-text>
feature_path: _concept/product-spec/features/<group>/<feature_slug>.md
phase: test | recap | refactor    # commit does not write a handoff file
tier: <enum from scope.yaml>
created_at: <ISO-8601 UTC Z>
last_updated: <ISO-8601 UTC Z>
---
```

Each phase file inherits `slice_id`, `feature_title`, `feature_path`, `tier` unchanged from the predecessor. `phase` is the only field each skill sets fresh. Validators enforce frontmatter consistency.

**Refuse-to-run gates (Iron Law § 7):**

| Skill | Hard gates (predecessor handoff(s)) | Soft gates |
|---|---|---|
| `impl-slice-test` | `_slice/impl/<id>/plan.md` | `package.json`, the project's test runner config |
| `impl-slice-recap` | `_slice/impl/<id>/test.md` | `_slice/impl/<id>/plan.md` (re-read for context) |
| `impl-slice-refactor` | `_slice/impl/<id>/recap.md` | `_slice/impl/<id>/plan.md`, `_slice/impl/<id>/test.md` |
| `impl-slice-commit` | `_slice/impl/<id>/test.md`, `_slice/impl/<id>/recap.md`, `_slice/impl/<id>/refactor.md` | git repo state (must be a working tree with the slice's edits unstaged or partially staged) |

Each skill MUST emit a clear refusal message (with the exact missing path) before exiting. Refusal is not a warning — it's a hard stop.

---

## Pinned: `test.md` Schema (output of `impl-slice-test`)

**This is the per-slice usability gate, NOT the project-wide regression test suite.** Boundary explained in § "Boundary with `impl-quality/test-*`".

Path: `_slice/impl/<slice_id>/test.md`

Frontmatter:

```yaml
---
slice_id: <slug>
feature_title: <free-text>
feature_path: _concept/product-spec/features/<group>/<feature_slug>.md
phase: test
tier: <enum from scope.yaml>
created_at: <ISO-8601 UTC Z>
last_updated: <ISO-8601 UTC Z>
---
```

**Required body sections (validator-enforced):**

1. `## Slice goal recap (1-2 lines)` — copied from `plan.md ## Slice scope` so reader doesn't re-open plan.md.
2. `## Manual checks done` — bullet list. Each bullet sourced from `plan.md ## Testing strategy ### Manual checks`. Each bullet has an explicit `[PASS|FAIL|SKIPPED]` tag and a 1-line note. **Validator requires every line in plan.md's manual-checks bullets to appear here, tagged.**
3. `## Automated tests run` — bullet list. Each bullet sourced from `plan.md ## Testing strategy ### Automated tests`. Each bullet has `[PASS|FAIL|SKIPPED]` and the actual command run + exit code. **Validator requires every line in plan.md's automated-tests bullets to appear here, tagged.**
4. `## Usability observations` — free-form bullets. The "does it feel right?" check that distinguishes this skill from `impl-quality/test-*`. Sample prompts the skill asks the user (each STANDALONE per Iron Law § 9):
   - "Did the flow feel awkward — too many clicks, too much text, hidden state?"
   - "Was anything surprising — buttons in wrong places, naming inconsistent with the rest of the app?"
   - "Would a new user get stuck anywhere?"
   - "Does any screen have too much going on?"
5. `## Outstanding issues` — numbered list. Each item has `[BLOCKER|SHOULD-FIX|NICE-TO-HAVE]`. **Validator: if the next section's `Decision` is "Done", this section MUST contain zero `[BLOCKER]` items.**
6. `## Decision` — exactly one of three lines, on its own row:
   - `Decision: Done` — slice passes the gate; ready for `recap`.
   - `Decision: Needs more work` — go back to `implement` for the listed `[BLOCKER]` items.
   - `Decision: Blocked` — outside-the-slice issue surfaced (concept gap, infra missing); slice cannot proceed without intervention.

   **Validator regex:** `^Decision: (Done|Needs more work|Blocked)$`. Anything else fails.

**Validator strategy for `test.md`:**
- Frontmatter has all 7 required keys + `phase == "test"` + `slice_id` matches dir.
- All 6 body section headers present, in order.
- For every bullet in plan.md's manual-checks list, a matching tagged bullet exists in this file's `## Manual checks done` (regex match by stripped-text prefix — flag if missing).
- Same for automated-tests list.
- Every `## Manual checks done` and `## Automated tests run` bullet has `[PASS|FAIL|SKIPPED]` tag.
- Exactly one `Decision: ...` line; value in {Done, Needs more work, Blocked}.
- If `Decision: Done` then `## Outstanding issues` has zero `[BLOCKER]` items.

---

## Pinned: `recap.md` Schema (output of `impl-slice-recap`)

Path: `_slice/impl/<slice_id>/recap.md`

Frontmatter: same shape as `test.md`, with `phase: recap`.

**Required body sections (validator-enforced):**

1. `## Slice goal recap (1-2 lines)` — copied from `plan.md ## Slice scope`.
2. `## What was built (1-3 sentences)` — plain-English summary of the slice's behavior in user-visible terms (NOT in implementation terms). Validator: must contain ≥ 1 sentence; ≤ 3 sentences (count by `.` outside of code spans, soft check — warn if > 3).
3. `## ASCII diagram` — **MANDATORY**. The skill MUST produce an ASCII diagram of the feature flow (data flow OR control flow OR component composition; the skill picks the type that best fits). The diagram lives inside a fenced code block with no language identifier. Validator: at least one fenced ` ``` ` block exists in this section, with ≥ 5 non-empty lines, and contains at least one of the characters `→`, `>`, `|`, `─`, or `+` (so a paragraph alone won't pass). **Starter shape the executing agent gives the LLM (in the SKILL.md body):**

   ```
   +----------+      submit       +-----------+      writes      +---------+
   |  <UI>    | ----------------> | <handler> | ---------------> | <data>  |
   |  screen  | <---------------- |  fn/route | <--------------- |  table/ |
   +----------+   re-render w/    +-----------+   row-back       |  store  |
                 fresh data                                       +---------+
   ```

   The skill SHOULD use this as a starting template and customize it (rename nodes; add branches; add error paths). The validator does NOT require the literal template — only the structural traits above.

4. `## Files touched` — bullet list. Each bullet is a relative path inside the repo, optionally annotated with `(new|modified|deleted)`. Validator: ≥ 1 bullet; each bullet matches a file pattern (regex `^- [^ ]+( \((new|modified|deleted)\))?$`).
5. `## Outcome vs. plan` — three sub-headings:
   - `### Met expectations` — bullets from `plan.md ## Definition of done` that are now true.
   - `### Deviated` — bullets where the implementation differs from `plan.md` (with 1-line "why").
   - `### Carried over` — bullets pulled from `plan.md ## Open carry-overs` that are still open.

**Validator strategy for `recap.md`:**
- Frontmatter has all 7 required keys + `phase == "recap"` + `slice_id` matches dir.
- All 5 body section headers present.
- `## ASCII diagram` body contains ≥ 1 fenced code block with ≥ 5 lines containing at least one of `→ > | ─ +`.
- `## What was built (1-3 sentences)` body has 1-3 sentences (warn if > 3).
- `## Files touched` body has ≥ 1 bullet matching the path regex.
- `## Outcome vs. plan` has all three required sub-headings.

---

## Pinned: `refactor.md` Schema (output of `impl-slice-refactor`)

**The "AI defaults to adding complexity" framing is critical.** This skill must ACTIVELY resist additions and only propose subtractions/simplifications. The MUST/NEVER block, STEP wording, and the schema below are all engineered for this.

Path: `_slice/impl/<slice_id>/refactor.md`

Frontmatter: same shape, `phase: refactor`.

**Required body sections (validator-enforced):**

1. `## Slice goal recap (1-2 lines)` — copied from `plan.md ## Slice scope` so a reviewer doesn't re-open plan.md.
2. `## Smallest improvement candidates` — numbered list, EXACTLY 1-3 items. Each item has the structure:

   ```markdown
   ### N. <one-line title>
   **Type:** subtraction | simplification | clarification
   **Files:** <relative paths>
   **Diff sketch:** (optional) a 5-15 line unified-diff-style sketch
   **Rationale:** 1-2 sentences. Why does removing/simplifying this make the code easier for the next reader?
   **Risk:** low | medium | high — <1 sentence on what could break>
   **Behavior preservation:** how do we know this doesn't change behavior? (test, manual check, or "no behavior to preserve — it's dead code")
   ```

   **Validator: at least N=1 candidate; at most N=3; each candidate has ALL six sub-fields.**

   **Validator: `Type` must be in {`subtraction`, `simplification`, `clarification`}.** The schema deliberately omits "addition" — there is no field for proposing a new helper, new abstraction, new file, etc. If the AI thinks "we need a new utility module here," that is OUT OF SCOPE for this skill.

3. `## What I considered but rejected (1-3 items)` — numbered list of refactor ideas the skill considered AND deliberately did NOT propose, with a 1-sentence "why not." This section forces the AI to surface its instincts and explain why each is wrong:
   - "Considered: extract a `useFormState` hook. Rejected: would add an abstraction for one caller; not yet a pattern."
   - "Considered: split `<List>` into `<ListContainer>` + `<ListPresentational>`. Rejected: only adds a layer, no concrete benefit yet."

   **Validator: ≥ 1 rejected item.** This is a hard requirement — the skill MUST surface at least one rejected candidate. If the AI cannot think of any candidate it rejected, that is itself a smell (it means it has not actually considered the design space).

4. `## User approval gate` — exactly one line: `Approval status: pending | approved | rejected | modified`.

   - `pending` is the default after the skill writes the proposal.
   - `approved` means the user has said "go ahead, apply candidate #N" for ≥ 1 candidate.
   - `rejected` means the user said "skip refactor entirely."
   - `modified` means the user edited the proposal text and re-approved.

   **Validator: regex `^Approval status: (pending|approved|rejected|modified)$`.**

5. `## Applied changes` — empty (`_(none — approval pending)_`) until the user approves. After approval, this section lists the actual edits made (file, hunk count, summary line). **Validator: if `Approval status: approved|modified` AND this section is `_(none — approval pending)_`, fail.**

**Behavior of the skill (steps; not part of the schema but coupled to it):**
- The skill writes `refactor.md` with `Approval status: pending` and the 1-3 candidates.
- The skill THEN asks the user (standalone message per Iron Law § 9): "Which candidate(s) should I apply, if any? You can also reject all and we move on to commit."
- ONLY after user response does the skill apply edits. The user's choice is recorded in `## Applied changes` and `Approval status` is updated.
- If the user says "no, skip refactor," `Approval status: rejected`, `## Applied changes` becomes `_(none — user declined refactor)_`. The skill exits successfully (refactor is OPTIONAL per acceptance criterion — but `refactor.md` is still required as a record).
- Per Iron Law § 8: NO code edits before this approval. The skill MUST refuse to edit any in-tree file before the user has approved a candidate.

**Validator strategy for `refactor.md`:**
- Frontmatter has all 7 required keys + `phase == "refactor"` + `slice_id` matches dir.
- All 5 body section headers present.
- `## Smallest improvement candidates` has 1-3 numbered items; each has all six required sub-fields; each `Type` value is in the allowed set.
- `## What I considered but rejected (1-3 items)` has ≥ 1 numbered item.
- `## User approval gate` has exactly one valid `Approval status:` line.
- If `Approval status: approved|modified`, `## Applied changes` is non-empty (not just `_(none — approval pending)_`).
- If `Approval status: rejected`, `## Applied changes` body is `_(none — user declined refactor)_` exactly.

---

## Pinned: `commit` behavior (no schema — this skill produces git commits, not a markdown handoff)

`impl-slice-commit` does NOT write a `commit.md` file. It is the lifecycle terminator: it produces git commits and deletes the slice scratch dir. This is the parallel to `concept-slice/design-feature` (which produces permanent `_concept/` artifacts and deletes `_slice/concept/<id>/`).

**Pre-flight (STEP 0 of the skill):**
- Verify all three predecessor handoffs exist: `_slice/impl/<id>/{test,recap,refactor}.md`. Refuse with explicit message if any missing (Iron Law § 7).
- Verify `test.md`'s `Decision:` line is `Done`. If `Needs more work` or `Blocked`, refuse with the message: "test.md decision is `<value>`. Resolve before committing." (Hard gate — this is the gate that makes the lifecycle correct.)
- Verify `refactor.md`'s `Approval status:` is in {`approved`, `rejected`, `modified`}. If `pending`, refuse with: "refactor.md approval is still pending. Resolve refactor before committing."
- Verify a git repo is present (`.git/` exists) and we're on a feature/implementation branch (NOT on `main`). If on `main`, refuse with explicit message.

**Atomic-commit logic (STEP 1-4 of the skill):**

The skill produces ONE OR MORE atomic commits. "Atomic" means: each commit, taken alone, leaves the repo in a working state and represents one logical unit of work. The parent plan's acceptance criterion says "atomic commits" (plural) — so multi-commit splits ARE supported.

- **STEP 1: Inventory.** Run `git status --porcelain` and `git diff --stat` (working tree + index) to enumerate every file the slice touched. Compose a pre-staging proposal: a list of `(file, status)` pairs. Show it to the user.
- **STEP 2: Logical-unit decomposition.** Ask the user (standalone per § 9): "Should this slice land as one commit, or several? If several, which files belong in each commit?" Default proposal:
  - Commit 1: schema/migration files (if any) — labeled `chore(<slice_id>): migrate <table>`.
  - Commit 2: data/handler/route logic — labeled `feat(<slice_id>): <feature_title>`.
  - Commit 3: UI files — labeled `feat(<slice_id>): wire UI for <feature_title>`.
  - Commit 4: tests — labeled `test(<slice_id>): cover <feature_title>`.
  - This split is a STARTING POINT — the user can collapse to one commit, or restructure freely.
- **STEP 3: User approval (CHECKPOINT `commit_plan`).** Show the proposed commit list (commits + files in each) to the user. Per Iron Law § 8, NO `git add` runs before this approval.
- **STEP 4: Stage + commit per atomic unit.** For each unit:
  - `git add <files>`
  - `git commit -m "<message>"` where the message is:

    ```
    <type>(<slice_id>): <one-line summary>

    Slice: <slice_id>
    Feature: <feature_title>
    Feature spec: <feature_path>
    ```

    (Frontmatter fields `slice_id`, `feature_title`, `feature_path` come from `recap.md`. The skill MUST embed all three in the commit body — this is the audit trail that survives `_slice/impl/<id>/` deletion.)
  - Verify commit landed: `git log -1 --pretty=%H` returns a hash; `git status --porcelain` shows the staged files cleared.
- **STEP 5: Lifecycle-terminator delete.** Only after ALL planned commits land successfully:
  - `rm -rf _slice/impl/<slice_id>/`
  - Verify the dir is gone.
- **STEP 6: Final EMIT.** `[impl-slice-commit] completed slice_id=<id> commits=<n> deleted=_slice/impl/<id>/`.

**Iron Law § 8 enforcement:** before each `git add`, the skill prints the file list and waits for user `yes`. The CHECKPOINT in STEP 3 is the global gate; the per-commit `git add` re-prompts only if the user wants per-commit confirmation (default is "approve all once at STEP 3").

**Failure handling:**
- If any `git commit` fails (e.g., pre-commit hook blocks), STOP. Do NOT delete the scratch dir. Do NOT attempt to roll back successful prior commits — they are valid work. Tell the user: "Commit N of M failed. Slice scratch is preserved at `_slice/impl/<id>/`. Fix the failure, then re-run `impl-slice-commit`."
- The skill is RE-ENTRANT: on retry, STEP 1 inventory will show fewer staged/unstaged files (because earlier commits already landed), and STEP 2 will propose only the remaining commits.

---

## Boundary with existing `impl-slice/git-prepare/` and `impl-slice/finish/`

This is a deliberate decision point flagged for confirmation, NOT executed in this task.

| Skill | Scope | Lifetime | What it commits |
|---|---|---|---|
| `impl-slice-git-prepare` (existing) | Project-level setup | Runs ONCE per project | `chore: init repository`, `chore: start supervised implementation of <app-name>`, `chore: record git state for supervised implementation` |
| `impl-slice-commit` (NEW, this task) | Per-slice atomic commits | Runs ONCE per slice | `feat(<slice_id>): ...`, `test(<slice_id>): ...`, `chore(<slice_id>): migrate ...` |
| `impl-slice-finish` (existing) | Branch closeout | Runs ONCE per project | The MERGE commit (squash) when collapsing the implementation branch back to `main`, OR opens a PR |

**Conclusion: `impl-slice-commit` does NOT replace `git-prepare` or `finish`. It composes with them.** The lifetimes don't overlap:
- `git-prepare` runs at project START → creates the implementation branch.
- `impl-slice-commit` runs N times during the slice loop → produces N×M commits on the branch.
- `finish` runs at project END → squash-merges or PR-opens the branch.

**Open boundary question (flagged in § "Open Questions" §1):** the existing `impl-slice-finish` reads `_implementation/superpowers-plan.md` (project-level plan from the OLD impl-plan/plan-vertical schema). Per Task 2C, that file no longer exists — we now have per-slice `_slice/impl/<id>/plan.md` files. This means `impl-slice-finish` will be UPDATED in a later task to read a different "all slices done" signal (e.g., scan `_slice/impl/` and find it empty, plus check the feature catalog). **That update is OUT OF SCOPE for Task 2D** — flag for the orchestrator team. The decision: leave `finish` as-is in this task; document the inconsistency; let a future Task 2X update `finish` once the broader migration settles.

---

## Boundary with `impl-quality/test-{unit,integration,e2e}`

| Skill | Scope | When it runs | What it tests |
|---|---|---|---|
| `impl-slice-test` (NEW) | Single slice | Inside the per-slice loop, BEFORE recap/refactor/commit | Did THIS slice's manual checks + automated tests (from `plan.md ## Testing strategy`) pass? Plus usability observations (does it feel right?). |
| `impl-quality/test-unit` | Whole codebase | Between slices, or at release | Run all unit tests; report regressions across the entire repo. |
| `impl-quality/test-integration` | Whole codebase | Same | Same, integration tier. |
| `impl-quality/test-e2e` | Whole codebase | Same | Same, e2e tier (driven by `stories.json`). |

**Key distinction:** `impl-slice-test` is a SLICE-SCOPED GATE. It refuses to pass the slice forward to `recap` until manual + automated tests for the slice's plan are tagged PASS. `impl-quality/*` are CODEBASE-WIDE REGRESSION SUITES. They are different skills with different responsibilities and live in different domains. There is no overlap and no tension.

`impl-slice-test`'s SKILL.md MUST include this boundary explicitly in `## When NOT to Use` so the LLM doesn't get confused into running the whole regression suite.

---

## File Targets

All paths absolute, inside `/mnt/localvault/workBench/SKAILE/skaile-dev-matthias/ai-assets/ai-assets-skaileup`.

For each of the four skills (`recap`, `refactor`, `test`, `commit`):
- **Create:** `impl-slice/<phase>/SKILL.md`
- **Create:** `impl-slice/<phase>/validator.py`
- **Create:** `impl-slice/<phase>/tests/test_validator.py`

Plus, per skill:

- **Create:** `impl-slice/recap/references/diagram-shapes.md` — short reference (≤80 lines) with 4-5 starter ASCII diagram shapes (data flow, control flow, component tree, request lifecycle, state machine). The skill body REFERENCES this file.
- **Create:** `impl-slice/recap/examples/team-todo-comments-recap.md` — golden recap.md the validator pins against in tests.
- **Create:** `impl-slice/refactor/references/anti-addition-rules.md` — long-form expansion of the "AI defaults to adding complexity" framing (≤120 lines), with three counter-examples of additions that LOOK like refactors but aren't.
- **Create:** `impl-slice/refactor/examples/team-todo-comments-refactor.md` — golden refactor.md (with 2 candidates and 1 rejected) the validator pins against in tests.
- **Create:** `impl-slice/test/references/usability-question-pillars.md` — short reference (≤80 lines) listing the four sample usability prompts plus 6-8 alternatives.
- **Create:** `impl-slice/test/examples/team-todo-comments-test.md` — golden test.md the validator pins against in tests.
- **Create:** `impl-slice/commit/references/commit-message-format.md` — short reference (≤60 lines) pinning the commit message body format (slice_id + feature_title + feature_path).
- **Create:** `impl-slice/commit/examples/team-todo-comments-commit-plan.json` — golden commit-plan JSON the skill produces in STEP 2 (used in tests for the validator's `--manifest` mode).

**No edits** to existing files in this task. (`impl-slice-finish` and `impl-slice-git-prepare` are NOT touched.)

---

## Iron Laws — How They Apply Across the Cluster

| Law | How enforced | Where to verify |
|---|---|---|
| § 7 No artifact without prerequisites | Each SKILL.md `metadata.prerequisites.files[]` lists the predecessor's handoff with `gate: hard`; STEP 0 verifies and EXITs on miss with explicit message. `commit` lists ALL THREE handoffs as hard gates | All 4 skills |
| § 8 No overwrite without approval | `refactor` MUST NOT edit any in-tree file before the user approves a candidate (CHECKPOINT before any edit). `commit` MUST NOT `git add` before the user approves the commit-plan (CHECKPOINT in STEP 3). `test`/`recap` only write into `_slice/impl/<id>/`, where re-entry shows a diff before any change | `refactor` and `commit` primarily; `test`/`recap` lighter |
| § 9 Questions are standalone messages | MUST line near top of each SKILL.md: "MUST send each interview question / approval prompt as its own assistant message; never bundle multiple questions in one turn; wait for answer before sending next." | All 4 skills (especially `test`'s usability interview and `commit`'s commit-plan dialog) |

---

## Per-skill commit boundary

**Recommended:** four commits, one per skill, in dependency order:

1. `feat(impl-slice): add test skill (Task 2D step 1)`
2. `feat(impl-slice): add recap skill (Task 2D step 2)`
3. `feat(impl-slice): add refactor skill (Task 2D step 3)`
4. `feat(impl-slice): add commit skill (Task 2D step 4)`

Then a final task (Task 5 below) for cross-skill verification with one wrap-up commit:

5. `feat(impl-slice): finalize cluster + cross-skill verification (Task 2D complete)`

(No 6th commit needed for the `git-prepare`/`finish` boundary — this task does NOT modify those skills; the boundary is documented in this plan and the open question is filed for a future task.)

Each per-skill commit covers `SKILL.md` + `validator.py` + `tests/` + `references/` + `examples/`.

---

## Task 1: Author `impl-slice-test`

**Skill `name:` field:** `impl-slice-test`

**Skill role:** Per-slice usability gate. Runs the manual checks + automated tests defined in `plan.md ## Testing strategy`, captures the results plus usability observations from the user, and emits a Done/NeedsMoreWork/Blocked decision. Distinct from `impl-quality/test-*` (codebase-wide regression suites).

**Files:**
- Create: `impl-slice/test/SKILL.md`
- Create: `impl-slice/test/validator.py`
- Create: `impl-slice/test/tests/test_validator.py`
- Create: `impl-slice/test/references/usability-question-pillars.md`
- Create: `impl-slice/test/examples/team-todo-comments-test.md`

### READS / WRITES (pinned)

```
READS
  _slice/impl/<slice_id>/plan.md                              — required (predecessor handoff per Task 2C)
  ? _slice/impl/<slice_id>/test.md                            — re-entry mode
  ? package.json / pyproject.toml                             — optional; test runner detection

WRITES
  _slice/impl/<slice_id>/test.md                              — handoff for impl-slice-recap
```

### Handoff file

Path: `_slice/impl/<slice_id>/test.md`. Schema per § "Pinned: `test.md` Schema" above.

### Authoring steps

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p impl-slice/test/references impl-slice/test/examples impl-slice/test/tests
```

Verify: `ls impl-slice/test/` → all four sub-dirs present.

- [ ] **Step 2: Write SKILL.md frontmatter**

`metadata.prerequisites`:
- `files`:
  - `_slice/impl/{slice_id}/plan.md` (gate: hard, "Per-slice plan required — produced by `impl-plan-plan-vertical`").
- `inputs_required`:
  - `slice_id` (text, "Slice id (== feature_slug); resolves to _slice/impl/<slice_id>/plan.md").
- `inputs_optional`: none.
- `reads`: package.json (optional, for test runner detection), prior test.md (re-entry).
- `produces`: `_slice/impl/{slice_id}/test.md`.

Tags: `impl-slice`, `test`, `usability`, `per-slice`, `gate`, `feedback-loop`. Stage `alpha`. Version `1.0.0`.

`description:` MUST start with `Use when`. Suggested: `Use when a slice's implement step has finished and you need a per-slice usability gate before proceeding to recap. Runs manual checks + automated tests from plan.md ## Testing strategy, captures user usability observations, emits a Done/NeedsMoreWork/Blocked decision. NOT a project-wide regression suite — for that, use impl-quality/test-{unit,integration,e2e}.`

- [ ] **Step 3: Write SKILL.md body**

Sections in order:
- `# impl-slice-test — per-slice usability gate`.
- `## Overview` — 3-4 sentences emphasizing per-slice scope vs. codebase-wide. Quote the boundary table from § "Boundary with `impl-quality/test-*`".
- `## When to Use` and `## When NOT to Use`. The latter MUST explicitly list "running the whole project's test suite — use `impl-quality/test-*` instead."
- `ROLE` — Per-slice usability gate; runs slice tests + asks usability questions; produces a Done/NeedsMoreWork/Blocked verdict.
- `READS` / `WRITES` — copy from § "READS / WRITES (pinned)".
- `REFERENCES`: `SKILL_GRAPH.md` § 5.2, `contracts/iron_laws.md`, `impl-slice/test/references/usability-question-pillars.md`, `docs/devlog/2C-impl-plan-align-vertical.md` (for plan.md schema).
- MUST/NEVER block (EARLY per `skill_grammar.md` § Authoring tip 4):
  - `MUST  ask each usability question as its own standalone message (iron_laws § 9)`
  - `MUST  refuse to run if _slice/impl/<slice_id>/plan.md is missing (iron_laws § 7)`
  - `MUST  copy slice_id, feature_title, feature_path, tier from plan.md frontmatter unchanged`
  - `MUST  tag every Manual checks done bullet with [PASS|FAIL|SKIPPED]`
  - `MUST  tag every Automated tests run bullet with [PASS|FAIL|SKIPPED]`
  - `MUST  emit exactly one "Decision: Done|Needs more work|Blocked" line`
  - `MUST  refuse to emit Decision: Done if Outstanding issues contains any [BLOCKER]`
  - `NEVER  run the project's full regression suite — that is impl-quality/test-*`
  - `NEVER  invent manual checks or automated tests not in plan.md ## Testing strategy`
  - `NEVER  proceed past a usability question until the user has answered it`
- `INPUT` block — read from `_concept/_grounding/impl-slice-test/input.json` if present; else interview.
- `STEP 0` — read `_slice/impl/<slice_id>/plan.md`. Refuse if missing. Extract `## Testing strategy` sub-sections.
- `STEP 1` — for each bullet in plan.md `### Manual checks`, ask the user (STANDALONE) "Did this manual check pass: <bullet>?" Record `[PASS|FAIL|SKIPPED]` + 1-line note.
- `STEP 2` — for each bullet in plan.md `### Automated tests`, run the test command. Capture exit code. Record `[PASS|FAIL|SKIPPED]` + actual command + exit code.
- `STEP 3` — usability interview (4 STANDALONE questions, sourced from `references/usability-question-pillars.md`).
- `STEP 4` — compose `## Outstanding issues` from FAILed manual checks, FAILed automated tests, and usability observations the user flagged. Tag each `[BLOCKER|SHOULD-FIX|NICE-TO-HAVE]`.
- `STEP 5` — propose a Decision: Done if zero BLOCKERs; NeedsMoreWork if ≥1 BLOCKER; Blocked if a question surfaced an outside-the-slice issue. Show to user; CHECKPOINT.
- `STEP 6` — write `_slice/impl/<slice_id>/test.md`.
- `EMIT  [impl-slice-test] completed slice_id=<id> decision=<value> blockers=<n>`.
- `CHECKLIST` (6 items: plan.md read, all manual checks tagged, all automated tests tagged, usability interview done, Decision line emitted, file written).

- [ ] **Step 4: Author `references/usability-question-pillars.md`**

Contents (≤80 lines):
- The 4 sample prompts from § "Pinned: `test.md` Schema" § 4.
- 6-8 alternative phrasings (e.g., "is anything noisy?", "what would a 5-year-old not get?").
- 1 short paragraph on tone: friendly, curious, NOT leading. Don't ask "is anything broken?" — ask "what would surprise a new user?"

- [ ] **Step 5: Author `examples/team-todo-comments-test.md`**

A complete, valid `test.md` for the `team-todo-comments` feature. Reuse the example feature from 2B/2C for consistency. All 6 sections; tier = `standard-app`; ≥ 2 manual checks, ≥ 1 automated test, ≥ 1 BLOCKER → `Decision: Needs more work`. Then a SECOND example file `examples/team-todo-comments-test-done.md` showing the happy path: zero BLOCKERs, `Decision: Done`. (The validator tests both.)

- [ ] **Step 6: Author `validator.py`**

Per § "Pinned: `test.md` Schema" validator strategy. CLI: `python3 validator.py <path/to/test.md> [--plan <path/to/plan.md>]`. The optional `--plan` argument enables the cross-file check (every plan.md bullet appears tagged in test.md). Without `--plan`, only the in-file checks run.

- [ ] **Step 7: Author `tests/test_validator.py`**

Tests:
1. Golden good-case fixture (Done variant) passes.
2. Golden good-case fixture (NeedsMoreWork variant) passes.
3. Missing `Decision:` line fails.
4. `Decision: Done` with a `[BLOCKER]` in Outstanding issues fails.
5. A `## Manual checks done` bullet without `[PASS|FAIL|SKIPPED]` tag fails.
6. `phase == "recap"` in frontmatter fails.
7. `slice_id` not matching parent dir fails.
8. With `--plan`: a plan.md manual-check bullet not appearing in test.md fails.

- [ ] **Step 8: Run tests**

Run: `pytest impl-slice/test/tests/ -v`
Expected: all 8 pass.

- [ ] **Step 9: Commit Task 1**

```bash
git add impl-slice/test/
git commit -m "feat(impl-slice): add test skill (Task 2D step 1)"
```

---

## Task 2: Author `impl-slice-recap`

**Skill `name:` field:** `impl-slice-recap`

**Skill role:** Mandatory recap-and-diagram step. After the slice has passed the test gate, the recap captures what was built (in user-visible terms) and an ASCII diagram of the feature flow. The diagram is REQUIRED — skipping it = losing decision authority over multi-slice features (per SKILL_GRAPH § 5.2 line 339).

**Files:**
- Create: `impl-slice/recap/SKILL.md`
- Create: `impl-slice/recap/validator.py`
- Create: `impl-slice/recap/tests/test_validator.py`
- Create: `impl-slice/recap/references/diagram-shapes.md`
- Create: `impl-slice/recap/examples/team-todo-comments-recap.md`

### READS / WRITES (pinned)

```
READS
  _slice/impl/<slice_id>/test.md                              — required (predecessor)
  _slice/impl/<slice_id>/plan.md                              — required (read for goal recap + DoD)
  ? _slice/impl/<slice_id>/recap.md                           — re-entry mode
  ? <implementation files identified by git diff>             — optional; informs Files touched

WRITES
  _slice/impl/<slice_id>/recap.md                             — handoff for impl-slice-refactor
```

### Handoff file

Path: `_slice/impl/<slice_id>/recap.md`. Schema per § "Pinned: `recap.md` Schema" above.

### Authoring steps

- [ ] **Step 1: Create directory**

```bash
mkdir -p impl-slice/recap/references impl-slice/recap/examples impl-slice/recap/tests
```

- [ ] **Step 2: Write SKILL.md frontmatter**

`metadata.prerequisites`:
- `files`:
  - `_slice/impl/{slice_id}/test.md` (gate: hard, "Predecessor handoff — slice must have passed the per-slice test gate").
  - `_slice/impl/{slice_id}/plan.md` (gate: hard, "Plan required for goal recap + DoD comparison").
- `inputs_required`: `slice_id` (text).
- `inputs_optional`: `diagram_type` (select: `data-flow | control-flow | component-tree | state-machine | request-lifecycle`, default `data-flow`).
- `reads`: prior recap.md (re-entry).
- `produces`: `_slice/impl/{slice_id}/recap.md`.

Tags: `impl-slice`, `recap`, `diagram`, `ascii`, `mandatory`, `per-slice`, `documentation`. Stage `alpha`. Version `1.0.0`.

`description:` MUST start with `Use when`. Suggested: `Use when a slice has passed the per-slice test gate and needs the mandatory recap step. Produces a 1-3 sentence "what was built" summary, an ASCII diagram of the feature flow (mandatory), a Files-touched list, and an Outcome-vs-plan comparison. Skipping this step loses decision authority over multi-slice features.`

- [ ] **Step 3: Write SKILL.md body**

Sections in order:
- `# impl-slice-recap — mandatory recap + diagram`.
- `## Overview` — 3-4 sentences. Lead with: "The diagram is mandatory. Skipping it produces a slice that no future agent can reason about without re-reading every file."
- `## When to Use` / `## When NOT to Use`.
- `ROLE` — Per-slice recap; produces a flow diagram + comparison to plan.
- `READS` / `WRITES`.
- `REFERENCES`: `SKILL_GRAPH.md` § 5.2, `contracts/iron_laws.md`, `impl-slice/recap/references/diagram-shapes.md`, `docs/devlog/2C-impl-plan-align-vertical.md`.
- MUST/NEVER block (EARLY):
  - `MUST  produce an ASCII diagram in a fenced code block — diagram is MANDATORY (SKILL_GRAPH § 5.2)`
  - `MUST  describe what was built in user-visible terms (what the user sees / does), NOT in implementation terms (which file changed)`
  - `MUST  cover all 5 body sections; the diagram section is non-negotiable`
  - `MUST  refuse to run if _slice/impl/<slice_id>/test.md is missing (iron_laws § 7)`
  - `MUST  copy slice_id, feature_title, feature_path, tier from test.md frontmatter unchanged`
  - `MUST  ask any clarification question as its own standalone message (iron_laws § 9)`
  - `NEVER  produce a recap without an ASCII diagram (paragraph-only is not acceptable)`
  - `NEVER  describe the slice in pure-implementation terms ("modified file X to call Y")`
  - `NEVER  exceed 3 sentences in "## What was built"`
- `INPUT` block.
- `STEP 0` — read `test.md` (verify Decision: Done — refuse otherwise), `plan.md` (for goal recap + DoD).
- `STEP 1` — derive Files touched: `git diff --name-status` against the slice's base commit (use `_implementation/git-state.json` if present, else use `git log` to detect the slice start). Annotate each path with `(new|modified|deleted)`.
- `STEP 2` — draft `## What was built` (1-3 sentences, user-visible terms).
- `STEP 3` — pick a diagram type (default `data-flow`; consult `references/diagram-shapes.md` for starter shapes). Customize the starter shape: rename nodes to match this slice; add error paths if relevant; add branches if the flow has decision points.
- `STEP 4` — compose `## Outcome vs. plan` from `plan.md ## Definition of done` (mark which are now true) + diff between intended plan rows and what actually shipped.
- `STEP 5` — assemble draft recap.md in memory. Show to user; CHECKPOINT `recap_draft`.
- `STEP 6` — write `_slice/impl/<slice_id>/recap.md`.
- `EMIT  [impl-slice-recap] completed slice_id=<id> diagram_type=<type> files_touched=<n>`.
- `CHECKLIST` (6 items: test.md verified done, plan.md read, all 5 sections present, diagram present in fenced block, file written, validator green).

- [ ] **Step 4: Author `references/diagram-shapes.md`** (≤80 lines)

Contents:
- 5 starter shapes (one per `diagram_type` enum value), each with a rendered ASCII example. Reuse the data-flow shape from § "Pinned: `recap.md` Schema" § 3 as the data-flow starter. Add similar starters for control-flow (decision diamonds with `+--+` and `<>`), component-tree (indent-tree), state-machine (named states with `→`), and request-lifecycle (sequence-style with timestamps).
- 1 short paragraph on customization rules: "Rename nodes; add branches; remove unused boxes; never copy the starter verbatim."

- [ ] **Step 5: Author `examples/team-todo-comments-recap.md`**

A complete, valid `recap.md` for the `team-todo-comments` example feature. All 5 sections; ASCII diagram of the comment-creation flow (UI → handler → comments table → re-render); files-touched list with ~5 entries.

- [ ] **Step 6: Author `validator.py`**

Per § "Pinned: `recap.md` Schema" validator strategy. CLI: `python3 validator.py <path/to/recap.md>`.

- [ ] **Step 7: Author `tests/test_validator.py`**

Tests:
1. Golden fixture passes.
2. Missing `## ASCII diagram` section fails.
3. `## ASCII diagram` body without a fenced code block fails.
4. Fenced block with < 5 lines fails.
5. Fenced block with no diagram characters (`→ > | ─ +`) fails (paragraph-only fails).
6. `## What was built` with > 3 sentences emits a warning (soft check; does not fail the validator).
7. `## Files touched` with zero bullets fails.
8. `phase == "test"` in frontmatter fails.

- [ ] **Step 8: Run tests**

Run: `pytest impl-slice/recap/tests/ -v`
Expected: all 8 pass.

- [ ] **Step 9: Commit Task 2**

```bash
git add impl-slice/recap/
git commit -m "feat(impl-slice): add recap skill (Task 2D step 2)"
```

---

## Task 3: Author `impl-slice-refactor`

**Skill `name:` field:** `impl-slice-refactor`

**Skill role:** Force-simplify the slice. Proposes 1-3 SMALLEST-IMPROVEMENT candidates that preserve behavior — subtractions, simplifications, clarifications. Actively resists the LLM default of ADDING (new abstractions, new helpers, new files). Asks the user to approve before applying any code edit (Iron Law § 8). May exit with no edits applied if the user declines or no candidate qualifies.

**Files:**
- Create: `impl-slice/refactor/SKILL.md`
- Create: `impl-slice/refactor/validator.py`
- Create: `impl-slice/refactor/tests/test_validator.py`
- Create: `impl-slice/refactor/references/anti-addition-rules.md`
- Create: `impl-slice/refactor/examples/team-todo-comments-refactor.md`

### READS / WRITES (pinned)

```
READS
  _slice/impl/<slice_id>/recap.md                             — required (predecessor)
  _slice/impl/<slice_id>/plan.md                              — required (slice goal context)
  _slice/impl/<slice_id>/test.md                              — required (verify Decision: Done before refactor)
  ? <implementation files (read-only inspection until approval)>
  ? _slice/impl/<slice_id>/refactor.md                        — re-entry mode

WRITES
  _slice/impl/<slice_id>/refactor.md                          — handoff for impl-slice-commit
  <in-tree code files>                                        — ONLY after user approval (Iron Law § 8)
```

### Handoff file

Path: `_slice/impl/<slice_id>/refactor.md`. Schema per § "Pinned: `refactor.md` Schema" above.

### Authoring steps

- [ ] **Step 1: Create directory**

```bash
mkdir -p impl-slice/refactor/references impl-slice/refactor/examples impl-slice/refactor/tests
```

- [ ] **Step 2: Write SKILL.md frontmatter**

`metadata.prerequisites`:
- `files`:
  - `_slice/impl/{slice_id}/recap.md` (gate: hard).
  - `_slice/impl/{slice_id}/plan.md` (gate: hard).
  - `_slice/impl/{slice_id}/test.md` (gate: hard, "Verify slice passes test gate before refactor").
- `inputs_required`: `slice_id` (text).
- `inputs_optional`: `max_candidates` (integer, default 3, range 1-3).
- `produces`: `_slice/impl/{slice_id}/refactor.md` AND optionally in-tree code edits (only after approval).

Tags: `impl-slice`, `refactor`, `simplify`, `subtract`, `force-simpler`, `per-slice`, `anti-addition`. Stage `alpha`. Version `1.0.0`.

`description:` MUST start with `Use when`. Suggested: `Use when a slice has been recapped and you need a forced-simplification pass. Proposes 1-3 SMALLEST-IMPROVEMENT candidates that preserve behavior — only subtractions, simplifications, clarifications, never additions. Asks user to approve before any code edit. May exit with no edits if user declines or no candidate qualifies.`

- [ ] **Step 3: Write SKILL.md body — engineered to resist additions**

Sections in order:
- `# impl-slice-refactor — force-simplify`.
- `## Overview` — 4-5 sentences. Lead with: "Your default is to ADD complexity — a new helper, a new abstraction, a new file. This skill exists to RESIST that. The only refactor types this skill produces are SUBTRACT, SIMPLIFY, CLARIFY. There is no field for additions."
- `## The "smallest improvement" question` — a dedicated section that quotes the SKILL_GRAPH § 5.2 wording: `"could a new dev follow this without mental jumps?"` Then expands to 4-5 sample questions:
  - "What is the SHORTEST piece of code that, if removed, would make a future reader's life easier?"
  - "Which name lies — promising more than the function does, or hiding what it does?"
  - "Where does a flow split into two paths that could be one?"
  - "Which abstraction is paying for itself with exactly one caller?"
  - "What state is being tracked twice in different shapes?"
- `## When to Use` / `## When NOT to Use`. The latter MUST list "if you are tempted to extract a new utility — that is OUT OF SCOPE for this skill."
- `ROLE` — Per-slice force-simplify; resists additions; proposes 1-3 subtract/simplify/clarify candidates with user approval before any edit.
- `READS` / `WRITES`.
- `REFERENCES`: `SKILL_GRAPH.md` § 5.2, `contracts/iron_laws.md`, `impl-slice/refactor/references/anti-addition-rules.md`, `docs/devlog/2C-impl-plan-align-vertical.md`.
- MUST/NEVER block (EARLY — these are LOAD-BEARING):
  - `MUST  propose ONLY subtractions, simplifications, or clarifications (Type field restricted to {subtraction, simplification, clarification})`
  - `MUST  produce 1-3 candidates — exactly. Not 0, not 4. If you cannot find 1, the slice is already minimal AND you must explain why in "## What I considered but rejected"`
  - `MUST  produce ≥ 1 item in "## What I considered but rejected" — naming an addition you considered and explaining why you did NOT propose it (this surfaces the bias and forces you to dismiss it explicitly)`
  - `MUST  ask the user for approval as a standalone message before any code edit (iron_laws § 8 + § 9)`
  - `MUST  set "Approval status: pending" in the initial write; update only after user response`
  - `MUST  refuse to run if recap.md, plan.md, or test.md is missing (iron_laws § 7)`
  - `MUST  refuse to run if test.md's Decision is not "Done"`
  - `MUST  copy slice_id, feature_title, feature_path, tier from recap.md frontmatter unchanged`
  - `MUST  preserve behavior — every candidate must declare HOW behavior preservation is verified (test, manual check, "no behavior to preserve")`
  - `NEVER  propose a new file, a new abstraction, a new helper, a new module — additions are out of scope (the schema has no "addition" Type)`
  - `NEVER  edit any in-tree file before "Approval status" is "approved" or "modified"`
  - `NEVER  exceed 3 candidates`
  - `NEVER  produce 0 candidates without an explicit explanation in "## What I considered but rejected"`
  - `NEVER  rationalize: "this is technically a simplification because it makes the future cleaner" — that is the bias talking`
- `INPUT` block.
- `STEP 0` — read recap.md, plan.md, test.md. Refuse if any missing or if test.md `Decision != Done`.
- `STEP 1` — load the implementation files (Files touched from recap.md). Read-only inspection.
- `STEP 2` — generate candidate ideas. EXPLICITLY enumerate 4-6 candidate refactor ideas (some additions, some subtractions). This is a deliberate over-generation step.
- `STEP 3` — FILTER: drop every idea whose Type is "addition" (new file, new helper, new abstraction). Drop every idea that doesn't preserve behavior. Drop every idea where Risk is "high" without a clear test.
- `STEP 4` — pick the 1-3 surviving candidates with the LOWEST risk and the SMALLEST diff. Reject the rest; record at least 1 rejection in `## What I considered but rejected`.
- `STEP 5` — write `refactor.md` with `Approval status: pending`, `## Applied changes: _(none — approval pending)_`. Show to the user.
- `STEP 6` — ask the user (STANDALONE per § 9): "Which candidate(s) should I apply, if any? You can also reject all and we move on to commit."
- `STEP 7` — depending on user response:
  - User says "apply candidate N": apply the diff to in-tree files. Run the validator and any associated test from `## Behavior preservation`. Update `Approval status: approved`. Populate `## Applied changes` with the actual edits.
  - User says "modify candidate N like so...": apply the modified version. `Approval status: modified`.
  - User says "reject all": `Approval status: rejected`. `## Applied changes: _(none — user declined refactor)_`.
- `STEP 8` — re-write `refactor.md` with the updated approval status and applied changes.
- `EMIT  [impl-slice-refactor] completed slice_id=<id> approval=<status> applied=<n>`.
- `CHECKLIST` (8 items: 1-3 candidates, ≥1 rejection logged, no Type=addition, approval gate pending then resolved, no edits before approval, validator green, file written).

- [ ] **Step 4: Author `references/anti-addition-rules.md`** (≤120 lines)

Contents:
- Long-form explanation of why the LLM defaults to additions ("seeing patterns where there are none; rewarding cleverness; bias from training data toward verbose code").
- Three counter-examples that LOOK like refactors but aren't:
  1. "Extract a `useFormState` hook from one form. Reality: adds an abstraction with one caller; not a pattern yet."
  2. "Split `<UserList>` into `<UserListContainer>` and `<UserListPresentational>`. Reality: adds a layer with no concrete benefit yet."
  3. "Introduce a `validateUser()` utility. Reality: collapses 3 lines of inline validation into a function, but the function is only called from one place — net code increase."
- A short paragraph on healthy refactor types: "Subtraction (delete dead code), simplification (collapse 2 paths into 1), clarification (rename a function whose name lies)."
- Decision tree: "If you're tempted to add — STOP. Re-read the candidate from a code-deletion perspective: what could be removed instead?"

- [ ] **Step 5: Author `examples/team-todo-comments-refactor.md`**

A complete, valid `refactor.md` for the `team-todo-comments` feature. 2 candidates (e.g., "delete unused `formatComment()` helper", "rename `handle()` to `submitComment()` for clarity"); 1 rejected ("considered: extract `<CommentList>` component — rejected: only one caller, not yet a pattern"); `Approval status: approved`; `## Applied changes` with the 2 applied edits.

- [ ] **Step 6: Author `validator.py`**

Per § "Pinned: `refactor.md` Schema" validator strategy. CLI: `python3 validator.py <path/to/refactor.md>`. Strict checks:
- Frontmatter has all 7 required keys + `phase == "refactor"` + slice_id matches dir.
- All 5 body sections present.
- `## Smallest improvement candidates` has 1-3 numbered items; each has `**Type:**` line; each Type value is in {`subtraction`, `simplification`, `clarification`}; each item has all six required sub-fields (`Type`, `Files`, `Diff sketch` (optional), `Rationale`, `Risk`, `Behavior preservation`).
- `## What I considered but rejected (1-3 items)` has ≥ 1 numbered item.
- `## User approval gate` has exactly one valid `Approval status:` line.
- If `Approval status: approved|modified`, `## Applied changes` is non-empty.
- If `Approval status: rejected`, `## Applied changes` body is `_(none — user declined refactor)_` exactly.
- Hard fail on any candidate Type containing the word "addition" or "add" (anti-addition guard, even if someone tries to sneak it past the enum).

- [ ] **Step 7: Author `tests/test_validator.py`**

Tests:
1. Golden fixture (approved variant) passes.
2. Golden fixture (rejected variant) passes (ALL candidates declined; `Applied changes` shows the rejection text).
3. A refactor.md with 4 candidates fails (max 3).
4. A candidate with `Type: addition` fails.
5. A candidate missing `Behavior preservation` field fails.
6. `## What I considered but rejected (1-3 items)` empty fails.
7. `Approval status: approved` with `## Applied changes: _(none — approval pending)_` fails.
8. `Approval status: rejected` with non-matching `## Applied changes` body fails.
9. `phase == "recap"` in frontmatter fails.

- [ ] **Step 8: Run tests**

Run: `pytest impl-slice/refactor/tests/ -v`
Expected: all 9 pass.

- [ ] **Step 9: Commit Task 3**

```bash
git add impl-slice/refactor/
git commit -m "feat(impl-slice): add refactor skill (Task 2D step 3)"
```

---

## Task 4: Author `impl-slice-commit`

**Skill `name:` field:** `impl-slice-commit`

**Skill role:** Lifecycle terminator for the impl slice. Verifies all three predecessor handoffs exist + `test.md`'s Decision is Done + `refactor.md`'s approval is resolved. Stages files in user-approved logical units, lands one or more atomic git commits, and deletes `_slice/impl/<id>/` on success. Mirrors `concept-slice/design-feature` (the concept-side lifecycle terminator). Does NOT replace `impl-slice-finish` (branch closeout) or `impl-slice-git-prepare` (project setup).

**Files:**
- Create: `impl-slice/commit/SKILL.md`
- Create: `impl-slice/commit/validator.py`
- Create: `impl-slice/commit/tests/test_validator.py`
- Create: `impl-slice/commit/references/commit-message-format.md`
- Create: `impl-slice/commit/examples/team-todo-comments-commit-plan.json`

### READS / WRITES (pinned)

```
READS
  _slice/impl/<slice_id>/test.md                              — required (predecessor)
  _slice/impl/<slice_id>/recap.md                             — required (predecessor)
  _slice/impl/<slice_id>/refactor.md                          — required (predecessor)
  _slice/impl/<slice_id>/plan.md                              — required (commit message context)
  ? <git working tree>                                        — required at runtime (.git/ exists, not on main)

WRITES
  <git commits>                                               — atomic; per logical unit; user-approved file list
  (DELETES) _slice/impl/<slice_id>/                           — entire scratch dir; ONLY on success
```

### Lifecycle-terminator behavior

Per § "Pinned: `commit` behavior" above:
- All three handoffs must exist; `test.md` Decision must be Done; `refactor.md` Approval must be resolved.
- Inventory the working tree (`git status --porcelain`).
- Decompose into 1-N logical commit units; user approves the plan via CHECKPOINT.
- Stage + commit each unit. Each commit message embeds `Slice: <slice_id>`, `Feature: <feature_title>`, `Feature spec: <feature_path>`.
- ON SUCCESS: `rm -rf _slice/impl/<slice_id>/`. Verify dir is gone.
- ON FAILURE (any commit): STOP, preserve scratch, tell user to fix and re-run.

### Authoring steps

- [ ] **Step 1: Create directory**

```bash
mkdir -p impl-slice/commit/references impl-slice/commit/examples impl-slice/commit/tests
```

- [ ] **Step 2: Write SKILL.md frontmatter**

`metadata.prerequisites`:
- `files`:
  - `_slice/impl/{slice_id}/test.md` (gate: hard).
  - `_slice/impl/{slice_id}/recap.md` (gate: hard).
  - `_slice/impl/{slice_id}/refactor.md` (gate: hard).
  - `_slice/impl/{slice_id}/plan.md` (gate: hard, "Read for commit message context").
- `inputs_required`: `slice_id` (text).
- `inputs_optional`: `single_commit` (boolean, default false; if true, propose 1 commit even when multiple logical units exist).
- `produces`: git commits on the active branch; `_slice/impl/{slice_id}/` is DELETED.

Tags: `impl-slice`, `commit`, `git`, `atomic`, `lifecycle-terminator`, `per-slice`, `cleanup`. Stage `alpha`. Version `1.0.0`.

`description:` MUST start with `Use when`. Suggested: `Use when a slice has been recapped and refactored and is ready to land. Verifies all 3 predecessor handoffs (test, recap, refactor), inventories the working tree, decomposes into 1-N atomic commits with user approval, lands the commits, and deletes _slice/impl/<id>/ scratch on success. Does NOT replace impl-slice-git-prepare (project setup) or impl-slice-finish (branch closeout).`

- [ ] **Step 3: Write SKILL.md body**

Sections in order:
- `# impl-slice-commit — atomic commits + lifecycle terminator`.
- `## Overview` — 4-5 sentences. Lead with: "This is the lifecycle terminator for the impl slice. After this skill runs, `_slice/impl/<id>/` is gone forever; the truth lives in commits + permanent code." Quote the boundary table from § "Boundary with existing `impl-slice/git-prepare/` and `impl-slice/finish/`".
- `## When to Use` / `## When NOT to Use`. The latter MUST list:
  - "if you have not yet run recap or refactor — those are required prerequisites"
  - "if you want to merge the implementation branch — use `impl-slice-finish`"
  - "if you need to set up git for a new project — use `impl-slice-git-prepare`"
- `ROLE` — Per-slice atomic commits + lifecycle terminator (deletes `_slice/impl/<id>/`).
- `READS` / `WRITES`.
- `REFERENCES`: `SKILL_GRAPH.md` § 5.2, `contracts/iron_laws.md`, `impl-slice/commit/references/commit-message-format.md`, `docs/devlog/2B-concept-slice-cluster.md` (parallel terminator pattern), `docs/devlog/2C-impl-plan-align-vertical.md` (lifecycle).
- MUST/NEVER block (EARLY):
  - `MUST  refuse to run if any of test.md, recap.md, refactor.md is missing (iron_laws § 7)`
  - `MUST  refuse to run if test.md's Decision is not "Done"`
  - `MUST  refuse to run if refactor.md's Approval status is "pending"`
  - `MUST  refuse to run on the main/master branch — work happens on the implementation branch`
  - `MUST  decompose into atomic commits — each commit leaves the repo in a working state`
  - `MUST  embed slice_id, feature_title, feature_path in every commit message body (audit trail survives _slice/ deletion)`
  - `MUST  show the commit-plan to the user and obtain approval BEFORE any "git add" runs (iron_laws § 8)`
  - `MUST  ask the commit-plan question as its own standalone message (iron_laws § 9)`
  - `MUST  delete _slice/impl/<slice_id>/ ONLY after every commit lands successfully`
  - `MUST  preserve _slice/impl/<slice_id>/ if any commit fails — re-entry depends on it`
  - `NEVER  force-push or rewrite history`
  - `NEVER  use "git add ." or "git add -A" — always stage explicit file lists from the approved plan`
  - `NEVER  delete _slice/impl/<slice_id>/ if any planned commit was skipped, refused, or failed`
  - `NEVER  attempt to roll back successful prior commits if a later commit fails — they are valid work`
- `INPUT` block.
- `STEP 0` — read all 4 handoffs (`test.md`, `recap.md`, `refactor.md`, `plan.md`). Refuse on any miss. Verify `test.md` Decision = Done; `refactor.md` Approval ∈ {approved, rejected, modified}. Verify `.git/` exists; verify NOT on main/master branch (`git rev-parse --abbrev-ref HEAD`).
- `STEP 1` — inventory: run `git status --porcelain` and `git diff --stat` (working tree + index). Build a `(file, status)` list. Filter out files NOT touched by this slice (sanity check against `recap.md ## Files touched`).
- `STEP 2` — propose a logical-unit decomposition. Default: 4 commits (migrate / feat-handler / feat-ui / test). If `single_commit=true`, propose 1. Show the proposal as a JSON-ish structure to the user.
- `STEP 3` — `CHECKPOINT commit_plan` — ask user (STANDALONE): "Approve this commit plan? (yes / no / edit)". On `no`, STOP. On `edit`, prompt for changes and regenerate.
- `STEP 4` — for each unit, in order:
  - `git add <files>`
  - Build the message:
    ```
    <type>(<slice_id>): <one-line summary>

    Slice: <slice_id>
    Feature: <feature_title>
    Feature spec: <feature_path>
    ```
  - `git commit -m "<message>"`
  - Verify with `git log -1 --pretty=%H` and `git status --porcelain`. If commit fails, STOP and report.
- `STEP 5` — only if ALL commits land: `rm -rf _slice/impl/<slice_id>/`. Verify gone. Run `ls _slice/impl/<slice_id>/ 2>&1` and confirm "No such file or directory".
- `EMIT  [impl-slice-commit] completed slice_id=<id> commits=<n> deleted=_slice/impl/<id>/`.
- `CHECKLIST` (8 items: 4 handoffs read, test Done verified, refactor Approval resolved, on-non-main-branch verified, commit plan approved, all commits landed, scratch dir deleted, audit trail in commit bodies).

- [ ] **Step 4: Author `references/commit-message-format.md`** (≤60 lines)

Contents:
- The pinned commit message format (subject + body).
- Type vocabulary: `feat`, `fix`, `chore`, `test`, `docs`, `refactor`. (`refactor` here means an in-tree code refactor — distinct from the `impl-slice-refactor` skill, which is a separate phase.)
- 4 worked examples (one per default-decomposition commit type).
- A short note on the audit trail: "the slice scratch dir is gone after this skill; the commit body is the only place where slice_id + feature_title + feature_path persist."

- [ ] **Step 5: Author `examples/team-todo-comments-commit-plan.json`**

A complete, valid commit-plan JSON (the artifact STEP 2 produces in memory) for the `team-todo-comments` feature. Schema:

```json
{
  "slice_id": "team-todo-comments",
  "feature_title": "Comments on team todo items",
  "feature_path": "_concept/product-spec/features/01_collab/team-todo-comments.md",
  "commits": [
    {
      "type": "chore",
      "summary": "migrate comments table",
      "files": ["migrations/20260508_add_comments.sql"],
      "body": "Slice: team-todo-comments\nFeature: ...\nFeature spec: ..."
    },
    {
      "type": "feat",
      "summary": "comments handler + route",
      "files": ["src/handlers/comments.ts", "src/routes/comments.ts"],
      "body": "..."
    },
    {
      "type": "feat",
      "summary": "wire UI for comments",
      "files": ["src/components/CommentList.tsx", "src/components/CommentForm.tsx"],
      "body": "..."
    },
    {
      "type": "test",
      "summary": "cover comments flow",
      "files": ["src/handlers/comments.test.ts"],
      "body": "..."
    }
  ]
}
```

The validator's manifest mode pins against this shape.

- [ ] **Step 6: Author `validator.py`**

Validator scope (deterministic — does NOT actually run `git`; that's the skill body's job):

- Mode A (`python3 validator.py --plan <path/to/commit-plan.json>`):
  - JSON has `slice_id`, `feature_title`, `feature_path`, `commits` (list, ≥1).
  - Each commit has `type` ∈ {feat, fix, chore, test, docs, refactor}, `summary` (≤80 chars), `files` (non-empty list), `body` (contains `Slice:`, `Feature:`, `Feature spec:` lines).
  - The union of all `commits[].files` matches a provided expected file list (optional `--expected-files <path>`).

- Mode B (`python3 validator.py --post-commit <path/to/_slice/impl/<id>/>`):
  - Asserts the dir does NOT exist (lifecycle terminator confirmation).
  - This mode is meant to run AFTER the skill completes successfully.

- Mode C (`python3 validator.py --pre-flight <slice_id>`):
  - Reads `_slice/impl/<slice_id>/{test,recap,refactor,plan}.md`. Asserts all four exist.
  - Asserts `test.md` contains `Decision: Done`.
  - Asserts `refactor.md` contains `Approval status:` value in {approved, rejected, modified}.
  - Used by tests to verify the pre-flight gate.

- [ ] **Step 7: Author `tests/test_validator.py`**

Tests:
1. Golden commit-plan JSON passes Mode A.
2. Commit-plan with `commits: []` fails Mode A.
3. Commit with `type: "invalid"` fails Mode A.
4. Commit body missing `Slice:` line fails Mode A.
5. Mode B: a tmpdir without the slice dir passes; a tmpdir with the slice dir present fails.
6. Mode C: golden 4-handoff fixture passes; fixture with `Decision: Needs more work` fails; fixture with `Approval status: pending` fails; fixture missing one handoff fails.

- [ ] **Step 8: Run tests**

Run: `pytest impl-slice/commit/tests/ -v`
Expected: all 6 pass.

- [ ] **Step 9: Commit Task 4**

```bash
git add impl-slice/commit/
git commit -m "feat(impl-slice): add commit skill (Task 2D step 4)"
```

---

## Task 5: Cross-skill verification & finalization

- [ ] **Step 1: Tree shape**

Run: `find impl-slice -type f \( -name 'SKILL.md' -o -name 'validator.py' -o -name 'test_validator.py' \) | sort`
Expected: at least 12 NEW files (4 SKILL.md + 4 validator.py + 4 test_validator.py) on top of the pre-existing `impl-slice/{finish,git-prepare,implement}/SKILL.md`.

Run: `find impl-slice -mindepth 2 -maxdepth 2 -type d | sort`
Expected: includes the four NEW dirs (`impl-slice/recap/`, `impl-slice/refactor/`, `impl-slice/test/`, `impl-slice/commit/`) plus existing `impl-slice/{finish,git-prepare,implement,skills}/`.

- [ ] **Step 2: Frontmatter integrity (per `CONTRIBUTING.md` § Integrity Checklist)**

```bash
python3 - <<'EOF'
import yaml
expected = {
  "impl-slice/test/SKILL.md":     "impl-slice-test",
  "impl-slice/recap/SKILL.md":    "impl-slice-recap",
  "impl-slice/refactor/SKILL.md": "impl-slice-refactor",
  "impl-slice/commit/SKILL.md":   "impl-slice-commit",
}
for path, name in expected.items():
    fm = yaml.safe_load(open(path).read().split('---')[1])
    assert fm['name'] == name, (path, fm['name'])
    assert fm['description'].startswith('Use when'), path
    assert isinstance(fm['metadata']['tags'], list) and len(fm['metadata']['tags']) >= 3, path
    assert fm['metadata']['stage'] in ('alpha','beta','stable'), path
    assert 'prerequisites' in fm['metadata'], path
    assert 'reads_from' not in fm['metadata'], f"deprecated reads_from in {path}"
    assert 'writes_to' not in fm['metadata'], f"deprecated writes_to in {path}"
    assert 'user_inputs' not in fm['metadata'], f"deprecated user_inputs in {path}"
print("OK: 4/4 SKILL.md files pass integrity check")
EOF
```
Expected: `OK: 4/4 SKILL.md files pass integrity check`.

- [ ] **Step 3: All four validators green**

Run: `pytest impl-slice/test/tests/ impl-slice/recap/tests/ impl-slice/refactor/tests/ impl-slice/commit/tests/ -v`
Expected: every test in all four `tests/` dirs passes.

- [ ] **Step 4: End-to-end handoff sequence (dry, against fixtures)**

Build a fixture chain in a tmpdir that walks the full impl-slice loop:
- Place a fake `_concept/_meta/scope.yaml` (tier=standard-app) and a fake `_concept/product-spec/features/01_collab/team-todo-comments.md`.
- Place fake `_slice/impl/team-todo-comments/{brainstorm,align,plan}.md` (golden examples — sourced from Task 2C's example fixtures).
- Run `impl-slice/test/validator.py` against `examples/team-todo-comments-test.md` (after copying it into the fixture tree). Verify exit 0.
- Same for `recap.md`, `refactor.md`.
- Run `impl-slice/commit/validator.py --plan examples/team-todo-comments-commit-plan.json --pre-flight team-todo-comments` (with the fixture's slice dir populated). Verify exit 0.
- Verify the validator chain reads frontmatter consistently: `slice_id`, `feature_title`, `feature_path`, `tier` are identical across all four handoffs.

This is a deterministic check; it doesn't exercise the LLM body. It proves the deterministic baton-pass works.

- [ ] **Step 5: Iron-Laws spot-check**

Visually verify each SKILL.md body contains:
- A MUST line referencing `iron_laws § 9` (standalone questions).
- For `refactor` and `commit` only: a MUST line referencing `iron_laws § 8` (no overwrite/staging without approval) AND an explicit CHECKPOINT in the steps.
- For all four: a MUST line referencing `iron_laws § 7` (refuse if predecessor handoff missing).
- For `refactor`: explicit "no Type=addition" rule near the top of the body.
- For `commit`: explicit "delete only after all commits land" rule near the top of the body.

- [ ] **Step 6: Boundary documentation cross-check**

Verify these specific boundary markers exist:
- `impl-slice/test/SKILL.md` `## When NOT to Use` mentions `impl-quality/test-{unit,integration,e2e}` by name.
- `impl-slice/commit/SKILL.md` `## When NOT to Use` mentions both `impl-slice-finish` and `impl-slice-git-prepare` by name.
- `impl-slice/refactor/SKILL.md` `## When NOT to Use` mentions "if you are tempted to extract a new utility — that is OUT OF SCOPE for this skill."

```bash
grep -n "impl-quality/test" impl-slice/test/SKILL.md
grep -n "impl-slice-finish\|impl-slice-git-prepare" impl-slice/commit/SKILL.md
grep -n "tempted to extract" impl-slice/refactor/SKILL.md
```
Expected: each grep returns ≥ 1 match.

- [ ] **Step 7: Composition smoke check**

Run: `grep -l "impl-slice-test\|impl-slice-recap\|impl-slice-refactor\|impl-slice-commit" flows/ 2>/dev/null || echo "no flows yet (expected — wired up in later task)"`
Expected: either no matches (flows wired in a later task) or an existing flow lists them. Both acceptable here.

- [ ] **Step 8: Lifecycle-terminator behavior assertion**

Read `impl-slice/commit/SKILL.md` and verify it contains the literal string `rm -rf _slice/impl/` somewhere in STEP 5 (the lifecycle-terminator delete). This is a structural check that the deletion is explicit, not handwaved.

```bash
grep -c "rm -rf _slice/impl/" impl-slice/commit/SKILL.md
```
Expected: ≥ 1.

- [ ] **Step 9: Final commit**

```bash
git add -A impl-slice/
git commit -m "feat(impl-slice): finalize cluster + cross-skill verification (Task 2D complete)"
```

---

## Validator strategy (per skill, summarized)

| Skill | Validator scope (deterministic) | Test count |
|---|---|---|
| `impl-slice-test` | Frontmatter shape + 6 body sections + Manual/Automated bullet tags + Decision regex + cross-file `--plan` check | 8 |
| `impl-slice-recap` | Frontmatter shape + 5 body sections + ASCII diagram (fenced + ≥5 lines + diagram chars) + 1-3 sentences soft check + Files-touched bullets | 8 |
| `impl-slice-refactor` | Frontmatter shape + 5 body sections + 1-3 candidates + Type ∈ {subtract, simplify, clarify} + ≥1 rejection + Approval status state machine + applied-changes consistency + anti-addition guard | 9 |
| `impl-slice-commit` | Mode A (commit-plan JSON) + Mode B (post-commit dir-gone) + Mode C (pre-flight 4-handoff gate) | 6 |

Validators do NOT test the LLM-driven interview body or actual git operations. They test that the *handoff files* and *commit-plan* conform to the cluster's structural contract. Determinism of LLM behavior is out of scope (matches the approach in Tasks 2A/2B/2C).

---

## Definition of Done

- [ ] `impl-slice/{recap,refactor,test,commit}/SKILL.md` all exist with valid frontmatter (`name:` matching dir, `description:` starts with "Use when", `metadata.version`, `metadata.tags ≥ 3`, `metadata.stage`, `metadata.prerequisites` populated; deprecated `metadata.{user_inputs,reads_from,writes_to}` ABSENT)
- [ ] Each skill enforces Iron Law § 7 via `prerequisites.files` (hard gate on the predecessor's handoff file) AND via STEP 0 explicit refusal logic
- [ ] Each skill enforces Iron Law § 9 via a top-of-body MUST line ("each interview question is a standalone message")
- [ ] `impl-slice-refactor` enforces Iron Law § 8 via the approval CHECKPOINT before any in-tree code edit AND a hard `Type ∈ {subtraction, simplification, clarification}` enum (no addition allowed)
- [ ] `impl-slice-refactor` produces 1-3 candidates AND ≥ 1 rejected-candidate entry — both validator-enforced
- [ ] `impl-slice-commit` enforces Iron Law § 8 via the commit-plan CHECKPOINT before any `git add`
- [ ] `impl-slice-commit` deletes `_slice/impl/<slice_id>/` ONLY after every planned commit lands successfully (lifecycle terminator — mirrors `concept-slice/design-feature`)
- [ ] `impl-slice-commit` embeds `slice_id`, `feature_title`, `feature_path` in every commit message body (audit trail survives `_slice/impl/<id>/` deletion)
- [ ] `impl-slice-test`'s `## When NOT to Use` explicitly distinguishes itself from `impl-quality/test-{unit,integration,e2e}`
- [ ] `impl-slice-recap` produces a MANDATORY ASCII diagram (validator enforces fenced block + ≥5 lines + diagram chars; paragraph-only fails)
- [ ] All 4 `validator.py` files exist; all 4 `tests/test_validator.py` files exist; `pytest impl-slice/{test,recap,refactor,commit}/tests/ -v` is green
- [ ] The four skills compose: a fixture-driven dry-run produces valid test.md + recap.md + refactor.md + commit-plan.json with consistent frontmatter (slice_id, feature_title, feature_path, tier identical across all four)
- [ ] `_slice/impl/<id>/` lifecycle is documented in each skill's body (who reads, who writes, who deletes — only commit deletes)
- [ ] `slice_id` continuity rule (slice_id == feature_slug from concept) is preserved — every skill copies frontmatter from predecessor unchanged
- [ ] No edits to existing `impl-slice/{finish,git-prepare,implement}/SKILL.md` (boundary documented; updates flagged for a future task)
- [ ] All 5 commits land with `feat(impl-slice): ...` prefix on the active migration branch
- [ ] Cluster ordering pinned: `implement → test → recap → refactor → commit` (matches SKILL_GRAPH § 5.2)

---

## Open Questions / Ambiguities

1. **`impl-slice-finish` references `_implementation/superpowers-plan.md` — stale path.** The existing `impl-slice/finish/SKILL.md` (lines 17-18) reads `_implementation/superpowers-plan.md` as a hard gate. Task 2C eliminated this file in favor of per-slice `_slice/impl/<id>/plan.md`. Therefore `finish` will fail its hard gate as soon as Task 2C lands. **Out of scope for Task 2D** — flag for a future task to update `finish` to a "all `_slice/impl/` slices terminated" signal (e.g., scan `_slice/impl/` and verify it's empty + check feature catalog completion). This plan documents the inconsistency; do NOT attempt to fix `finish` here.

2. **`impl-slice-git-prepare` references `_concept/discovery/brief.md`.** This appears to still be valid in the new structure (`_concept/discovery/` is the standard discovery zone). No action required, but verify during Task 5's Step 6 that the path still resolves once the catalog is fully migrated.

3. **`impl-slice-implement` produces `_implementation/progress.json`** (lines 42-44 of the existing SKILL.md). This is a project-wide file. Is it still relevant per-slice, or should the per-slice progress live inside `_slice/impl/<id>/`? **Out of scope for Task 2D** (we don't modify `implement`). Flag for a future task on `implement` migration.

4. **Single-question-per-message enforcement.** Iron Law § 9 says questions are standalone messages. Each skill adds a MUST line, but there's no automatic check the LLM honored it (only post-hoc transcript review). The `lab/judge` skill (per SKILL_GRAPH § 8) could grade transcripts. Out of scope here.

5. **ASCII diagram rendering across MD viewers.** Some markdown viewers render `→` poorly. The validator accepts `→ > | ─ +` — the wider charset gives the LLM flexibility. If a downstream viewer strips `→`, the diagram still has structural chars. Flag as soft for now.

6. **Refactor max_candidates=1 case.** When the slice is genuinely minimal, the skill should produce exactly 1 candidate (likely a clarification rename). The schema requires 1-3, so 1 is allowed. The risk is that the AI manufactures a fake "clarification" just to fill the quota. Mitigation: the `## What I considered but rejected` section, with its mandatory ≥ 1 rejection, surfaces the reasoning. If the AI cannot articulate a real rejection, that's a smell the user should catch. Validator does NOT catch this — it's an LLM-quality concern, not a schema concern.

7. **Commit message subject-line length.** The validator caps `summary` at 80 chars. Conventional-Commits-style subject lines are typically ≤72. Open: tighten to 72? Defer to user/CI pre-commit hook. Plan accepts 80 as a soft maximum.

8. **`commit` and pre-commit hooks.** If a `pre-commit` hook (e.g., linters) blocks a commit, the skill's STEP 4 fails and STOP fires. The user must fix the hook output and re-run. The skill is RE-ENTRANT — STEP 1 inventory will show the new state. Document this in the SKILL.md `## Common Mistakes` table. (The skill MUST NOT add `--no-verify` to bypass hooks — that's a footgun.)

9. **Atomic vs. squash.** The plan adopts atomic per-logical-unit commits (default 4: chore/feat-handler/feat-ui/test). Some workflows prefer one squash commit per slice. Hence `single_commit: boolean` input. **Open question:** should the default be `false` (atomic, the more disciplined option) or `true` (single, the simpler workflow)? Plan picks `false` (atomic) as default; revisit if user feedback says otherwise.

10. **Slice-id collision.** Two slices for the same feature should never coexist. Task 2C's `_slice/impl/<id>/` lifecycle invariant says "at most one per active slice." `impl-slice-commit` deletes the dir. If a re-run is attempted (e.g., revert + redo), the slice dir won't exist; the user must re-run the upstream chain. This is by design — flag in `impl-slice-commit/SKILL.md ## Common Mistakes`.
