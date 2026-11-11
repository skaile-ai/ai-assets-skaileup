---
name: build-branch
description: "Use when implementation work needs somewhere to live or somewhere to go — opens the build branch and optional worktree before the first spec is built, and merges, PRs, keeps or discards it after the last. Triggers on 'start implementing', 'set up the branch', 'finish the branch', 'merge the work'."
version: "0.1.0"
metadata:
  requires:
    - contract:@skaile-ai/shared-contracts
  artifacts:
    requires:
      - { id: brief }
      - { id: features }
    produces:
      - { id: proposals, path: "_concept/proposals/<date>-build-branch-<scope>.yaml" }
  prerequisites:
    files:
      - { path: "_concept/brief.md", gate: soft }
      - { path: "_concept/05_features", gate: soft, min_entries: 1 }
---

# build-branch

The bookend around a run of specs: it opens the branch each spec's integration branch is cut
from and merged back into, and it closes it. Nothing between the two ends is its business:
`build-implement` builds and this skill never commits a feature. Most steps are plain git; two
rules are its own, each stated at the step it binds: no close while a spec is unlanded (step 5),
and no merge or discard without the word typed back (step 7).

Read `tree/protocol/running.md` once per session. The app slug is a fact to resolve, not a file to demand (`tree/protocol/running.md § How a skill runs`, rule 1): `_concept/brief.md` carries the app name (format: `tree/brief.md`); without it take the project's package name or directory name, and ask only when neither gives one. A
spec's parent issue is its frontmatter `tracker.issue` (`tree/05_features/[featureset]/[feature].md § Format`).

## Steps

1. **Read which end this is from git, not from the user.** No branch matching
   `build/<app-slug>` (the slug resolved above) means open. The branch checked out with
   commits on it means close. Both readings possible (the branch exists and no spec has
   landed) is a resume: say which branch you found and continue on it.

### Opening

2. **Start from a clean tree.** `git status --porcelain` empty, or stop and say what is
   uncommitted: a branch cut over someone's work carries it along invisibly. Initialize the
   repo with a `.gitignore` first if there is none.
3. **Create `build/<app-slug>`** and give it an empty initial commit, so the branch has a base
   to diff and revert against before any spec touches it.
4. **Offer a worktree.** `git worktree add .worktrees/<app-slug> build/<app-slug>` keeps the
   build checkout beside the main one, which is worth it when the user wants to run or read
   `main` while a spec is in flight and is overhead otherwise. Add `.worktrees/` to
   `.gitignore`; a worktree is local and belongs to nobody else.

### Closing

5. **Rule one: close only when every spec landed.** For every spec with a `tracker.issue`,
   `gh api repos/{owner}/{repo}/issues/<n>/sub_issues` lists its tickets and
   `gh pr list --search "<n>" --json number,state,headRefName` its pull request from
   `spec/<featureset>-<feature>`. An open ticket, or a pull request not yet merged into this
   branch, is a spec whose work never landed: name them and stop, because closing the branch is
   how that work gets lost.
6. **Run the full suite** and stop on a failure. Merging or opening a PR on red asks somebody
   else to discover it.
7. **Offer the four endings and let the user choose one.** **merge** squash-merges to the base
   branch and deletes the branch; **pull-request** opens a PR with the merged spec PRs and the
   parent issues they close in the body and leaves the branch for review; **keep** leaves everything as it
   is; **discard** deletes the branch and its work. **Rule two: merge and discard each need the
   word typed back** before anything runs, since they are the two that cannot be undone from
   here. The chosen ending is a git state, and git is its only record.
8. **Resolve conflicts with `resolving-merge-conflicts`** if the merge hits any. Both sides of
   a conflict here are deliberate work: one is a landed spec with tickets behind it, and that
   spec is the intent the resolution preserves.
9. **Remove the worktree** on every ending, and report the branch's final state: merged and
   deleted, open with a PR URL, kept, or discarded.

A choice either end makes that passes the three-test gate (a base branch other than the
default, history rewritten on purpose) is a decision record in the run's proposal file
(`tree/docs/adr/README.md § Writing it`: target `docs/adr/`, anchor `adr:<slug>`); the
ending itself is a git state and takes none.

**Done when** the branch exists and is checked out (opening), or the user's chosen ending has
run and the worktree is gone (closing).
