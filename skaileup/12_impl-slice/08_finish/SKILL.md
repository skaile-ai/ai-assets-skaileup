---
name: impl-slice-finish
description: "Use when ending an implementation branch after all per-slice work is committed. Presents four options: merge to main, create pull request, keep branch, or discard. Requires explicit confirmation for merge and discard. Refuses if any _implementation/slices/<id>/ dossier is not yet frozen (missing index.md) — those signal uncommitted slices."
metadata:
  version: '2.0.0'
  tags:
    - 'git'
    - 'branch'
    - 'merge'
    - 'pull-request'
    - 'finish'
    - 'cleanup'
  stage: beta
  artifacts:
    requires:
      - id: impl-git-state
        gate: hard
    consumes:
      - id: impl-decisions
        gate: soft
  prerequisites:
    files:
      - path: '_implementation/git-state.json'
        gate: hard
        description: 'Git state required for branch name and worktree path'
    inputs_required:
      - id: 'finish_action'
        label: 'What to do with the implementation branch?'
        type: 'select'
        options:
          - 'merge'
          - 'pull-request'
          - 'keep'
          - 'discard'
        hint: 'merge = squash-merge to main now; pull-request = open PR for review; keep = leave branch as-is; discard = delete branch and worktree'
---

# Finish Branch

## Overview

Closes out the supervised implementation run by handling the implementation branch.

Four options are presented — the user must choose one. Destructive options (merge and discard)
require typed confirmation before executing.

| Option         | When to use                                                                 |
| -------------- | --------------------------------------------------------------------------- |
| `merge`        | Implementation is verified and ready for main. Squash-merges to main.       |
| `pull-request` | Work is done but needs team review. Opens a PR with implementation summary. |
| `keep`         | Work is done but not ready to merge yet. Branch stays; worktree cleaned up. |
| `discard`      | Implementation is abandoned or superseded. Branch and worktree deleted.     |

## When to Use

- After `implement-supervised` completes and all tasks are done
- After a manual decision to close, archive, or abandon an implementation branch

---

ROLE Branch completion — presents merge / PR / keep / discard options and executes the chosen action with appropriate safeguards.

READS
\_implementation/slices/ — every `<id>/` must be FROZEN (contain index.md); any slice dir without index.md signals an uncommitted slice
\_implementation/git-state.json — branch name, git_mode, worktree path
\_implementation/decisions.md — concerns to include in PR/merge message (optional)

MUST verify every _implementation/slices/<id>/ contains index.md (is frozen) before merge or PR
MUST require typed "merge" confirmation before squash-merging to main
MUST require typed "discard" confirmation before deleting the branch
MUST clean up worktree if git_mode=worktree and action is merge, keep, or discard
NEVER squash-merge without running the full test suite first
NEVER force-push or rewrite git history
NEVER delete the branch without explicit typed confirmation

# ── Workflow ───────────────────────────────────────────────────────

STEP 1: Pre-flight checks

- Scan `_implementation/slices/` for any slice dir that is NOT frozen (missing index.md):
  $ find _implementation/slices -mindepth 1 -maxdepth 1 -type d \! -exec test -e '{}/index.md' \; -print 2>/dev/null
  IF any dirs are returned
  - STOP. Report: "N slices are not yet committed (no index.md). Run `impl-slice-commit` for each before closing the branch."
  - List the un-frozen slice dirs
  (Frozen slice dossiers — those WITH index.md — are kept as documentation and are expected to remain.)
- Read git-state.json: branch, git_mode, worktree_path

STEP 2: Run final tests

- Run full test suite
  IF any tests fail
  - STOP. Report failing tests. Do not offer merge/PR until tests pass.

STEP 3: Present options

> "Implementation is complete. All slices committed (every `_implementation/slices/<id>/` is frozen with an index.md), all tests passing.
>
> What would you like to do with the implementation branch?
>
> 1. **merge** — Squash-merge to main now. Branch is deleted after merge.
> 2. **pull-request** — Open a pull request for team review.
> 3. **keep** — Leave the branch as-is for now. Come back to merge or PR later.
> 4. **discard** — Delete the branch (and worktree if applicable). Work is lost.
>
> Choose an option:"

STEP 4: Execute chosen action

CASE merge: - Ask for typed confirmation: "Type 'merge' to confirm squash-merge to main:"
IF user did not type "merge" exactly - STOP. Do not proceed. - Build merge commit message:
```
feat: implement <app-name> — supervised build

      Tasks: N completed
      [If DONE_WITH_CONCERNS logged]: Concerns: see _implementation/decisions.md
      ```
    $ git checkout main
    $ git merge --squash implement/<app-slug>
    $ git commit -m "<merge message>"
    $ git branch -d implement/<app-slug>
    IF worktree_path exists:
      $ git worktree remove .worktrees/<app-slug>
    - Update git-state.json: status = merged
    > "Merged to main. Branch implement/<app-slug> deleted."

CASE pull-request: - Build PR body from: - Per-slice commit history on this branch (`git log --oneline main..HEAD`, grouped by `Slice:` trailer from impl-slice-commit) - decisions.md concerns (if any) - Test counts
$ gh pr create \
 --title "feat: implement <app-name>" \
 --body "<PR body>" \
 --base main \
 --head implement/<app-slug>
IF worktree_path exists:
$ git worktree remove .worktrees/<app-slug>
(worktree removed; branch stays open for PR review) > "Pull request opened: <PR URL> > The implementation branch remains open for review."

CASE keep:
IF worktree_path exists:
$ git worktree remove .worktrees/<app-slug> > "Worktree removed. Branch implement/<app-slug> kept."
ELSE > "Branch implement/<app-slug> kept. Run finish-branch again when ready." - Update git-state.json: status = kept

CASE discard: - Ask for typed confirmation: "Type 'discard' to permanently delete this branch:"
IF user did not type "discard" exactly - STOP. Do not proceed.
IF worktree_path exists:
$ git worktree remove .worktrees/<app-slug> --force
$ git checkout main
$ git branch -D implement/<app-slug> - Update git-state.json: status = discarded > "Branch implement/<app-slug> deleted. Implementation work has been discarded."

CHECKLIST

- [ ] every `_implementation/slices/<id>/` verified frozen (has index.md) before merge or PR
- [ ] Full test suite passed before merge or PR
- [ ] Typed confirmation received for merge and discard
- [ ] Worktree cleaned up if git_mode=worktree
- [ ] git-state.json updated with final status

---

## Common Mistakes

| Mistake                                                    | What to do instead                                      |
| ---------------------------------------------------------- | ------------------------------------------------------- |
| Closing the branch with uncommitted slices                 | Run `impl-slice-commit` for each un-frozen `_implementation/slices/<id>/` (no index.md) first |
| Merging without typed "merge" confirmation                 | Always require it — prevents accidental merges          |
| Forgetting to remove the worktree                          | Always clean up the worktree on merge, keep, or discard |
| Using `git branch -D` without typed "discard" confirmation | Require the typed word — lost work destroys trust       |
