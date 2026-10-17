# 0016 — Published formats where one exists

**Status:** accepted

Supersedes the `11_build/interaction.yaml` path in [ADR 0015](0015-interaction-decisions-live-in-app-design.md);
the rest of that record stands.

## Context

Most files under `_concept/` took a shape that suited the skill writing them. For a handful
the shape is a bespoke copy of something with a published specification, a version and
tooling: a design-token file with its own keys, a verdict file that records `file:line`
violations in a private layout, an architecture note with no named levels. The cost of a
private shape is paid by everyone downstream. Build tools cannot read it, editors cannot
validate it, and the host's own copy of the shape has already drifted from the collection's
(`forge` keeps TypeBox copies of the token and seed shapes, and `check.py` had nothing that
told the two apart).

Two research files record what exists and what it would cost to adopt. They are the
evidence for this record and are not repeated here:
`.scratch/research/concept-standards-sources-2026-10-17.md` (versions, status and URLs of each
standard) and `.scratch/research/concept-standards-recommendations-2026-10-17.md` (each
artifact mapped to its closest standard, with a verdict: migrate, align, add, keep).

The test applied to each artifact is the one that has kept the tree small: adopt a published
format when it is a real standard with a consumer, and keep ours when the only candidates are
vendor layouts that move faster than we can follow or have no tooling in this space.

## Decision

Seven changes, each adopting one published format. Files for which no such format exists are
listed under *Alternatives* and stay as they are.

