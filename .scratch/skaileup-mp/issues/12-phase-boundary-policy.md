# 12: Phase-boundary policy — replace the hardcoded `/clear`

**Type:** grilling
**Blocked by:** None (02 resolved)
**Status:** ready

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

_(pending)_

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
