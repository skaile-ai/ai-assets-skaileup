# 0036 — build-plan and build-implement are adapters on to-tickets and implement-spec

**Status:** accepted

Amends [ADR 0006](0006-the-slice-loop-composes.md) (the slice loop), [ADR 0012](0012-foreign-skills-and-the-two-libraries.md)
(two more foreign skills, both `user-followed`) and [ADR 0027](0027-agents-and-levelled-decisions.md)
K1 (the lead composes `build-implement`). Supersedes [ADR 0010](0010-no-plan-file-and-no-status-file.md)
where it concerns slice dossiers and the trace.

## Context

The build loop restated upstream work. `build-plan` cut a frozen spec into vertical slices and
wrote one dossier per slice under `_concept/11_build/slices/<slice_id>/` (`plan.md`, a
transient `progress.yaml`, a frozen `index.md`); `build-implement` built one slice at a time,
ran `tdd` and `code-review`, committed, froze the dossier, flipped ledger rows and appended the
slice to `_concept/11_build/trace.yaml`, the feature → slice → commit → code join that
`ops-review`, `quality-release` and `quality-review` read. Upstream `to-tickets` already cuts a
spec into tracer-bullet tickets with native blocked-by edges, and `implement-spec` already
builds a ticket graph on one integration branch with an implementer subagent per ticket and a
merger, ending in a draft PR. The project's issue tracker records everything the trace and the
slice dossiers recorded, and keeps it current without a skill writing it.

## Decision

1. **A feature spec has a parent issue.** The spec's frontmatter carries `tracker: { issue: <n> }`
   in the tracker `docs/agents/issue-tracker.md` names. `build-plan` creates the issue once
   (title the feature name, label `spec`, body the spec path, a summary and the ledger path) and
   writes that one key into the spec; a rerun reuses it.
2. **`build-plan` is an adapter on `to-tickets`.** After the walk gate and a proposal gate (no
   pending entry targets the spec, its screens or `model.yaml`), it reads the installed
   `to-tickets` skill and follows it with the parent issue as its source. The tickets are
   sub-issues with native blocked-by edges, labelled `ready-for-agent`; each claims criterion
   ids, every id exactly once. It then creates the criteria ledger, each untested row naming its
   ticket (`- [ ] AC-<id> — #<ticket>`).
3. **`build-implement` is an adapter on `implement-spec`.** After the same two gates, it reads
   the installed `implement-spec` skill and follows it with the spec's parent issue: integration
   branch `spec/<featureset>-<feature>`, an implementer subagent per ticket that calls the Skill
   tool with "tdd", a merger per landed ticket, and a draft PR with `Closes #<parent>`. It
   declares `implement-spec` and `tdd`; `code-review` leaves it for `quality-review`, which
   reviews from a context that did not write the code. It writes no ledger row, no trace and no
   dossier: its `produces` holds only its proposal file, so it keeps a `## Steps` body.
4. **Issue ↔ PR links are the trace.** `_concept/11_build/slices/` and
   `_concept/11_build/trace.yaml` are removed with their nodes and schema. Readers ask the
   tracker: `gh issue view <n> --json state,closedByPullRequestsReferences`,
   `gh api repos/{owner}/{repo}/issues/<n>/sub_issues`, `gh pr list --search "<n>"`.
   `ops-review`, `quality-release`, `quality-review`, `quality-test` and `build-branch` read
   these; a leftover `trace.yaml` or `slices/` is an `ops-review` finding.
5. **The lead composes `build-implement`.** `implement-spec` starts subagents, and a delegate
   cannot, so `build-implement` runs in the lead's own context; `skaileup-builder` keeps
   `build-branch`, `build-scaffold`, `build-database` and `build-plan`. Each skill is still
   composed by exactly one agent.
6. **The loop is per spec.** `build-plan` runs once per spec and `build-implement` once per
   spec; the flows' comments say so, and their graphs are otherwise unchanged.

## Options rejected

- **Keep the trace and fill it from the tracker.** A second record of what the tracker already
  holds drifts the first time a ticket is reopened by hand.
- **Keep slice dossiers beside the tickets.** Two descriptions of one slice, one of which no
  upstream skill reads.
- **Delegate `build-implement` to `skaileup-builder`.** A delegate cannot start the implementer
  and merger subagents `implement-spec` depends on.
- **Call `to-tickets` and `implement-spec` through the Skill tool.** Both carry
  `disable-model-invocation: true` (ADR 0035).

## Consequences

- A project that builds needs a tracker with sub-issues and `gh`; without one, `ops-review` says
  its coverage half did not run.
- The ledger names tickets; `quality-review` flips its rows (the rewiring of `quality-review` on
  `code-review` follows separately).
- `CONTEXT.md` gains **Parent issue**, **Ticket** and **Integration branch**; a slice dossier
  is no longer a term.
