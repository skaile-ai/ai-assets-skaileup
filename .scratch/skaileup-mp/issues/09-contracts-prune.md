# 09: Prune the contracts layer

**Type:** grilling
**Blocked by:** None (01, 05 resolved)
**Status:** resolved

## Question

29 contract `.md` files (50 files total). Settled: keep the load-bearing spine, "maybe reduce
even further". Ticket 01 says which are read by machines; ticket 05 says which vocabulary
moves into `CONTEXT.md`. Decide the final set.

**Ticket 01 changed this ticket's biggest assumption.** `artifacts.yaml` was on the spine
because forge-concept reads it. It doesn't, as deployed: `artifact-contract.ts` only finds it
under `--link`, and the default copy install leaves the recursive search empty, so forge-concept
falls back to session-driven completion and nobody notices. So decide explicitly:

- **Drop it** — it is 1,000+ lines of registry serving a code path that never runs.
- **Keep and fix** — one line at `forge-concept/server/utils/artifact-contract.ts:138` makes it
  reachable. That is a forge-concept edit, which the map puts out of scope; if the registry is
  worth keeping, this ticket should say so and the fix becomes its own effort.
- **Keep as documentation only** — the id↔path map is useful to humans and to skills even if
  no machine reads it, but then it stops being a contract and stops needing machine rigour.

**Ticket 03 adds one registry question to this ticket.** Both ports cut frontmatter to
ticket 01's read-set with nothing missed (`concept-brief` 87 → 15 lines, astro 51 → 18),
but the residue is lopsided: astro's 18 lines are real gates, while `concept-brief`'s 15 are
almost entirely `prerequisites.inputs_optional` — an 8-field **input dialog spec** that
forge-concept renders as a form. That is UI data sitting in a prose file, and it is the only
thing keeping concept-side frontmatter off mp's 4–6 lines. Same shape as the `artifacts.yaml`
question above: does the machine layer own this registry, or does each skill carry its own
copy? Decide both together — they are one question about where machine-read data lives.

Candidate spine: `artifacts.yaml` · `iron_laws.md` · `golden_principles.md` ·
`concept_structure.md` · `frontmatter.md` · `acceptance_criteria.md` · `domain_model.md` ·
`elements_block.md`.

Dying with the DSL: `skill_grammar.md` · `skill_template.md` · `skill_testing.md` ·
`agent_patterns.md`.

Undecided: `semantic_types.md` · `flows.md` · `plans.md` · `feedback_loop.md` ·
`seed_data.md` · `preview_compatibility.md` · `walkthrough_renderer.md` ·
`wireframe_conventions.md` · `grill_bank.md` · `evaluator.md` · `doc_tracking.md` ·
`asset_frontmatter.md` · `phase_procedures.md` · `slice_loop.md` · plus `schemas/`,
`profiles/`, `scripts/`, `tests/`.

For each: keep as a contract, fold into `CONTEXT.md`, fold into the one skill that reads it,
or delete. A contract only earns its place if **more than one** skill reads it, or a machine does.

## Answer

**28 contract `.md` files / 5,663 lines → 14 surviving files.** Deleted outright before any
rewriting: `artifacts.yaml` (~1,000), `flows.md` (588), `asset_frontmatter.md` (530).

### The rule that decided the registry question (Q1)

`artifacts.yaml` and `prerequisites.inputs_optional` were posed as one question, and one rule
answers both — in opposite directions: **machine-read data lives where forge-concept already
reliably looks**, which is `SKILL.md` frontmatter resolved via `name:`, and nowhere else.

- **`artifacts.yaml` is dropped.** Reviving it costs a forge-concept edit
  (`artifact-contract.ts:138`), which the map rules out of scope. A 1,000-line registry
  serving a code path that never runs does not survive on potential.
- **`inputs_optional` stays in frontmatter.** It is *live* — forge-concept reads
  `prerequisites.*` and renders the dialog. Moving it to a sibling `inputs.yaml` costs an
  equally out-of-scope forge-concept edit. The map's own boundary cuts both ways.
- **Accepted cost:** concept-side frontmatter stays ~15 lines against mp's 4–6. The
  `inputs.yaml` move is recorded as a follow-on gated on the forge-concept fix (see Out of scope).
