# 31: `review.yaml` and `reviews/` are one letter apart and mean different things

**Type:** grilling
**Blocked by:** None — 23 and 26 both resolved 2026-09-05
**Status:** ready

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

_(pending)_
