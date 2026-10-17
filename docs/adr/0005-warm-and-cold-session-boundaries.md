# 0005 — Two session boundaries, warm and cold, named without slash commands

**Status:** accepted

## Context

The old collection stated one answer at seven sites: "`/clear` between every phase", justified
by a dumb-zone guard ("no phase carries the whole slice in context, ~100k").

`ask-matt/PHASE-BOUNDARIES.md` offers a five-question ordered tree instead — Continue, `/clear`,
`/handoff`, Subagent, `/compact` — with **Continue** ruled out first because it "costs nothing
and loses nothing", and it names the cost of getting it wrong as one-way: clear a *relevant*
context and the **why** behind the work does not come back. By that tree, two of the old sites
were wrong: brainstorm → align is the standard *continue*, because align wants the reasoning
verbatim rather than a summary of it.

Two facts about the hosts decide the shape of the answer:

- **forge-concept has no `/clear` and no `/compact`.** It keeps one long-lived agent process per
  concept (`server/utils/concept-agent.ts:174`); running a flow node sends another prompt into
  that same session (`server/api/flows/nodes/[nodeId]/run.post.ts:83`). The only affordance is a
  manual "Clear conversation" button (`app/components/ConceptAiDrawer.vue:39,745`). The old
  instruction described a click that host may never make.
- **forge-concept writes a handoff of its own.** `run.post.ts:59-75` walks
  `edges.filter(e => e.type === "flow")`, reads `session.outputs[depId]`, and prepends
  `## Context from Prior Nodes` — label, status, summary, files changed — at every node run.

## Decision

**Two named cases, and no slash command in the vocabulary.**

- **Warm boundary** — the next skill may continue in this context; continuing is the default.
- **Cold resume** — nothing carries; the durable artifact is the whole input.

**The answer is fixed per boundary, chosen at authoring time.** The tree is judgement "with
taste in it"; the loops' boundaries are known when the flow is written, so an agent re-deriving
them each run buys inconsistency. brainstorm → align **warm** · align → scope/plan **warm** ·
scope → design-feature **cold** · implement → test → recap **warm** · commit → next slice
**cold** · annotate → feedback **cold**.

**The dumb-zone guard survives as a soft gate.** A warm boundary is a default, not a promise:
continue unless the context is already large, then fall back to cold resume. It carries **no
number** — two hosts, two windows, and the tree's ~150k is a different model's figure.

**One statement, referenced not restated.** The rule lives in one section of the slice-loop
contract; orchestrator skills and flow docs point at it.

**The engine's channel gets the same non-duplication rule as the dossier:** a node's summary
names the dossier file it wrote and never restates its content.

## Consequences

- The blanket `/clear` is gone, and with it the claim that no phase carries a slice in context.
  Three concept phases now share one context by default, which is the point.
- `handoff` does not become a skill here — it is for portability (new harness, directory,
  colleague), never touches `_concept/`, and stays a global install. Its two rules are absorbed.
- `phase_procedures.md` does not port. `emit_lifecycle` is dead with `EMIT` (ADR 0003);
  `read_predecessor` folds into the boundary section, because it *is* cold resume made
  operational; `draft_checkpoint_write` moves to `agent_patterns.md`.
- A `boundary:` key on flow edges was rejected: the engine reads `type` alone and the runtime
  schema is loose, so the key would validate and be read by nobody (ADR 0004's rule for data).
- Any skill that assumes it holds its predecessor's reasoning must say which case it is written
  for. A skill written for a warm boundary that runs cold reads an artifact that has to stand
  alone — so cold-resume artifacts carry the burden, not the prose around them.
