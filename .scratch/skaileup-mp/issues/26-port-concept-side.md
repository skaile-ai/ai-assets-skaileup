# 26: Port the concept side — write the 10 skills

**Type:** task
**Blocked by:** None (08, 19, 21 resolved)
**Status:** ready

## Question

Nothing to decide — tickets 08 and 21 settled the shape, this writes it. Same relation 14 has
to 06, 19 to 07, and 23 to 17. Graduated from the map's *"the port itself, per domain"* fog by
ticket 21, which added two skills to the group and left the concept side as the only sized
domain with no port ticket.

**Ten skills.** Nine from ticket 08 (of which `spec-feature` already landed in ticket 19 and is
not rewritten here), plus two from ticket 21:

| skill | from | note |
|---|---|---|
| `concept-brief` | `concept-brief` + `goals` + `comparable` | ticket 03's worked port (289 → 80) lives in `docs/examples/`; that draft predates ADR 0007 |
| `concept-onboard` | `concept-grounding-onboard` + `seeds` + mp's `to-questionnaire` | writes `02_grounding/onboarding/` |
| `concept-research` | `concept-grounding-research` + `design-inspiration` + mp's `research` | writes `02_grounding/research/` |
| `concept-reverse` | `ops-reverse-engineer` (621 lines) | **ticket 21** — thin orchestrator, see below |
| `design-brand` | `design-brand-visual` | `design-brand-voice` does not port (ticket 08) |
| `experience-journeys` | `experience-journeys` | writes `04_journeys/stories.yaml` |
| `experience-behaviors` | `experience-behaviors` | `.allium` dies; markdown state tables (ticket 08) |
| `experience-shell` | `experience-screens`, narrowed | shell only — the loop owns screens (W1) |
| `spec-featuresets` | `product-spec-features`, narrowed | featureset grouping; `spec-feature` writes the specs |
| `ops-review` | `ops-review` + `sync` + `trace` + `ready` + `audit` Phase 2 | **ticket 21** — see below |

Constraints, all already settled: `SKILL.md` under the **140-line ceiling** (ticket 03), dir name
== `name:` character for character (ticket 04), **no `MUST`/`NEVER` block** — constraints stated
positively at the step they bind — `data.phase` declared by the flows and not by the name, and
**every path written against ADR 0007's tree**, not the pre-0007 one still present in several
contracts (ticket 19 found four; ticket 16 owns the sweep).

## The two skills from ticket 21

**`concept-reverse`** is ticket 02's mechanism carried the whole way: it keeps only Steps 1, 2 and
9 of the old 621-line skill — validate, repo discovery, and the `extracted`/`inferred`/
`needs_review` confidence grading that is its own invention — and **calls** `concept-brief`,
`architecture-techstack`, `architecture-datamodel`, `design-brand`, `experience-shell` and the
`spec-feature` loop rather than restating their output templates. The ~210 lines of stack-specific
detection (Nuxt/Next/Prisma/Drizzle globs, the 8-source ORM priority list, tailwind/CSS-var token
recipes, per-framework page globs) are the one thing no other skill owns and become
`references/detection/{techstack,datamodel,brand,screens}.md`. Fix in the port: the structural
defect at `11_reverse-engineer/SKILL.md:339-368` — two `##` headings and a 23-line fence sitting
inside the workflow between Steps 5 and 6.

**`ops-review`** is four skills merged, ~900 source lines into the 140 ceiling, and ticket 21
flagged this as the port's real risk. It writes **`11_build/review.yaml`** (verdict + score +
findings) and **`11_build/trace.yaml`** (the feature → slice → commits → code matrix). Every
finding **names the skill that fixes it** — that is `ready`'s remediation command, generalised.
The trace half is a **one-to-many join**: ticket 19 decoupled `slice_id` from `feature_slug`, so a
feature has N slices, and the old singular `slice_ref` lookup is wrong. Dead work not to carry:
`ops-sync`'s group-alignment check (matches a shape ADR 0007 removed) and most of its
feature↔screen repair (unreachable once `spec-feature` became sole writer of both trees).

**Fallbacks, in order, if `ops-review` does not fit:** a `references/checks.md`; failing that, a
split back into `ops-review` (concept-tree integrity) and `ops-trace` (build coverage), which is
the seam ticket 21 crossed. Report which one was needed — it is the first real test of whether
the 140 ceiling holds for a merge this size.

## Also in scope

- **~4 lines into the landed `spec-feature`** (ticket 21, from `ops-add-feature`): the
  blast-radius grill emitting which of `04_journeys/`, `techstack.md`, `architecture.md`,
  `datamodel/*` and `07_screens/` need their owner re-run; the *"preserve existing `screens:` and
  `data_entities:` arrays"* data-loss guard on the refinement branch; and one line naming
  `build-plan` when the project is already built. **The cascade itself does not port.**
- **`contracts/grill_bank.md`** (ticket 09, 0 in-body readers) survives only if one of these
  skills reads it at a step. Otherwise delete.

## Answer

_(pending)_
