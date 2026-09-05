# 18: Architecture + build — the eleven skills nobody owned

**Type:** grilling
**Blocked by:** None (07 resolved)
**Status:** resolved

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

## Note from ticket 17

**`eval-code`'s `scaffold` scope is `build-scaffold`'s done-check, not a skill.** Ticket 17
deletes `impl-quality-eval-code`; its three scopes split cleanly, and the smallest one lands
here. At `scope: scaffold` the skill runs `lint → typecheck → build` with
*"MUST stop immediately if build fails"* and nothing else — no sub-agents, no tests, because
at that point there are no features to review. That is a scaffold smoke test: it belongs at
the end of `build-scaffold` as a step, the way ticket 07 put build+test inside
`build-implement` rather than in a separate skill.

The other two scopes go to `build-implement` (`feature`: + unit tests) and to
`quality-review` (`full`: + analysis, which now means calling `code-review`).

## Answer

**Eleven skills / 2,706 lines → five.** `architecture` stays a domain of its own (3 skills);
`build` gains 2 one-time-setup skills beside ticket 07's four. Three skills die outright, two
merge into survivors, one folds into another domain's skill.

| survivor | absorbs | dies with it |
|---|---|---|
| `architecture-techstack` | `templates-select` | — |
| `architecture-system` (shrunk) | — | `references/output_template.md` (184), Standalone Mode block (34) |
| `architecture-datamodel` | — | — |
| `build-scaffold` | `foundation` | the Storybook theming step |
| `build-database` | `migrate` + `seed` | the per-ORM branch tables |
| — | — | `infrastructure` · `generate` · `docs` |

**One rule did most of the work, and it is now ADR 0009: stack-specific knowledge lives in a
template; a skill is stack-neutral or it is not a skill.** It killed `generate` (25% of body
lines name one vendor, zero flows, its STEP 3/5 *is* `template-postxl`'s `## Codegen`) and
`infrastructure` (which admits the NestJS assumption in its own body, `SKILL.md:56-57`, while
wearing a stack-neutral name), and it **re-grounds ticket 06's `storybook-types` ruling** —
which had used "PostXL-only" as the criterion, a test that would also condemn `template-postxl`
itself. The two skills shared only the word PostXL; what actually condemns both is carrying
vendor codegen in a skill body.

### `architecture` stays a domain

Unanimous machine evidence: every flow that declares a phase puts the architecture block in
`conceptualization` and the build block in `implementation`, and **`skaileup-concept-only` runs
the whole `architecture` sub-flow and never reaches a build node** — architecture is reachable
without build, build never without architecture. The counter-argument (`datamodel` → `migrate` →
`seed` is one data pipeline cut in half) is answered one level down by merging `migrate`+`seed`
rather than by moving the domain line: **the seam is the artifact**, `10_blueprint/` versus the
app's source tree. Folding would also re-create a trap — `skaileup-concept-reverse` declares no
`data.phase` on its `system`/`datamodel` nodes, so the name prefix decides, and
`build-datamodel` would read as implementation inside a `conceptualization` group.

**`architecture-system` survives but shrinks sharply.** Its concept-side readership is already
gone — `architecture.md`'s readers were `experience-screens` and `experience-screens-technical`,
**both deleted by ticket 08** — and its STEP 3 baselines every section from what the stack
provides out of the box, which is the template's job under ADR 0009. It now records **only what
the project adds beyond the template's defaults**: custom modules, protocols, external
integrations — exactly the frontmatter it already emits. That makes `system: skip` in
`appbuilder-simple` and `appbuilder-cli` correct rather than a gap.

**`architecture-datamodel` gains `10_blueprint/glossary.md`.** ADR 0007 puts the file in the
tree and **nothing wrote it** — the same hole `decisions.md` had until ticket 13 supplied a
writer. `datamodel` is the only skill holding the whole vocabulary at once (it already derives
semantic entities and writes feedback into feature frontmatter, and `golden_principles.md`
already makes `model.json` the canonical name source), so it writes entity and field names with
their one-line meanings as a step.

**`templates-select` is not a skill.** `techstack` already scans the same directory, already
"selects the best matching profile", already writes `tech_stack_skill`, and its own checklist
already requires that field to name a real template directory — then `templates-select` **opens
by no-opping** when it did, behind a second human approval checkpoint over the same field. Its
edge is `type: optional` (ticket 15: orders nothing), its node is `optional: true` everywhere,
2 of 6 consumers pass `templates: skip`, `skaileup-stepwise` omits it, its own `DOMAIN.md`
Sequence never mentions it, and it hardcodes the seven ids in a table immediately after a `MUST`
forbidding exactly that. Its ~60 lines of genuine content — weighted score (frontend ×3, ui ×2,
backend/db ×1), tier tie-break from `scope.yaml`, existence check, `custom` escape — become
`techstack`'s selection rubric, replacing a narrative "select the best matching profile".

### `build`: two one-time skills, not five

**`scaffold` + `foundation` merge into `build-scaffold`.** Both are one-time, both read
`techstack.md` + the template, both write seed files, and `foundation`'s five phases each open
*"Read `<key>` from tech stack profile"* against keys that do not exist. Once ADR 0009 puts the
recipe in named template sections and ADR 0009 deletes the `PLANS.md`/`progress.yaml` writes,
`scaffold` is a scaffold command plus a git branch and `foundation` is "walk four template
sections in order" — ticket 02's mechanism exactly: the recipe lives elsewhere, the skill is
order plus checkpoints.

**`migrate` + `seed` merge into `build-database`.** Measured: `migrate` is **3%** per-ORM (4
lines), `seed` **8%** (12 lines); everything else is stack-neutral — DBML↔`model.json`
cross-check, semantic-type translation, UUID PKs, junction tables, insert-order dependency
graph, scenario entry point, two 6-point validations. They chain hard and share every input.
The merge also **removes a triple-write**: seed was written by three skills and migration by two
today, with `scaffold` running the first migration before `migrate` appears in flow order at
all. `build-scaffold` now migrates and seeds nothing; it hands off.

Vocabulary, recorded in `CONTEXT.md`: **datamodel** is the designed schema in
`10_blueprint/datamodel/`; **database** is the materialised thing in the built app.

**The Storybook theming step dies, and the consequence is stated rather than patched.**
`foundation` Phase 5 gates on `_concept/prototype/storybook/` — the **mockup** project — to theme
the **app's** Storybook: it tests A to act on B. All three of its bullets (theme decorator,
brand CSS vars, viewport presets) are already performed on the mockup project by
`mockup-storybook`, and the app-side recipe is `## Storybook Config` in all seven templates. So:
**the built app gets no Storybook from this collection.** A built app that wants one follows the
template section as ordinary `build-implement` work. This confirms ticket 07's correction of
ticket 06 from the build side, and goes one step further — not only scaffolding but theming
leaves `foundation`.

