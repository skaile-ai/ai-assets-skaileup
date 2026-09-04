# 14: Port the mockup domain — write the 4 skills

**Type:** task
**Blocked by:** 11 (06 resolved)
**Status:** resolved

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

**Written and committed in `ai-assets-skaileup-mp`** — four commits, `ce0e118`..`f5ea080`,
on `main`, not pushed. Working tree clean. **6,597 lines → 344 lines of `SKILL.md` + 469 of
`references/` prose**, against ticket 06's ~450 estimate.

| skill | SKILL.md | ported from | source lines |
|---|---|---|---|
| `mockup-walkthrough` | **91** | `01_a_text` · `01_b_static-html` · `01_c_astro` · `01_d_lit` · `01_e_framework` | 4,326 |
| `mockup-storybook` | **89** | `01_setup` · `02_components` · `03_pages` · `04_journeys` · `06_orchestrator` | 921 |
| `mockup-annotate` | **78** | `07/01_annotate` | 187 |
| `mockup-feedback` | **86** | `07/02_triage` · `03_patch` · `04_apply` | 533 |

All four are `name:` == directory, frontmatter is the ticket-01 read-set only (`version`,
`artifacts.requires[]`, `prerequisites.files[]` — `produces` dropped per the template, which
the landed astro example still carries), and no `MUST`/`NEVER` block anywhere.

### What the `references/` directories hold

- **`mockup-walkthrough/references/{static-html,astro}/`** — `RENDERER.md` (82 / 59 lines:
  the render steps that renderer alone performs and where it reads the shared contract
  differently), `validator.py`, and `tests/`. `astro/` additionally carries `scaffold/` (the
  seven real files it copies at init) and `specs-json.md`, both moved from
  `docs/examples/mockup-walkthrough-astro/`.
- **`mockup-storybook/references/`** — `scaffold.md` (76: the `package.json`, three
  `.storybook/` configs and `brand.css` step 2 writes, with the token keys each reads) and
  `story-conventions.md` (96: directory layout, story titles, named variants per layer, the
  `pages/manifest.json` shape, the click-dummy pattern).
- **`mockup-annotate/`** — `overlay/annotation-overlay.js` verbatim, `validator.py`, `tests/`,
  and `references/session.schema.json`.
- **`mockup-feedback/`** — `references/patch-format.md` (156: the section-anchored diff
  grammar, the four category templates, both promotion patches, the `review.md` shape, test
  impact) plus the three schemas; `scripts/` holds `triage.py`, `apply.py` and the three
  validators renamed to `validate_{triage,patches,applied}.py`; `tests/` holds all three
  fixture sets plus the shared session fixtures.

### Contracts

- **`walkthrough_renderer.md` 414 → 446.** Gained `## items[] id derivation` as a first-class
  section between § Auto-slug fallback and § Spec reference panel, and the per-renderer copies
  are gone — that rule was written out in each of five renderers and had to agree across all
  of them. Header retargeted at two renderers behind one skill; `renderer_version` now reads
  `mockup-walkthrough`'s `version` rather than a per-renderer `metadata.version`; `<variant>`
  narrowed to `static-html | astro`; `lit`/`framework` removed from the `source_anchor`
  scheme note; `mockup-feedback-annotate`/`-triage` renamed to `mockup-annotate`/
  `mockup-feedback`. The `## Shared MUST / NEVER` block **stays** — ticket 09 already ruled
  that ticket 03's amendment binds skill-body prose, and these are exactly what `validator.py`
  checks.
- **`elements_block.md` carried unchanged in content**, but its three references to
  `mockup-walkthrough-*` / `mockup-feedback-*` were renamed. Shipping a live contract that
  points at skills which do not exist is worse than "unchanged".
