# 18: Architecture + build — the eleven skills nobody owned

**Type:** grilling
**Blocked by:** None (07 resolved)
**Status:** ready

## Question

Graduated from ticket 07, which found the gap: the map's tickets covered the mockup domains
(06/14), the slice loops (07), the concept half (08) and the contracts (09), and
`09_impl-architecture` + `10_impl-build` fell between them — visible only inside the "the
port itself, per domain" fog patch.

Eleven skills / 2,706 lines:

- `09_impl-architecture/`: `techstack` (328) · `templates-select` (223) · `system` (279) ·
  `datamodel` (373)
- `10_impl-build/`: `scaffold` (234) · `foundation` (279) · `infrastructure` (238) ·
  `migrate` (169) · `seed` (190) · `generate` (139) · `docs` (254)

Ticket 04 puts both clusters in the **`build`** domain (`architecture` is one of the nine,
so the split may survive as `architecture-*` + `build-*`). Ticket 07 added
`spec-feature` · `build-plan` · `build-implement` · `build-branch` to that domain already.

Decide:

- The surviving set, and for each of the 11: merge / step-inside-another / dies.
- Whether `architecture` stays a domain of its own or folds into `build` — four skills that
  all write `_concept/blueprint/` before any code exists is an argument either way.
- **`PLANS.md`, handed over by ticket 07.** `contracts/plans.md` is deleted, but the artifact
  has **9 in-body readers** — `impl-build-{scaffold,foundation,infrastructure}`, three
  `ops-*`, `concept-brief`, and two skills ticket 07 collapsed. Does `PLANS.md` survive at
  all, now that `progress.yaml` holds status and the flow graph holds order?
- **`impl-build-generate` (139 lines) is referenced by zero flows.** Ticket 06 also sent
  `mockup-component-storybook-types` (schema-driven codegen, PostXL-only) to its grave rather
  than here — check whether `generate` was the home it should have had, or whether both go.
- **Storybook configuration.** Ticket 07 corrected ticket 06's premise: `build-foundation`
  only *themes* an existing Storybook (`SKILL.md:74-75`), it does not scaffold one, so
  scaffolding went to `mockup-storybook` (ticket 14). Confirm that split from this side.
- `templates-select` resolves the stack decision to one concrete scaffold template — is that
  a skill, or the last step of `techstack`?
- How much of `seed` / `migrate` is stack-specific enough to belong in `profiles/` (hoisted
  to the repo root by ticket 09) rather than in a skill body.

## Note from ticket 14

The mockup port handed two things to this ticket:

- **`contracts/preview_compatibility.md` (292 lines) is yours or it is lost.** Ticket 06
  assumed it belonged to the mockup domain and ruled it folded into
  `walkthrough_renderer.md`; ticket 14 found that wrong. It is per-framework base-path
  recipes for a **scaffolded app** behind the workspace preview proxy, and its seven readers
  are all `09_impl-architecture/templates/template-*/TEMPLATE.md` — zero in the mockup
  domain, and neither surviving renderer nor the renderer contract mentions preview or
  iframe. It was **not** folded in and did **not** port.
- **Storybook stack resolution asks for six values the templates carry four of.**
  `story_extension`, `component_library` and `icon_library` appear in no `TEMPLATE.md`, so
  the old "ask if missing" branch fired on every run; ticket 14's port derives them instead.
  Decide whether the templates grow the keys — this is the same broken skill↔template
  contract as `scaffold_command` / `css_vars_mapping` / `seed_format`.

Also confirmed from the mockup side: `build-foundation` keeps only the **real app's**
Storybook theming; scaffolding the standalone Storybook landed in `mockup-storybook`.