**1. Design tokens are W3C DTCG Format Module 2025.10.** `03_brand/brand.tokens.json`
replaces `tokens.json`; a dark mode adds `brand.dark.tokens.json` (colour overrides) and
`brand.resolver.json` (DTCG Resolver Module 2025.10, one modifier `mode` with contexts `light`
and `dark`). Build tools and design tools already read DTCG, and light and dark become
expressible, which the old file could not do. The hand-written `tailwind` block goes —
renderers and build tools derive CSS from the tokens — and `atmosphere` moves to `identity.md`.
`contracts/design_tokens.md` fixes the subset: the required tokens, a colour `$value` that
always carries `hex` (Style Dictionary's 2025.10 support is partial), the `ai.skaile`
extension for `mode` and `approved`, and one flattening rule to `--token-*` custom
properties that every renderer shares.

**2. Machine files get JSON Schema 2020-12.** One schema per file under
`contracts/schemas/<name>.schema.json`, each with `$id`, `title` and an `x-artifact` naming
the `_concept/` path it describes. Skills, `check.py` and editors then share one definition
of each shape. Schemas are lenient — open `additionalProperties`, `required` only for what a
contract or the writing skill calls required — so adopting one never rejects a file a skill
legitimately wrote last month. The writer cites its schema at the step that writes; `check.py`
checks the schemas and that every producer cites its own.

**3. The interaction verdict is OASIS SARIF 2.1.0.** `11_build/interaction.sarif` replaces
`interaction.yaml` (produces id `interaction-review` is unchanged). Located violations are
what SARIF is for, and GitHub code scanning shows the same file on pull requests. Violations
are `kind: fail` results with a `level` from the severity (critical and high → `error`,
medium → `warning`, low → `note`); exemplars are `kind: pass`; a proposed exception is a
`suppressions` entry; the score, change list and unread regions ride in `runs[0].properties`.
`contracts/evaluator.md` carries the severity-to-level table. `reviews/<slug>.yaml` stays
YAML: its findings are mostly unlocated and gain nothing from SARIF's shape.

**4. API contracts are OpenAPI 3.2 and AsyncAPI 3.1.** `10_blueprint/openapi.yaml` and
`10_blueprint/asyncapi.yaml` are written by `architecture-system` — the first when the
project serves an HTTP API to clients other than its own UI (always for `api-service`), the
second when it publishes or consumes messages on a channel. Before this the `api-service`
profile had no machine-readable interface at all. Payload schemas name entities from
`model.json`; names are read, never coined. `cli-tool` and `library` list both under
`not_grown`, so a hard gate on them cannot arise there. A file a skill writes only under a
condition is not listed in `produces`, because the router and the host call a node done when
every listed path exists; readers gate on it soft. Neither contract is a `produces` entry of
`architecture-system` for that reason, and neither has an artifact id.

**5. Decision records use MADR 4.0.0 vocabulary.** `10_blueprint/decisions.md` and
`11_build/decisions.md` stay single append-only files with tiny entries behind the three-test
gate. The optional lines take MADR's names — `Status`, `Considered Options`, `Consequences` —
and `contracts/domain_model.md` cites MADR 4.0.0. This costs one contract edit and no path.

**6. Architecture is organised by C4 level, with arc42 as a map.** `architecture.md` runs
`System context`, `Containers`, `Components` (only where a container's insides matter),
`Deployment`, `Risks and technical debt`. The external-integration record stays under system
context. arc42 is not adopted as a structure; `contracts/concept_structure.md § arc42 map`
shows where each of its twelve sections lives. The map exposed two gaps — deployment topology
and risks — and the last two sections above close them.

**7. A scaffolded project gets an `AGENTS.md` pointer.** Coding agents outside this collection
load `AGENTS.md` (the Linux Foundation AAIF convention), not `APP-DESIGN.md`, so without a
pointer they never see the interaction rules. When `build-scaffold` creates the project it
writes one line into the root `AGENTS.md`, creating the file if absent, that points to
`APP-DESIGN.md` where that file exists. In a project that existed before scaffolding, skills
leave `AGENTS.md` and `CLAUDE.md` alone and say a link is missing, as `contracts/app_design.md`
already requires.

## Alternatives

**Keep the file where no standard exists.** The glossary stays Markdown: SKOS is RDF with no
consumer here, and Markdown matches arc42 §12 and DDD practice. Behaviours stay state tables:
SCXML's JavaScript tooling is alpha (`@xstate/scxml` 1.0.0-alpha.2), XState is vendor-owned
and moving to v6, and a table carries guards better than a diagram. The acceptance ledger
stays a checkbox file, because the host parser reads the checkbox lines, and neither JUnit XML
(no specification) nor CTRF (pre-1.0) is a standard; a row's evidence pointer may cite either
kind of report. Feature specs stay as they are: Spec Kit, Kiro and OpenSpec are tool
conventions that change quickly, and ours already has their shape — a file per feature, EARS
criteria, tasks kept apart.

**Structurizr DSL for architecture.** A `workspace.dsl` would be a second form of the same
content, worth having only if something renders it. Nothing does.

**MADR per file — `10_blueprint/decisions/NNNN-title.md`.** It would let Structurizr's
`!adrs` and Log4brains render the records. It costs the tree, `produces` and `ops-review`'s
reads, and it creates a `decisions.md` against `decisions/` pair across the two phases.
Not adopted: no renderer is in use. This repo's own `docs/adr/` follows the per-file
convention, which is a different log with a different reader.

**Generate a registry from the schemas.** Rejected on the argument ADR 0013 used against a
generated `artifacts.yaml`: a second copy of the shape needs its own freshness rule.

## Consequences

- **Paths change.** `03_brand/tokens.json` becomes `03_brand/brand.tokens.json`, with two
  optional siblings; `11_build/interaction.yaml` becomes `11_build/interaction.sarif`;
  `10_blueprint/` gains two optional files. `contracts/concept_structure.md`'s tree fence
  lists all of them, because `check.py` rejects a `produces` path that is not in it.
  `contracts/` goes from sixteen files to seventeen (`design_tokens.md`) and gains `schemas/`.
- **ADR 0015 is amended on one path.** `quality-interaction` writes `interaction.sarif`; the
  placement, one-writer and names-are-read rules of that record are untouched.
- **`AGENTS.md` is not a second artifact outside `_concept/`.** It is project code that a
  scaffold writes, like `package.json`, and no skill lists it under `produces`, so ADR 0015's
  rule — one named artifact beside `_concept/`, `APP-DESIGN.md` — holds.
- **Host reads still to switch, named and not fixed here.** In `forge`: the `BrandTokens`
  TypeBox copy and the `seed.ts` copy of the seed shape read the pre-DTCG token keys and a
  private seed shape, so they diverge from the schemas until they take them; and the coverage
  page reads `_implementation/` paths where this collection writes `_concept/11_build/`
  (`review-coverage.ts`). Each is a one-sided dependency the way ADR 0013 records
  `produced_by`: this collection does not change the host, and `verify_host.py` is where a
  `host_facts.py` row makes the gap visible.
- **Existing projects are not migrated.** A project with `tokens.json` or `interaction.yaml`
  keeps it. `ops-review`'s `check_concept.py` lists both under its `RETIRED` paths and reports
  them as unowned, naming the replacement, which is the signal to move the content by hand.
  There is no migration tool.
- Every skill that writes a machine file gains a step that cites its schema, and `check.py`
  gains the schema rules and a `produces` check for the new paths; the cost is in the gate,
  not in the skill bodies, which stay under the 140-line ceiling.
