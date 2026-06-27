---
name: impl-slice-commit
description: "Use when a slice has been recapped and refactored and is ready to land. Verifies all 3 predecessor handoffs (test, recap, refactor), inventories the working tree, decomposes into 1-N atomic commits with user approval, lands the commits, and freezes _implementation/slices/<id>/ on success (writes index.md, keeps the dossier as documentation, removes only transient progress.json). Does NOT replace impl-slice-git-prepare (project setup) or impl-slice-git-finish (branch closeout)."
metadata:
  version: "1.0.0"
  tags:
    - impl-slice
    - commit
    - git
    - atomic
    - lifecycle-terminator
    - per-slice
    - cleanup
  stage: alpha
  artifacts:
    requires:
      - id: slice-impl-test
        gate: hard
      - id: slice-impl-recap
        gate: hard
      - id: slice-impl-refactor
        gate: hard
      - id: slice-impl-plan
        gate: hard
    produces:
      - id: slice-impl-index
  prerequisites:
    files:
      - path: "_implementation/slices/{slice_id}/test.md"
        gate: hard
        description: "Predecessor handoff — must contain Decision: Done."
      - path: "_implementation/slices/{slice_id}/recap.md"
        gate: hard
        description: "Predecessor handoff — drives commit-message context."
      - path: "_implementation/slices/{slice_id}/refactor.md"
        gate: hard
        description: "Predecessor handoff — Approval status must be approved|rejected|modified."
      - path: "_implementation/slices/{slice_id}/plan.md"
        gate: hard
        description: "Read for commit-message context (slice_id, feature_title, feature_path)."
    inputs_required:
      - id: slice_id
        label: "Slice id (== feature_slug); resolves to _implementation/slices/<slice_id>/*.md"
        type: text
        hint: "Inherited verbatim from upstream phases."
    inputs_optional:
      - id: single_commit
        label: "Collapse all changes into ONE commit (default: false → atomic per-logical-unit)"
        type: boolean
        default: false
    produces:
      - path: "<git commits on the active branch>"
        description: "1-N atomic commits per logical unit; each commit body embeds slice_id, feature_title, feature_path."
      - path: "_implementation/slices/{slice_id}/index.md"
        description: "Frozen slice dossier written on successful completion (lifecycle terminator). Folder kept as documentation; only progress.json is removed."
---

# impl-slice-commit — atomic commits + lifecycle terminator

## Overview

This is the lifecycle terminator for the impl slice. After this skill runs, the
slice's work lives in commits + permanent code, and `_implementation/slices/<slice_id>/`
is **frozen, not deleted**: the skill writes `index.md` and keeps the phase
handoffs (`brainstorm · align · plan · test · recap · refactor`) as permanent
per-feature documentation, removing only the transient `progress.json`. The skill
verifies all three predecessor handoffs, inventories the working tree, asks the
user to approve a commit-plan (1-N atomic commits), lands the commits, and freezes
the dossier on success. Mirrors `concept-slice/design-feature` (the concept-side
lifecycle terminator). (This is the Suggestion-B convention: slices are durable
documentation, not throwaway scratch.)

| Skill | Scope | Lifetime |
|---|---|---|
| `impl-slice-git-prepare` (existing) | Project-level git setup | ONCE per project at start |
| `impl-slice-commit` (this) | Per-slice atomic commits | ONCE per slice during the loop |
| `impl-slice-git-finish` (existing) | Branch closeout / merge | ONCE per project at end |

The lifetimes do not overlap: `git-prepare` runs at project start, this skill
runs N times during slice work, `finish` runs at project end.

## When to Use

- All three predecessor handoffs (`test.md`, `recap.md`, `refactor.md`) exist for the slice.
- `test.md` shows `Decision: Done`.
- `refactor.md` shows `Approval status: approved | rejected | modified` (NOT pending).
- The active branch is NOT `main` / `master`.

## When NOT to Use

- If you have not yet run recap or refactor — those are required prerequisites; run `impl-slice-recap` and `impl-slice-refactor` first.
- If you want to merge the implementation branch — use `impl-slice-git-finish`.
- If you need to set up git for a new project — use `impl-slice-git-prepare`.
- If the working tree has changes from MULTIPLE slices interleaved — separate them first; this skill commits ONE slice's work.

---

ROLE Per-slice atomic commits + lifecycle terminator (freezes `_implementation/slices/<id>/` with an index.md; keeps the dossier).

READS
  _implementation/slices/{slice_id}/test.md                              — required (predecessor)
  _implementation/slices/{slice_id}/recap.md                             — required (predecessor)
  _implementation/slices/{slice_id}/refactor.md                          — required (predecessor)
  _implementation/slices/{slice_id}/plan.md                              — required (commit-message context)
  ? <git working tree>                                        — required at runtime (.git/ exists, NOT on main)

