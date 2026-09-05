# 08: Concept-side consolidation

**Type:** grilling
**Blocked by:** None (04, 12 resolved)
**Status:** ready

## Question

The concept half is 21 skills across four domains, and it's the half the user said should
"mainly stay the same" — so the question is pruning and clarity, not restructuring.

- `01_concept/`: `brief` · `goals` · `comparable` · `grounding/{onboard,research,seeds}`
- `02_design/`: `brand-visual` · `brand-voice` · `inspiration`
- `03_experience/`: `journeys` · `behaviors` · `screens` · `screens-technical` · `components`
- `04_product-spec/`: `features`

Decide:

- Which survive as skills vs. become `depth`/`optional` parameters of a neighbour.
  (`goals` and `comparable` are already described as optional passes over what `brief`
  writes lightly — is that two extra skills or two flags?)
- `screens` vs. `screens-technical` vs. `components` — three skills writing into the same
  `experience/screens/` tree. One skill, or three?
- Where the absorbed `research` skill lands relative to `grounding/research`.
- Whether `brand-voice` and `inspiration` earn their own skills.
- How `features` and the featureset grouping are named after ticket 04.
- What the concept-side `_concept/` output tree looks like once domains are renamed — this
  is what `artifacts.yaml` encodes, so changes here ripple into ticket 09.

## Answer

_(pending)_

## Note from ticket 07

Ticket 07 moved the per-feature concept loop into one skill, **`spec-feature`**, and that
skill **writes screen specs** — `_concept/experience/features/<group>/<slug>.md` *and*
`_concept/experience/screens/<slug>/<screen>.md`, as `design-feature` does today. So the
`screens` question in this ticket is no longer "one skill or three" in isolation:

- **`experience-screens` now has to justify itself against `spec-feature`.** Ticket 07's
  ruling is that it covers screens *not* reached by a feature loop — the whole-app pass. If
  that pass has no real user, `experience-screens` collapses into `spec-feature` here rather
  than surviving as a second writer into the same tree.
  **Corrected 2026-09-05 (brief 08, re-verified) — that test is already passed, so do not
  re-run it here.** `experience-screens` is the **sole writer of `00_layout/shell.md`**
  (`03_screens/SKILL.md:151` *"MUST write 00_layout/shell.md before any individual screen
  specs"*, `:205` `OUTPUT …/shell.md`) and the **sole concept-side writer of the `elements:`
  block** — the only `elements:` writer across `01_`–`04_` and `08_`. `design-feature` is a
  **reader**: its single mention omits `layout` when shell.md is absent
  (`04_design-feature/SKILL.md:255`). Eleven skills read `shell.md`, including both surviving
  renderers and `build-foundation`. A cross-feature app shell is **structurally unproducible by
  a per-feature loop**, so the whole-app pass has a real user and `experience-screens` does not
  collapse. What is still open is therefore the *boundary*, not the survival:
  **absorb-with-a-shell-mode vs survive-with-one-directory-shape** — and whichever shape wins
  also settles `<NN_group>/` vs flat featuresets, since `screens/` mirrors `features/`.
- `screens-technical` and `components` write into the same tree and inherit the same test.

Also settled by ticket 07 and not open here: the concept-side working directory is
**`_concept/dossiers/<feature_slug>/`** (ticket 05 made `slice` impl-only), one file, frozen
by `spec-feature`. And `grilling` is a global install called by name — no skill in `-mp`
re-teaches the interview, which is what collapsed four grill-shaped skills to zero.
