# 0029 — The concept is walked top-down

**Status:** accepted

Amends [ADR 0019](0019-scoped-fact-resolution.md) ("hard gates only for machine-read formats")
and [ADR 0023](0023-two-advisory-flows.md) ("order is advisory") for four skills only:
`build-scaffold`, `build-database`, `build-plan` and `build-implement` gate on the walk.
Consistent with [ADR 0008](0008-gates-live-at-the-step-they-bind.md): the gate lives at the step
it binds. [ADR 0010](0010-no-plan-file-and-no-status-file.md) governs the build side and is
untouched: the new state file records concept-stage decisions, never build progress. Extends
[ADR 0027](0027-agents-and-levelled-decisions.md): the interview relay also holds on hosts
without the skaileup agents.

## Context

The filmkit Studio app was built in three omp sessions with this collection installed. The
intent of skaileup is a top-down walk before anything is built: the whole app's look (shell,
navigation, brand), then the data types and how each is represented, then the features, each
layer confirmed by the user. None of it happened:

- **F1** The concept was decided inside the implementation plan, then run by a subagent told to
  answer every skill's batch from that plan, with no user in the loop.
- **F2** No user decision reached the user during concept work: 0 `ask` calls, 0 `NEEDS_CONTEXT`,
  entries tagged `(user, …)` whose text came from the plan, `approved:` never asked.
- **F3** Build preceded concept; every later user prompt (Kunde switch, editor blocks, data in
  the db, logins, footer slot) was a concept decision the flow should have asked up front.
- **F4** The top-down order was not enforced: brand skipped because `03_brand/` was absent, the
  shell placed after the screens, data representation decided by an agent's design doc.
- **F5** The planning session decided a look-free architecture before any question; brand
  appeared only in an unchosen option, and the user approved an implementation plan, not a concept.
- **F6** The greenfield flow is not top-down (shell after screens) and has a single late
  Storybook round; `depth: sketch` was read as "skip mockups".
- **F7** The concept lived in `_concept/`, Storybook and the app, and the three drifted; a
  decision record against Storybook was never superseded after one was built.
- **F8** The second plan again carried silent agent decisions (magic link vs password, own Ton
  block) with 0 `ask` calls.
- **F9** skaileup's build half and its lead agent were bypassed: a generic plan → tickets →
  orchestrate pipeline ran, the relay depended on agents not installed, and gates checked
  existence only, never `approved:`.
- **F10** skaileup is a router: nothing held walk state across sessions, so each new session
  restarted from the latest prompt.
- **F11** Representation of data types has an owner (`APP-DESIGN.md § Objects`) that never ran;
  "without a user" paths let a run finish with recommendations, and entity stories waited for screens.

## Decision

**W1 — Four stages, fixed order.** `frame` → `look` → `data` → `features`. Each stage ends with
the user's explicit yes or a recorded waive; `look`, `data` and `features` each end on a
Storybook checkpoint (look: the App frame with pending destinations; data: entity stories;
features: screens, App and journeys).

**W2 — One state file.** `_concept/01_meta/walkthrough.yaml`, owner `skaileup`, node
`tree/01_meta/walkthrough.md`. It stores only the user's stage decisions (approved, waived,
reopened) and their sources. Everything else — which artifacts exist, which carry `approved:`,
which hold open markers — is computed by `skills/skaileup/scripts/walkthrough.py`, so nothing
duplicates the artifacts. ADR 0010 is untouched: the file is concept state, and the build side
still keeps no plan file and no status file.

**W3 — Build skills gate on the walk.** `build-scaffold`, `build-database`, `build-plan` and
`build-implement` carry a hard gate on `walkthrough.yaml` and run `walkthrough.py gate build`
(`build-plan` and `build-implement`: `gate feature <featureset>/<feature>`) as their first step.
This amends ADR 0019's "no hard gates" and ADR 0023's "advisory" for these four skills only;
every other skill and both flows stay advisory.

**W4 — No silent completion inside the walk.** A question the user owns is never closed with a
recommendation; a delegate returns `NEEDS_CONTEXT`; a stage cannot be approved while its
artifacts hold `[open Q` or `(proposed by` markers.

**W5 — `depth` thins, never removes.** `depth` changes how much each stage writes. A stage or
its checkpoint is skipped only by a waive backed by a decision record the user agreed to.

**W6 — Change reopens.** A request that changes an approved stage reopens it and every later
stage before any code changes; the concept is updated and re-approved, then the code follows.

**W7 — Hosts without the skaileup agents.** Where `skaileup-lead` and its delegates are not
installed, the session agent is the lead: the relay rules of `tree/protocol/delegation.md § Delegation` apply
to the generic subagents it sends, and a plan the session agent writes answers no skill's
decision batch in advance. `skaileup` writes a marked guard section into the project's agent
file so the host's own planning sees the gate.

## Options rejected

- **Gates in the flows.** Flows stay recipes (ADR 0023); a host that never loads a flow — the
  filmkit case — would skip them.
- **A status file that also tracks artifacts.** It would duplicate what `approved:` frontmatter
  and the files already say, and drift from them.
- **Global harness rules.** The guard is written per project; the host's global rules stay
  untouched.
- **One mockup round at the end.** The first artefact the user could react to came after every
  spec was written (F6).

## Consequences

- New node `tree/01_meta/walkthrough.md` with `tree/01_meta/walkthrough.schema.json`; its
  `## Format` stage table is the contract `walkthrough.py`'s `STAGES` mirrors, and a test holds
  them equal.
- `skaileup` becomes the guide: it opens the walk, walks the open stage, shows its checkpoint
  and records the user's yes; it writes the guard section into `AGENTS.md` or `CLAUDE.md`.
- The greenfield flow follows the four stages, with Storybook nodes for look and data.
- The build skills' prerequisite on `walkthrough.yaml` is `soft`, because a hard gate needs an
  upstream writer in every flow that runs the skill and `skaileup` is no flow node; the route's
  `gate` step is what stops the build, and a missing file counts as every stage open.
- The "without a user" fallbacks in `tree/APP-DESIGN.md` and `experience-interaction` become
  `NEEDS_CONTEXT`; an entry the user defers keeps its stage open.
- `demo/_concept/01_meta/walkthrough.yaml` is the worked example.