**`impl-build-docs` does not port, and it was never a build skill.** Its `_sources` examples are
`agent-framework/cli/src/commands/run.ts`; its path convention is *"relative path from monorepo
root"*; it excludes *"AI resource catalog pages (auto-generated by the ai-resource-loader)"* and
*"pages that cover skills/agents/flows"*. It is **this repo's own doc tooling misfiled under
`impl-build`** — plus a live TODO admitting Starlight lock-in, the only one of the eleven with
no `artifacts:` block, and a `requires: implementation-contract` naming a contract `-mp` does
not have. `contracts/doc_tracking.md` (225 lines, routed *into* `build-docs` by ticket 09) dies
with it. **No replacement**: documenting the built app is ordinary `build-implement` work, not a
254-line staleness engine.

**This disentangles the map's "docs site" fog patch**, which had two different Starlight sites
inside it. The patch is about `docs/scripts/generate-skill-pages.mjs` — *this* collection's site
— and nothing else.

### The broken skill↔template contract (ADR 0009)

Every key any skill MUST-extract is **0/7** across 3,799 lines: `scaffold_command`,
`build_command`, `package_manager`, `env_setup_command`, `project_structure`, `lint_command`,
`type_check_command`, `css_vars_mapping`, `auth_setup`, `app_shell`, `seed_format`, plus ticket
14's `story_extension` / `component_library` / `icon_library`. So `foundation`'s fallback —
*"If any section is missing from the profile, ask the user for guidance"* — **fired on every
run**, and ticket 14 had to derive three values rather than read them.

The fix is to **type the seam**, because two shapes were being confused under one word.
**Atoms** (one value, extracted by name) go to **template frontmatter**; **recipes**
(paragraphs) stay **named sections** cited by heading. *No skill names a key that is not in
template frontmatter, and no skill invents a section heading.* Pretending a recipe was a key is
what broke this. Ticket 16 gains a cheap check: every template declares the atom set, and this
retires ticket 14's derive-instead-of-ask workaround by giving those three values a home.

### `templates/` is a root asset kind

The ticket asked whether the residue "belongs in `profiles/`". **It does not — that destination
does not exist.** Ticket 05 settled the words (profile = project type, template = tech-stack
reference) and `-mp`'s `profiles/` is six artifact-path maps with zero stack content.

`templates/` lands at the **repo root**, sibling to `skills/` · `flows/` · `contracts/` ·
`profiles/`, one directory per template, directory name == template id (ticket 04's rule applied
to a second asset kind). **No line ceiling** — ticket 03's 140 governs instruction an agent
follows top to bottom; a template is reference data an agent loads one section of, and the seven
run 422–722 lines because the stacks are that large.