- **`preview_compatibility.md` is NOT folded in, and this contradicts ticket 06.** Its 292
  lines are per-framework base-path recipes (SvelteKit `paths.base`, Next `basePath`, Nuxt
  `app.baseURL`, Vite `base`) for an app running behind the workspace preview proxy. Its
  audience line names stack-profile authors and `impl-build-scaffold`/`-foundation`; grep
  finds **seven readers, all `09_impl-architecture/templates/template-*/TEMPLATE.md`, and zero
  in the mockup domain** — neither surviving renderer, nor `walkthrough_renderer.md`, mentions
  preview or iframe at all. Ticket 06 read it as "will this preview inside a host page", which
  is not what it is. Folding it would have put 292 lines of framework config into the contract
  of the one domain that never reads it, and stranded seven real readers. **It belongs to
  ticket 18** (architecture + build), which owns `templates/`. It is not in `-mp` today, so
  nothing is broken meanwhile — but ticket 18 has to claim it or it is lost.

### Fixtures ruling: both come across; the harness question stays with ticket 16

Split the question in two, because the ticket's phrasing conflates them.

**`validator.py` is not test infrastructure — it is a step of the skill.** Step 6 of
`mockup-walkthrough` and step 5 of `mockup-annotate` run it against the produced site, and
ticket 03's whole "hard guardrail is a named failure with a check behind it" rests on it. It
had to ship regardless of ticket 16. Three came across (`static-html`, `astro`, `annotate`),
plus `mockup-feedback`'s three as `scripts/validate_*.py`.

**The fixtures came too**, under `references/<renderer>/tests/` and `skills/<skill>/tests/`,
next to the validator each one tests. 140 KB across the walkthrough pair; co-locating them
needs no new top-level directory, which would have pre-empted a structural decision ticket 16
owns. **I re-pointed every harness at the new layout and ran all five green** — `static-html`,
`astro`, `annotate`, `feedback/triage`, `feedback/apply` — so they are live, not archived, and
`python` was changed to `python3` where the shebangless call failed on this machine.

**What ticket 16 still owns:** whether CI runs them, and whether `tests/` should move out of
the installed skill directory (a copy install ships them into every project's
`.claude/skills/`). Also worth its judgement — and worth saying plainly — **these harnesses do
not test the renderers.** Both walkthrough harnesses say so in their own header: they `cp
expected/ → rendered/` and validate that, "proves the validator is internally consistent
before the renderer is wired up… when the renderer ships, replace the cp step". So the "only
test coverage in the domain" is a self-consistency check on the validator plus a hand-curated
snapshot of correct output. The snapshot still earns its place (it is the contract made
concrete, and `mockup-walkthrough`'s `references/` section points an agent at it for exactly
that), but nobody should read a green run as evidence the renderer works. The
`mockup-feedback` apply tests **are** real integration tests — throwaway git repos, before/
→ after/ diffs — and are the strongest coverage in the domain.

One more for ticket 16: `static-html/validator.py` and `astro/validator.py` are 1,049 and
1,068 lines with a 366-line diff, most of it the renderer name. They are now siblings in one
skill, which makes the merge obvious and the risk real; I did not attempt it blind.

### What had to differ from ticket 06, and why

1. **`preview_compatibility.md` not folded** — above.
2. **The renderer override lives in `_grounding/onboarding/onboarding.yaml`**, per ticket 05,
   but `-mp`'s own `contracts/concept_structure.md` still documents `profile.yaml` +
   `decisions.yaml` separately. The skill is written to ticket 05's answer and the contract
   lags. **Ticket 08 has to land that rename** or step 1 of `mockup-walkthrough` points at a
   file the contract says does not exist.
3. **Every walkthrough renderer hard-gated on `design/tokens.json`, which nothing writes.**
   `design-brand-visual` writes `_concept/discovery/brand/tokens.json`; only the five
   walkthrough renderers said `design/`. A hard gate that can never pass. Corrected in the
   port. The fixtures keep `design/` — they are a self-contained fixture project passed via
   `--project-root`, and no validator reads the path.
