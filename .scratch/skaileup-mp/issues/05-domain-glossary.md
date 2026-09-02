# 05: The shared domain vocabulary (CONTEXT.md)

**Type:** grilling
**Blocked by:** 04 (resolved)
**Status:** resolved

## Question

The stated goal is "a common domain understanding" taken from the mp skills. mp gets this
from `domain-modeling`: a single `CONTEXT.md` glossary plus ADRs. skaileup spreads the same
job across `contracts/domain_model.md`, `semantic_types.md`, `DOMAIN.md` files per domain,
and 25k lines of prose that each redefine terms locally.

Write `-mp`'s `CONTEXT.md`: the ubiquitous language every skill uses without redefining.
Terms that need pinning down, at minimum:

- **artifact** vs. **asset** vs. **output** — three words for overlapping things today.
- **feature** vs. **featureset** vs. **story** vs. **slice** vs. **screen** vs. **component**.
- **slice** — used for both the per-feature concept dossier and the per-feature impl loop.
- **dossier**, **frozen**, **tier**, **flow**, **profile**, **gate** (hard vs. soft), **seed mode**.
- **concept** vs. **blueprint** vs. **implementation** as tree-level names.
- Where mp's vocabulary is better (**tracer bullet**, **vertical slice**, **frontier**,
  **deep module**, **seam**) and should replace the local term outright.

Decide also: does `-mp` keep per-domain `DOMAIN.md` files, or does one `CONTEXT.md` + ADRs
replace them?

## Answer

**`-mp/CONTEXT.md` is drafted: `.scratch/skaileup-mp/CONTEXT.md`, 139 lines** (under the
140 ceiling), glossary-only, zero paths. Ticket 11 drops it into the skeleton verbatim.

**Two vocabularies, never one.** `CONTEXT.md` is the *collection's* language (artifact,
slice, tier, gate — hand-written, read by skill authors). The *project's* language
(Order, Customer, Invoice) stays a generated artifact and keeps the word **glossary**.
`CONTEXT` is never called a glossary.

**Per-domain `DOMAIN.md` files die** — all 16. Every job they do is duplicated by
something machine-read: sequence → the flow graph, when-to-use → `description`, skill
list → the directory, cross-refs → `requires`. Ticket 04's flat tree removes the folders
they lived in anyway. Generate a domain map if a human needs one.

**Terms settled:**

- **asset** (this repo's shipped things) vs **artifact** (files a skill writes into a
  project) — canonizes the split already latent in the collection. **`output` retires as
  a noun**, with `deliverable`.
- **slice = vertical slice**, impl-side only. The concept-side per-feature work is a
  **feature dossier**; **dossier** (74 uses today) is the noun for both directories,
  qualified as *feature* or *slice*.
- **featureset** replaces **feature group** outright — a rename, not a new level (the
  word appears **0 times** in 24,646 lines today; `feature group`/`<group>` is the live
  term). Features belong to exactly one featureset; nothing sits between them.
- **profile = project type, only.** The other two senses split off: onboarding's
  `profile.yaml` merges away (below), and "tech stack profile" becomes **template**
  (the files are already `TEMPLATE.md`). This also makes ticket 10's `appbuilder-cli` →
  `cli-tool` profile demotion consistent rather than a fourth sense.
- **tier · phase · gate · frozen** each keep one job. **`phase` is a machine contract**
  (forge-concept's `data.phase` ∈ conceptualization|implementation|review) and must not
  be reused loosely — so ticket 12's concept is a **session boundary**, not a phase
  boundary.
- **seed scenario**, not "seed mode" — the ticket's term was a phantom (0 uses; the live
  word is `scenario`, 127 uses).
- **mp imports: `vertical slice` only.** `tracer bullet` is a second word for the same
  concept — the disease this ticket treats. `deep module` and `seam` stay
  `codebase-design`'s vocabulary, called by name per ticket 02's REFERENCE verdict.
  `frontier` skipped — no ticket proposes wayfinder-style planning inside `-mp`.
- **`_concept/` tree renaming: principle only.** The tree is user-visible in
  forge-concept, so churn is expensive; fix only where it is actively wrong (`features`
  sits under `experience/` while written by `spec-features`). The folder-by-folder list
  waits on tickets 08 and 09.

**Decision records — three levels, one rule.** A decision record is append-only and must
pass all three gates (hard to reverse · surprising without context · real trade-off).
The level is fixed by what the decision binds:

| Level | Binds |
|---|---|
| collection | `-mp` itself — flat tree, no MUST/NEVER, the nine domains |
| design-time | the project's concept |
| build-time | the project's implementation |

`contracts/domain_model.md` survives as the shared format spec for all three.
**`-mp` gains its own** — seeded from tickets 01–04, which all clear the gate. See
tickets 11 and 13 for the two knock-ons.

**`decisions.yaml` was not decisions** — it held onboarding *answers* with confidence
levels, one directory from the real ADR store. **`decision` is now reserved for the
3-test sense.** Onboarding's `profile.yaml` and `decisions.yaml` **merge into a single
`onboarding.yaml`**: same wizard, same moment, already read together
(`concept_structure.md:207`). `inputs/` stays. One artifact id replaces two.
