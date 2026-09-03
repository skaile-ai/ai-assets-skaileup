# 12: Phase-boundary policy — replace the hardcoded `/clear`

**Type:** grilling
**Blocked by:** None (02 resolved)
**Status:** resolved

## Question

Ticket 02 found that mp's `PHASE-BOUNDARIES.md` is a **five-question ordered tree** for what to
do at a boundary between phases — continue / `/clear` / `handoff` / subagent / `/compact` — with
**continue** as the option to rule out first and `/compact` as the default at the bottom.
skaileup hardcodes exactly one of those five answers, `/clear`, at **seven sites**, including the
brainstorm → align hops that the tree's own worked example says should *continue*.

Clearing a context that was still relevant is the one-way mistake here: the work to rebuild it
is exactly the primary-source reading that made the context worth having.

Decide for `-mp`:

- Does the collection adopt the decision tree, and where does it live — a contract, a section of
  `CONTEXT.md`, or an absorbed skill?
- What replaces each of the seven hardcoded `/clear` sites: a per-site fixed answer chosen
  deliberately, or a pointer to the tree so the agent decides at runtime?
- Does `handoff` become a skaileup skill (ticket 02 verdict: ABSORB), and what is its role
  between the concept-side and impl-side dossiers, which already serve a similar bridging job?
- Whether the per-slice dossiers make some boundaries safe to `/clear` that otherwise wouldn't
  be — the dossier *is* the durable context, so it may justify skaileup's current default in
  the specific places it applies.

Read `research/02-mp-skills-mined.md` (branch `research/mp-skills-mined`) and
`~/.agents/skills/wayfinder/PHASE-BOUNDARIES.md` first. This blocks tickets 07 and 08 because
both design loops whose steps sit on these boundaries.

## Answer

**The tree does not port as a tree, because two of its five options do not exist in the host
that matters.** forge-concept keeps **one long-lived agent process per concept**
(`server/utils/concept-agent.ts:174`, `processManager.create`); running a flow node just sends
another prompt into that same session (`server/api/flows/nodes/[nodeId]/run.post.ts:83`). There
is no `/clear` and **no `/compact` at all** — the only affordance is a manual "Clear
conversation" trash button wired to `/api/agent/reset`
(`app/components/ConceptAiDrawer.vue:39,745`). So skaileup's "`/clear` between every phase" is
Claude-Code vocabulary, addressed to a human, describing a click that in the primary host may
never happen. `-mp` names **no slash command anywhere** — the same discipline ticket 05 forced
on `phase`, for the same reason: it is one harness's word for a thing the collection must state
host-neutrally.

**Two named cases replace the five options.** A **warm boundary** — the next phase may continue
in this context, and continuing is the default. A **cold resume** — days later, possibly another
person, where the durable artifact is the whole input and nothing carries. The slice loops'
internal hops are warm; `mockup-annotate` -> `mockup-feedback` (ticket 06's multi-day
stakeholder wait) and every dossier resume are cold. Two cases, not one and not fifteen: a
general rule over ~30 skill-to-skill hops would say nothing, and the old blanket answer was
wrong precisely because it had no second case.

**The answers are fixed per site, not derived at runtime.** mp's own file calls the tree
judgement "with taste in it"; the loop's boundaries are known at authoring time, so making every
agent re-derive them buys inconsistency and nothing else. The assignments — brainstorm ->
align **warm** (mp's own worked example: align wants the reasoning verbatim, not a summary of
it), align -> scope/plan **warm**, scope -> `design-feature` **cold** (design reads frozen
artifacts, not the argument that produced them), implement -> test -> recap **warm**, commit ->
next slice **cold**. The tree survives as the *reasoning* in **ADR 0005**, not as a runtime
instruction.

**The dumb-zone guard survives as a soft gate, and it had to.** The old rule paired the blanket
`/clear` with its justification — "no phase carries the whole slice in context (~100k)" — and
the fixed answers above **contradict it**: three phases now share one context. So a warm
boundary is a default, not a promise: continue *unless* the context is already large, in which
case fall back to cold resume. Soft per `CONTEXT.md`'s **Gate** term, and **carrying no
number** — the two hosts have different windows and mp's ~150k is a different model's figure.
The fallback is free only because the dossier exists, which is the whole reason it is safe.

**Where it lives: one section in the loop contract ticket 07 owns, plus ADR 0005.** Not a new
`contracts/session_boundary.md` — a 5-line rule with 2-3 readers fails the bar ticket 09 just
set, while the loop contract clears it already. Not `CONTEXT.md`, which is glossary-only.

### The seven sites were mostly a deletion problem

