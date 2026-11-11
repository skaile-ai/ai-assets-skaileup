# 0027 — Agents and levelled decisions

**Status:** accepted; K1 amended 2026-11-05 (the delegates keep their own names, no `as:` alias); K7 amended by [0031](0031-proposals-are-files-per-run.md) (`concept-brief` is the roster's sole owner; `spec-feature` proposes its roster moves); K4 and K5 amended by [0032](0032-one-decision-log-under-docs-adr.md) (a record is a file under `docs/adr/`, cited by slug `adr:<slug>`; levels, kinds and patterns unchanged); K1 amended by [0036](0036-build-adapters-on-to-tickets-and-implement-spec.md) (the lead composes `build-implement`, which `skaileup-builder` no longer does); K1 and K5 amended by [0037](0037-parallel-specs-serialise-at-four-points.md) (several specs run at once and serialise at four points)

Extends [ADR 0017](0017-the-instruction-tree-mirrors-the-artifact-tree.md): an agent holds no
procedure; the instruction stays in the tree. Extends
[ADR 0019](0019-scoped-fact-resolution.md): the lead routes by demand through `skaileup`. Amends
[ADR 0022](0022-shared-artifact-contracts-and-proposed-entries.md): the record gains level and
kind, and the roster takes proposals.

## Context

The collection's 31 skills ran in one session window: every skill body, every node it cited and
the whole conversation shared one context, and the session that wrote the code was the one that
reviewed it. Spec 0.2 of `@skaile/workspaces` agents offers a way out: a composed agent with
`binding: delegate` becomes a native subagent of the harness (Claude Code, omp), which the lead
hands a task to and which runs in a fresh context. Such a subagent cannot ask the user anything;
only the session's own agent can.

The user also asked for an expectations interview: what they will judge the result by, and how
much the agents decide on their own in each domain.

## Decision

**K1 — Eight agents; every skill belongs to one.** `skaileup-lead` is the session's agent. It
composes `skaileup`, the router, and seven delegates under `as:` aliases with
`binding: delegate`; each of the other 30 skills is composed by exactly one delegate:

| delegate (`as`) | skills |
|---|---|
| researcher | concept-research, concept-reverse |
| product | concept-onboard, concept-brief, concept-glossary, experience-journeys |
| designer | design-brand, experience-interaction, experience-screen, experience-shell, mockup-storybook, mockup-feedback |
| architect | architecture-datamodel, architecture-techstack, architecture-system |
| spec | spec-feature, experience-behaviors |
| builder | build-scaffold, build-database, build-plan, build-implement, build-branch |
| reviewer | quality-standards, quality-test, quality-e2e, quality-review, quality-design, quality-interaction, quality-release, ops-review |

**K1 amended 2026-11-05 ([#3](https://github.com/skaile-ai/ai-assets-skaileup/issues/3)).** The
lead composes the seven delegates under their own names (`skaileup-researcher` …
`skaileup-reviewer`), without `as:`. The install renders a delegate twice when it carries an
alias: once as the lead's sub-agent under the alias, once under its own name as a dependency.
A workspace then listed 15 agents instead of 8. Without the alias both renders write one file.
The table above keeps the short names as roles; the lead's `SOUL.md` names the agents.

A `SOUL.md` says how its agent works with the others and cites the tree instead of restating it;
the hand-over protocol (verbatim task, status block, evidence passes, parallel runs only on
disjoint write sets) lives once, in `tree/protocol/delegation.md § Delegation`. The researcher is shared: an
evidence pass another agent's run needs goes back to the lead, which sends it to the researcher.
The reviewer reviews only work it did not write and never fixes; a finding names the skill that
owns the fix, and the lead sends the fix there.

**K2 — The interview relay.** Delegates never talk to the user. A delegate resolves what tools
settle, keeps its draft where its route keeps work in progress (or returns it in the status block
when its node writes nothing before the yes) and returns `NEEDS_CONTEXT` with one decision batch.
The lead answers the batch per the domain's autonomy (K3): under `user decides` it puts the batch
to the user unchanged. It sends the run again with the answers verbatim and the draft. A skill run
or evidence pass that another agent owns goes back to the lead the same way, never to the user,
and the lead sends it to that agent. An approval is a decision batch like any other, so
`approved:` is written only in the run that carries the user's yes. The lead never edits an
artifact a delegate owns.

**K3 — Expectations come first.** `tree/01_meta/expectations.md` is the one up-front interview,
because every run the lead sends reads it: `## The result` holds what the user will judge the
product by, `## Working together` the autonomy per domain (concept, design, architecture, specs,
build, review), the review cadence, the check-ins and the language. `skaileup` writes it first
when a project has none; a user who declines gets the recommended defaults, marked `default`.
An autonomy value changes how the lead answers a delegate's batch, never what `approved:` means:
it stays the user's yes.

**K4 — A decision record has a level.** Each record says how far it reaches: `product`,
`featureset <slug>` or `feature <featureset>/<feature>`
(`tree/docs/adr/README.md § Levels`). A skill reads the records from the top down before
asking, and a question a binding record answers is not asked. A lower choice never overrides a
higher record: it goes to the user, and when accepted it becomes a new record at the higher level
that supersedes the old one. The levels live in the one log, not in a second file.

**K5 — A pattern is a decision record.** A record of `Kind: pattern` generalises what two or more
features share into one rule, with an `Applies when` sentence a later feature is matched
against; each feature that follows it lists its id in `follows:`, and in the build it is one
shared module.

**K6 — The similarity check precedes the grill.** Before it grills, `spec-feature` compares a new
feature with every spec, every idea in the roster and the `Applies when` of every `pattern` record,
on the entities, actions, screens and floorplans they share
(`tree/05_features/[featureset]/[feature].md § Writing it`, step 2). Each match goes to the user
with three options: reuse the existing feature, generalise the shared part into a `pattern`
record both specs follow, or keep them separate with a reason. The choice and its reason are
recorded in the dossier's `## Similar features`, so the next comparison does not raise it again.

**K7 — Ideas live in the roster.** A candidate feature nobody has specified is a row of
`## Ideas` in `_concept/05_features/featuresets.md` (`tree/05_features/featuresets.md § Ideas`).
`concept-brief` co-owns the roster and writes the first ideas, approved with the brief and goals;
`spec-feature` moves a row into its featureset's table when it specifies it, or under `## Cut`
when the user declines it, and a DEFER that names an unspecified feature adds an idea.
`experience-journeys` and `concept-research` propose ideas.

## Options rejected

- **One agent per skill, or per domain.** The domain prefix is the wrong seam: `experience-*` is
  split across product, designer and spec, and 31 agents leave the lead routing among names
  instead of work.
- **Delegates that ask the user.** Impossible in Claude Code and omp: a subagent has no channel to
  the user.
- **The lead does everything with every skill loaded.** That is the one window this record
  replaces, and the code still reviews itself.
- **A separate decision-tree file, or one file per level.** The drift ADR 0022 removed.
- **A separate ideas file.** A second list beside `## Cut`.
- **Patterns as their own artifact.** Collides with `02_grounding/research/patterns.md`, and a
  chosen pattern is a decision.

## Consequences

- `scripts/check.py` gains `check_agents` (rules `agent-yaml`, `agent-name`, `agent-spec-version`,
  `agent-fields`, `agent-soul`, `agent-deprecated-field`, `agent-ref-resolves`, `agent-binding`,
  `agent-alias`, `agent-skill-composed-once`), cites the SOULs' tree citations, and holds the
  README `## Agents` table to the `agents/` directories (`readme-agent-index`, `agent-path-resolves`).
- A flow's `requires:` rejects an `agent:` ref (`requires-no-agent`): a flow node runs a skill,
  and an agent is installed through the workspace's `dependencies:`.
- The demo's `skaile.yaml` lists the eight agents.
- The companion change in skaile-forge (branch `feat/concept-lead-agent`) pins the collection tag
  in the concept template and runs `skaileup-lead` as the space's agent.
- The lead applies `## Working together` to every run it sends
  (`tree/01_meta/expectations.md § Reading it`); `skaileup` 0.3.0 produces
  `_concept/01_meta/expectations.md` and runs the interview first when it is absent.
- Records older than the level and kind fields read as `product`/`decision`; they are not edited.
- `concept-brief` produces `_concept/05_features/featuresets.md` and
  `_concept/10_blueprint/decisions.md` and is an owner of the decisions node, because every owner
  of a node that takes proposals records the decisions it declines. Per
  `host:node-done-from-produces`, forge marks `concept-brief` done only once `decisions.md` exists.
