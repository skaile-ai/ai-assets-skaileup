# 01: What the machine layer's public API actually is

**Type:** research
**Blocked by:** None (can start immediately)
**Status:** resolved

## Question

`-mp` may rename skills, restructure domains, and prune contracts freely — but only in the
places nothing outside the collection reads. Establish exactly what the collection's
**public API** is, so later tickets know what is renameable and what is a contract.

Investigate against primary sources (the consuming code, not docs):

- `forge/forge-concept/server/utils/artifact-contract.ts` — which fields of
  `contracts/artifacts.yaml` it reads (`id`, `path`, `kind`, `side`, `produced_by`, …), and
  how it resolves `flow node → data.skill → artifact → path`.
- `forge/forge-concept/server/utils/flow-manager.ts`, `flow-extended-state.ts`,
  `flow-route-choice.ts` — the flow YAML schema actually parsed: which node fields, `group`
  containers, router nodes, `phase`, `parameters`.
- `workspaces/packages/workspaces/factory-assets/connectors/flow/engine/loader.ts` + `types.ts`
  — the second flow consumer; does it agree with forge-concept's schema?
- `workspaces/packages/workspaces/{discovery,cli}` — how skills are discovered and deployed
  (`.skaile/flows`, `.claude/skills`), and whether skill `name:` or directory path is the key.
- `forge/forge-concept/tests/integration/skaileup-flows.test.ts` — the hardcoded flow and
  skill names, i.e. the literal compatibility surface.
- Which frontmatter fields under `metadata:` are read by anything, vs. documentation-only.

## Answer

**Findings:** [`research/01-machine-layer-public-api.md`](../research/01-machine-layer-public-api.md)
on branch `research/machine-layer-api` (committed, not merged, not pushed). Every claim carries a
`path:line` citation against the consuming code, plus one live run of the installed
`@skaile/workspaces@0.48.1` discovery against this repo.

**Verdict — the public API is far smaller than the repo implies.**

Three things are load-bearing:

1. **Skill identity = SKILL.md `name:` frontmatter. Nothing else.** Directory paths carry zero
   identity — verified live: **95 of 95** skills already have `name:` ≠ parent directory name.
   `name` → `.claude/skills/<name>/` → `data.skill` → `produced_by` → `_concept/_grounding/<name>/`.
   Must match `/^[a-z0-9]+(?:-[a-z0-9]+)*$/`.
2. **Flow identity = the `<id>.flow.yaml` stem, inside a directory named `<id>`, with `id: <id>`.**
   Parsed node schema: `id`, `type` ∈ {skill, group, sub-flow, router}, `parentNode`,
   `data.{skill,flow,routes,label,optional,phase,parallel_group,approval.mandatory,overrides}`,
   and `edges[].type` ∈ {flow, parallel, optional}. Plus the top-level `requires:` install
   manifest (`kind:@skaile-ai/name`) — **that one is a hard contract**: it is what makes a flow
   install pull its skills and contracts.
3. **The `_concept/` / `_implementation/` output tree**, parts of which forge-concept hardcodes
   rather than derives (`experience/features/`, `_implementation/trace.yaml`, `impl_status:`).

Two assumed contracts are **not** contracts:

- **`skaile.yaml`'s `assets:` block is dead** — discovery runs in glob mode (no
  `skaile.manifest.yaml`), so frontmatter names win. Proof: it declares `impl-slice-finish`
  while the file says `impl-slice-git-finish`. `-mp` should not reproduce it (the newer
  workspaces *throws* on publication keys in `skaile.yaml`).
- **`contracts/artifacts.yaml` is read only under `skaile install --link`.** The default copy
  install leaves it unreachable from `.skaile/flows/`, so forge-concept silently falls back to
  session-driven node completion. Of its fields only `path`, `produced_by` (first entry =
  canonical) and `kind: durable` are read; `side` is parsed-and-ignored, `description` and
  `version` are not parsed at all.

Free to rename/restructure: all directory paths and `NN_` prefixes, the domain count and
grouping, `metadata.{tags,stage,source,parameters}`, `metadata.artifacts.produces/consumes`,
flow `meta.category` values, `modes:`/`tier_presets:`/`artifact_handoff:`/`next_flows:`,
`data.parameters`/`data.writes`/node geometry, router `condition` strings (never evaluated),
the DSL grammar, and most of `flow.schema.json` (gate nodes, review-loop edges, `data.user_inputs`).

Contract owners: **`@skaile/workspaces`** owns name resolution, deploy layout,
node-kind union, `requires:` install, `metadata.prerequisites`, `metadata.version`.
**`forge-concept`** owns the `data.phase` enum, the phase/domain name-prefix heuristics
(`concept-`/`design-`/`experience-`/`product-spec-`/`mockup-`/`impl-`/`quality`), the
artifacts.yaml reader, the renderer-subfolder matching rule, the `_implementation/` review
artifacts, and the hardcoded test names (`appbuilder-{mvp,simple,standard,complex}`,
`skaileup-slice-{concept,impl}`, `concept-brief`, `concept-goals`).