Only about three survive the prune: two are `DOMAIN.md` (all 16 die, ticket 05), two are
`agents/*/SOUL.md` (the `-mp` skeleton has no `agents/`), one is the old repo's `CLAUDE.md`.
What genuinely needs the answer is the **loop contract** (ticket 07), the **orchestrator
skill(s)**, and the **flow docs** (ticket 10) — and the last two *point at* the contract section
rather than restating it, which is the rule that let the blanket answer get copied seven times
in the first place.

### The engine writes a handoff of its own

`run.post.ts:59-75` walks `edges.filter(e => e.type === "flow")`, reads
`session.outputs[depId]`, and prepends `## Context from Prior Nodes` — label, status, summary,
files changed — at every node run, whether or not anyone cleared anything. That is a **second
handoff channel running beside the dossier**, machine-built, and the contract must name it or
the two drift. One rule: **a node's summary names the dossier file it wrote and never restates
its content.** Which is `handoff`'s non-duplication rule, applied to the one handoff the engine
writes for you.

### `handoff` does not become a skill; its two rules do

Ticket 02's ABSORB verdict is narrowed to the rules. mp's `handoff` is explicitly *only* for
portability — new harness, new directory, a colleague, a mid-phase fork — and never touches
`_concept/`; map premise 6 keeps domain-neutral skills as global installs. `-mp` absorbs the two
rules that the frozen-dossier shape actively invites phases to violate: **do not duplicate what
another artifact already holds, reference it by path**, and **name the next skills**. Both into
the dossier/handoff-frontmatter section of ticket 07's contract.

### `phase_procedures.md` dies by name, half of it survives

Ticket 09 handed it over at default-delete (34 lines, 0 in-body readers). Its three PROCEDUREs
age differently: **`emit_lifecycle` is dead** (ticket 03 killed `EMIT`; ticket 03 also found
`EMIT` is read by no code at all). **`read_predecessor` is the boundary-crossing mechanism** —
open the predecessor handoff, refuse if missing, copy `slice_id`/`feature_title` verbatim, never
re-derive — which is exactly what "cold resume" means operationally, so it folds into the same
contract section. **`draft_checkpoint_write`** (compose -> show -> approve -> write -> validate)
is a real shared behaviour with nothing boundary-specific about it: it goes to
`agent_patterns.md`, which ticket 09 already re-scoped to agent dispatch and kept on 9 in-body
readers. The file does not port; nothing is lost.

### Rejected: `boundary:` as edge data

Ticket 02 §B.1 proposed annotating each slice-loop edge with which branch it takes, "data the
flow YAMLs could carry". **No.** Ticket 15 established the engine reads `source`/`target`/`type`
and orders on `type === "flow"` alone; the runtime schema is a `looseObject`, so a `boundary:`
key would validate and be read by nobody. A key with zero readers is what ticket 09 deleted
`artifacts.yaml` over. The flow graph orders nodes; authoring judgement stays in prose.

### Vocabulary

`CONTEXT.md`'s **Session boundary** entry listed mp's four options ("continue, clear, hand
off, or dispatch a subagent") and is wrong the moment slash commands leave the vocabulary. It
is rewritten host-neutrally, and **`warm boundary`** + **`cold resume`** are added as entries,
since skills now refer to them by name.

### Handed on

- **Ticket 07** writes the contract section (and inherits `read_predecessor` +
  `draft_checkpoint_write`'s new home). It also inherits **`impl-quality-debug-handoff`**,
  flagged **lean-delete**: it is the cold-resume case with a bug-shaped argument-hint, and
  ticket 02 already found skaileup's debug pair does what `diagnosing-bugs` forbids, so the
  whole debug cluster is re-cut there — deciding one of its two skills from here would pre-empt
  that.
- **Ticket 10** gets the rule that flow docs point at the contract section rather than restate
  it, and that no flow carries boundary data.

## Note from ticket 05

**Rename this ticket's concept: `session boundary`, not `phase boundary`.** `phase` is a
machine contract with forge-concept (`data.phase` ∈ conceptualization | implementation |
review) and `CONTEXT.md` reserves it for that. mp's file is `PHASE-BOUNDARIES.md`, so the
collision is inherited, not invented — rename on the way in.

## Handed over by ticket 09

Ticket 09 left **`contracts/phase_procedures.md`** (34 lines, **0 in-body readers**, 5
citations) to this ticket rather than rule on it, since the session-boundary policy decides
whether anything still needs it.

Ticket 09's bar: a contract earns its place only if **more than one skill reads it in-body**,
or a machine does. It fails on both counts today, so **the default is deletion**. If this
ticket's boundary policy needs a written procedure shared by more than one skill, it comes
back as that — otherwise the seven hardcoded `/clear` sites are replaced without it.

Note the name: ticket 05 fixed **`phase` as a forge-concept machine contract**, so whatever
replaces this file is a **session boundary** procedure and must not be called `phase_*`.