4. **The `preserved intent` step cited fields that do not exist.** Both the old renderers and
   ticket 03's astro port tell the agent to read the devlog's `target_paths` and
   `patch_summary`. `apply.py` writes neither: the devlog block is `## <date> · session <sid>`
   / `### <file>` / `- <patchId> applied (<category>): '<body>'`. Rewritten against the real
   shape. Anything else in `-mp` that inherited those two field names is wrong the same way.
5. **The overlay script tag was broken on every page but `index.html`.** `01_annotate`
   injected a bare `src="annotation-overlay.js"` into every file, and the single overlay copy
   sits at the site root — so `screen/00_auth/login.html` resolved it to
   `screen/00_auth/annotation-overlay.js` and 404'd. Every screen page, i.e. the entire
   annotatable surface. The expected fixtures encoded the broken form and the validator
   compared the literal string, so the harness was green on it. Now depth-relative
   (`../../annotation-overlay.js`), with the validator computing the expected `src` per file
   and three fixture files updated; harness re-run green.
6. **`patches.schema.json` was missing `target-promotion`** from its `kind` enum, while
   `03_patch` emits that kind and `04_apply`'s step-2 schema pre-flight validates against it —
   a promotion patch would have been rejected by its own pipeline. Added.
7. **Storybook scaffolding is step 2 of `mockup-storybook`**, per ticket 07's note, not
   `build-foundation`. Confirmed from the source: `build-foundation` themes a Storybook only
   "if `prototype/storybook/` exists AND Storybook is installed".
8. **The stack resolution in step 1 is six values, three of which no template carries.** The
   orchestrator's STEP 1 claims to read `storybook_addon`, `story_format`, `story_extension`,
   `component_library`, `component_import`, `icon_library` from `TEMPLATE.md`; all seven
   templates ship a `## Storybook Config` block with exactly four keys, and
   `story_extension` / `component_library` / `icon_library` are in none of them. So the old
   skill's "ask the user if a field is missing" branch fired on every stack, every run. The
   port derives extension from format and library from the `## Component Library` section, and
   confirms all six once. **Ticket 18 should decide whether `TEMPLATE.md` grows the three
   keys** — that is the real fix and it is on the template side.
9. **`05_types` was already orphaned** — the orchestrator never calls it at any step. It dies
   as ticket 06 ruled, but it was dead before the ruling.
10. **The storybook validator was pointed at a directory nothing writes.**
    `06_orchestrator/validator.py` and `CLI.md` both hardcode
    `_concept/experience/4_storybook`, while all five skills write
    `_concept/prototype/storybook/`. It is not ported; `mockup-storybook` closes on a build
    that passes plus per-layer story counts instead. If ticket 16 wants a structural check
    here, it is net-new work, not a port.

### A gap the port could not close, and a ticket it may deserve

**Nothing writes `_concept/_feedback/sessions/<sid>.json`.** Outside forge-concept's iframe
the overlay collects annotations in the page and offers a Download button that saves
`annotations-<8-char-hash>.json` to the reader's downloads folder; `mockup-feedback` keys
everything — patches, review file, audit trail — off the filename stem of a file in
`sessions/`. A human has to move and rename it, and `_feedback/index.json` is created by
`mockup-annotate` and never appended to by anything. I wrote the manual hop into
`mockup-annotate` explicitly, including that the chosen filename becomes the session id, since
an undocumented hop is a feedback round that silently never happens. **A writer for that hop —
or a decision that forge-concept's iframe is the only supported path — is worth its own
ticket.** Two smaller ones ride along: `triage.py` resolves a journey annotation to
`experience/journeys/<id>.md` while journeys live in `stories.yaml`, and the overlay never
emits `specRef.feature` although `triage.py` resolves it (an in-file TODO).

**Also noticed, not acted on:** ticket 09 sent `contracts/wireframe_conventions.md` to
`mockup-walkthrough/references/`, but its three readers are `experience-screens`,
`experience-components` and a screen-spec template — none in this domain. Same shape of error
as `preview_compatibility.md`. It belongs to ticket 08; it is not in `-mp` today.


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
