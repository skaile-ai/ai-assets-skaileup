# 06: Mockup domain — 17 skills to ~6

**Type:** grilling
**Blocked by:** 04 (resolved)
**Status:** resolved

## Question

The three mockup domains are 17 skills and 6,597 lines — 26% of all prose in the collection —
and they are the part explicitly worth keeping, since Storybook is how the app gets built
incrementally. Settled in principle: one `mockup` domain of ~6 skills, with the renderer
choice becoming a **parameter** rather than five sibling skills. Work out the detail.

Today:

- `05_mockup-walkthrough/`: `00_migrate-elements` + renderers `text` · `static-html` · `astro`
  · `lit` · `framework` (the last three are 1,133 / 1,248 / 973 lines).
- `06_mockup-component/`: `isolated-html` + Storybook `setup` · `components` · `pages` ·
  `journeys` · `types` · `orchestrator`.
- `07_mockup-feedback/`: `annotate` → `triage` → `patch` → `apply`.

**What ticket 03's astro port showed, before you re-litigate the 17 → 6 count.** The
1,133-line skill ports to **110 lines** — under mp's 140 ceiling — with `references/scaffold/`
(the 7 file bodies as real files it copies) and `references/specs-json.md` beside it. So
length alone does not force the collapse; **duplication** does. Two specifics:

- ~200 lines of the astro skill's STEP 2 were restating `contracts/walkthrough_renderer.md`
  § Target resolution, § Auto-slug fallback and § Spec reference panel almost verbatim. Five
  renderers × that duplication is most of the 4,540 lines, and it is why they drift.
- The **`items[]` id-derivation rule belongs in the shared contract, not in each renderer.**
  The astro skill spends ~30 lines deriving it and says outright that it "follows directly
  from" the contract's `data-spec-*` table. Every renderer needs it and every renderer must
  agree on it. Move it into `walkthrough_renderer.md` and it stops being written five times.

This sharpens the renderer-parameter question rather than answering it: if what differs
between renderers is only the scaffold and a handful of resolution rules, the difference may
be a `references/<renderer>/` directory rather than a parameter or a skill.

Decide:

- The ~6 surviving skills and their names (proposed: `setup` · `components` · `pages` ·
  `journeys` · `walkthrough` · `feedback`).
- How the renderer parameter works: which renderers survive at all, whether the differences
  are genuinely parametric or whether one is a `references/` file per renderer.
- Whether the 4-step feedback chain (annotate → triage → patch → apply) collapses. `triage`
  is deterministic and non-LLM; `apply` writes commits — do those want to stay separate?
- What `00_migrate-elements` and the `elements:` block contract become.
- Where Storybook sits relative to `impl-build` — it is both a mockup surface and a real
  build artifact, and today that's split across two domains.

## Answer

