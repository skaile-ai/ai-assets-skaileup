# 03: Skill body shape — settled by prototype

**Type:** prototype
**Blocked by:** None (can start immediately)
**Status:** resolved

## Question

What does a `-mp` `SKILL.md` look like? The agreed target is: prose body ~80 lines, a short
`MUST`/`NEVER` block for hard constraints, everything long moved to `references/`, and
frontmatter cut to `name` / `description` / whatever the machine layer genuinely reads.
Confirm or correct that by **porting two real skills** and looking at the result.

Port both:

1. **`skaileup/01_concept/01_brief/SKILL.md`** — a small, conversational skill; tests whether
   the new shape has enough structure.
2. **`skaileup/05_mockup-walkthrough/01_c_astro/SKILL.md`** (1,133 lines) — the worst case;
   tests whether `references/` actually absorbs the bulk or just hides it.

**Settle the `MUST`/`NEVER` question here.** Map premise 4 specifies a `MUST`/`NEVER` block,
but ticket 02 measured **zero uppercase MUST/NEVER/ALWAYS across all 2,945 lines** of the mp
collection, and `writing-for-agents` argues prohibition makes the banned behaviour *more*
available to the model and should be a last resort. skaileup's hard gates are real, though —
"no data model without features" has to bind. So the prototype is the test: port both skills
**without** a MUST/NEVER block, expressing each constraint positively, and see what (if
anything) stops binding. Premise 4 is amended by whatever this ticket concludes.

Keep both on a `prototype/skill-body-shape` branch, out of main. Judge on:

- Does the DSL's disappearance lose anything an agent needed, or only ceremony?
- Where does the 1,133-line skill's content go — how many reference files, and does an agent
  know when to load them?
- Frontmatter is now **answered by ticket 01** — read by code: `version`,
  `artifacts.requires[].id`, `prerequisites.*`, `requires`. Documentation-only, therefore
  droppable: `tags`, `stage`, `source`, `parameters`, `artifacts.produces`, `artifacts.consumes`.
  mp ships four keys total; `product-spec-features` currently spends 30% of the file on
  frontmatter. Prototype against the read-set plus `name`/`description` and see what's missed.
- Line-count reduction achieved, extrapolated across 95 skills. Ticket 02 identified six
  mechanical moves worth ≈550 lines on the astro skill alone (see `research/02-mp-skills-mined.md`
  §C.6) — read those before starting, and treat mp's **140-line max** as the target ceiling.
- Whether constraints survive without a MUST/NEVER block.

Decide from the two ports: the skill template `-mp` uses everywhere.

## Answer

**Prototype:** [`prototype/`](../prototype/) on branch `prototype/skill-body-shape` (commit
`33d7334`, committed, not merged, not pushed) — two real skills ported, plus
[`FINDINGS.md`](../prototype/FINDINGS.md) and the resulting
[`TEMPLATE.md`](../prototype/TEMPLATE.md). Check the branch out to read the ports.

**The shape holds, and it holds on the worst case.**

| | source | port | body only |
|---|---|---|---|
| `concept-brief` | 289 (87 frontmatter) | **80** (15 fm) | 202 → **65** (−68%) |
| `mockup-walkthrough-astro` | 1,133 (51 fm) | **110** (18 fm) | 1,082 → **92** (−91%) |

**Premise 4 is amended: no `MUST`/`NEVER` block.** All 13 MUSTs and NEVERs across the two
skills re-expressed positively at the step they bind, and two got sharper for it — the three
separate astro-config MUSTs collapsed into one section naming what the four settings buy,
pointing at the scaffold file that encodes them. Hard guardrails survive as **named failures
with a check behind them** (`dist/` must not exist; the validator must exit 0), which is
`writing-for-agents`' allowance rather than a block of nine. Only **4 of 88** skills carried
a `MUST`/`NEVER`, `CHECKLIST` or `ROLE/READS/WRITES` heading at all — the DSL is a cost
`skill_grammar.md` charges to all 88 and four spend.

**The DSL loses nothing.** Every construct resolved to something already elsewhere:
`ROLE`/`READS`/`WRITES` restated frontmatter and the contracts list; the 20-item `CHECKLIST`
restated `validator.py` (verified — all 20 are mechanical checks in it, and item 20 was
literally "Validator exits 0"); `MUST`/`NEVER` restated the steps; **`EMIT` is consumed by
nothing** — grepping both consumers finds `EMIT` only inside other `SKILL.md` files.

**Where the 1,133 lines went.** Two reference files, both reached by a named pointer:
`references/scaffold/` (the 7 verbatim file bodies, extracted into **295 lines of real files**
the skill copies — reached only by the init branch) and `references/specs-json.md` (130 lines,
reached at steps 4 and 6). Nothing moved into `contracts/walkthrough_renderer.md` or
`validator.py` — **the removed ~200 lines of STEP 2 were already there**, restated. That
duplication, not length, is what made the skill 1,133 lines.

**Frontmatter against ticket 01's read-set:** nothing missed, but the cut is uneven. Astro's
18 lines are all real gates. `concept-brief`'s 15 are almost entirely
`prerequisites.inputs_optional` — an 8-field **input dialog spec**, UI data that forge-concept
renders, sitting in a prose file. Move it to the machine layer and that frontmatter is **4
lines**, matching mp. Recorded as an open question on ticket 09.

**Collection-wide, before rewriting a line of prose** (measured across 88 `SKILL.md`,
24,646 lines): frontmatter 4,562 (18%) · code fences 2,250 (9%) · the ten boilerplate
sections 3,972 (16%) = **10,784 lines, 44%, mechanically removable**. The ports went further
because the remaining prose duplicated shared contracts. At ~30 skills averaging the ports'
~95 lines, `-mp` lands near **3,000 lines against 24,646** — mp's order of magnitude.

**Ceiling: 140 lines**, mp's measured maximum; both ports came in under 110. Note for ticket
06: the astro port fitting at 110 weakens the argument that the five renderers *must* collapse
to become tractable — they should still collapse, but for duplication, not length.
