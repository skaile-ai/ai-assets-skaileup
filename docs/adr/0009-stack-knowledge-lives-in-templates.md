# 0009 — Stack-specific knowledge lives in a template, not in a skill

**Status:** accepted

## Context

The old collection's architecture and build domains held eleven skills (2,706 lines) beside
seven `TEMPLATE.md` tech-stack references (3,799 lines). **The reference data was larger than
all eleven skills combined**, and the line between them had never been drawn — so it drifted
in both directions.

Drifting one way, skills absorbed stack knowledge that belonged in a template:

- **`impl-build-generate`** (139 lines) is a PostXL regeneration skill: hard-gated on
  `postxl-schema.json`, `pnpm`-pinned, **25% of its body lines name a concrete tool** — five to
  twenty-five times every other skill in the two domains. Its STEP 3/5 *is*
  `template-postxl/TEMPLATE.md`'s `## Codegen` section. **Zero flows reference it.**
- **`impl-build-infrastructure`** (238 lines) writes `backend/libs/<module>/src/` and
  `backend/apps/<process>/src/` from a stack-neutral name, and says so in its own body:
  *"the concrete implementation details (NestJS module/service patterns, `@fastify/websocket`,
  `docker-compose.yml`) assume a NestJS-based backend"* (`SKILL.md:56-57`). One of the seven
  templates is NestJS.
- **`impl-build-foundation`** themed the *app's* Storybook behind a gate on the *mockup*
  project's directory — testing A to act on B — while the app-side recipe already sat in every
  template's `## Storybook Config`.

Drifting the other way, the skill↔template contract was **broken for every key any skill
extracts**. Literal-key grep across all seven templates:

`scaffold_command` · `build_command` · `package_manager` · `env_setup_command` ·
`project_structure` · `lint_command` · `type_check_command` · `css_vars_mapping` ·
`auth_setup` · `app_shell` · `seed_format` · `story_extension` · `component_library` ·
`icon_library` — **0/7, every one.**

The information exists as prose under `## Scaffold Recipe`, `## CSS Variables / Theming`,
`## Auth Setup`, `## App Shell`; the names do not. So `impl-build-foundation`'s fallback —
*"If any section is missing from the profile, ask the user for guidance"* — fired on **every
run**, and ticket 14 had to make the storybook port derive three values rather than read them.

Ticket 06 had already killed `mockup-component-storybook-types` on the grounds of being
"PostXL-only". But that criterion cannot be the rule: `template-postxl` is PostXL-only and is
kept deliberately. Two skills that share only the word *PostXL* were being judged by a test
that would also condemn the template they belong in.

## Decision

**Stack-specific knowledge lives in a template. A skill is stack-neutral or it is not a
skill.**

That single rule replaces the case-by-case judgements:

- **`impl-build-generate` does not port.** Its four-level conflict cascade and
  `<<<<<<< Custom` preservation rule become part of `template-postxl`'s `## Codegen` section —
  the only thing it added over content already there.
- **`impl-build-infrastructure` does not port.** Custom modules, extra processes and
  WebSocket/SSE setup are *declared* by `architecture-system`, cut into slices by `build-plan`,
  and built by `build-implement` like any other work. The NestJS recipe belongs in
  `template-postxl`.
- **The Storybook theming step dies**, and the consequence is accepted rather than patched
  over: **the built app gets no Storybook from this collection.** The mockup Storybook is the
  mockup domain's; a built app that wants one follows the template's `## Storybook Config` as
  ordinary `build-implement` work.
- Ticket 06's ruling is re-grounded: `storybook-types` dies because it carried vendor codegen
  in a skill body, not because PostXL is disfavoured.

**The seam is typed, and the typing is what makes the rule enforceable.** Two shapes were
being confused under one word, "key":

- **Atoms** — one value, machine-extractable (`scaffold_command`, `package_manager`,
  `build_command`, `lint_command`, `type_check_command`, `story_extension`,
  `component_library`, `icon_library`, `seed_format`). These become **template frontmatter**.
- **Recipes** — paragraphs, not values (`## Scaffold Recipe`, `## CSS Variables / Theming`,
  `## Auth Setup`, `## App Shell`, `## Migration / ORM`, `## Seed`, `## Storybook Config`,
  `## Codegen`). These stay **named sections**, and a skill cites the heading.

**No skill names a key that is not in template frontmatter, and no skill invents a section
heading.** Pretending a recipe was a key is what broke the contract in the first place.

**Templates carry no line ceiling.** ADR 0003's 140 lines governs skills — instruction an
agent follows top to bottom. A template is reference data an agent loads one section of, and
the seven run 422–722 lines each because the stacks are genuinely that large.

**`templates/` is a root asset kind**, sibling to `skills/` · `flows/` · `contracts/` ·
`profiles/`, one directory per template with the directory name as the template id — ADR 0002's
rule applied to a second kind of asset. It is not `contracts/` (skills do not read it at a
step) and it is not `profiles/` (ADR 0002's vocabulary: **profile = project type**, **template
= tech-stack reference**).

## Consequences

- **`templates/preview_compatibility.md`** lands beside the templates rather than in
  `contracts/`. Its seven readers are template `## Preview Compatibility` sections — reference
  data, not skills — so it fails ADR 0004's bar while being genuinely needed. Duplicating 292
  lines seven times was the alternative.
- **Each template grows a `## Seed` section.** `impl-build-seed`'s twelve per-ORM lines are the
  only place that layout is written down; the migration equivalent already exists as
  `## Migration / ORM` in all seven.
- **`prog-expert-*` stops being a `MUST`.** Every template's `## Expert Skills` names nine
  skills that live in a different collection (`ai-assets/dev-implementation-experts-*`), and
  `skaile.yaml` has **no dependency mechanism at all** — so the dependency cannot be declared
  even if it were wanted. ADR 0003 requires a check behind a guardrail; there is none behind a
  `MUST` pointing at nothing installed. The sections become *"if `prog-expert-<x>` is
  installed, consult it"*.
- **The templates must be ported before the skills that read them**, or the port repeats the
  defect it was made to fix.
- **A stack this collection has no template for is a gap in `templates/`, not in `skills/`.**
  That is the trade: adding a stack is now seven-section reference work rather than a skill
  edit, and a project on an unsupported stack has fewer places to wedge special-casing in.