**17 skills to 4**, and the count was never the hard part: what forced it was *duplication*
(ticket 03's finding) plus a renderer ladder nobody climbs. Surviving set, all `mockup-`
2-segment names per ticket 04:

- **`mockup-walkthrough`** — one skill, two renderers behind `references/<renderer>/`.
- **`mockup-storybook`** — story authoring only, all three layers in one skill.
- **`mockup-annotate`** — instrument a walkthrough, hand out the link.
- **`mockup-feedback`** — triage -> patch -> apply on a session file.

Estimated ~450 lines of `SKILL.md` plus `references/`, from 6,597 today (26% of the
collection's prose). Nothing here needs a fifth skill to hold it.

### Renderers: two survive, and the difference is a directory

**`static-html` and `astro` survive. `text`, `lit` and `framework` are dropped.**

- **`framework`** (973 lines) dropped on the strongest argument in the ticket: rendering the
  walkthrough in the project's *chosen* stack from the selected scaffold template is building
  the app, and `build-scaffold` + `build-foundation` do that better. A mockup that *is* the
  app is a second copy of the real codebase, waiting to drift. Its 7 flow references are the
  complex tier reaching for fidelity it should get from the real build.
- **`lit`** (1,248 lines) dropped: **1** flow reference, no `validator.py`, no fixtures, and a
  single niche (drop into an existing host shell).
- **`text`** (337 lines) dropped: its "3 stacks" (Alpine+Shoelace / Vue+PrimeVue / Preact+HTM)
  is a *fourth* renderer axis nested inside a renderer. It is low-fidelity `static-html`.
- The two survivors are also the only two carrying `validator.py` + `tests/fixtures/` +
  `tests/expected/`, and `astro` is the one ticket 03 already ported to 110 lines.

**The difference between them is `references/<renderer>/`, not a parameter.** Ticket 03
showed the astro skill's real per-renderer content was `references/scaffold/` — the 7 file
bodies it copies — while ~200 lines of its STEP 2 restated `contracts/walkthrough_renderer.md`
verbatim. One skill body states the shared pipeline once; each renderer contributes a scaffold
directory and a short resolution note. **The `items[]` id-derivation rule moves into
`contracts/walkthrough_renderer.md`** so it is written once instead of five times — it is the
rule every renderer needs and every renderer must agree on.

**The choice moves to data.** Today it is encoded three times: in the skill name, in the flow
graph (`appbuilder-standard.flow.yaml` carries two optional sibling nodes, `mock-astro` labelled
"via router" and `mock-static-fallback` labelled "router default"), and in the descriptions
("best for appbuilder-simple/standard/complex"). With one skill there is **one flow node**, and
the renderer is resolved: **tier sets the default** (`appbuilder-mvp`/`simple` -> `static-html`,
`standard`/`complex` -> `astro`), **`onboarding.yaml` records an override**, skill reads
onboarding first. Ticket 05 merged `profile.yaml` + `decisions.yaml` into `onboarding.yaml`, so
the home already exists. Consequence for ticket 10: the pick-one sibling-node pattern disappears
from every flow that uses it.

### Feedback chain: 4 to 2, split at the human wait

`annotate` -> `triage` -> `patch` -> `apply` collapses to **`mockup-annotate`** and
**`mockup-feedback`**. The split is not arbitrary: between instrumenting the site and reading
what came back sits a **multi-day wait for stakeholders**, which is a real session boundary
(ticket 12's subject). Within `mockup-feedback`, triage -> patch -> apply is one continuous
pass over one session file.

`triage` does not survive as a skill because **it is not one** — 98 lines wrapping a
deterministic `triage.py` with no LLM in the loop. Deterministic code is a script the skill
runs. `apply` writing a git commit does not earn separation either; committing is the last
step of applying, and the review artifact (`patches/<sid>.review.md`) is the approval gate,
not the skill boundary.

### Storybook: split by artifact, not by tool

Storybook is named in **9 `SKILL.md` outside the mockup domain** — `impl-build/scaffold`,
`impl-build/foundation`, `impl-slice/implement`, `impl-slice/implement-page`,
`impl-quality/ready`, `experience/screens`, `impl-architecture/templates-select`,
`concept/grounding/onboard`, and the orchestrator. It is genuinely both surfaces, so the line
is drawn at **what is being produced**, not at the tool:

- **Configuration -> `build-foundation`**, which already "configures Storybook with brand theme
  if present". `01_setup` (171 lines) is a duplicate of work the build domain does anyway.
- **Story authoring -> `mockup-storybook`**, one skill covering components -> pages -> journeys.
  `06_orchestrator` already "delegates to 4 sub-skills in sequence" — that is mp's `implement`
  pattern (15 lines composing `tdd` + `code-review`) written the long way. The composition is
  the skill; the three layers are its steps.
- **`05_types` dies.** Replacing placeholder types with `model.json`-generated interfaces is
  schema-driven codegen against the real data model — a build concern — and it is PostXL-only.

**`isolated-html` is dropped** (233 lines over 5 Python scripts and 6 test files — the
most-tested asset in the domain). It is the component-side twin of the renderer sprawl: a
second way to look at components when `mockup-storybook` is the answer. Its tests test
scripts, not the decision. If the no-Node-toolchain component view is missed — the one real
argument for it, for the concept-only flow — it returns as a `references/` renderer inside
`mockup-storybook`, the same mechanism as the walkthrough renderers.

### `migrate-elements` does not port; the `elements:` block stays

**`mockup-walkthrough-migrate-elements` (214 lines) is dropped deliberately**, not overlooked.
It is a one-time backfill that mines legacy screen prose into an `elements:` block for specs
authored *before* the block existed. `-mp` is opt-in for new projects (premise 2) and its
`experience-screens` writes `elements:` from the start, so the skill has no population to
serve. Premise 5 covers the exception: the old repo stays available for a project that
genuinely needs the backfill.

**The `elements:` block itself is load-bearing and stays.** `elements:` is read by **9
skills** — all 6 walkthrough renderers, `experience-screens`, `isolated-html`, and
`feedback-patch` — the clearest multi-reader contract in the collection by ticket 09's own
test.

### Handed to ticket 09 (contracts)

- **`contracts/walkthrough_renderer.md` (414) survives and grows** — absorbs the `items[]`
  id-derivation rule; read by both surviving renderers.
- **`contracts/elements_block.md` (410) survives** — 9 readers.
- **`contracts/preview_compatibility.md` (292) folds into `walkthrough_renderer.md`** — with
  `lit` and `framework` gone, "will this preview inside a host page" is a question only the
  two survivors ask, and 292 lines is a contract-sized answer to a section-sized concern.

### Numbers

| | today | `-mp` |
|---|---|---|
| skills | 17 | 4 |
| `SKILL.md` lines | 6,597 | ~450 + `references/` |
| walkthrough renderers | 5 (+3 sub-stacks in `text`) | 2, as `references/` dirs |
| component renderers | 2 (Storybook, isolated-html) | 1 |
| feedback steps as skills | 4 | 2 |