WRITES
  <git commits>                                               — atomic; per logical unit; user-approved file list
  _implementation/slices/{slice_id}/index.md                  — frozen dossier; ONLY on success
  (FREEZES) _implementation/slices/{slice_id}/                — kept as documentation; handoffs retained, only progress.json removed

REFERENCES
  SKILL_GRAPH.md                                              — § 5.2 per-slice impl loop
  contracts/iron_laws.md                                      — § 7, § 8, § 9
  contracts/skill_grammar.md                                  — DSL keywords
  contracts/asset_frontmatter.md                              — Skill SKILL.md schema
  impl-slice/commit/references/commit-message-format.md       — commit message format pin
  docs/superpowers/plans/2B-concept-slice-cluster.md          — parallel terminator pattern (concept-slice/design-feature)
  docs/superpowers/plans/2C-impl-plan-align-vertical.md       — _implementation/slices/<id>/ lifecycle pin
  docs/superpowers/plans/2D-impl-slice-cluster.md             — § Pinned commit behavior

REQUIRES
  hard: _implementation/slices/{slice_id}/test.md
  hard: _implementation/slices/{slice_id}/recap.md
  hard: _implementation/slices/{slice_id}/refactor.md
  hard: _implementation/slices/{slice_id}/plan.md
  hard: git

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  refuse to run if any of test.md, recap.md, refactor.md is missing (iron_laws § 7)
MUST  refuse to run if test.md's Decision is not "Done"
MUST  refuse to run if refactor.md's Approval status is "pending"
MUST  refuse to run on the main/master branch — work happens on the implementation branch
MUST  decompose into atomic commits — each commit leaves the repo in a working state
MUST  embed slice_id, feature_title, feature_path in every commit message body (audit trail co-located with the kept dossier)
MUST  show the commit-plan to the user and obtain approval BEFORE any "git add" runs (iron_laws § 8)
MUST  ask the commit-plan question as its own standalone message (iron_laws § 9)
MUST  write _implementation/slices/<slice_id>/index.md ONLY after every commit lands successfully
MUST  keep _implementation/slices/<slice_id>/ and its phase handoffs — they are permanent documentation
MUST  remove ONLY the transient _implementation/slices/<slice_id>/progress.json at STEP 5 (never the handoffs)

NEVER  force-push or rewrite history
NEVER  use "git add ." or "git add -A" — always stage explicit file lists from the approved plan
NEVER  delete the slice dossier or its phase handoffs (freeze, never delete)
NEVER  write index.md if any planned commit was skipped, refused, or failed
NEVER  attempt to roll back successful prior commits if a later commit fails — they are valid work
NEVER  bypass pre-commit hooks with --no-verify

INPUT
  Read from: _concept/_grounding/impl-slice-commit/input.json
  If missing, ask the user:
  - slice_id: Slice id (required) default: <none>
  - single_commit: Collapse to one commit? (optional) default: false

# ── Workflow ───────────────────────────────────────────────────────

STEP 0: Verify predecessors and branch
  - Resolve test.md, recap.md, refactor.md, plan.md under _implementation/slices/<slice_id>/.
  - If any is missing: refuse with explicit message naming the missing file.
  - Verify test.md contains the literal line `Decision: Done`. Otherwise refuse:
    > "[impl-slice-commit] test.md decision is `<value>`. Resolve before committing."
  - Verify refactor.md contains `Approval status:` with value in
    {approved, rejected, modified}. If `pending`, refuse:
    > "[impl-slice-commit] refactor.md approval is still pending. Resolve refactor before committing."
  - Verify .git/ exists; verify NOT on main/master:
    $ git rev-parse --abbrev-ref HEAD
    Refuse on main/master with explicit message.
  - Cache slice_id, feature_title, feature_path from plan.md frontmatter
    (these go into every commit body — the audit trail).

STEP 1: Inventory the working tree
  $ git status --porcelain
  $ git diff --stat
  - Build a list of `(file, status)` pairs (status ∈ {M, A, D, R, ??}).
  - Cross-check against recap.md "## Files touched" — if a file appears in
    the working tree but not in recap.md, surface it to the user (it might
    belong to a different slice).

