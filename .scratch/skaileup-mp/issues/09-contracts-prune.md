# 09: Prune the contracts layer

**Type:** grilling
**Blocked by:** 05 (01 resolved)
**Status:** blocked

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

_(pending)_
