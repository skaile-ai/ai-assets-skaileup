# 14: Port the mockup domain — write the 4 skills

**Type:** task
**Blocked by:** 11 (06 resolved)
**Status:** ready

## Question

Nothing to decide — ticket 06 settled the shape, this writes it. Graduated from the map's
fog ("the port itself, per domain") once 06 landed. Needs the repo skeleton (ticket 11) to
have somewhere to land.

Write four skills into `skills/`, each `SKILL.md` under the 140-line ceiling from ticket 03,
dir name == `name:` exactly (ticket 04):

- **`mockup-walkthrough`** — shared pipeline in the body; `references/static-html/` and
  `references/astro/` carry the scaffolds (the astro port on branch
  `prototype/skill-body-shape` is the starting point, at 110 lines). Renderer resolved from
  `onboarding.yaml`, falling back to the tier default (mvp/simple → static-html,
  standard/complex → astro).
- **`mockup-storybook`** — composes components → pages → journeys as steps, the way mp's
  `implement` composes rather than restates. Port the four story-authoring skills' content;
  do **not** port `01_setup` (goes to `build-foundation`, ticket 07) or `05_types` (dies).
- **`mockup-annotate`** — port `07_mockup-feedback/01_annotate` plus its
  `overlay/annotation-overlay.js`.
- **`mockup-feedback`** — triage → patch → apply as one pass; `triage.py` ships as a script,
  not a skill. Carry over the `patches/<sid>.review.md` approval gate.

Also in scope:

- Move the `items[]` id-derivation rule into `contracts/walkthrough_renderer.md` and delete
  the per-renderer copies. Fold `preview_compatibility.md` into it.
- Carry `contracts/elements_block.md` across unchanged.
- Decide what happens to the surviving `validator.py` + `tests/expected/` fixtures from
  `static-html` and `astro` — they are the only test coverage in the domain, and the map's
  "CI and validation" fog is still open. If they come across, say under what harness.

Record in the answer: final line counts per skill, what the `references/` directories hold,
and anything that had to differ from ticket 06's shape.

## Answer

_(pending)_

## Note from ticket 07

**Ticket 06's premise about Storybook setup was wrong, and ticket 07 sent the step back
here.** `impl-build-foundation` only *themes a Storybook that already exists* ("only if
`prototype/storybook/` exists AND Storybook is installed",
`10_impl-build/02_foundation/SKILL.md:74-75`), while `mockup-component-storybook-setup`
(171 lines) **scaffolds a standalone Storybook project**. Different artifacts — so the step
is not covered by the build domain and would have been lost.

**Scaffolding the standalone Storybook is a step inside `mockup-storybook`.** The real app's
Storybook config stays with `build-foundation`; ticket 18 confirms that split from the build
side. `mockup-component-storybook-types` still dies, as ticket 06 ruled.