STEP 2: Logical-unit decomposition
  IF single_commit is true:
    - Propose ONE commit. Type = `feat`; summary = feature_title.
  ELSE:
    - Default proposal: 4 commits if all four buckets non-empty, else fewer.
      1. chore(<slice_id>): migrate <table>           — schema/migration files
      2. feat(<slice_id>): <feature_title>            — handler/route/service/data logic
      3. feat(<slice_id>): wire UI for <feature_title> — UI/component files
      4. test(<slice_id>): cover <feature_title>       — test files
    - Skip empty buckets; user can re-bucket freely.
  - Build a JSON-shaped `commit-plan`:
    ```json
    {
      "slice_id": "<slice_id>",
      "feature_title": "<copied verbatim from recap.md>",
      "feature_path": "<copied verbatim from recap.md>",
      "commits": [
        {"type": "chore|feat|fix|test|docs|refactor",
         "summary": "<≤80 chars>",
         "files": ["..."],
         "body": "Slice: <slice_id>\nFeature: <feature_title>\nFeature spec: <feature_path>"}
      ]
    }
    ```

STEP 3: User approval (CHECKPOINT commit_plan)
  CHECKPOINT commit_plan
    > "Here's the proposed commit plan for `<slice_id>` (N commits, M files).
    >  Approve? (yes / no / edit). On `no`, I stop. On `edit`, tell me which
    >  files move to which commit (or to collapse multiple commits into one)."
  Wait for response (STANDALONE message per iron_laws § 9).
  Inline MUST: NO `git add` runs before user replies `yes` (iron_laws § 8).

STEP 4: Stage + commit per atomic unit (in order)
  For each unit in the approved commit-plan:
    $ git add <files>      # explicit file list — never `.` or `-A`
    $ git commit -m "<type>(<slice_id>): <summary>

Slice: <slice_id>
Feature: <feature_title>
Feature spec: <feature_path>"
    - Verify: $ git log -1 --pretty=%H returns a hash; $ git status --porcelain
      shows the staged files cleared.
    - On failure (e.g., pre-commit hook blocks):
      - STOP. Do NOT freeze the slice (do NOT write index.md, do NOT remove progress.json).
      - Do NOT roll back successful prior commits — they are valid work.
      - Tell the user:
        > "Commit N of M failed. Slice dossier is intact at
        >  _implementation/slices/<slice_id>/. Fix the failure, then re-run impl-slice-commit."
      - Exit non-zero.

STEP 5: Lifecycle-terminator freeze
  Only after ALL planned commits land successfully. Do NOT delete the dossier —
  keep brainstorm/align/plan/test/recap/refactor in place.
  1. Write _implementation/slices/<slice_id>/index.md with this shape:
     ```
     ---
     slice_id: <slice_id>
     feature_title: <feature_title>
     feature_path: <feature_path>
     phase: frozen
     status: shipped
     commits: [<sha>, ...]
     last_updated: YYYY-MM-DD
     ---

     # Slice: <feature_title>

     Frozen impl dossier. Truth lives in the code + commits below; the phase
     handoffs are the decision record.

     ## Commits
     - <sha> <type>(<slice_id>): <summary>

     ## Feature spec
     - <feature_path>

     ## Process history (kept)
     - brainstorm.md · align.md · plan.md · test.md · recap.md · refactor.md
     ```
  2. Remove ONLY the transient resume state:
     $ rm -f _implementation/slices/<slice_id>/progress.json
  3. Verify index.md exists and its frontmatter parses; verify the handoffs are
     still present. If index.md is missing, surface the failure and exit non-zero.

EMIT  [impl-slice-commit] completed slice_id=<id> commits=<n> frozen=_implementation/slices/<id>/

CHECKLIST
  - [ ] All 4 handoffs (test.md, recap.md, refactor.md, plan.md) read
  - [ ] test.md Decision: Done verified
  - [ ] refactor.md Approval status ∈ {approved, rejected, modified}
  - [ ] Active branch is NOT main/master
  - [ ] commit-plan approved by user (CHECKPOINT commit_plan)
  - [ ] Every commit landed with `Slice:`/`Feature:`/`Feature spec:` audit trail
  - [ ] _implementation/slices/<slice_id>/index.md written; handoffs kept; progress.json removed (lifecycle freeze)
  - [ ] No force-push, no --amend across already-pushed commits

---

## Common Mistakes

| Mistake | What to do instead |
|---|---|
| Running `git add .` to stage everything | Stage explicit files from the approved commit-plan only |
| Deleting the slice dossier or its handoffs | Freeze, never delete — write index.md and keep the handoffs as documentation |
| Writing `index.md` before all commits land | Freeze ONLY after all commits in STEP 4 succeed |
| Using `--no-verify` to bypass a pre-commit hook | Fix the hook output and re-run; the skill is RE-ENTRANT |
| Rolling back successful commits when a later one fails | Leave them — they are valid work; STOP and surface the partial state |
| Committing files from another slice (interleaved working tree) | Separate the slices first; this skill commits ONE slice's work |
| Re-running after the slice was frozen | A frozen slice has an `index.md` and is already shipped — re-running is a no-op; start a new slice instead |
