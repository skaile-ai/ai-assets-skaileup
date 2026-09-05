# 35: The docs site is generated from a tree that no longer exists

**Type:** grilling
**Blocked by:** None — graduated from the map's fog 2026-09-06
**Status:** ready

## Question

Graduated from the **docs site** fog patch, narrowed twice already (ticket 18 cut the
second Starlight site out of it, ticket 33 supplied the reason to decide rather than defer).

The old repo carries a full Starlight site at `docs/` — **60 hand-written source files**, a
**470-line generator** (`docs/scripts/generate-skill-pages.mjs`), Astro + Starlight + mermaid
deps, and a `prebuild` hook that regenerates before every build. `-mp`'s `docs/` is **not a
site**: 14 plain markdown files (11 ADRs, the skill template, `examples/WHY.md`, the ADR
README).

Measured against `-mp` as it stands, the generator's inputs are mostly gone:

- **It emits a page per `DOMAIN.md`** (`:11`, `:345-348`, `:408`) and keys domains off a
  hardcoded `SKAILEUP_DOMAINS` set (`:98`, `:339`). **Ticket 05 deleted all 16 `DOMAIN.md`
  files** and ticket 04 made the tree flat — so the domain half of the generator has no input
  at all, and the synthesised fallback (`:427`, "_No DOMAIN.md authored yet._") would fire for
  every domain.
- **It hardcodes six contract paths** (`:35-40`); ticket 09 deleted **four** of them —
  `skill_grammar.md`, `asset_frontmatter.md`, `iron_laws.md`, `flows.md`. Only
  `golden_principles.md` and `semantic_types.md` survive, and `-mp` has eleven more contract
  files the list never names.
- **Three hand-written pages** (`docs/src/content/docs/domains/{meta,concept,impl}-group.md`)
  describe the old domain grouping, which ticket 04 replaced with nine name-carried domains.

Ticket 33 gave the reason this cannot just be deferred: **`check.py` globs `skills/` and
`contracts/` and never looks at `docs/`**, so anything skill-shaped living there has no gate
behind it — which is exactly how two worked examples drifted onto a dead tree and three dead
skill names went unnoticed until 33 found them.

So: **does `-mp` have a documentation site, and if so what generates it?**

1. **Port and rewrite** — carry the site over and rewrite the generator for a flat tree with
   no `DOMAIN.md`, thirteen contract files, and four flows. The generator is the bulk of the
   work; the 60 source pages are prose that has to be re-checked against a collection that
   changed shape in every dimension the site describes.
2. **Regenerate small** — drop the hand-written pages, keep a generated index over
   `skills/`, `flows/` and `contracts/` and nothing else. The site becomes a rendering of the
   collection rather than a document about it.
3. **Drop it** — `README.md`, `CONTEXT.md`, `contracts/README.md` and eleven ADRs already
   carry what the site's prose carried, and `-mp` is one third the size. The old repo keeps
   its site for as long as it runs.

Whatever the answer, it decides whether `docs/` needs a gate: today nothing checks it, and
`-mp` already ships `docs/examples/` that ticket 33 had to correct by hand.

## Answer

_(pending)_
