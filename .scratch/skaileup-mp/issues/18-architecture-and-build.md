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
