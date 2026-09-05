# 33: `docs/examples/` is frozen against a tree that no longer exists

**Type:** task
**Blocked by:** None — 30 resolved 2026-09-05 and scoped it out deliberately

**Status:** ready

## Question

Ticket 30 swept 32 files onto ADR 0007's tree and stopped at `docs/examples/`, correctly: those
are **frozen worked examples** from ticket 03, kept to show what a ported skill looks like, and
rewriting a frozen artifact needs a reason. They now carry **14 pre-0007 paths**, and one of
them — the astro walkthrough example — **is superseded outright** by the landed
`skills/mockup-walkthrough`, which ticket 30 found is itself the better demonstration.

So the question is per-example, and the criterion is what the example still teaches that the
landed collection does not:

- **`docs/examples/concept-brief/`** — ticket 03's worked port, 289 → 80 lines. Ticket 26 already
  flagged that this draft **predates ADR 0007** and wrote the real `concept-brief` against the
  current tree. Does the before/after still earn its keep as a demonstration of the *shape*
  (which is what ticket 03 made it for), or does the landed skill demonstrate that better?
- **`docs/examples/mockup-walkthrough-astro/`** — superseded by a landed skill that does the same
  job on the right tree.
- **`docs/examples/{README,WHY}.md`** — whatever survives has to still describe it.

Three ways out, and the ticket is to pick per example and do it: **re-sweep** onto 0007 (keeps
the demonstration, costs the freeze), **delete** (the landed skill is the demonstration now), or
**keep frozen with a dated header** saying what tree it was written against and pointing at the
skill that superseded it — which is the only option that preserves *why* ticket 03 wanted a
worked example at all.

Whatever the outcome, `docs/examples/` must stop being a place where a reader can copy a path
that resolves to nothing. That is the bar, not the method.

## Not in scope

`docs/adr/*` — ticket 30 left those deliberately and was right to: an ADR is a dated record of a
decision as it was made, and sweeping its paths destroys the thing it exists to preserve. If an
ADR's paths mislead, the fix is a superseding ADR, not an edit.

## Answer

_(pending)_
