# 31: `review.yaml` and `reviews/` are one letter apart and mean different things

**Type:** grilling
**Blocked by:** None — 23 and 26 both resolved 2026-09-05
**Status:** resolved

## Question

Two tickets placed two different artifacts one letter apart, and **neither saw the other**:

- **`11_build/review.yaml`** — ticket 21, written by `ops-review`: the whole-project verdict,
  score, and findings over the *concept tree and build coverage*.
- **`11_build/reviews/<feature_slug>.yaml`** — ticket 17, written by `quality-review`: the
  per-feature *code review*, `approved` / `changes-requested`, whose findings are code defects.

Ticket 21 resolved before ticket 17's note could reach it and vice versa; ticket 26 found the
collision only once both had landed. Both files now exist in `-mp` and both writers are ported.

The two are genuinely different artifacts, so this is not a merge — it is a **naming** question,
and the reason it is a ticket rather than a sweep item is that the wrong answer is cheap to type
and expensive later: a human reading `11_build/` sees a file and a directory that look like
singular and plural of one thing, and a skill author writing a path from memory will get it
wrong in the direction that silently reads nothing.

Constraints that already bind whichever way this goes:

- **The host reads one of them.** `review-coverage.ts` walks the per-feature reviews directory
  and accepts the verdict tokens `approved` / `changes-requested` / `pending`. Ticket 23 already
  recorded that its path is a **second** host change beyond the ADR 0007 prefix — the host walks
  `_implementation/review/`, *singular*. So the per-feature side is the one with a live host
  constraint, and the register entry moves with whatever this ticket decides.
- **ADR 0007 owns the tree.** Whatever the names become, they are `11_build/`-rooted.
- Both writers are landed skills (`ops-review` at 107 lines, `quality-review` at 89), so a
  rename is an edit to two skill bodies plus `contracts/concept_structure.md`.

The decision is what the two artifacts are *called* such that neither can be mistaken for the
other's plural — and, secondarily, whether the whole-project verdict belongs under `11_build/`
at all, given it grades the concept tree as much as the build.

## Answer

**The whole-project verdict stops being a file.** `11_build/review.yaml` is deleted from the
tree; `11_build/reviews/<feature_slug>.yaml` keeps its name unchanged. The collision is
resolved by removing one side, not by renaming either.

The asymmetry that decided it was measured, not argued:

- **`review.yaml` had zero readers.** Not forge-concept, not any `-mp` skill, not a flow's
  `requires:`. `ops-review` wrote it and nothing consumed it — and it wrote it *after* the
  report (`:99-105`), which is what the user actually acts on.
- **`reviews/` has two.** `quality-release:38` in-collection, and the host's
  `review-coverage.ts:131`.
- **`reviews/` is also the idiomatic one.** Every per-thing collection in the tree is a
  plural directory (`slices/`, `acceptance-criteria/`, `reviews/`). The singular file
  sharing that stem was the only one of its kind.

This map has killed unread machine artifacts three times before (ticket 09 → `artifacts.yaml`,
ticket 10 → `data.writes`, ticket 32 recording the fallout), and the verdict fails the same
test for a sharper reason: it is **recomputed, not decided**. A code review is a judgment that
cannot be re-derived, so it earns a file. A tree audit is a reading of the tree as it stands
this minute, so a copy on disk can only be a stale one. `trace.yaml` is equally derived and
survives only because the host reads it.

**Nothing durable replaces it.** A dated one-line echo into `11_build/decisions.md` was
considered and refused: `decisions.md` records build-time decisions, and a derived verdict
filed there is the same category error in a different file. A reader who wants the verdict
runs the skill again.

**The tree gets an explicit rule, gated.** `concept_structure.md`'s Naming section now
carries: *no two siblings may differ only by singular and plural*, with this pair as the
worked example. `check.py:check_tree_names` enforces it against the contract's own fenced
tree — the same block `_fenced_tree` already parses, now walked with depth so siblings are
comparable. Verified both ways: re-adding `review.yaml` produces
`` `_concept/11_build` declares `review` and `reviews`, which differ only by plural ``;
removing it returns 29 skills · 4 flows · 0 errors. The gate reads the contract, not skill
prose — skill-body paths are already gated for existence, and a second grep over prose buys
noise.

**`-mp` does not bend to the host's spelling.** Measured while resolving: the host reads
`_implementation/review/` (**singular**) *and* `_implementation/acceptance_criteria`
(**underscore**), while the tree's convention is uniformly hyphenated
(`design-inspiration.md`, `colors-fonts.md`, `behavioral-patterns.md`) — so on both counts
the host is the outlier. Conforming would have shrunk the successor host change to a pure
prefix swap at the price of importing a singular directory-of-many and an underscore that
contradicts the tree's own naming rule, in the one ticket that exists to call that wrong. The
register entry grows instead, from one path edit to three, all in two files.

### Landed

- `contracts/concept_structure.md` — `review.yaml` removed from the `11_build/` tree; the
  anti-plural rule added under `## Naming`.
- `skills/ops-review/SKILL.md` (109 lines) — intro and step 12 rewritten: it writes one file,
  not two, and states why the review half writes none. `**Done when**` follows.
- `scripts/check.py` — `check_tree_names` + `TREE_NODE_RE`, `_tree_entry_stem`,
  `_is_plural_of`; wired into `run()`.