**`contracts/preview_compatibility.md` is claimed — and relocated.** Ticket 14 was right that
ticket 06's fold-in was wrong; it never happened, so `-mp` simply does not have the file. Its
seven readers are template `## Preview Compatibility` sections — **reference data, not skills** —
so it fails ticket 09's bar for `contracts/` while being genuinely needed. It ports as
**`templates/preview_compatibility.md`**, the shared proxy/base-path rules beside the seven files
that cite it; each template keeps its short framework-specific section. Duplicating 292 lines
seven times was the alternative. `-mp`'s `contracts/README.md` row for the fold-in is wrong and
is corrected by the templates port.

**`prog-expert-*` stops being a `MUST`.** Nine skills named by every template's `## Expert
Skills` and by `migrate` STEP 4 live in `ai-assets/dev-implementation-experts-*` — a different
collection — and the decisive fact is that **`skaile.yaml` has no dependency mechanism at all**
(no `assets:` block by design, glob discovery only), so the dependency is not expressible. Ticket
03 requires a check behind a guardrail; there is none behind a `MUST` whose target was never
installed. The sections become *"if `prog-expert-<x>` is installed, consult it"* — optional, no
gate, nothing declared.

### `PLANS.md` and `progress.yaml` both die (ADR 0009)

The nine in-body readers do not survive inspection — the same ~2.5× inflation ticket 09 found
for `frontmatter.md`. **Three mention it only to disclaim it** (two say it carries no status, one
says it belongs to someone else), **one is a different file** (the out-of-scope umbrella
`PLANS.md`), **one tests existence only**. Of what remains, order is the flow graph — the
contract's Phases list is `impl-build-setup.flow.yaml` written out node-for-node, and the graph
is a live machine contract while prose is not — and status is duplication by construction, with
`ops-review`'s PLAN-DRIFT check existing *only* because of it.

**The escape hatch does not exist either.** Three old skills say status lives in
`progress.yaml`, but ADR 0007 gives `11_build/` exactly two entries (`slices/<slice_id>/` and
`decisions.md`), so a project-level `progress.yaml` is as homeless as `PLANS.md`, and ticket 07
already deletes the per-slice one as transient. **Both die. `11_build/` stays as 0007 drew it —
no twelfth entry, no new root file.**

The residue was three sites and all three were scope: `scaffold`'s Scope paragraph (**Source
Artifacts is recomputed, never stored** — it was an inventory of files that exist), and two with
existing homes — `concept-brief`'s **`## Raw Description`**, which is not in `contracts/plans.md`'s
schema at all and is an *answer* bound for `02_grounding/onboarding/onboarding.yaml` per ticket
05, and `ops-add-feature`'s backlog note, handed to ticket 21. Completion is git plus the
engine's per-node `flowExecution` record (ticket 15), written whether or not a skill remembers.

Accepted, and recorded in the ADR so it does not read as an omission: **nothing renders a
human-readable plan of the whole build.** The flow graph is the plan. If that turns out to
matter the fix is a rendering of the graph, not a second file to keep in step with it.

### Landed in `-mp`

- **ADR 0009** — `docs/adr/0008-stack-knowledge-lives-in-templates.md`
- **ADR 0009** — `docs/adr/0009-no-plan-file-and-no-status-file.md`
- `docs/adr/README.md` — 0008 and 0009 indexed, **and 0007, which ticket 08 never added**
- `CONTEXT.md` — **datamodel** / **database** as a glossary pair; **Template** sharpened to name
  the atoms/recipes split and the stack-neutrality rule

### Graduated and handed off

Two tickets, **strictly ordered** — the skills read atoms that do not exist yet, so porting them
first would repeat the exact defect this ticket found:

- **[24: Port the templates](24-port-templates.md)** — 7 × `TEMPLATE.md`, 3,799 lines.
- **[25: Port architecture + build — write the 5 skills](25-port-architecture-and-build.md)**,
  blocked by 24.

Handed off: **ticket 10** — the two sub-flows go 11 nodes → 5, and their `type: optional` edges
order nothing today (ticket 15), so 10 should set real edge types on `techstack → system →
datamodel`. **Ticket 16** — `-mp`'s `profiles/` still carry pre-0007 paths (`blueprint/`,
`discovery/`, `experience/features/`), the same staleness it already owns for the four mockup
skills; plus the new template-atom check. **Ticket 21** resolved concurrently with this one and
**absorbs both handoffs rather than receiving them**: it deletes `ops-add-feature` outright (into
~4 lines of `spec-feature`), so the implementation-backlog note dies with it — the surviving
lines must not reintroduce a `PLANS.md` write — and its merged `ops-review` simply has no
PLAN-DRIFT entropy indicator to port, nor the two `references/` gardening steps behind it, since
the artifact those checked is gone. Nothing is left open for 21.

**One thing ADR 0009 does *not* touch:** the **per-slice** `11_build/slices/<slice_id>/progress.yaml`,
which ADR 0006 already deletes on freeze and `build-implement` still uses to resume. Only the
project-level file dies.
