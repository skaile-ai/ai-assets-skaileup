---
name: impl-slice-commit
description: "Use when a slice has been recapped and refactored and is ready to land. Verifies all 3 predecessor handoffs (test, recap, refactor), inventories the working tree, decomposes into 1-N atomic commits with user approval, lands the commits, and deletes _slice/impl/<id>/ scratch on success. Does NOT replace impl-slice-git-prepare (project setup) or impl-slice-finish (branch closeout)."
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
  prerequisites:
    files:
      - path: "_slice/impl/{slice_id}/test.md"
        gate: hard
        description: "Predecessor handoff — must contain Decision: Done."
      - path: "_slice/impl/{slice_id}/recap.md"
        gate: hard
        description: "Predecessor handoff — drives commit-message context."
      - path: "_slice/impl/{slice_id}/refactor.md"
        gate: hard
        description: "Predecessor handoff — Approval status must be approved|rejected|modified."
      - path: "_slice/impl/{slice_id}/plan.md"
        gate: hard
        description: "Read for commit-message context (slice_id, feature_title, feature_path)."
    inputs_required:
      - id: slice_id
        label: "Slice id (== feature_slug); resolves to _slice/impl/<slice_id>/*.md"
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
      - path: "_slice/impl/{slice_id}/"
        description: "DELETED on successful completion (lifecycle terminator)."
---

# impl-slice-commit — atomic commits + lifecycle terminator

## Overview

This is the lifecycle terminator for the impl slice. After this skill runs,
`_slice/impl/<slice_id>/` is gone forever; the truth lives in commits +
permanent code. The skill verifies all three predecessor handoffs, inventories
the working tree, asks the user to approve a commit-plan (1-N atomic commits),
lands the commits, and deletes the scratch dir on success. Mirrors
`concept-slice/design-feature` (the concept-side lifecycle terminator).

| Skill | Scope | Lifetime |
|---|---|---|
| `impl-slice-git-prepare` (existing) | Project-level git setup | ONCE per project at start |
| `impl-slice-commit` (this) | Per-slice atomic commits | ONCE per slice during the loop |
| `impl-slice-finish` (existing) | Branch closeout / merge | ONCE per project at end |

The lifetimes do not overlap: `git-prepare` runs at project start, this skill
runs N times during slice work, `finish` runs at project end.

## When to Use

- All three predecessor handoffs (`test.md`, `recap.md`, `refactor.md`) exist for the slice.
- `test.md` shows `Decision: Done`.
- `refactor.md` shows `Approval status: approved | rejected | modified` (NOT pending).
- The active branch is NOT `main` / `master`.

## When NOT to Use

- If you have not yet run recap or refactor — those are required prerequisites; run `impl-slice-recap` and `impl-slice-refactor` first.
- If you want to merge the implementation branch — use `impl-slice-finish`.
- If you need to set up git for a new project — use `impl-slice-git-prepare`.
- If the working tree has changes from MULTIPLE slices interleaved — separate them first; this skill commits ONE slice's work.

---

ROLE Per-slice atomic commits + lifecycle terminator (deletes `_slice/impl/<id>/`).

READS
  _slice/impl/{slice_id}/test.md                              — required (predecessor)
  _slice/impl/{slice_id}/recap.md                             — required (predecessor)
  _slice/impl/{slice_id}/refactor.md                          — required (predecessor)
  _slice/impl/{slice_id}/plan.md                              — required (commit-message context)
  ? <git working tree>                                        — required at runtime (.git/ exists, NOT on main)

WRITES
  <git commits>                                               — atomic; per logical unit; user-approved file list
  (DELETES) _slice/impl/{slice_id}/                           — entire scratch dir; ONLY on success

REFERENCES
  SKILL_GRAPH.md                                              — § 5.2 per-slice impl loop
  contracts/iron_laws.md                                      — § 7, § 8, § 9
  contracts/skill_grammar.md                                  — DSL keywords
  contracts/asset_frontmatter.md                              — Skill SKILL.md schema
  impl-slice/commit/references/commit-message-format.md       — commit message format pin
  docs/superpowers/plans/2B-concept-slice-cluster.md          — parallel terminator pattern (concept-slice/design-feature)
  docs/superpowers/plans/2C-impl-plan-align-vertical.md       — _slice/impl/<id>/ lifecycle pin
  docs/superpowers/plans/2D-impl-slice-cluster.md             — § Pinned commit behavior

