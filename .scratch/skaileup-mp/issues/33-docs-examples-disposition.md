# 33: `docs/examples/` is frozen against a tree that no longer exists

**Type:** task
**Blocked by:** None — 30 resolved 2026-09-05 and scoped it out deliberately

**Status:** resolved

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

**Both ports deleted; `WHY.md` kept with a dated header. Resolved 2026-09-05.**

The three options were re-sweep / delete / freeze-with-header, and the disposition splits
because the two ports and the write-up are three different artifacts, not one.

### `docs/examples/mockup-walkthrough-astro/` — **deleted**

Superseded outright, and measurably so. `references/scaffold/` is **byte-identical** to
`skills/mockup-walkthrough/references/astro/scaffold/` (`diff -r` is empty);
`references/specs-json.md` differs from the landed copy in **exactly ten lines, all of them
the pre-0007 paths**; and the port's prose — "What is different about Astro", the three
astro-only consequences, the init/update mode detection, the load-bearing config section —
survives sharpened in `references/astro/RENDERER.md`. Freezing it would have preserved
nothing except ten of the thirteen stale paths.

### `docs/examples/concept-brief/` — **deleted**

The ticket allowed that a before/after showing ADR 0003's shape might earn its keep even with
stale paths. It does not, for a reason that only shows up on reading the directory: **there is
no "before" in this repo.** The 289-line source lives in the old collection; `docs/examples/`
held two *after* halves and nothing else. So the pair a reader could actually read was never
there — the only before/after in `-mp` is `WHY.md`'s tables.

Against that, the port is a strictly worse copy of a skill that landed. `skills/concept-brief/SKILL.md`
is the same skill in the same shape at 69 lines, written by ticket 26 against the current tree,
and covered by `scripts/check.py` — which globs `skills/*/SKILL.md` and `contracts/*.md` and
**never looks at `docs/`**. A stale SKILL.md under `docs/` is a body of skill prose with no CI
behind it; that is how it drifted this far unnoticed.

And its drift runs past paths, which is what settled it against a dated header. Beyond the two
`_grounding/` hits the grep catches, the port hands off to `research`, `design-brand-visual` and
`product-spec-features` — **three skill names, none of which exist**; the landed collection has
`concept-research`, `design-brand` and `spec-feature`. It also writes
`{ "complexity", "complexity_rationale" }` on a `small`/`standard`/`complex` scale, vocabulary
ticket 10 retired along with `tier`. A header dating the paths would leave a reader free to copy
a dead skill name or a retired scope field out of a file explicitly kept as a model of good
practice. Nothing in it is evidence `WHY.md` does not already carry.

(One of the ticket's fourteen counted hits was a false positive: `_concept/01_meta/scope.yaml`
matched on `_meta/` and is a live 0007 path.)

### `docs/examples/WHY.md` — **kept, dated header**

This is the thing ADR 0003 wanted a worked example *for*, and the one artifact the landed
collection cannot reproduce. It holds the before/after measurements (289 → 80, 1,133 → 110),
the collection-wide 44%-mechanically-removable table, the per-section boilerplate counts across
88 skills — and the constraint-transformation table, eight `MUST` / `NEVER` lines shown becoming
positive statements at the step they bind. That table is the only readable record of *how* the
shape change was made rather than what it produced, and it is what a skill author needs that a
finished skill cannot show. A landed skill demonstrates the after; only this demonstrates the move.

Its header names the date, names the superseded tree by its directories, states that the port
files are gone, and points at both landed successors, so a reader meets the live shape before any
stale vocabulary below. Two dead pointers were repaired and nothing else: `TEMPLATE.md` →
`../skill-template.md`, and the astro displaced-content list now says its `references/*` entries
live under `skills/mockup-walkthrough/references/astro/`. Measurements and findings are untouched.
Old skill names inside *quoted port prose* were left as quotations.

### `docs/examples/README.md` — **deleted**

Its whole content was the two-port table and a pointer at `WHY.md`. With one file left in the
directory, an index pointing at that file is a no-op. Root `README.md`'s "Writing a skill"
paragraph absorbed what was still true and now points at a landed skill first, `WHY.md` second.
ADR 0003's `../examples/` and root README's `docs/examples/WHY.md` both still resolve.

### Verification

`grep -rn "discovery/\|experience/\|_implementation/\|blueprint/\|_grounding/\|_meta/" docs/examples/`
returns **one line**: the header's own naming of the superseded tree ("the artifact tree that
preceded ADR 0007 — the one with `_concept/discovery/`, `experience/`, `blueprint/` and
`_grounding/`"), which is the sentence telling a reader those paths are dead. `scripts/check.py`
→ `29 skill(s) · 4 flow(s) · 0 error(s)`, exit 0; `scripts/test_check.py` → 31 passed. Every
relative link in `docs/examples/` and root `README.md` resolves.

### Handed off, not fixed here

`skills/mockup-walkthrough/references/{astro,static-html}/RENDERER.md` both open on
`_concept/mockup-walkthrough/<renderer>/` while their own `SKILL.md` (lines 23, 40, 78) and the
feedback cluster use 0007's `_concept/09_mockup/walkthrough/<renderer>/`. Two pre-0007 paths ticket
30 missed, in landed skills, in the first sentence a renderer-branch agent reads. Left untouched
per this session's scope — `skills/` is not editable here.
