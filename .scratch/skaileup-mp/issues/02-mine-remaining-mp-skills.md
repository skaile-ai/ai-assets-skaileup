# 02: Mine the remaining mattpocock skills for ideas

**Type:** research
**Blocked by:** None (can start immediately)
**Status:** resolved

## Question

Five mp skills are already slated for absorption (`grilling`, `to-spec`, `to-tickets`, an
`ask-matt`-style router, `research`). The other ~20 are installed at
`~/.agents/skills` and unexamined: `handoff`, `triage`, `wait-what`, `to-questionnaire`,
`wizard`, `diagnosing-bugs`, `codebase-design`, `implement`, `tdd`, `code-review`,
`prototype`, `teach`, `writing-for-agents`, `grill-with-docs`, `improve-codebase-architecture`,
`resolving-merge-conflicts`, `wayfinder`, `setup-matt-pocock-skills`, `PHASE-BOUNDARIES.md`.

Read them and report **which ideas belong in `-mp`'s build skillset**, distinguishing:

- **Absorb** — the idea fills a gap skaileup has (name the gap and the skaileup skill it lands in).
- **Reference** — leave as a global install, but `-mp` skills should call it by name.
- **Skip** — no fit.

Pay particular attention to structural ideas rather than features: the phase-boundary
decision tree, `handoff` as the inter-session bridge, `triage` as an on-ramp for work you
didn't create, `wait-what` as an in-conversation corrective, `writing-for-agents` as the
authoring standard for the rewrite, and how `implement` composes `tdd` + `code-review`
rather than duplicating them.

Also report the **authoring conventions** worth copying: how mp keeps a skill to ~80 lines,
what it puts in the body vs. a sibling `.md`, and how `ask-matt` documents a flow in prose
without a YAML graph.

## Answer

**Findings:** [`.scratch/skaileup-mp/research/02-mp-skills-mined.md`](../research/02-mp-skills-mined.md)
on throwaway branch `research/mp-skills-mined` (committed, not merged, not pushed).

**Verdicts** (20 skills + `PHASE-BOUNDARIES.md`; the five slated ones excluded):

| verdict | skills |
|---|---|
| **ABSORB** | `PHASE-BOUNDARIES.md` · `handoff` · `triage` · `wait-what` · `to-questionnaire` · `writing-for-agents` · `implement` (pattern) · `grill-me`/`grill-with-docs` (pattern) · `setup-matt-pocock-skills` (pattern) |
| **ALREADY ABSORBED** | `domain-modeling` — `skaileup/contracts/domain_model.md` is a faithful 141-line port; verify, don't redo |
| **ABSORB + REFERENCE** | `diagnosing-bugs` (absorb Phase 1's red-loop gate, reference the skill) · `codebase-design` (reference the skill, absorb its four-section vocabulary form) |
| **REFERENCE** | `tdd` · `code-review` · `prototype` · `wizard` · `resolving-merge-conflicts` · `improve-codebase-architecture` · `wayfinder` |
| **SKIP** | `teach` — learning workspace, no fit (steal only its `./assets/` reuse rule) |

**Headline structural findings**

1. `PHASE-BOUNDARIES.md` is a five-question ordered tree; skaileup hardcodes one of its five
   answers (`/clear` between every phase) at seven sites, including the two hops the tree's own
   worked example says should *continue*.
2. `implement` (15 lines) composes `tdd` + `code-review` instead of restating them — 140 lines
   across 3 files vs `12_impl-slice`'s 8 skills / 2,094 lines. This is the mechanism for 16 → 6.
3. skaileup has no on-ramp for work it didn't create, and no durable memory of rejected scope
   (`.out-of-scope/`); `mockup-feedback-triage` is the narrow special case of the general skill.
4. `13_impl-quality`'s debug pair (619 lines) interviews for a hypothesis first — the exact move
   `diagnosing-bugs` (138 lines) forbids until a red-capable loop exists.

**Authoring conventions** — mp: 25 skills / 2,945 lines total; `SKILL.md` mean 64, median 71,
**max 140**; frontmatter 4–6 lines with exactly four keys (`name`, `description`,
`disable-model-invocation`, `argument-hint`); **zero uppercase MUST/NEVER/ALWAYS in 2,945 lines**;
14 of 25 skills user-invoked. skaileup: 95 skills / 25,075 lines, mean 264, max 1,248; frontmatter
up to 30% of a file; all 95 model-invoked. `ask-matt` routes 23 skills in 90 lines of prose with no
YAML graph — enough to replace the per-flow `.md` docs with one router, keeping `.flow.yaml` for the
engine. Six mechanical moves would cut ≈550 lines from the 1,133-line astro skill without losing an
instruction (§C.6).

**Conflict to settle:** map premise 4 specifies a `MUST`/`NEVER` block; `writing-for-agents` argues
prohibition is a last resort and the collection contains none. Needs a decision ticket.