- The id↔path map survives as **prose in `concept_structure.md`**, not as a registry.

### The bar (Q2)

**A reader is a skill that consults the contract at a step in its body.** Naming it in
`REQUIRED BACKGROUND` or the DSL `REFERENCES` block is a *citation*, not a read — and ticket 03
is deleting both blocks. Measured post-boilerplate across all 95 skills, citations excluded:

```
iron_laws 16 · concept_structure 15 · frontmatter 13 · agent_patterns 9 · elements_block 8
walkthrough_renderer 5 · semantic_types 4 · evaluator 4 · feedback_loop 4 · CONTRACT 4
seed_data 3 · domain_model 3 · README 3 · golden_principles 2
plans 1 · slice_loop 1 · wireframe_conventions 1 · skill_grammar 1 · acceptance_criteria 1
doc_tracking 0 · phase_procedures 0 · grill_bank 0 · asset_frontmatter 0 (11 cited, 530 lines)
flows 0 · skill_testing 0 · skill_template 0 · preview_compatibility 0
```

Raw reference counts were inflated ~2.5× by boilerplate — `frontmatter.md` shows 86 refs but
13 real readers. **Deciding on raw counts would have kept three of the largest dead files.**

### Two corrections to the ticket's own premises

- **`agent_patterns.md` does not die with the DSL (Q5).** The ticket filed it under "dying",
  but it has **9 in-body readers, 4th highest in the layer**. It survives, re-scoped to agent
  dispatch / subagent patterns (the DSL-flavoured parts go with `skill_grammar`), and absorbs
  `10_impl-build/contracts/subagent_dispatch.md`, the only other place this lives.
- **`iron_laws` and `golden_principles` are not in tension with ticket 03 (Q10).** Ticket 03's
  amendment killed `MUST`/`NEVER` **blocks in skill bodies**; these two document
  *machine-enforced* gates — `iron_laws` explains the `requires`/`prerequisites.*` gates ticket
  01 confirmed the machine reads, `golden_principles` is what `ops-review` checks
  automatically. Ticket 03 demanded a hard guardrail survive "as a named failure with a check
  behind it" — **`requires` is that check**. Both clear the bar on its machine clause.
  Recorded so 07/08 do not re-litigate it.

### Deletions and merges

- **`flows.md` deleted (Q3)** — 588 lines, the largest contract in the layer, **zero readers**
  (only `contracts/README.md` and `contracts/DOMAIN.md` mention it). `flow.schema.json` is kept
  as the flow contract's machine form; `flows/_meta/verify_flows.py` validates against it.
  **Subject to ticket 15** — platform's newer flow-execution implementation may make it stale.
- **Two frontmatter contracts become one (Q6).** `frontmatter.md` survives, **renamed
  `artifact_frontmatter.md`** so ticket 05's asset/artifact split is explicit in the filename.
  `asset_frontmatter.md` is deleted: 530 lines, **0 in-body readers**, and after Q1 its entire
  read-set is ticket 01's five fields — a 20-line table that belongs in the skill template
  where an author actually looks.
- **`skill_grammar` · `skill_template` · `skill_testing` die with the DSL (Q11).** Ticket 03's
  replacement template goes to **`docs/skill-template.md`, not `contracts/`** — by this
  ticket's own bar a template has no runtime reader, and putting it in `contracts/` would
  reintroduce the docs-in-the-contracts-folder problem this ticket exists to remove.
- **`CONTRACT.md` + `README.md` merge into one `contracts/README.md`; `DOMAIN.md` deleted (Q9).**
- **`preview_compatibility.md` folds into `walkthrough_renderer.md`** (ticket 06, accepted here).
- **`doc_tracking` folds into `build-docs`; `wireframe_conventions` folds into
  `mockup-walkthrough`'s `references/` (Q13).** Promote back only if 07/08 give either a
  second reader.
- **`acceptance_criteria` survives, shrunk to the EARS grammar (Q13)** — machine clause
  (`scripts/ac_lib.py`), and EARS is the format ticket 05 kept across spec and experience.

