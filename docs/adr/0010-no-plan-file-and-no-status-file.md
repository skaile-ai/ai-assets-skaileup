# 0010 — The build side keeps no plan file and no status file

**Status:** accepted

## Context

The old collection's build half was governed by `_implementation/PLANS.md` beside
`progress.yaml`, `decisions.md` and `git-state.yaml`. `contracts/plans.md` described `PLANS.md`
as *"a **lean scope + phase plan**, not a status tracker and not a decision log"*, answering two
questions only: what is in scope for this session, and what are the phases, in order.

The file was handed to this decision carrying **nine in-body readers**. The count did not
survive inspection — the same inflation ADR 0004 found for `frontmatter.md` (86 references, 13
real readers):

| reader | what it actually takes |
|---|---|
| `impl-build-scaffold` | **creates** it — Scope, Source Artifacts, ordered Phases |
| `impl-build-foundation` | nothing — a parenthetical saying *"PLANS.md carries no checkboxes"* |
| `impl-build-infrastructure` | nothing — a checklist row saying *"PLANS.md carries no status"* |
| `impl-plan-plan-vertical` | nothing — an ownership fence, *"owned by a different skill"* |
| `impl-slice-git-prepare` | **existence only**, to detect a resume |
| `concept-brief` | a `## Raw Description` section |
| `ops-review` | status, as a **drift check on duplicated status** |
| `ops-add-feature` | writes an implementation-backlog note |
| `ops-project-review` | **a different file** — the multi-product umbrella `PLANS.md`, out of scope |

So: three readers mention it only to disclaim it, one is a different artifact, one tests
existence. Of what remains, **order is covered exactly** — the contract's Phases list
(1 scaffold · 2 foundation · 3 infrastructure · 4 migrate→seed · 5 slice loop · 6 e2e→deploy)
is `impl-build-setup.flow.yaml` written out node-for-node, and the flow graph is a live machine
contract (ADR 0001) while the prose list is not. **Status is duplication by construction**, and
`ops-review`'s PLAN-DRIFT check exists *only* because the duplication does.

The escape hatch the old skills reached for does not exist either. Three of them say status
lives in `progress.yaml` — but **ADR 0007 gives `11_build/` exactly two entries**,
`slices/<slice_id>/` and `decisions.md`. A project-level `progress.yaml` has no home in the
tree, and ADR 0006's `build-implement` already deletes the per-slice one as transient.

The residue, after removing status and order, is **three sites and all three are scope**:
`scaffold`'s Scope paragraph plus its Source Artifacts pointer list, `concept-brief`'s
`## Raw Description`, and `ops-add-feature`'s backlog note. Two facts weaken even that.
`## Raw Description` **is not in `contracts/plans.md`'s schema at all** — the one genuinely
non-status, non-order reader was reading an undocumented section — and ADR 0002's vocabulary
already reclassified user-supplied text as an **answer**, which belongs in `onboarding.yaml`.

## Decision

**Neither `PLANS.md` nor a project-level `progress.yaml` ports.** `11_build/` stays exactly as
ADR 0007 drew it: no twelfth top-level entry, no new root file.

Each of the three functions is answered by something that already exists:

- **Order** is the flow graph. It is machine-read, it is validated, and it cannot drift from
  itself.
- **Completion** is git plus the engine's own per-node execution record
  (`flowExecution.model.json`), which is written whether or not a skill remembers to.
- **Scope** is the feature spec's `## Scope` section for one feature, and
  `10_blueprint/decisions.md` for anything cross-feature — the writer ADR 0007's tree gained
  from the rejected-scope ruling.

Consequently:

- **Source Artifacts is recomputed, never stored.** It was an inventory of files that exist;
  a listing beats a list.
- **`## Raw Description` lands in `02_grounding/onboarding/onboarding.yaml`** as an answer.
- **`ops-add-feature`'s backlog note** is the `ops` domain's problem, not the build side's.
- **`ops-review`'s PLAN-DRIFT entropy check disappears** with the duplication that caused it,
  along with its two `references/` gardening steps.

## Consequences

- **A build pipeline with no plan file and no status file will read as an omission to anyone
  opening `11_build/` cold.** That is the whole reason this record exists: the absence is
  deliberate and this is where to look.
- **Resume works differently.** `impl-slice-git-prepare` detected a resume by testing whether
  `PLANS.md` existed; `git branch`, `git worktree list` and the slice dossier carry that now
  (ADR 0006 already dropped `git-state.yaml` on the same argument).
- **Nothing renders a human-readable plan of the whole build.** The flow graph is the plan, and
  reading it means reading YAML or the host's flow view. If that turns out to matter, the fix is
  a rendering of the graph, not a second file that has to be kept in step with it.
- `contracts/plans.md` was never in this repo — ADR 0006's "delete" was a no-port, and this
  record makes the artifact's death match the contract's.
