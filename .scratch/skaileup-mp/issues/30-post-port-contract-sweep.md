# 30: The post-port contract sweep — what four ports found and none owned

**Type:** task
**Blocked by:** None — 23, 24, 25, 26 all resolved 2026-09-05
**Status:** ready

## Question

Nothing to decide. Four port sessions (23, 24, 25, 26) each hit the same class of defect from a
different side and none of them owned the file: a contract or a landed skill still describing
the collection as it was before ADR 0007, before ticket 24's atoms, or before a skill that this
migration deleted. Ticket 16 owned the path sweep and its commit `e63316c` **did not reach
these** — that is the finding, not a reproach: the sweep ran before the ports existed, so the
files with no reader yet had nothing to pull them into scope.

Every item below was **measured by a port session at the step it bound**, and each names its
finder.

### Contracts still on the pre-0007 tree

1. **`contracts/artifact_frontmatter.md` is wholly pre-0007** — `discovery/brief.md`,
   `experience/features/<group>/`, `_implementation/slices/`. Found independently by **23** and
   **26**.
2. **`contracts/feedback_loop.md`** — same, found by **23**.
3. **`contracts/seed_data.md`** carries `blueprint/` paths, found by **25**.

### Contracts disagreeing with each other or with a landed skill

4. **`artifact_frontmatter.md` omits `tech_stack_skill` entirely** (found by **25**) — the field
   `architecture-techstack` writes and `build-scaffold` + `build-database` read.
5. **`feature_map.json` vs `feature-map.json`** — `artifact_frontmatter.md` and
   `concept_structure.md` disagree on the separator (**25**). One is wrong; the landed
   `architecture-datamodel` picked one and that is the tiebreaker.
6. **`contracts/README.md`'s "no reader yet" rows for `golden_principles.md` and `evaluator.md`
   are now false** (**26**) — `ops-review` reads both, `quality-review` and `quality-release`
   read `evaluator.md`. The rows exist to put an unread contract on notice; leaving them stale
   defeats ticket 09's own mechanism.

### Landed skills naming things that no longer exist

7. **`skills/mockup-storybook` still *derives* three atoms that ticket 24 made 7/7**
   (`story_extension`, `component_library`, `icon_library`) **and points at `build-foundation`,
   a skill ticket 25's merge means will never exist.** Found by **24** and confirmed by **25**;
   a two-line fix each, belonging to whoever ports last, which is this ticket.
8. **`skills/mockup-walkthrough` step 1 uses unnumbered `_grounding/` and `_meta/`** (**26**).
9. **`skills/mockup-walkthrough`'s `05_features/**/*.md` glob catches
   `05_features/featuresets.md`** as a phantom manifest feature (**26**) — ticket 26 created that
   file, so the glob was correct until this week. One line.

### Also in scope

- **Re-run the sweep, do not just fix the list.** The nine items are what four sessions happened
  to trip over; the same grep that finds them (`grep -rn 'discovery/\|experience/\|_implementation/\|blueprint/' contracts/ skills/`,
  minus legitimate `10_blueprint/` and `11_build/`) will find whatever the ports did not touch.
  Report the full result, not just these nine.
- `scripts/check.py` and `scripts/test_check.py` stay green.

## Not in scope

**The `11_build/review.yaml` vs `11_build/reviews/<slug>.yaml` near-collision** — that is
ticket 31, and it is a naming decision, not a sweep. Do not rename either file here; if the
sweep touches a line mentioning one of them, leave the name as it stands.

## Answer

_(pending)_