### Registries (Q8)

Q1 killed `artifacts.yaml`, their only machine reader.

- **Deleted:** `tests/` (tests the thing Q1 deleted) · `schemas/onboarding-profile-v1.yaml` +
  `onboarding-decisions-v1.yaml` (superseded by ticket 05's merged `onboarding.yaml`) ·
  `schemas/audiences-v1.yaml` + `competitors-v1.yaml` (0 readers).
- `schemas/design-inspiration-v1.yaml` follows its skill.
- **`profiles/` survives but leaves `contracts/`** — project-type profiles are *data the skills
  consume*, not a contract, and ticket 05 fixed `profile = project type only`. They land at
  **`profiles/` in the repo root**, next to `flows/`.

### Nested per-domain contracts (Q12)

Ticket 04's flat tree deletes their folders. `subagent_dispatch.md` → `agent_patterns.md`.
The three domain `CONTRACT.md` files (`implementation-contract`, `evaluate-contract`,
`standards-contract`) **fold into the single skill that reads each** — domain-local by
construction, so they fail the multi-reader bar; promoted back only if 07/08 give one a second
reader. `14_ops/contracts/CONTRACT.md` is **ruled out of scope** (see below).

### The surviving set — 14 files

`iron_laws` · `golden_principles` · `concept_structure` · `artifact_frontmatter` ·
`agent_patterns` (+`subagent_dispatch`) · `elements_block` · `walkthrough_renderer`
(+`preview_compatibility`) · `semantic_types` · `evaluator` · `feedback_loop` · `seed_data` ·
`domain_model` · `acceptance_criteria` · `README` (merged from `CONTRACT.md`).

Plus `flow.schema.json` (machine, pending ticket 15) and `profiles/` (moved to repo root).

### What this ticket deliberately did not decide

Four files whose fate belongs to tickets still blocked — ruling on them here would pre-empt
three tickets on stale information (Q7):

- **`slice_loop` (1 reader) + `plans` (1)** → **ticket 07**
- **`phase_procedures` (0)** → **ticket 12**
- **`grill_bank` (0)** → the absorbed-skills fog patch
- **`scripts/` + the CI validators** → **ticket 16**, graduated from the map's CI fog patch (Q4)

In each case the default is deletion unless that ticket's consolidation gives the file a reader.

## Note from ticket 05

`CONTEXT.md` is drafted (139 lines, `.scratch/skaileup-mp/CONTEXT.md`) and takes the
vocabulary job off the contracts layer. Consequences for this ticket:

- **All 16 `DOMAIN.md` files are already ruled out**, including `contracts/DOMAIN.md`.
- `contracts/domain_model.md` **survives** — it is now the format spec for decision
  records at all three levels (collection, design-time, build-time), not just the
  project's.
- `contracts/concept_structure.md` **survives** — `CONTEXT.md` is barred from carrying
  paths, so the path map has to live somewhere and this is it.
- `semantic_types.md` is untouched by ticket 05 (it is a type table, not vocabulary).
- New: `onboarding.yaml` replaces `profile.yaml` + `decisions.yaml` as one artifact —
  fewer ids in whatever registry survives, and `onboarding-decisions-v1.yaml` in
  `contracts/schemas/` needs merging or dropping with them.

## Note from ticket 06

The mockup domain's three contracts are decided; ticket 09 only has to accept them.

- **`walkthrough_renderer.md` survives and grows.** Read by both surviving renderers
  (`static-html`, `astro`), and it *gains* the `items[]` id-derivation rule that each renderer
  currently re-derives (~30 lines each). Clears the multi-reader bar with room to spare.
- **`elements_block.md` survives** — `elements:` is read by 9 skills today; even after the
  domain collapses it is read by `experience-screens`, `mockup-walkthrough` and
  `mockup-feedback`. The clearest multi-reader contract in the collection.
- **`preview_compatibility.md` (292) folds into `walkthrough_renderer.md`.** With `lit` and
  `framework` dropped, host-page embedding is a concern of only the two survivors.
- No mockup skill carries an input-dialog frontmatter block, so this domain does not weigh in
  on the `prerequisites.inputs_optional` question either way.
