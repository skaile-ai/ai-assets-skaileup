# 0027 — Agents and levelled decisions

**Status:** accepted

Extends [ADR 0017](0017-the-instruction-tree-mirrors-the-artifact-tree.md): an agent holds no
procedure; the instruction stays in the tree. Extends
[ADR 0019](0019-scoped-fact-resolution.md): the lead routes by demand through `skaileup`.

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

A `SOUL.md` says how its agent works with the others and cites the tree instead of restating it;
the hand-over protocol (verbatim task, status block, evidence passes, parallel runs only on
disjoint write sets) lives once, in `tree/README.md § Delegation`. The researcher is shared: an
evidence pass another agent's run needs goes back to the lead, which sends it to the researcher.
The reviewer reviews only work it did not write and never fixes; a finding names the skill that
owns the fix, and the lead sends the fix there.

**K2 — The interview relay.** Delegates never talk to the user. A delegate resolves what tools
settle, writes its draft without `approved:` and returns `NEEDS_CONTEXT` with one decision batch;
the lead puts that batch to the user unchanged and sends the run again with the answers verbatim
and the draft path. An approval is a decision batch like any other, so `approved:` is written only
in the run that carries the user's yes. The lead never edits an artifact a delegate owns.

**K3 — Expectations come first.** `tree/01_meta/expectations.md` is the one up-front interview,
because every run the lead sends reads it: `## The result` holds what the user will judge the
product by, `## Working together` the autonomy per domain (concept, design, architecture, specs,
build, review), the review cadence, the check-ins and the language. `skaileup` writes it first
when a project has none; a user who declines gets the recommended defaults, marked `default`.
An autonomy value changes how the lead answers a delegate's batch, never what `approved:` means:
it stays the user's yes.

## Options rejected

- **One agent per skill, or per domain.** The domain prefix is the wrong seam: `experience-*` is
  split across product, designer and spec, and 31 agents leave the lead routing among names
  instead of work.
- **Delegates that ask the user.** Impossible in Claude Code and omp: a subagent has no channel to
  the user.
- **The lead does everything with every skill loaded.** That is the one window this record
  replaces, and the code still reviews itself.

## Consequences

- `scripts/check.py` gains `check_agents` (rules `agent-yaml`, `agent-name`, `agent-spec-version`,
  `agent-fields`, `agent-soul`, `agent-deprecated-field`, `agent-ref-resolves`, `agent-binding`,
  `agent-skill-composed-once`), cites the SOULs' tree citations, and holds the README `## Agents`
  table to the `agents/` directories (`readme-agent-index`, `agent-path-resolves`).
- A flow's `requires:` rejects an `agent:` ref (`requires-no-agent`): a flow node runs a skill,
  and an agent is installed through the workspace's `dependencies:`.
- The demo's `skaile.yaml` lists the eight agents.
- The forge concept template pins the collection tag and runs `skaileup-lead` as the space's agent.
- The lead applies `## Working together` to every run it sends
  (`tree/01_meta/expectations.md § Reading it`); `skaileup` 0.3.0 produces
  `_concept/01_meta/expectations.md` and runs the interview first when it is absent.