REQUIRES
  hard: _slice/impl/{slice_id}/test.md
  hard: _slice/impl/{slice_id}/recap.md
  hard: _slice/impl/{slice_id}/refactor.md
  hard: _slice/impl/{slice_id}/plan.md
  hard: git

# Constraints (placed early per skill_grammar.md § Authoring tip 4)

MUST  refuse to run if any of test.md, recap.md, refactor.md is missing (iron_laws § 7)
MUST  refuse to run if test.md's Decision is not "Done"
MUST  refuse to run if refactor.md's Approval status is "pending"
MUST  refuse to run on the main/master branch — work happens on the implementation branch
MUST  decompose into atomic commits — each commit leaves the repo in a working state
MUST  embed slice_id, feature_title, feature_path in every commit message body (audit trail survives _slice/ deletion)
MUST  show the commit-plan to the user and obtain approval BEFORE any "git add" runs (iron_laws § 8)
MUST  ask the commit-plan question as its own standalone message (iron_laws § 9)
MUST  delete _slice/impl/<slice_id>/ ONLY after every commit lands successfully
MUST  preserve _slice/impl/<slice_id>/ if any commit fails — re-entry depends on it
MUST  use `rm -rf _slice/impl/<slice_id>/` to delete the scratch dir at STEP 5

NEVER  force-push or rewrite history
NEVER  use "git add ." or "git add -A" — always stage explicit file lists from the approved plan
NEVER  delete _slice/impl/<slice_id>/ if any planned commit was skipped, refused, or failed
NEVER  attempt to roll back successful prior commits if a later commit fails — they are valid work
NEVER  bypass pre-commit hooks with --no-verify

INPUT
  Read from: _concept/_grounding/impl-slice-commit/input.json
  If missing, ask the user:
  - slice_id: Slice id (required) default: <none>
  - single_commit: Collapse to one commit? (optional) default: false

# ── Workflow ───────────────────────────────────────────────────────

STEP 0: Verify predecessors and branch
  - Resolve test.md, recap.md, refactor.md, plan.md under _slice/impl/<slice_id>/.
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
      - STOP. Do NOT delete the scratch dir.
      - Do NOT roll back successful prior commits — they are valid work.
      - Tell the user:
        > "Commit N of M failed. Slice scratch is preserved at
        >  _slice/impl/<slice_id>/. Fix the failure, then re-run impl-slice-commit."
      - Exit non-zero.

STEP 5: Lifecycle-terminator delete
  Only after ALL planned commits land successfully:
    $ rm -rf _slice/impl/<slice_id>/
  Verify: $ ls _slice/impl/<slice_id>/ 2>&1
  Expected output: "No such file or directory".
  If the dir still exists, surface the failure and exit non-zero — do NOT
  retry implicitly.

EMIT  [impl-slice-commit] completed slice_id=<id> commits=<n> deleted=_slice/impl/<id>/

CHECKLIST
  - [ ] All 4 handoffs (test.md, recap.md, refactor.md, plan.md) read
  - [ ] test.md Decision: Done verified
  - [ ] refactor.md Approval status ∈ {approved, rejected, modified}
  - [ ] Active branch is NOT main/master
  - [ ] commit-plan approved by user (CHECKPOINT commit_plan)
  - [ ] Every commit landed with `Slice:`/`Feature:`/`Feature spec:` audit trail
  - [ ] _slice/impl/<slice_id>/ deleted (lifecycle terminator)
  - [ ] No force-push, no --amend across already-pushed commits

---

## Common Mistakes

| Mistake | What to do instead |
|---|---|
| Running `git add .` to stage everything | Stage explicit files from the approved commit-plan only |
| Deleting `_slice/impl/<slice_id>/` before all commits land | Delete ONLY after all commits in STEP 4 succeed |
| Using `--no-verify` to bypass a pre-commit hook | Fix the hook output and re-run; the skill is RE-ENTRANT |
| Rolling back successful commits when a later one fails | Leave them — they are valid work; STOP and surface the partial state |
| Committing files from another slice (interleaved working tree) | Separate the slices first; this skill commits ONE slice's work |
| Re-running after the scratch dir was deleted | The scratch dir is gone after success — re-running requires re-running the upstream chain |
