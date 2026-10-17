---
name: build-branch
description: "Use when implementation work needs somewhere to live or somewhere to go — opens the build branch and optional worktree before the first slice, and merges, PRs, keeps or discards it after the last. Triggers on 'start implementing', 'set up the branch', 'finish the branch', 'merge the work'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
    produces: []
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: hard }
---

# build-branch

The bookend around a run of slices: it opens the branch the slices are committed to, and it
closes it. Nothing between the two ends is its business: `build-implement` commits and this
skill never does. Most steps are plain git; two rules are its own, each stated at the step it
binds: no close while a slice is unlanded (step 5), and no merge or discard without the word
typed back (step 7).

Read `tree/README.md` once per session. The app slug comes from `tree/brief.md`; slice
dossiers are `tree/11_build/slices/README.md`'s.

## Steps

1. **Read which end this is from git, not from the user.** No branch matching
   `build/<app-slug>` (the slug from `brief.md`) means open. The branch checked out with
   commits on it means close. Both readings possible (the branch exists and no slice has
   landed) is a resume: say which branch you found and continue on it.

### Opening

2. **Start from a clean tree.** `git status --porcelain` empty, or stop and say what is
   uncommitted: a branch cut over someone's work carries it along invisibly. Initialize the
   repo with a `.gitignore` first if there is none.
3. **Create `build/<app-slug>`** and give it an empty initial commit, so the branch has a base
   to diff and revert against before any slice touches it.
4. **Offer a worktree.** `git worktree add .worktrees/<app-slug> build/<app-slug>` keeps the
   build checkout beside the main one, which is worth it when the user wants to run or read
   `main` while a slice is in flight and is overhead otherwise. Add `.worktrees/` to
   `.gitignore`; a worktree is local and belongs to nobody else.

### Closing

5. **Rule one: close only when every slice landed.** Any directory under
   `_concept/11_build/slices/` without an `index.md` is a slice whose commits never happened
   (`tree/11_build/slices/README.md`): name them and stop, because closing the branch is how
   that work gets lost. Frozen dossiers stay; they are the documentation.
6. **Run the full suite** and stop on a failure. Merging or opening a PR on red asks somebody
   else to discover it.
7. **Offer the four endings and let the user choose one.** **merge** squash-merges to the base
   branch and deletes the branch; **pull-request** opens a PR with the slice commits and their
   feature specs in the body and leaves the branch for review; **keep** leaves everything as it
   is; **discard** deletes the branch and its work. **Rule two: merge and discard each need the
   word typed back** before anything runs, since they are the two that cannot be undone from
   here. The chosen ending is a git state, and git is its only record.
8. **Resolve conflicts with `resolving-merge-conflicts`** if the merge hits any. Both sides of
   a conflict here are deliberate work: one is a landed slice with a spec behind it, and that
   spec is the intent the resolution preserves.
9. **Remove the worktree** on every ending, and report the branch's final state: merged and
   deleted, open with a PR URL, kept, or discarded.

**Done when** the branch exists and is checked out (opening), or the user's chosen ending has
run and the worktree is gone (closing).
